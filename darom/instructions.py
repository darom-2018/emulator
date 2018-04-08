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

from . import constants
from . import instruction

import operator


class NOP(instruction.Instruction):
    def __init__(self):
        super().__init__(b'\x00', 'NOP')


class HALT(instruction.Instruction):
    def __init__(self):
        super().__init__(b'\x01', 'HALT')

    def execute(self, vm):
        vm.cpu.halt()


class DUP(instruction.Instruction):
    def __init__(self):
        super().__init__(b'\x10', 'DUP')

    def execute(self, vm):
        allocation = vm.rm.get_memory_allocation_for_vm(vm)
        head = vm.rm.memory.read_word(allocation, vm.cpu.sp)
        vm.cpu.sp += vm.rm.cpu.word_size
        vm.rm.memory.write_word(allocation, vm.cpu.sp, head)


class POP(instruction.Instruction):
    def __init__(self):
        super().__init__(b'\x11', 'POP')

    def execute(self, vm):
        vm.stack_pop()


def to_byte_address(vm, block, word):
    return (
        vm.cpu.ds +
        (block * vm.rm.memory.block_size * vm.rm.cpu.word_size) +
        (word * vm.rm.cpu.word_size)
    )


class POPM(instruction.Instruction):
    def __init__(self):
        super().__init__(b'\x12', 'POPM')

    def execute(self, vm):
        word = int.from_bytes(vm.stack_pop(), byteorder='little')
        block = int.from_bytes(vm.stack_pop(), byteorder='little')
        head = vm.stack_pop()

        vm.rm.memory.write_word(vm.memory, to_byte_address(vm, block, word), head)


class PUSH(instruction.Instruction):
    def __init__(self):
        super().__init__(b'\x13', 'PUSH', takes_arg=True)

    def execute(self, vm):
        vm.stack_push(self.arg)


class PUSHM(instruction.Instruction):
    def __init__(self):
        super().__init__(b'\x14', 'PUSHM')

    def execute(self, vm):
        word = int.from_bytes(vm.stack_pop(), byteorder='little')
        block = int.from_bytes(vm.stack_pop(), byteorder='little')

        word = vm.rm.memory.read_word(vm.memory, to_bytes(vm, block, word))
        vm.stack_push(word)


class PUSHF(instruction.Instruction):
    def __init__(self):
        super().__init__(b'\x15', 'PUSHF')

    def execute(self, vm):
        vm.stack_push(vm.cpu.flags)


class PUSHDS(instruction.Instruction):
    def __init__(self):
        super().__init__(b'\x16', 'PUSHDS')

    def execute(self, vm):
        pass


class ADD(instruction.BinaryOperation):
    def __init__(self):
        super().__init__(b'\x20', 'ADD', operator.add)


class CMP(instruction.BinaryOperation):
    def __init__(self):
        super().__init__(b'\x21', 'CMP', operator.sub)


class DEC(instruction.Instruction):
    def __init__(self):
        super().__init__(b'\x22', 'DEC')

    def execute(self, vm):
        pass


class DIV(instruction.BinaryOperation):
    def __init__(self):
        super().__init__(b'\x23', 'DIV', operator.floordiv)


class INC(instruction.Instruction):
    def __init__(self):
        super().__init__(b'\x24', 'INC')

    def execute(self, vm):
        pass


class MUL(instruction.BinaryOperation):
    def __init__(self):
        super().__init__(b'\x25', 'MUL', operator.mul)


class SUB(instruction.BinaryOperation):
    def __init__(self):
        super().__init__(b'\x26', 'SUB', operator.sub)


class AND(instruction.BinaryOperation):
    def __init__(self):
        super().__init__(b'\x30', 'AND', operator.and_)


class NOT(instruction.Instruction):
    def __init__(self):
        super().__init__(b'\x31', 'NOT')

    def execute(self, vm):
        head = int.from_bytes(vm.stack_pop(), byteorder='little')
        result = (head ^ constants.WORD_MAX) & constants.WORD_MAX

        vm.stack_push(result.to_bytes(vm.rm.cpu.word_size, byteorder='little'))


class OR(instruction.BinaryOperation):
    def __init__(self):
        super().__init__(b'\x32', 'OR', operator.or_)


class XOR(instruction.BinaryOperation):
    def __init__(self):
        super().__init__(b'\x33', 'XOR', operator.xor)


def _jmp(instruction, vm, offset):
    # The offset is calculated from the beginning of the instruction.
    # but PC will have been incremented after executing JMP.
    offset = int.from_bytes(offset, byteorder='little', signed=True)
    vm.cpu.pc += offset - instruction.length


