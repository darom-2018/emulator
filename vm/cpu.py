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
    def __init__(self, code, mnemonic, takes_args=False, arg=None, length=-1):
        self._code = code
        self._mnemonic = mnemonic
        self._takes_args = takes_args
        if not self.takes_args and arg is not None:
            raise Exception(
                'Instruction {} does not take arguments'.format(self.mnemonic)
            )
        self._arg = arg
        self._length = length

    def __repr__(self):
        return '({}, {}, {}, {})'.format(
            self._code, self._mnemonic, self._takes_args, self._arg
        )

    @property
    def code(self):
        return self._code

    @property
    def mnemonic(self):
        return self._mnemonic

    @property
    def takes_args(self):
        return self._takes_args

    @property
    def arg(self):
        return self._arg

    @arg.setter
    def arg(self, arg):
        if not self.takes_args:
            raise Exception(
                'Instruction {} does not take arguments'.format(self.mnemonic)
            )
        self._arg = arg

    @property
    def length(self):
        return self._length


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
    def __init__(self, instruction_set, word_size=2):
        self._instruction_set = instruction_set
        self._word_size = word_size

    @property
    def instruction_set(self):
        return self._instruction_set

    @property
    def word_size(self):
        return self._word_size

    def run(self, program):
        pass


class HLP(CPU):
    def __init__(self):
        instruction_set = InstructionSet(1, {
            'NOP': Instruction(b'0x00', 'NOP'),
            'HALT': Instruction(b'0x01', 'HALT'),

            'DUP': Instruction(b'0x10', 'DUP'),
            'POP': Instruction(b'0x11', 'POP'),
            'POPM': Instruction(b'0x12', 'POPM'),
            'PUSH': Instruction(b'0x13', 'PUSH', takes_args=True),
            'PUSHM': Instruction(b'0x14', 'PUSHM'),
            'PUSHF': Instruction(b'0x15', 'PUSHF'),
            'PUSHDS': Instruction(b'0x16', 'PUSHDS'),

            'ADD': Instruction(b'0x20', 'ADD'),
            'CMP': Instruction(b'0x21', 'CMP'),
            'DEC': Instruction(b'0x22', 'DEC'),
            'DIV': Instruction(b'0x23', 'DIV'),
            'INC': Instruction(b'0x24', 'INC'),
            'MUL': Instruction(b'0x25', 'MUL'),
            'SUB': Instruction(b'0x26', 'SUB'),

            'AND': Instruction(b'0x30', 'AND'),
            'NOT': Instruction(b'0x31', 'NOT'),
            'OR': Instruction(b'0x32', 'OR'),
            'XOR': Instruction(b'0x33', 'XOR'),

            'JMP': Instruction(b'0x40', 'JMP'),
            'JC': Instruction(b'0x41', 'JC'),
            'JE': Instruction(b'0x42', 'JE'),
            'JG': Instruction(b'0x43', 'JG'),
            'JGE': Instruction(b'0x44', 'JGE'),
            'JL': Instruction(b'0x45', 'JL'),
            'JLE': Instruction(b'0x46', 'JLE'),
            'JNC': Instruction(b'0x47', 'JNC'),
            'JNE': Instruction(b'0x48', 'JNE'),
            'JNP': Instruction(b'0x49', 'JNP'),
            'JP': Instruction(b'0x4A', 'JP'),
            'LOOP': Instruction(b'0x4B', 'LOOP'),

            'IN': Instruction(b'0x50', 'IN'),
            'INI': Instruction(b'0x51', 'INI'),
            'OUT': Instruction(b'0x52', 'OUT'),
            'OUTI': Instruction(b'0x53', 'OUTI'),

            'SHREAD': Instruction(b'0x60', 'SHREAD'),
            'SHWRITE': Instruction(b'0x61', 'SHWRITE'),
            'SHLOCK': Instruction(b'0x62', 'SHLOCK'),

            'LED': Instruction(b'0x70', 'LED'),
        })
        CPU.__init__(self, instruction_set)
