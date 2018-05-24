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

import operator

from darom import constants
from darom import instruction
from darom import util


class NOP(instruction.Instruction):
    def __init__(self):
        super().__init__(b'\x00', 'NOP')


class HALT(instruction.Instruction):
    def __init__(self):
        super().__init__(b'\x01', 'HALT')

    def execute(self, virtual_machine):
        virtual_machine.real_machine.cpu.si = 1


class DUP(instruction.Instruction):
    def __init__(self):
        super().__init__(b'\x10', 'DUP')

    def execute(self, virtual_machine):
        head = virtual_machine.real_machine.memory.read_word(
            virtual_machine.cpu.sp - constants.WORD_SIZE, virtual=True
        )
        virtual_machine.real_machine.memory.write_word(
            virtual_machine.cpu.sp, head, virtual=True)
        virtual_machine.cpu.sp += constants.WORD_SIZE


class POP(instruction.Instruction):
    def __init__(self):
        super().__init__(b'\x11', 'POP')

    def execute(self, virtual_machine):
        virtual_machine.stack_pop()


class POPM(instruction.Instruction):
    def __init__(self):
        super().__init__(b'\x12', 'POPM')

    def execute(self, virtual_machine):
        word = int.from_bytes(
            virtual_machine.stack_pop(),
            byteorder=constants.BYTE_ORDER)
        page = int.from_bytes(
            virtual_machine.stack_pop(),
            byteorder=constants.BYTE_ORDER)
        head = virtual_machine.stack_pop()

        byte_address = util.to_byte_address(page, word)

        virtual_machine.real_machine.memory.write_word(byte_address, head)


class PUSH(instruction.Instruction):
    def __init__(self):
        super().__init__(b'\x13', 'PUSH', takes_arg=True)

    def execute(self, virtual_machine):
        virtual_machine.stack_push(self.arg)


class PUSHM(instruction.Instruction):
    def __init__(self):
        super().__init__(b'\x14', 'PUSHM')

    def execute(self, virtual_machine):
        word = int.from_bytes(
            virtual_machine.stack_pop(),
            byteorder=constants.BYTE_ORDER
        )
        page = int.from_bytes(
            virtual_machine.stack_pop(),
            byteorder=constants.BYTE_ORDER
        )

        byte_address = util.to_byte_address(page, word)

        word = virtual_machine.real_machine.memory.read_word(
            byte_address, virtual=True
        )

        virtual_machine.stack_push(word)


class PUSHF(instruction.Instruction):
    def __init__(self):
        super().__init__(b'\x15', 'PUSHF')

    def execute(self, virtual_machine):
        virtual_machine.stack_push(virtual_machine.cpu.flags)


class PUSHDS(instruction.Instruction):
    def __init__(self):
        super().__init__(b'\x16', 'PUSHDS')

    def execute(self, virtual_machine):
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

    def execute(self, virtual_machine):
        pass


class DIV(instruction.BinaryOperation):
    def __init__(self):
        super().__init__(b'\x23', 'DIV', operator.floordiv)


class INC(instruction.Instruction):
    def __init__(self):
        super().__init__(b'\x24', 'INC')

    def execute(self, virtual_machine):
        word = int.from_bytes(
            virtual_machine.stack_pop(), byteorder=constants.BYTE_ORDER
        )
        word += 1

        virtual_machine.stack_push(
            word.to_bytes(constants.WORD_SIZE, byteorder=constants.BYTE_ORDER)
        )


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

    def execute(self, virtual_machine):
        head = int.from_bytes(
            virtual_machine.stack_pop(),
            byteorder=constants.BYTE_ORDER)
        result = (head ^ constants.WORD_MAX) & constants.WORD_MAX

        virtual_machine.stack_push(
            result.to_bytes(
                constants.WORD_SIZE,
                byteorder=constants.BYTE_ORDER))


class OR(instruction.BinaryOperation):
    def __init__(self):
        super().__init__(b'\x32', 'OR', operator.or_)


class XOR(instruction.BinaryOperation):
    def __init__(self):
        super().__init__(b'\x33', 'XOR', operator.xor)


def _jmp(instruction, virtual_machine, offset):
    # The offset is calculated from the beginning of the instruction.
    # but PC will have been incremented after executing JMP.
    offset = int.from_bytes(
        offset,
        byteorder=constants.BYTE_ORDER,
        signed=True)
    virtual_machine.cpu.pc += offset - instruction.length


class JMP(instruction.Instruction):
    def __init__(self):
        super().__init__(b'\x40', 'JMP')

    def execute(self, virtual_machine):
        offset = virtual_machine.stack_pop()
        _jmp(self, virtual_machine, offset)


class JC(instruction.Instruction):
    def __init__(self):
        super().__init__(b'\x41', 'JC')

    def execute(self, virtual_machine):
        cf, pf, zf = virtual_machine.cpu.test_flags()
        if cf:
            JMP().execute(virtual_machine)


