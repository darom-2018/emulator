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
    print("HALT")
    rm._vm.cpu.halt()


def instr_in(rm):
    print("IN")
    block = int.from_bytes(rm._vm.stack_pop(), byteorder='little')
    word = int.from_bytes(rm._vm.stack_pop(), byteorder='little')
    character_count = int.from_bytes(rm._vm.stack_pop(), byteorder='little')


def instr_ini(rm):
    print("INI")
    block = int.from_bytes(rm._vm.stack_pop(), byteorder='little')
    word = int.from_bytes(rm._vm.stack_pop(), byteorder='little')
    character_count = int.from_bytes(rm._vm.stack_pop(), byteorder='little')


def instr_out(rm):
    print("OUT")
    block = int.from_bytes(rm._vm.stack_pop(), byteorder='little')
    word = int.from_bytes(rm._vm.stack_pop(), byteorder='little')
    character_count = int.from_bytes(rm._vm.stack_pop(), byteorder='little')
    string = bytes()
    for i in range(character_count):
        address = rm._vm.cpu.ds + rm.memory.translate_address(block, word)
        string += rm.memory.read_byte(rm._vm.memory, address + i)
    print(string.decode('ascii'))


def instr_outi(rm):
    print("OUTI")
    word = int.from_bytes(rm._vm.stack_pop(), byteorder='little')
    # string = bytes()
    # for i in range(character_count):
    #     address = rm._vm.cpu.ds + rm.memory.translate_address(block, word)
    #     string += rm.memory.read_byte(rm._vm.memory, address + i)
    print(word)


def instr_shread(rm):
    print("SHREAD")


def instr_shwrite(rm):
    print("SHWRITE")


def instr_shlock(rm):
    print("SHLOCK")


def instr_shunlock(rm):
    print("SHUNLOCK")


def instr_led(rm):
    print("LED")
    B = int.from_bytes(rm._vm.stack_pop(), byteorder='little')
    G = int.from_bytes(rm._vm.stack_pop(), byteorder='little')
    R = int.from_bytes(rm._vm.stack_pop(), byteorder='little')
    print(R, G, B)


def timeout(rm):
    print("TIMEOUT")
    rm._vm.cpu.halt()
