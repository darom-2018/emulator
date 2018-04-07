# © 2018 Ernestas Kulik

# This file is part of Darom.

# Darom is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Darom is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Darom.  If not, see <http://www.gnu.org/licenses/>.

from . import cpu
from . import label
from . import program

from ply import lex
from ply.lex import TOKEN

from ply import yacc

import copy


class AssemblerError(Exception):
    def __init__(self, file_name, line, column, message):
        super().__init__('{}:{}:{}: {}'.format(file_name, line, column, message))


class Assembler():
    def __init__(self, cpu):
        self._cpu = cpu
        self._lexer = lex.lex(module=self, debug=True)
        self._parser = yacc.yacc(module=self, debug=True)
        self._labels = {}

    # Lexer
    global _sections
    _sections = {
        'PROGRAM': 'PROGRAM',
        'DATA': 'DATA',
        'CODE': 'CODE',
        'END': 'END'
    }
    tokens = list(_sections.values()) + [
        'BYTE_STRING',
        'COMMENT',
        'ID',
        'INSTRUCTION',
        'INTEGER',
        'LABEL',
        'SECTION',
        'LABEL_REFERENCE',
    ]

    t_ignore = ' \t'

    def _calculate_column(self, t):
        return t.lexpos - self._lexpos

    def t_BYTE_STRING(self, t):
        r'"([^"]*)"'
        try:
            t.value = t.value[1:-1].encode('ascii')
        except UnicodeEncodeError as e:
            raise AssemblerError(
                # Adding 1 to the column index since we slice the string.
                self._file_name, t.lineno, self._calculate_column(t) + 1, str(e)
            )
        return t

    def t_COMMENT(self, t):
        r';.*'
        pass

    def t_INTEGER(self, t):
        r'[\dA-Fa-f]+h|0[Xx][\dA-Fa-f]+|0\d+|\d+'
        if t.value.startswith('0') and not t.value.lower().startswith('0x'):
            t.value = int(t.value, 8)
        elif t.value.endswith('h'):
            t.value = int(t.value[:-1], 16)
        else:
            t.value = int(t.value, 0)
        try:
            t.value = t.value.to_bytes(self._cpu.word_size, byteorder='little')
        except OverflowError as e:
            raise AssemblerError(
                self._file_name, t.lineno, self._calculate_column(t), str(e)
            )
        return t

    def t_ID(self, t):
        r'(?i)@[\da-z]+|[\da-z]+\:|[\da-z]+'
        if t.value.startswith('@'):
            t.type = 'LABEL_REFERENCE'
        if t.value.endswith(':'):
            t.type = 'LABEL'
            t.value = t.value[:-1]
            if t.value in self._labels:
                raise AssemblerError(
                    self._file_name, t.lineno, self._calculate_column(t),
                    'Redefinition of label “{}”'.format(t.value)
                )
            self._labels[t.value] = 0
        else:
            instruction = self._cpu.instruction_set.find_instruction(t.value)
            if instruction is not None:
                t.type = 'INSTRUCTION'
                t.value = copy.deepcopy(instruction)
        return t

    def t_SECTION(self, t):
        r'\$[A-Z]+'
        t.type = _sections.get(t.value[1:])
        return t

    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)
        self._lexpos = t.lexpos

    def t_error(self, t):
        print('Error: {}:{}: Illegal character: {}'.format(t.lineno,
                                                           self._calculate_column(t),
                                                           t.value[0]))

    # Parser
    def p_program(self, p):
        '''
        program : PROGRAM BYTE_STRING DATA data CODE code END
        '''
        p[0] = program.Program(p[2], p[4], p[6])

    def p_data(self, p):
        '''
        data :
             | BYTE_STRING data
             | INTEGER data
        '''
        if len(p) == 1:
            p[0] = []
        else:
            p[0] = [p[1]] + p[2]

    def p_argument(self, p):
        '''
        argument : INTEGER
                 | LABEL_REFERENCE
        '''
        p[0] = p[1]

    def p_instruction(self, p):
        '''
        instruction : INSTRUCTION
                    | INSTRUCTION argument
        '''
        if len(p) == 3:
            p[1].arg = p[2]
        p[0] = p[1]

    def p_labeled_instruction(self, p):
        '''
        labeled_instruction : LABEL instruction
        '''
        p[0] = label.Label(p[1], p[2])

    def p_code(self, p):
        '''
        code :
             | code instruction
             | code labeled_instruction
        '''

        if len(p) == 1:
            p[0] = []
        else:
            p[0] = p[1] + [p[2]]

    def p_error(self, p):
        raise TypeError(
            'Syntax error: token type {} not expected: {}'.format(p.type,
                                                                  p.value)
        )

    def assemble(self, file):
        self._file_name = file.name
        program = yacc.parse(file.read(), lexer=self._lexer)

        offset = 0

        for instruction in program.code:
            if isinstance(instruction, label.Label):
                self._labels[instruction.label] = offset
            offset += self._cpu.instruction_set.instruction_size
            if instruction.takes_args:
                offset += self._cpu.word_size

        offset = 0

        for instruction in program.code:
            offset += self._cpu.instruction_set.instruction_size
            if instruction.takes_args:
                offset += self._cpu.word_size
                if isinstance(instruction.arg, bytes):
                    continue
                if instruction.arg.startswith('@'):
                    label_reference = instruction.arg[1:]
                    if label_reference not in self._labels:
                        raise Exception('Label “{}” not defined'.format(
                            label_reference)
                        )
                    offset_to_label = self._labels.get(label_reference) - offset
                    # Two’s-complement the offset
                    if offset_to_label < 0:
                        offset_to_label += 1
                    instruction.arg = offset_to_label.to_bytes(
                        self._cpu.word_size,
                        byteorder='little',
                        signed=True
                    )
