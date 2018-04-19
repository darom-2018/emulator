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
    rm._vm.cpu.halt()


def In(rm):
    print("IN")
    block = int.from_bytes(rm._vm.stack_pop(), byteorder='little')
    word = int.from_bytes(rm._vm.stack_pop(), byteorder='little')
    character_count = int.from_bytes(rm._vm.stack_pop(), byteorder='little')
    address = rm._vm.cpu.ds + rm.memory.translate_address(block, word)

    rm._channel_device.dc = constants.DST_MEMORY
    rm._channel_device.address = address
    rm._channel_device.byte_count = 4
    rm._channel_device.buffer = [b't',b'e',b's',b't']
    rm._channel_device.transfer_data()

def Ini(rm):
    print("INI")
    block = int.from_bytes(rm._vm.stack_pop(), byteorder='little')
    word = int.from_bytes(rm._vm.stack_pop(), byteorder='little')
    character_count = int.from_bytes(rm._vm.stack_pop(), byteorder='little')
    address = rm._vm.cpu.ds + rm.memory.translate_address(block, word)

    # rm._channel_device.dc = constants.DST_MEMORY
    # rm._channel_device.addres = address
    # rm._channel_device.byte_count = 4
    # rm._channel_device.buffer = [b'4']
    # rm._channel_device.transfer_data()


def Out(rm):
    print("OUT")
    block = int.from_bytes(rm._vm.stack_pop(), byteorder='little')
    word = int.from_bytes(rm._vm.stack_pop(), byteorder='little')
    character_count = int.from_bytes(rm._vm.stack_pop(), byteorder='little')

    rm._channel_device.dc = constants.DST_STDOUT
    string = bytes()
    for i in range(character_count):
        address = rm._vm.cpu.ds + rm.memory.translate_address(block, word)
        string += rm.memory.read_byte(rm._vm.memory, address + i)
    rm._channel_device.buffer = string
    rm._channel_device.transfer_data()


def Outi(rm):
    print("OUTI")
    word = int.from_bytes(rm._vm.stack_pop(), byteorder='little')
    # string = bytes()
    # for i in range(character_count):
    #     address = rm._vm.cpu.ds + rm.memory.translate_address(block, word)
    #     string += rm.memory.read_byte(rm._vm.memory, address + i)
    print(word)


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
    B = int.from_bytes(rm._vm.stack_pop(), byteorder='little')
    G = int.from_bytes(rm._vm.stack_pop(), byteorder='little')
    R = int.from_bytes(rm._vm.stack_pop(), byteorder='little')

    rm._channel_device.dc = constants.DST_LED
    rm._channel_device.buffer = [R, G, B]
    rm._channel_device.transfer_data()


def Timeout(rm):
    print("TIMEOUT")
    rm._vm.cpu.halt()
