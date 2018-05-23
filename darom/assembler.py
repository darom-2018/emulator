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

from ply import lex
from ply import yacc

from darom import constants
from darom import instructions
from darom.instruction import Label
from darom.program import Program


class AssemblerError(Exception):
    def __init__(self, file_name, line, column, message):
        super().__init__('{}:{}:{}: {}'.format(file_name, line, column, message))


class Assembler():
    def __init__(self, cpu):
        self._cpu = cpu
        self._labels = {}
        self._lexer = lex.lex(module=self)
        self._lexpos = 0
        self._parser = yacc.yacc(module=self, errorlog=yacc.NullLogger())
        self._file_name = None

    # Lexer
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

    def _calculate_column(self, token):
        return token.lexpos - self._lexpos

    def t_BYTE_STRING(self, token):
        r'"([^"]*)"'

        try:
            token.value = token.value[1:-1].encode('ascii')
        except UnicodeEncodeError as exception:
            raise AssemblerError(
                self._file_name,
                token.lineno,
                # Adding 1 to the column index since we slice the string.
                self._calculate_column(token) + 1, str(exception)
            )
        return token

    def t_COMMENT(self, token):
        r';.*'

        pass

    def t_INTEGER(self, token):
        r'[\dA-Fa-f]+h|0[Xx][\dA-Fa-f]+|0\d+|\d+'

        value = token.value
        if value.startswith('0') and not value.lower().startswith('0x'):
            value = int(value, 8)
        elif value.endswith('h'):
            value = int(value[:-1], 16)
        else:
            value = int(value, 0)

        try:
            token.value = value.to_bytes(
                constants.WORD_SIZE,
                byteorder=constants.BYTE_ORDER
            )
        except OverflowError as exception:
            raise AssemblerError(
                self._file_name,
                token.lineno,
                self._calculate_column(token),
                str(exception)
            )

        return token

    def t_ID(self, token):
        r'(?i)@[\da-z]+|[\da-z]+\:|[\da-z]+'

        if token.value.startswith('@'):
            token.type = 'LABEL_REFERENCE'
        elif token.value.endswith(':'):
            token.type = 'LABEL'
            token.value = token.value[:-1]
            if token.value in self._labels:
                raise AssemblerError(
                    self._file_name,
                    token.lineno,
                    self._calculate_column(token),
                    'Redefinition of label “{}”'.format(token.value)
                )
            self._labels[token.value] = 0
        else:
            token.type = 'INSTRUCTION'

        return token

    def t_SECTION(self, token):
        r'\$[A-Z]+'

        token.type = self._sections.get(token.value[1:])

        return token

    def t_newline(self, token):
        r'\n+'

        token.lexer.lineno += len(token.value)
        self._lexpos = token.lexpos

    def t_error(self, token):
        print(
            'Error: {}:{}: Illegal character: {}'.format(
                token.lineno,
                self._calculate_column(token),
                token.value[0]
            )
        )

    # Parser
    def p_program(self, production):
        '''
        program : PROGRAM BYTE_STRING DATA data CODE code END
        '''

        production[0] = Program(production[2], production[4], production[6])

    def p_data(self, production):
        '''
        data :
             | BYTE_STRING data
             | INTEGER data
        '''

        if len(production) == 1:
            production[0] = []
        else:
            production[0] = [production[1]] + production[2]

    def p_argument(self, production):
        '''
        argument : INTEGER
                 | LABEL_REFERENCE
        '''

        production[0] = production[1]

    def p_instruction(self, production):
        '''
        instruction : INSTRUCTION
                    | INSTRUCTION argument
        '''

        arg = None

        if len(production) == 3:
            arg = production[2]

        production[0] = getattr(instructions, production[1].upper())()
        production[0].arg = arg

    def p_labeled_instruction(self, production):
        '''
        labeled_instruction : LABEL instruction
        '''

        production[0] = Label(production[1], production[2])

    def p_code(self, production):
        '''
        code :
             | code instruction
             | code labeled_instruction
        '''

        if len(production) == 1:
            production[0] = []
        else:
            production[0] = production[1] + [production[2]]

    def p_error(self, production):
        raise TypeError(
            'Syntax error: token type {} not expected: {}'.format(
                production.type,
                production.value
            )
        )

    def assemble_from_data(self, data):
        program = yacc.parse(data, lexer=self._lexer)

        offset = 0

        for instr in program.code:
            if isinstance(instr, Label):
                self._labels[instr.label] = offset

            offset += instr.length

        offset = 0

        for instr in program.code:
            offset += instr.length

            if instr.takes_arg and isinstance(instr.arg, str):
                if instr.arg.startswith('@'):
                    label_reference = instr.arg[1:]
                    if label_reference not in self._labels:
                        raise Exception(
                            'Label “{}” not defined'.format(label_reference)
                        )
                    offset_to_label = self._labels.get(label_reference) - offset
                    instr.arg = offset_to_label.to_bytes(
                        constants.WORD_SIZE,
                        byteorder=constants.BYTE_ORDER,
                        signed=True
                    )

        return program

    def assemble(self, file):
        self._file_name = file.name

        return self.assemble_from_data(file.read())
