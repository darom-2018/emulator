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


class Instruction():
    def __init__(self, code, mnemonic, nargs, args=None, length=-1):
        self._code = code
        self._mnemonic = mnemonic
        self._nargs = nargs
        if args is not None and len(args) > nargs:
            raise Exception(
                'Instruction {} takes {} arguments, but {} were provided'.format(
                    mnemonic, nargs, len(args)
                )
            )
        self._args = args
        self._length = length

    def __repr__(self):
        return '({}, {}, {}, {})'.format(
            self._code, self._mnemonic, self._nargs, self._args
        )

    @property
    def code(self):
        return self._code

    @property
    def mnemonic(self):
        return self._mnemonic

    @property
    def nargs(self):
        return self._nargs

    @property
    def length(self):
        return self._length

    @property
    def supports_args(self):
        return self._nargs > 0

    @property
    def args(self):
        return self._args

    @args.setter
    def args(self, args):
        self._args = args


class InstructionSet():
    def __init__(self, instruction_size, instructions):
        self._instruction_size = instruction_size
        self._instructions = instructions

    @property
    def instruction_size(self):
        return self._instruction_size

    @property
    def instructions(self):
        return self._instructions

    def find_instruction(self, mnemonic):
        return self._instructions.get(mnemonic, None)


class CPU():
    def __init__(self, instruction_set):
        self._instruction_set = instruction_set

    @property
    def instruction_set(self):
        return self._instruction_set

    def run(self, program):
        pass


class HLP(CPU):
    def __init__(self):
        instruction_set = InstructionSet(1, {
            'NOP': Instruction(b'0x00', 'NOP', 0),
            'HALT': Instruction(b'0x01', 'HALT', 0),

            'DUP': Instruction(b'0x10', 'DUP', 0),
            'POP': Instruction(b'0x11', 'POP', 0),
            'POPM': Instruction(b'0x12', 'POPM', 0),
            'PUSH': Instruction(b'0x13', 'PUSH', 1),
            'PUSHM': Instruction(b'0x14', 'PUSHM', 0),
            'PUSHF': Instruction(b'0x15', 'PUSHF', 0),
            'PUSHDS': Instruction(b'0x16', 'PUSHDS', 0),

            'ADD': Instruction(b'0x20', 'ADD', 0),
            'CMP': Instruction(b'0x21', 'CMP', 0),
            'DEC': Instruction(b'0x22', 'DEC', 0),
            'DIV': Instruction(b'0x23', 'DIV', 0),
            'INC': Instruction(b'0x24', 'INC', 0),
            'MUL': Instruction(b'0x25', 'MUL', 0),
            'SUB': Instruction(b'0x26', 'SUB', 0),

            'AND': Instruction(b'0x30', 'AND', 0),
            'NOT': Instruction(b'0x31', 'NOT', 0),
            'OR': Instruction(b'0x32', 'OR', 0),
            'XOR': Instruction(b'0x33', 'XOR', 0),

            'JMP': Instruction(b'0x40', 'JMP', 0),
            'JC': Instruction(b'0x41', 'JC', 0),
            'JE': Instruction(b'0x42', 'JE', 0),
            'JG': Instruction(b'0x43', 'JG', 0),
            'JGE': Instruction(b'0x44', 'JGE', 0),
            'JL': Instruction(b'0x45', 'JL', 0),
            'JLE': Instruction(b'0x46', 'JLE', 0),
            'JNC': Instruction(b'0x47', 'JNC', 0),
            'JNE': Instruction(b'0x48', 'JNE', 0),
            'JNP': Instruction(b'0x49', 'JNP', 0),
            'JP': Instruction(b'0x4A', 'JP', 0),
            'LOOP': Instruction(b'0x4B', 'LOOP', 0),

            'IN': Instruction(b'0x50', 'IN', 0),
            'INI': Instruction(b'0x51', 'INI', 0),
            'OUT': Instruction(b'0x52', 'OUT', 0),
            'OUTI': Instruction(b'0x53', 'OUTI', 0),

            'SHREAD': Instruction(b'0x60', 'SHREAD', 0),
            'SHWRITE': Instruction(b'0x61', 'SHWRITE', 0),
            'SHLOCK': Instruction(b'0x62', 'SHLOCK', 0),

            'LED': Instruction(b'0x70', 'LED', 0),
        })
        CPU.__init__(self, instruction_set)
