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
from . import exceptions
from . import instructions
from . import interrupt_handlers

from .assembler import Assembler
from .instruction import Instruction, IOInstruction
from .memory import Memory
from .vm import VM

import inspect
import sys

import pdb


class InstructionSet():
    def __init__(self, instructions):
        self._mnemonic_dict = {instruction.mnemonic: type(
            instruction) for instruction in instructions}
        self._code_dict = {
            instruction.code: type(instruction) for instruction in instructions
        }

    def find_by_mnemonic(self, mnemonic):
        if mnemonic in self._mnemonic_dict:
            return self._mnemonic_dict.get(mnemonic, None)
        else:
            raise exceptions.UnknownCommandMnemonic(mnemonic)

    def find_by_code(self, code):
        if code in self._code_dict:
            return self._code_dict.get(code, None)
        else:
            raise exceptions.UnknownCommandCode(code)


class _DaromInstructionSet(InstructionSet):
    def __init__(self):
        instrs = []
        for k, v in inspect.getmembers(instructions, inspect.isclass):
            if issubclass(v, Instruction):
                instrs.append(v())
        super().__init__(instrs)


class HLP:
    def __init__(self):
        self._vpu = None

        self.ptr = 0
        self.pc = 0
        self.sp = 0
        self.shm = 0
        self.flags = bytearray(2)
        self.mode = 0
        self.si = 0
        self.pi = 0
        self.ti = 99

        self._instruction_set = _DaromInstructionSet()

    @property
    def instruction_set(self):
        return self._instruction_set

    @property
    def pi(self):
        return self._pi

    @pi.setter
    def pi(self, value):
        self._pi = value

    @property
    def si(self):
        return self._si

    @si.setter
    def si(self, value):
        self._si = value

    @property
    def ti(self):
        return self._ti

    @ti.setter
    def ti(self, value):
        self._ti = value

    def reset_registers(self):
        self._si = 0
        self._pi = 0
        self._ti = 99


class RM:
    def __init__(self):
        self._cpu = HLP()
        self._memory = Memory(66, constants.BLOCK_SIZE // constants.WORD_SIZE)
        self._shared_memory = self._memory.allocate(2)
        self._vms = []

    @property
    def cpu(self):
        return self._cpu

    @property
    def memory(self):
        return self._memory

    @property
    def vm_count(self):
        return len(self._vms)

    @property
    def last_vm(self):
        return self._vms[-1][0]

    def get_memory_allocation_for_vm(self, vm):
        for k, v in self._vms:
            if k is vm:
                return v

    def load(self, program):
        self.cpu.reset_registers()
        data_size, code_size = program.size()

        allocation = self.memory.allocate_bytes(
            data_size + code_size + 2 * self.memory.block_size * constants.WORD_SIZE)

        data_bytes, code_bytes = program.as_bytes()

        ds = 0
        cs = data_size
        ss = cs + code_size

        for i in range(data_size):
            self.memory.write_byte(allocation, i, bytes([data_bytes[i]]))
        for i in range(code_size):
            address = i + data_size
            self.memory.write_byte(allocation, address, bytes([code_bytes[i]]))

        vm = VM(program, self)

        vm.cpu.pc = cs
        vm.cpu.sp = ss
        vm.cpu.ds = ds

        self._vms.append((vm, allocation))

    def _dump_registers(self):
        print(
            '\tPC: {}\n'
            '\tSP: {}\n'
            '\tDS: {}\n'
            '\tFLAGS: {}\n'
            '\tPI: {}\n'
            '\tSI: {}\n'
            '\tTI: {}\n'.format(
                self._vm.cpu.pc,
                self._vm.cpu.sp,
                self._vm.cpu.ds,
                self._vm.cpu.flags,
                self._cpu._pi,
                self._cpu._si,
                self._cpu._ti
            )
        )

    def test(self):
        pi_handlers = [
            None,
            interrupt_handlers.incorrect_instruction_code,
            interrupt_handlers.incorrect_operand,
            interrupt_handlers.paging_error,
            interrupt_handlers.stack_overflow
        ]
        si_handlers = [
            None,
            interrupt_handlers.instr_halt,
            interrupt_handlers.instr_in,
            interrupt_handlers.instr_ini,
            interrupt_handlers.instr_out,
            interrupt_handlers.instr_outi,
            interrupt_handlers.instr_shread,
            interrupt_handlers.instr_shwrite,
            interrupt_handlers.instr_shlock,
            interrupt_handlers.instr_shunlock,
            interrupt_handlers.instr_led
        ]

        if (self._cpu._pi) > 0:
            pi_handlers[self._cpu._pi](self)
        elif (self._cpu._si) > 0:
            self._dump_registers()
            si_handlers[self._cpu._si](self)
        elif self._cpu._ti <= 0:
            interrupt_handlers.timeout(self)

    def run(self, vm_id):
        self._vm, _ = self._vms[vm_id]
        while self._vm.running:
            self.step(vm_id)

    def step(self, vm_id):
        self._vm, allocation = self._vms[vm_id]
        if self._vm.running:
            # print('Memory dump:')
            # self.memory._dump(allocation)
            # print('Register dump:')
            # self._dump_registers()
            # pdb.set_trace()
            try:
                instruction = self.memory.read_byte(
                    allocation, self._vm.cpu.pc)
                self._vm.cpu.pc += 1
                instruction = self._cpu.instruction_set.find_by_code(
                    instruction)()
                if instruction.takes_arg:
                    instruction.arg = self.memory.read_word(
                        allocation, self._vm.cpu.pc)
                    self._vm.cpu.pc += constants.WORD_SIZE
                instruction.execute(self._vm)
                if isinstance(instruction, IOInstruction):
                    self._cpu._ti -= 3
                else:
                    self._cpu._ti -= 1
            except exceptions.UnknownCommandCode as e:
                self._cpu._pi = 1
            except exceptions.PagingError as e:
                self._cpu._pi = 3
            self.test()
