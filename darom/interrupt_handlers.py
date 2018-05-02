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

from darom import constants
from darom import util


def invalid_instruction_code(real_machine):
    print('Invalid instruction code')
    real_machine.current_vm.cpu.halt()


def invalid_operand(real_machine):
    print('Invalid operand')
    real_machine.current_vm.cpu.halt()


def page_fault(real_machine):
    print('Page fault')
    real_machine.current_vm.cpu.halt()


def stack_overflow(real_machine):
    print('Stack overflow')
    real_machine.current_vm.cpu.halt()


def halt(real_machine):
    real_machine.current_vm.cpu.halt()
    print('Halted')


def in_(real_machine):
    block = int.from_bytes(
        real_machine.current_vm.stack_pop(),
        byteorder=constants.BYTE_ORDER)
    word = int.from_bytes(
        real_machine.current_vm.stack_pop(),
        byteorder=constants.BYTE_ORDER)
    character_count = int.from_bytes(
        real_machine.current_vm.stack_pop(),
        byteorder=constants.BYTE_ORDER)
    address = real_machine.current_vm.cpu.ds + \
        util.to_byte_address(block, word)

    data = real_machine.channel_device.read_stdinput()
    for i, byte in enumerate(data):
        real_machine.memory.write_byte(
            address + i,
            int.from_bytes(
                byte,
                byteorder=constants.BYTE_ORDER),
            virtual=True)


def ini(real_machine):
    data = real_machine.channel_device.read_stdinput(convert_to_int=True)
    real_machine.current_vm.stack_push(data)


def out(real_machine):
    block = int.from_bytes(
        real_machine.current_vm.stack_pop(),
        byteorder=constants.BYTE_ORDER)
    word = int.from_bytes(
        real_machine.current_vm.stack_pop(),
        byteorder=constants.BYTE_ORDER)
    character_count = int.from_bytes(
        real_machine.current_vm.stack_pop(),
        byteorder=constants.BYTE_ORDER)
    address = real_machine.current_vm.cpu.ds + \
        util.to_byte_address(block, word)

    string = ''
    for i in range(character_count):
        string += chr(real_machine.memory.read_byte(address + i, virtual=True))
    real_machine.channel_device.write_stdoutput(string)


def outi(real_machine):
    word = int.from_bytes(
        real_machine.current_vm.stack_pop(),
        byteorder=constants.BYTE_ORDER)
    real_machine.channel_device.write_stdoutput(str(word))


def shread(real_machine):
    word_count = int.from_bytes(
        real_machine.current_vm.stack_pop(),
        byteorder=constants.BYTE_ORDER)
    dst_word = int.from_bytes(
        real_machine.current_vm.stack_pop(),
        byteorder=constants.BYTE_ORDER)
    dst_block = int.from_bytes(
        real_machine.current_vm.stack_pop(),
        byteorder=constants.BYTE_ORDER)
    shared_word = int.from_bytes(
        real_machine.current_vm.stack_pop(),
        byteorder=constants.BYTE_ORDER)
    shared_block = int.from_bytes(
        real_machine.current_vm.stack_pop(),
        byteorder=constants.BYTE_ORDER)

    dst_address = util.to_byte_address(dst_block, dst_word)
    shared_address = util.to_byte_address(
        real_machine.shared_memory[shared_block], shared_word)

    for i in range(word_count):
        word = real_machine.memory.read_word(
            shared_address + (i * constants.WORD_SIZE))
        real_machine.memory.write_word(
            dst_address + (i * constants.WORD_SIZE),
            word,
            virtual=True
        )


def shwrite(real_machine):
    word_count = int.from_bytes(
        real_machine.current_vm.stack_pop(),
        byteorder=constants.BYTE_ORDER)
    src_word = int.from_bytes(
        real_machine.current_vm.stack_pop(),
        byteorder=constants.BYTE_ORDER)
    src_block = int.from_bytes(
        real_machine.current_vm.stack_pop(),
        byteorder=constants.BYTE_ORDER)
    shared_word = int.from_bytes(
        real_machine.current_vm.stack_pop(),
        byteorder=constants.BYTE_ORDER)
    shared_block = int.from_bytes(
        real_machine.current_vm.stack_pop(),
        byteorder=constants.BYTE_ORDER)

    src_address = util.to_byte_address(src_block, src_word)
    shared_address = util.to_byte_address(
        real_machine.shared_memory[shared_block], shared_word)

    for i in range(word_count):
        word = real_machine.memory.read_word(
            src_address + (i * constants.WORD_SIZE), virtual=True)
        real_machine.memory.write_word(
            shared_address + (i * constants.WORD_SIZE), word)


def shlock(real_machine):
    if real_machine.semaphore.acquire():
        print('Shared memory locked')
    else:
        print('Waiting for shared memory to unlock')
        real_machine.current_vm.cpu.pc -= 1


def shunlock(real_machine):
    real_machine.semaphore.release()


def led(real_machine):
    blue = real_machine.current_vm.stack_pop()
    green = real_machine.current_vm.stack_pop()
    red = real_machine.current_vm.stack_pop()

    real_machine.channel_device.write_led([red, green, blue])


def timeout(real_machine):
    print('Timeout')
    real_machine.current_vm.cpu.halt()
