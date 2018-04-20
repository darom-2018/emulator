# © 2018 Justinas Valatkevičius

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


def incorrect_instruction_code(rm):
    print("INCORRECT_INSTRUCTION_CODE")
    rm._vm.cpu.halt()


def incorrect_operand(rm):
    print("INCORRECT_OPERAND")
    rm._vm.cpu.halt()


def paging_error(rm):
    print("PAGING_ERROR")
    rm._vm.cpu.halt()


def stack_overflow(rm):
    print("STACK_OVERFLOW")
    rm._vm.cpu.halt()


def instr_halt(rm):
    rm._vm.cpu.halt()
    print("HALTED")


def instr_in(rm):
    block = int.from_bytes(rm._vm.stack_pop(), byteorder='little')
    word = int.from_bytes(rm._vm.stack_pop(), byteorder='little')
    character_count = int.from_bytes(rm._vm.stack_pop(), byteorder='little')


def instr_ini(rm):
    block = int.from_bytes(rm._vm.stack_pop(), byteorder='little')
    word = int.from_bytes(rm._vm.stack_pop(), byteorder='little')
    character_count = int.from_bytes(rm._vm.stack_pop(), byteorder='little')


def instr_out(rm):
    block = int.from_bytes(rm._vm.stack_pop(), byteorder='little')
    word = int.from_bytes(rm._vm.stack_pop(), byteorder='little')
    character_count = int.from_bytes(rm._vm.stack_pop(), byteorder='little')
    string = bytes()
    for i in range(character_count):
        address = rm._vm.cpu.ds + rm.memory.translate_address(block, word)
        string += rm.memory.read_byte(rm._vm.memory, address + i)
    print(string.decode('ascii'))


def instr_outi(rm):
    word = int.from_bytes(rm._vm.stack_pop(), byteorder='little')
    print(word)


def instr_shread(rm):
    word_count = int.from_bytes(rm._vm.stack_pop(), byteorder='little')
    dst_word = int.from_bytes(rm._vm.stack_pop(), byteorder='little')
    dst_block = int.from_bytes(rm._vm.stack_pop(), byteorder='little')
    shared_word = int.from_bytes(rm._vm.stack_pop(), byteorder='little')
    shared_block = int.from_bytes(rm._vm.stack_pop(), byteorder='little')

    dst_address = rm.memory.translate_address(dst_block, dst_word)
    shared_address = rm.memory.translate_address(shared_block, shared_word)

    for i in range(word_count):
        word = rm.memory.read_word(rm.shared_memory, shared_address + (i * constants.WORD_SIZE))
        rm.memory.write_word(rm._vm.memory, dst_address + (i * constants.WORD_SIZE), word)


def instr_shwrite(rm):
    word_count = int.from_bytes(rm._vm.stack_pop(), byteorder='little')
    src_word = int.from_bytes(rm._vm.stack_pop(), byteorder='little')
    src_block = int.from_bytes(rm._vm.stack_pop(), byteorder='little')
    shared_word = int.from_bytes(rm._vm.stack_pop(), byteorder='little')
    shared_block = int.from_bytes(rm._vm.stack_pop(), byteorder='little')

    src_address = rm.memory.translate_address(src_block, src_word)
    shared_address = rm.memory.translate_address(shared_block, shared_word)

    for i in range(word_count):
        word = rm.memory.read_word(rm._vm.memory, src_address + (i * constants.WORD_SIZE))
        rm.memory.write_word(rm.shared_memory, shared_address + (i * constants.WORD_SIZE), word)


def instr_shlock(rm):
    if rm.semaphore.p():
        print("SHARED MEMORY LOCKED")
    else:
        print("WAITING FOR SHARED MEMORY TO UNLOCK")
        rm._vm.cpu.pc -= 1


def instr_shunlock(rm):
    rm.semaphore.v()


def instr_led(rm):
    B = int.from_bytes(rm._vm.stack_pop(), byteorder='little')
    G = int.from_bytes(rm._vm.stack_pop(), byteorder='little')
    R = int.from_bytes(rm._vm.stack_pop(), byteorder='little')


def timeout(rm):
    print("TIMEOUT")
    rm._vm.cpu.halt()
