# © 2018 Ernestas Kulik, Justinas Valatkevičius

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

    @length.setter
    def length(self, len):
        self._length = len


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

    def find_instruction_by_code(self, code):
        for instr in self._instructions.values():
            if (instr.code == code):
                return self.find_instruction(instr.mnemonic)


class CPU():
    def __init__(self, instruction_set, memory, word_size=2):
        self._instruction_set = instruction_set
        self._memory = memory
        self._word_size = word_size
        self._PC = 0
        self._DS = 0
        self._SP = 0

    @property
    def instruction_set(self):
        return self._instruction_set

    @property
    def word_size(self):
        return self._word_size

    @property
    def DS(self):
        return self._DS

    @property
    def PC(self):
        return self._PC

    @PC.setter
    def PC(self, pc):
        self._PC = pc

    def PC_inc(self, amount=1):
        self.PC += amount

    def add_int_to_word(self, i, word):
        (int.from_bytes(word, 'little') + i).to_bytes(2, 'little')

    def run(self, program):
        self.load_program(program)
        self._memory.dump(5)
        self.execute_program()

    def load_program(self, program):
        program_len = self.load_code(program.code)
        # DS nustatom i pirma bloka, uz kodo segmento
        self._DS = ((program_len // self._memory.bytes) + 1) * self._memory.bytes
        self.load_data(program.data)

    def load_code(self, code):
        address = 0
        for instr in code:
            self.write_to_memory(address, instr.code)
            if instr.takes_args:
                self.write_to_memory(address + 1, instr.arg[0].to_bytes(1, 'little'))
                if instr.arg.__len__() == 2:
                    self.write_to_memory(address + 2, instr.arg[1].to_bytes(1, 'little'))
                else:
                    self.write_to_memory(address + 2, (0).to_bytes(1, 'little'))
            address += instr.length
        return address

    def load_data(self, program_data):
        address = self.DS
        for data_item in program_data:
            if isinstance(data_item, str):
                for c in data_item:
                    self.write_to_memory(address, bytes(c, 'utf-8'))
                    address += 1
            else:
                for byte in data_item:
                    self.write_to_memory(address, bytes([byte]))
                    address += 1

    def execute_program(self):
        instr = None
        while not (instr == self.instruction_set.find_instruction('HALT')):
            instr = self.get_instruction()
            self.execute_instruction(instr)

    def get_instruction(self):
        pc = self.PC
        instr_code = self.read_memory(pc)
        instr = self._instruction_set.find_instruction_by_code(instr_code)
        if instr.takes_args:
            instr.arg = self.read_memory(pc + 1) + self.read_memory(pc + 2)
            self.PC_inc(2)
        self.PC_inc()
        return instr

    def write_to_memory(self, relative_address, data):
        # todo: padaryti puslapiu transliacija
        absolute_address = relative_address
        self._memory.write(absolute_address, data)

    def read_memory(self, relative_address):
        if isinstance(relative_address, bytes):
            absolute_address = int.from_bytes(relative_address, 'little')
        else:
            absolute_address = relative_address
        # atlikti transliacija
        return self._memory.read(absolute_address)


class HLP(CPU):
    def __init__(self, memory):
        instruction_set = InstructionSet(1, {
            'NOP': Instruction(b'\x00', 'NOP'),
            'HALT': Instruction(b'\x01', 'HALT'),

            'DUP': Instruction(b'\x10', 'DUP'),
            'POP': Instruction(b'\x11', 'POP'),
            'POPM': Instruction(b'\x12', 'POPM'),
            'PUSH': Instruction(b'\x13', 'PUSH', takes_args=True),
            'PUSHM': Instruction(b'\x14', 'PUSHM'),
            'PUSHF': Instruction(b'\x15', 'PUSHF'),
            'PUSHDS': Instruction(b'\x16', 'PUSHDS'),

            'ADD': Instruction(b'\x20', 'ADD'),
            'CMP': Instruction(b'\x21', 'CMP'),
            'DEC': Instruction(b'\x22', 'DEC'),
            'DIV': Instruction(b'\x23', 'DIV'),
            'INC': Instruction(b'\x24', 'INC'),
            'MUL': Instruction(b'\x25', 'MUL'),
            'SUB': Instruction(b'\x26', 'SUB'),

            'AND': Instruction(b'\x30', 'AND'),
            'NOT': Instruction(b'\x31', 'NOT'),
            'OR': Instruction(b'\x32', 'OR'),
            'XOR': Instruction(b'\x33', 'XOR'),

            'JMP': Instruction(b'\x40', 'JMP'),
            'JC': Instruction(b'\x41', 'JC'),
            'JE': Instruction(b'\x42', 'JE'),
            'JG': Instruction(b'\x43', 'JG'),
            'JGE': Instruction(b'\x44', 'JGE'),
            'JL': Instruction(b'\x45', 'JL'),
            'JLE': Instruction(b'\x46', 'JLE'),
            'JNC': Instruction(b'\x47', 'JNC'),
            'JNE': Instruction(b'\x48', 'JNE'),
            'JNP': Instruction(b'\x49', 'JNP'),
            'JP': Instruction(b'\x4A', 'JP'),
            'LOOP': Instruction(b'\x4B', 'LOOP'),

            'IN': Instruction(b'\x50', 'IN'),
            'INI': Instruction(b'\x51', 'INI'),
            'OUT': Instruction(b'\x52', 'OUT'),
            'OUTI': Instruction(b'\x53', 'OUTI'),

            'SHREAD': Instruction(b'\x60', 'SHREAD'),
            'SHWRITE': Instruction(b'\x61', 'SHWRITE'),
            'SHLOCK': Instruction(b'\x62', 'SHLOCK'),

            'LED': Instruction(b'\x70', 'LED'),
        })
        CPU.__init__(self, instruction_set, memory)

    def execute_instruction(self, instr):
        mnemonic = instr.mnemonic
        print(mnemonic)