class JMP(instruction.Instruction):
    def __init__(self):
        super().__init__(b'\x40', 'JMP')

    def execute(self, vm):
        offset = vm.stack_pop()
        _jmp(self, vm, offset)


class JC(instruction.Instruction):
    def __init__(self):
        super().__init__(b'\x41', 'JC')

    def execute(self, vm):
        cf, pf, zf = vm.cpu.test_flags()
        if cf:
            JMP().execute(vm)


class JE(instruction.Instruction):
    def __init__(self):
        super().__init__(b'\x42', 'JE')

    def execute(self, vm):
        cf, pf, zf = vm.cpu.test_flags()
        if zf:
            JMP().execute(vm)


class JG(instruction.Instruction):
    def __init__(self):
        super().__init__(b'\x43', 'JG')

    def execute(self, vm):
        cf, pf, zf = vm.cpu.test_flags()
        if not zf and cf:
            JMP().execute(vm)


class JGE(instruction.Instruction):
    def __init__(self):
        super().__init__(b'\x44', 'JGE')

    def execute(self, vm):
        cf, pf, zf = vm.cpu.test_flags()
        if (not zf and cf) or zf:
            JMP().execute(vm)


class JL(instruction.Instruction):
    def __init__(self):
        super().__init__(b'\x45', 'JL')

    def execute(self, vm):
        cf, pf, zf = vm.cpu.test_flags()
        if not zf and not cf:
            JMP().execute(vm)


class JLE(instruction.Instruction):
    def __init__(self):
        super().__init__(b'\x46', 'JLE')

    def execute(self, vm):
        cf, pf, zf = vm.cpu.test_flags()
        if (not zf and not cf) or zf:
            JMP().execute(vm)


class JNC(instruction.Instruction):
    def __init__(self):
        super().__init__(b'\x47', 'JNC')

    def execute(self, vm):
        cf, pf, zf = vm.cpu.test_flags()
        if not cf:
            JMP().execute(vm)


class JNE(instruction.Instruction):
    def __init__(self):
        super().__init__(b'\x48', 'JNE')

    def execute(self, vm):
        cf, pf, zf = vm.cpu.test_flags()
        if not zf:
            JMP().execute(vm)


class JNP(instruction.Instruction):
    def __init__(self):
        super().__init__(b'\x49', 'JNP')

    def execute(self, vm):
        cf, pf, zf = vm.cpu.test_flags()
        if not pf:
            JMP().execute(vm)


class JP(instruction.Instruction):
    def __init__(self):
        super().__init__(b'\x4A', 'JP')

    def execute(self, vm):
        cf, pf, zf = vm.cpu.test_flags()
        if pf:
            JMP().execute(vm)


class LOOP(instruction.Instruction):
    def __init__(self):
        super().__init__(b'\x4B', 'LOOP')

    def execute(self, vm):
        offset = vm.stack_pop()
        counter = int.from_bytes(vm.stack_pop(), byteorder='little')
        if not counter > 0:
            return
        counter -= 1
        vm.stack_push(counter.to_bytes(constants.WORD_SIZE, byteorder='little'))
        _jmp(self, vm, offset)

class IN(instruction.Instruction):
    def __init__(self):
        super().__init__(b'\x50', 'IN')

    def execute(self, vm):
        pass


class INI(instruction.Instruction):
    def __init__(self):
        super().__init__(b'\x51', 'INI')

    def execute(self, vm):
        pass


class OUT(instruction.Instruction):
    def __init__(self):
        super().__init__(b'\x52', 'OUT')

    def execute(self, vm):
        block = int.from_bytes(vm.stack_pop(), byteorder='little')
        word = int.from_bytes(vm.stack_pop(), byteorder='little')
        character_count = int.from_bytes(vm.stack_pop(), byteorder='little')
        string = bytes()
        for i in range(character_count):
            address = vm.cpu.ds + vm.rm.memory.translate_address(block, word)
            string += vm.rm.memory.read_byte(vm.memory, address + i)
        print(string.decode('ascii'))


class OUTI(instruction.Instruction):
    def __init__(self):
        super().__init__(b'\x53', 'OUTI')

    def execute(self, vm):
        pass


class SHREAD(instruction.Instruction):
    def __init__(self):
        super().__init__(b'\x60', 'SHREAD')

    def execute(self, vm):
        pass


class SHWRITE(instruction.Instruction):
    def __init__(self):
        super().__init__(b'\x61', 'SHWRITE')

    def execute(self, vm):
        pass


class SHLOCK(instruction.Instruction):
    def __init__(self):
        super().__init__(b'\x62', 'SHLOCK')

    def execute(self, vm):
        pass


class LED(instruction.Instruction):
    def __init__(self):
        super().__init__(b'\x70', 'LED')

    def execute(self, vm):
        pass
