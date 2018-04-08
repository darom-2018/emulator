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

        self._CF = 0
        self._ZF = 0
        self._PF = 0

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
        self._memory.dump(5)

    def load_program(self, program):
        program_len = self.load_code(program.code)
        # SP nustatom i pirma bloka, uz kodo segmento
        self._SP = ((program_len // self._memory.bytes) + 1) * self._memory.bytes
        # DS nustatom iskart uz steko (du blokai)
        self._DS = (program_len // self._memory.bytes) + 3
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
        address = self.DS * self._memory.bytes
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
            print(self._PC, end='\t')
            instr = self.get_instruction()
            print(instr.mnemonic, end='\t')
            if instr.takes_args:
                print(int.from_bytes(instr.arg, 'little', signed=True))
            else:
                print()
            self.execute_instruction(instr)

    def get_instruction(self):
        pc = self.PC
        instr_code = self.read_memory(pc)
        print(instr_code, end='\t')
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

    def write_word_to_memory(self, relative_address, word):
        absolute_address = relative_address
        self._memory.write(absolute_address, bytes([word[0]]))
        self._memory.write(absolute_address + 1, bytes([word[1]]))

    def read_memory(self, relative_address):
        if isinstance(relative_address, bytes):
            absolute_address = int.from_bytes(relative_address, 'little')
        else:
            absolute_address = relative_address
        # atlikti transliacija
        return self._memory.read(absolute_address)

    def read_memory_word(self, relative_addres):
        lower_byte = self.read_memory(relative_addres)
        upper_byte = self.read_memory(relative_addres + 1)
        return lower_byte + upper_byte

    # kai bus FLAGS registras reikes pakeisti, kad dirbtu su juo
    def set_CF(self, value):
        self._CF = value

    def get_CF(self):
        return self._CF

    def set_ZF(self, value):
        self._ZF = value

    def get_ZF(self):
        return self._ZF

    def set_PF(self, value):
        self._PF = value

    def get_PF(self):
        return self._PF

    def dump_flags(self):
        print("CF: {}\nZF: {}\nPF: {}".format(self.get_CF(), self.get_ZF(), self.get_PF()))


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

        if mnemonic == 'NOP':
            self.Nop()
        elif mnemonic == 'HALT':
            self.Halt()
        elif mnemonic == 'DUP':
            self.Dup()
        elif mnemonic == 'POP':
            self.Pop()
        elif mnemonic == 'POPM':
            self.Popm()
        elif mnemonic == 'PUSH':
            self.Push(instr.arg)
        elif mnemonic == 'PUSHM':
            self.Pushm()
        elif mnemonic == 'PUSHF':
            self.Pushf()
        elif mnemonic == 'PUSHDS':
            self.Pushds()
        elif mnemonic == 'ADD':
            self.Add()
        elif mnemonic == 'CMP':
            self.Cmp()
        elif mnemonic == 'DEC':
            self.Dec()
        elif mnemonic == 'DIV':
            self.Div()
        elif mnemonic == 'INC':
            self.Inc()
        elif mnemonic == 'MUL':
            self.Mul()
        elif mnemonic == 'SUB':
            self.Sub()
        elif mnemonic == 'AND':
            self.And()
        elif mnemonic == 'NOT':
            self.Not()
        elif mnemonic == 'OR':
            self.Or()
        elif mnemonic == 'XOR':
            self.Xor()
        elif mnemonic == 'JMP':
            self.Jmp()
        elif mnemonic == 'JC':
            self.Jc()
        elif mnemonic == 'JE':
            self.Je()
        elif mnemonic == 'JG':
            self.Jg()
        elif mnemonic == 'JGE':
            self.Jge()
        elif mnemonic == 'JL':
            self.Jl()
        elif mnemonic == 'JLE':
            self.Jle()
        elif mnemonic == 'JNC':
            self.Jnc()
        elif mnemonic == 'JNE':
            self.Jne()
        elif mnemonic == 'JNP':
            self.Jnp()
        elif mnemonic == 'JP':
            self.Jp()
        elif mnemonic == 'LOOP':
            self.Loop()
        elif mnemonic == 'IN':
            self.In()
        elif mnemonic == 'INI':
            self.Ini()
        elif mnemonic == 'OUT':
            self.Out()
        elif mnemonic == 'OUTI':
            self.Outi()
        elif mnemonic == 'SHREAD':
            self.Shread()
        elif mnemonic == 'SHWRITE':
            self.Shwrite()
        elif mnemonic == 'SHLOCK':
            self.Shlock()
        elif mnemonic == 'LED':
            self.Led()

    def Nop(self):
        self._memory.dump(5)
        return

    def Halt(self):
        pass

    def Dup(self):
        word = self.read_memory_word(self._SP)
        self.Push(word)

    def Pop(self):
        word = self.read_memory_word(self._SP)
        self._SP -= 2
        return word

    def Popm(self):
        word_num = int.from_bytes(self.Pop(), 'little', signed=False)
        block_num = int.from_bytes(self.Pop(), 'little', signed=False)
        data = self.Pop()
        self.write_word_to_memory(
            block_num * self._memory.block_size + word_num * self._memory.word_size,
            data
        )

    def Push(self, word):
        self._SP += 2
        self.write_word_to_memory(self._SP, word)

    def Pushm(self):
        word_num = int.from_bytes(self.Pop(), 'little', signed=False)
        block_num = int.from_bytes(self.Pop(), 'little', signed=False)
        data = self.read_memory_word(
            block_num * self._memory.block_size + word_num * self._memory.word_size
        )
        self.Push(data)

    def Pushf(self):
        pass

    def Pushds(self):
        self.Push(self.to_word(self._DS))

    def Add(self):
        a, b = self.get_two_ints_from_stack()
        try:
            result = a + b
            self.Push(self.to_word(result))
            self.check_flags(result)
        except OverflowError:
            self.set_CF(1)
            self.set_ZF(0)
            # sutalpina per dideli rezultata i viena zodi
            result = (a + b) & int.from_bytes(b'\xff' * self._word_size, 'little')
            self.Push(self.to_word(result))
            self.check_PF(result)

    def Cmp(self):
        self.Sub()

    def Dec(self):
        stack_top = self.get_int_from_stack()
        stack_top -= 1
        try:
            self.Push(self.to_word(stack_top))
            self.check_flags(stack_top)
        except OverflowError:
            self.set_CF(1)
            self.set_ZF(0)
            self.Push(self.to_word(stack_top, signed=True))
            self.check_PF(stack_top)

    def Div(self):
        a, b = self.get_two_ints_from_stack(signed=False)
        result = a // b
        self.Push(self.to_word(result))
        self.check_flags(result)

    def Inc(self):
        self.Push(b'\x01\x00')
        self.Add()

    def Mul(self):
        a, b = self.get_two_ints_from_stack(signed=False)
        try:
            result = a * b
            self.Push(self.to_word(result))
            self.check_flags(result)
        except OverflowError:
            self.set_CF(1)
            self.set_ZF(0)
            # sutalpina per dideli rezultata i viena zodi
            result = (a * b) & int.from_bytes(b'\xff' * self._word_size, 'little')
            self.Push(self.to_word(result))
            self.check_PF(result)

    def Sub(self):
        a, b = self.get_two_ints_from_stack()
        try:
            result = a - b
            self.Push(self.to_word(result))
            self.check_flags(result)
        except OverflowError:
            self.set_CF(1)
            self.set_ZF(0)
            result = (a - b) & int.from_bytes(b'\xff' * self._word_size, 'little')
            self.Push(self.to_word(result))
            self.check_PF(result)

    def And(self):
        a, b = self.get_two_ints_from_stack()
        result = a & b
        self.Push(self.to_word(result))
        self.check_flags(result)

    def Not(self):
        self.Push(b'\xff' * self._memory.word_size)
        self.Xor()

    def Or(self):
        a, b = self.get_two_ints_from_stack()
        result = a | b
        self.Push(self.to_word(result))
        self.check_flags(result)

    def Xor(self):
        a, b = self.get_two_ints_from_stack()
        result = a ^ b
        self.Push(self.to_word(result))
        self.check_flags(result)

    def Jmp(self):
        offset = self.get_int_from_stack(signed=True)
        # hackas, kad veiktu
        if(offset < 0):
            self._PC += offset - 2
        else:
            self._PC += offset - 1

    def Jc(self):
        if self.get_CF() == 1:
            self.Jmp()

    def Je(self):
        if self.get_ZF() == 0:
            self.Jmp()

    def Jg(self):
        if (self.get_ZF() == 0) and (self.get_CF() == 1):
            self.Jmp()

    def Jge(self):
        if ((self.get_ZF() == 0) and (self.get_CF() == 1)) or (self.get_ZF == 1):
            self.Jmp()

    def Jl(self):
        if (self.get_ZF() == 0) and (self.get_CF() == 0):
            self.Jmp()

    def Jle(self):
        if ((self.get_ZF() == 0) and (self.get_CF() == 0)) or (self.get_ZF == 1):
            self.Jmp()

    def Jnc(self):
        if self.get_CF() == 0:
            self.Jmp()

    def Jne(self):
        if self.get_ZF() == 0:
            self.Jmp()

    def Jnp(self):
        if self.get_PF() == 0:
            self.Jmp()

    def Jp(self):
        if self.get_PF() == 1:
            self.Jmp()

    def Loop(self):
        counter = int.from_bytes(self.read_memory_word(self._SP - 2), 'little', signed=False)
        if counter > 0:
            jmp_location = self.Pop()
            self.Dec()  # sumazinam ciklo counteri
            self.Push(jmp_location)
            self.Jmp()
        else:
            self.Pop()
            self.Pop()

    def In(self):
        pass

    def Ini(self):
        pass

    def Out(self):
        pass

    def Outi(self):
        pass

    def Shread(self):
        pass

    def Shwrite(self):
        pass

    def Shlock(self):
        pass

    def Led(self):
        pass

    def check_flags(self, value):
        self.check_PF(value)
        self.check_ZF(value)

    def check_PF(self, number):
        if (number % 2) == 0:
            self.set_PF(1)
        else:
            self.set_PF(0)

    def check_ZF(self, value):
        if value == 0:
            self.set_ZF(1)
        else:
            self.set_ZF(0)

    def get_two_ints_from_stack(self, signed=False):
        a = int.from_bytes(self.Pop(), 'little', signed=signed)
        b = int.from_bytes(self.Pop(), 'little', signed=signed)
        return (a, b)

    def get_int_from_stack(self, signed=False):
        return int.from_bytes(self.Pop(), 'little', signed=signed)

    def to_word(self, int, signed=False):
        return int.to_bytes(2, 'little', signed=signed)
