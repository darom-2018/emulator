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
from . import util


def invalid_instruction_code(rm):
    print('Invalid instruction code')
    rm.current_vm.cpu.halt()


def invalid_operand(rm):
    print('Invalid operand')
    rm.current_vm.cpu.halt()


def page_fault(rm):
    print('Page fault')
    rm.current_vm.cpu.halt()


def stack_overflow(rm):
    print("STACK_OVERFLOW")
    rm.current_vm.cpu.halt()


def halt(rm):
    rm.current_vm.cpu.halt()
    print("HALTED")


def in_(rm):
    block = int.from_bytes(rm.current_vm.stack_pop(), byteorder='little')
    word = int.from_bytes(rm.current_vm.stack_pop(), byteorder='little')
    character_count = int.from_bytes(rm.current_vm.stack_pop(), byteorder='little')
    address = rm.current_vm.cpu.ds + util.to_byte_address(block, word)

    data = rm.channel_device.read_stdinput()
    for i, byte in enumerate(data):
        rm.memory.write_byte(address + i, byte, virtual=True)


def ini(rm):
    data = rm.channel_device.read_stdinput(convert_to_int=True)
    rm.current_vm.stack_push(data)


def out(rm):
    block = int.from_bytes(rm.current_vm.stack_pop(), byteorder='little')
    word = int.from_bytes(rm.current_vm.stack_pop(), byteorder='little')
    character_count = int.from_bytes(rm.current_vm.stack_pop(), byteorder='little')
    address = rm.current_vm.cpu.ds + util.to_byte_address(block, word)

    string = ""
    for i in range(character_count):
        string += chr(rm.memory.read_byte(address + i, virtual=True))
    rm.channel_device.write_stdoutput(string)


def outi(rm):
    word = int.from_bytes(rm.current_vm.stack_pop(), byteorder='little')
    rm.channel_device.write_stdoutput(str(word))


def shread(rm):
    word_count = int.from_bytes(rm.current_vm.stack_pop(), byteorder='little')
    dst_word = int.from_bytes(rm.current_vm.stack_pop(), byteorder='little')
    dst_block = int.from_bytes(rm.current_vm.stack_pop(), byteorder='little')
    shared_word = int.from_bytes(rm.current_vm.stack_pop(), byteorder='little')
    shared_block = int.from_bytes(rm.current_vm.stack_pop(), byteorder='little')

    dst_address = util.to_byte_address(dst_block, dst_word)
    shared_address = util.to_byte_address(rm.shared_memory[shared_block], shared_word)

    for i in range(word_count):
        word = rm.memory.read_word(shared_address + (i * constants.WORD_SIZE))
        rm.memory.write_word(dst_address +
                             (i * constants.WORD_SIZE), word,
                             virtual=True)


def shwrite(rm):
    word_count = int.from_bytes(rm.current_vm.stack_pop(), byteorder='little')
    src_word = int.from_bytes(rm.current_vm.stack_pop(), byteorder='little')
    src_block = int.from_bytes(rm.current_vm.stack_pop(), byteorder='little')
    shared_word = int.from_bytes(rm.current_vm.stack_pop(), byteorder='little')
    shared_block = int.from_bytes(rm.current_vm.stack_pop(), byteorder='little')

    src_address = util.to_byte_address(src_block, src_word)
    shared_address = util.to_byte_address(rm.shared_memory[shared_block], shared_word)

    for i in range(word_count):
        word = rm.memory.read_word(src_address + (i * constants.WORD_SIZE), virtual=True)
        rm.memory.write_word(shared_address + (i * constants.WORD_SIZE), word)


def shlock(rm):
    if rm.semaphore.p():
        print("SHARED MEMORY LOCKED")
    else:
        print("WAITING FOR SHARED MEMORY TO UNLOCK")
        rm.current_vm.cpu.pc -= 1


def shunlock(rm):
    rm.semaphore.v()


def led(rm):
    B = rm.current_vm.stack_pop()
    G = rm.current_vm.stack_pop()
    R = rm.current_vm.stack_pop()

    rm.channel_device.write_led([R, G, B])


def timeout(rm):
    print("TIMEOUT")
    rm.current_vm.cpu.halt()
