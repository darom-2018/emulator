from . import constants


def Incorrect_instruction_code(rm):
    print("INCORRECT_INSTRUCTION_CODE")
    rm._vm.cpu.halt()


def Incorrect_operand(rm):
    print("INCORRECT_OPERAND")
    rm._vm.cpu.halt()


def Paging_error(rm):
    print("PAGING_ERROR")
    rm._vm.cpu.halt()


def Stack_overflow(rm):
    print("STACK_OVERFLOW")
    rm._vm.cpu.halt()


def Halt(rm):
    print("HALT")
    rm._memory._dump(rm._vm.memory)
    rm._vm.cpu.halt()


def In(rm):
    print("IN")
    block = int.from_bytes(rm._vm.stack_pop(), byteorder='little')
    word = int.from_bytes(rm._vm.stack_pop(), byteorder='little')
    character_count = int.from_bytes(rm._vm.stack_pop(), byteorder='little')
    address = rm._vm.cpu.ds + rm.memory.translate_address(block, word)

    data = rm.channel_device.read_stdinput()
    for i, byte in enumerate(data):
        rm.memory.write_byte(rm._vm.memory, address + i, byte)


def Ini(rm):
    print("INI")
    data = rm.channel_device.read_stdinput(convert_to_int=True)
    rm._vm.stack_push(data)


def Out(rm):
    print("OUT")
    block = int.from_bytes(rm._vm.stack_pop(), byteorder='little')
    word = int.from_bytes(rm._vm.stack_pop(), byteorder='little')
    character_count = int.from_bytes(rm._vm.stack_pop(), byteorder='little')

    byte_string = bytes()
    for i in range(character_count):
        address = rm._vm.cpu.ds + rm.memory.translate_address(block, word)
        byte_string += rm.memory.read_byte(rm._vm.memory, address + i)
    rm.channel_device.write_stdoutput(byte_string.decode('ascii'))


def Outi(rm):
    print("OUTI")
    word = int.from_bytes(rm._vm.stack_pop(), byteorder='little')
    rm.channel_device.write_stdoutput(str(word))


def Shread(rm):
    print("SHREAD")


def Shwrite(rm):
    print("SHWRITE")


def Shlock(rm):
    print("SHLOCK")


def Shunlock(rm):
    print("SHUNLOCK")


def Led(rm):
    print("LED")
    B = rm._vm.stack_pop()
    G = rm._vm.stack_pop()
    R = rm._vm.stack_pop()

    rm.channel_device.write_led([R, G, B])

    # rm._channel_device.dc = constants.DST_LED
    # rm._channel_device.buffer = [R, G, B]
    # rm._channel_device.transfer_data()


def Timeout(rm):
    print("TIMEOUT")
    rm._vm.cpu.halt()
