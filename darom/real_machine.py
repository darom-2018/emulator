# © 2018 Ernestas Kulik, Justinas Valatkevičius, Tautvydas Baliukynas

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

import inspect

from darom import constants
from darom import exceptions
from darom import instructions
from darom import interrupt_handlers
from darom import util
from darom.assembler import Assembler
from darom.channel_device import ChannelDevice
from darom.devices import InputDevice, OutputDevice, LedDevice, StorageDevice
from darom.instruction import Instruction, IOInstruction
from darom.memory import Memory
from darom.semaphore import Semaphore
from darom.virtual_machine import VirtualMachine


class InstructionSet():
    def __init__(self, instructions):
        self._mnemonic_dict = {instruction.mnemonic: type(
            instruction) for instruction in instructions}
        self._code_dict = {
            instruction.code: type(instruction) for instruction in instructions
        }

    def find_by_mnemonic(self, mnemonic):
        try:
            return self._mnemonic_dict[mnemonic]
        except KeyError:
            raise exceptions.InvalidInstructionMnemonicError(mnemonic)

    def find_by_code(self, code):
        try:
            return self._code_dict[code]
        except KeyError:
            raise exceptions.InvalidInstructionCodeError(code)


class _DaromInstructionSet(InstructionSet):
    def __init__(self):
        instrs = []
        for key, value in inspect.getmembers(instructions, inspect.isclass):
            if issubclass(value, Instruction):
                instrs.append(value())
        super().__init__(instrs)


class HLP:
    def __init__(self):
        self.ptr = bytearray(4)
        self.shm = 0
        self.mode = 0
        self.si = 0
        self.pi = 0
        self.ti = 100

        self._instruction_set = _DaromInstructionSet()

    @property
    def instruction_set(self):
        return self._instruction_set

    def reset_registers(self):
        self.si = 0
        self.pi = 0
        self.ti = 100


class RealMachine:
    def __init__(self):
        self._cpu = HLP()
        self._user_memory = Memory(70, self.cpu)
        self._shared_memory = self._user_memory.allocate(2)
        self._semaphore = Semaphore(1)
        self._vms = []
        self._current_vm = None
        self._channel_device = ChannelDevice(self)
        self._input_device = InputDevice()
        self._output_device = OutputDevice()
        self._led_device = LedDevice()
        self._storage_devices = []

    @property
    def cpu(self):
        return self._cpu

    @property
    def memory(self):
        return self._user_memory

    @property
    def current_vm(self):
        return self._current_vm

    @property
    def vm_count(self):
        return len(self._vms)

    @property
    def last_vm(self):
        return self._vms[-1][0]

    @property
    def shared_memory(self):
        return self._shared_memory

    @property
    def semaphore(self):
        return self._semaphore

    @property
    def channel_device(self):
        return self._channel_device

    @property
    def input_device(self):
        return self._input_device

    @property
    def output_device(self):
        return self._output_device

    @property
    def led_device(self):
        return self._led_device

    def add_storage_device(self, storage_device):
        print(
            'Adding storage device with programs: {}'.format(
                list(storage_device.programs.keys())
            )
        )

        self._storage_devices.append(storage_device)

    def load(self, program):
        # TODO: This really doesn’t belong here.
        self.cpu.reset_registers()

        program_text = None

        for storage_device in self._storage_devices:
            program_text = storage_device.programs.get(program.upper())
            if program_text is not None:
                break

        program = Assembler(self.cpu).assemble_from_data(program_text)

        data_size, code_size = program.size()
        page_count = util.to_page_count(data_size + code_size)

        self._current_vm = VirtualMachine(program, self)
        ptr = bytearray(4)

        ptr[0] = data_size + code_size
        ptr[1] = page_count + 2
        ptr[2] = self.memory.allocate(1)[0]
        ptr[3] = 0

        self.cpu.ptr = ptr

        vm_allocation = self.memory.allocate(page_count + 2)

        for i, page in enumerate(vm_allocation):
            word = page.to_bytes(
                constants.WORD_SIZE,
                byteorder=constants.BYTE_ORDER
            )
            self.memory.write_word(
                util.to_byte_address(self.cpu.ptr[2], i), word
            )

        data_bytes, code_bytes = program.as_bytes()

        ds = 0
        cs = data_size
        ss = cs + code_size

        for i in range(data_size):
            self.memory.write_byte(i, data_bytes[i], virtual=True)
        for i in range(code_size):
            self.memory.write_byte(i + data_size, code_bytes[i], virtual=True)

        self._current_vm.cpu.pc = cs
        self._current_vm.cpu.sp = ss
        self._current_vm.cpu.ds = ds

        self._vms.append((self._current_vm, ptr))

    def _dump_registers(self):
        print(
            '\tPC: {}\n'
            '\tSP: {}\n'
            '\tDS: {}\n'
            '\tFLAGS: {}\n'
            '\tPTR: {}\n'
            '\tPI: {}\n'
            '\tSI: {}\n'
            '\tTI: {}\n'.format(
                self._current_vm.cpu.pc,
                self._current_vm.cpu.sp,
                self._current_vm.cpu.ds,
                self._current_vm.cpu.flags,
                self._cpu.ptr,
                self._cpu.pi,
                self._cpu.si,
                self._cpu.ti
            )
        )

    def test(self):
        pi_handlers = [
            None,
            interrupt_handlers.invalid_instruction_code,
            interrupt_handlers.invalid_operand,
            interrupt_handlers.page_fault,
            interrupt_handlers.stack_overflow
        ]
        si_handlers = [
            None,
            interrupt_handlers.halt,
            interrupt_handlers.in_,
            interrupt_handlers.ini,
            interrupt_handlers.out,
            interrupt_handlers.outi,
            interrupt_handlers.shread,
            interrupt_handlers.shwrite,
            interrupt_handlers.shlock,
            interrupt_handlers.shunlock,
            interrupt_handlers.led
        ]

        if (self._cpu.pi) > 0:
            pi_handlers[self._cpu.pi](self)
            self._cpu.pi = 0
        if (self._cpu.si) > 0:
            self._dump_registers()
            si_handlers[self._cpu.si](self)
            self._cpu.si = 0
        if self._cpu.ti <= 0:
            interrupt_handlers.timeout(self)

    def run(self, vm_id):
        self._current_vm, self.cpu.ptr = self._vms[vm_id]

        while self._current_vm.running:
            self.step(vm_id)

    def step(self, vm_id):
        self._current_vm, self.cpu.ptr = self._vms[vm_id]

        if not self._current_vm.running:
            return

        try:
            instruction = self.memory.read_byte(
                self._current_vm.cpu.pc,
                virtual=True
            )
            instruction = instruction.to_bytes(
                1, byteorder=constants.BYTE_ORDER)

            self._current_vm.cpu.pc += 1

            instruction = self._cpu.instruction_set.find_by_code(instruction)()
            if instruction.takes_arg:
                instruction.arg = self.memory.read_word(
                    self._current_vm.cpu.pc,
                    virtual=True
                )
                self._current_vm.cpu.pc += constants.WORD_SIZE

            instruction.execute(self._current_vm)

            if isinstance(instruction, IOInstruction):
                self._cpu.ti -= 3
            else:
                self._cpu.ti -= 1
        except exceptions.InvalidInstructionCodeError:
            self._cpu.pi = 1
        except exceptions.PageFaultError:
            self._cpu.pi = 3

        self.test()