class JE(instruction.Instruction):
    def __init__(self):
        super().__init__(b'\x42', 'JE')

    def execute(self, virtual_machine):
        cf, pf, zf = virtual_machine.cpu.test_flags()
        if zf:
            JMP().execute(virtual_machine)


class JG(instruction.Instruction):
    def __init__(self):
        super().__init__(b'\x43', 'JG')

    def execute(self, virtual_machine):
        cf, pf, zf = virtual_machine.cpu.test_flags()
        if not zf and cf:
            JMP().execute(virtual_machine)


class JGE(instruction.Instruction):
    def __init__(self):
        super().__init__(b'\x44', 'JGE')

    def execute(self, virtual_machine):
        cf, pf, zf = virtual_machine.cpu.test_flags()
        if (not zf and cf) or zf:
            JMP().execute(virtual_machine)


class JL(instruction.Instruction):
    def __init__(self):
        super().__init__(b'\x45', 'JL')

    def execute(self, virtual_machine):
        cf, pf, zf = virtual_machine.cpu.test_flags()
        if not zf and not cf:
            JMP().execute(virtual_machine)


class JLE(instruction.Instruction):
    def __init__(self):
        super().__init__(b'\x46', 'JLE')

    def execute(self, virtual_machine):
        cf, pf, zf = virtual_machine.cpu.test_flags()
        if (not zf and not cf) or zf:
            JMP().execute(virtual_machine)


class JNC(instruction.Instruction):
    def __init__(self):
        super().__init__(b'\x47', 'JNC')

    def execute(self, virtual_machine):
        cf, pf, zf = virtual_machine.cpu.test_flags()
        if not cf:
            JMP().execute(virtual_machine)


class JNE(instruction.Instruction):
    def __init__(self):
        super().__init__(b'\x48', 'JNE')

    def execute(self, virtual_machine):
        cf, pf, zf = virtual_machine.cpu.test_flags()
        if not zf:
            JMP().execute(virtual_machine)


class JNP(instruction.Instruction):
    def __init__(self):
        super().__init__(b'\x49', 'JNP')

    def execute(self, virtual_machine):
        cf, pf, zf = virtual_machine.cpu.test_flags()
        if not pf:
            JMP().execute(virtual_machine)


class JP(instruction.Instruction):
    def __init__(self):
        super().__init__(b'\x4A', 'JP')

    def execute(self, virtual_machine):
        cf, pf, zf = virtual_machine.cpu.test_flags()
        if pf:
            JMP().execute(virtual_machine)


class LOOP(instruction.Instruction):
    def __init__(self):
        super().__init__(b'\x4B', 'LOOP')

    def execute(self, virtual_machine):
        offset = virtual_machine.stack_pop()
        counter = int.from_bytes(
            virtual_machine.stack_pop(),
            byteorder=constants.BYTE_ORDER
        )
        if not counter > 0:
            return
        counter -= 1
        virtual_machine.stack_push(
            counter.to_bytes(
                constants.WORD_SIZE,
                byteorder=constants.BYTE_ORDER
            )
        )
        _jmp(self, virtual_machine, offset)


class IN(instruction.Instruction):
    def __init__(self):
        super().__init__(b'\x50', 'IN')

    def execute(self, virtual_machine):
        virtual_machine.real_machine.cpu.si = 2


class INI(instruction.IOInstruction):
    def __init__(self):
        super().__init__(b'\x51', 'INI')

    def execute(self, virtual_machine):
        virtual_machine.real_machine.cpu.si = 3


class OUT(instruction.IOInstruction):
    def __init__(self):
        super().__init__(b'\x52', 'OUT')

    def execute(self, virtual_machine):
        virtual_machine.real_machine.cpu.si = 4


class OUTI(instruction.IOInstruction):
    def __init__(self):
        super().__init__(b'\x53', 'OUTI')

    def execute(self, virtual_machine):
        virtual_machine.real_machine.cpu.si = 5


class SHREAD(instruction.Instruction):
    def __init__(self):
        super().__init__(b'\x60', 'SHREAD')

    def execute(self, virtual_machine):
        virtual_machine.real_machine.cpu.si = 6


class SHWRITE(instruction.Instruction):
    def __init__(self):
        super().__init__(b'\x61', 'SHWRITE')

    def execute(self, virtual_machine):
        virtual_machine.real_machine.cpu.si = 7


class SHLOCK(instruction.Instruction):
    def __init__(self):
        super().__init__(b'\x62', 'SHLOCK')

    def execute(self, virtual_machine):
        virtual_machine.real_machine.cpu.si = 8


class SHUNLOCK(instruction.Instruction):
    def __init__(self):
        super().__init__(b'\x63', 'SHUNLOCK')

    def execute(self, virtual_machine):
        virtual_machine.real_machine.cpu.si = 9


class LED(instruction.Instruction):
    def __init__(self):
        super().__init__(b'\x70', 'LED')

    def execute(self, virtual_machine):
        virtual_machine.real_machine.cpu.si = 10
