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

import argparse
import inspect
import sys

import pdb


class InstructionSet():
    def __init__(self, instructions):
        self._mnemonic_dict = {
            instruction.mnemonic: type(instruction) for instruction in instructions
        }
        self._code_dict = {
            instruction.code: type(instruction) for instruction in instructions
        }

    def find_by_mnemonic(self, mnemonic):
        if mnemonic in self._mnemonic_dict:
            return self._mnemonic_dict.get(mnemonic, None)
        else:
            raise exceptions.UnknownCommandMnemonic(mnemonic);

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

        self._mode = 0
        self._ptr = 0
        self._shm = 0
        self._pi = 0
        self._si = 0
        self._ti = 100

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


class RM:
    def __init__(self):
        self._cpu = HLP()
        self._memory = Memory(66, 16)
        self._shared_memory = self._memory.allocate(2)
        self._vms = []

    @property
    def cpu(self):
        return self._cpu

    @property
    def memory(self):
        return self._memory

    def get_memory_allocation_for_vm(self, vm):
        for k, v in self._vms:
            if k is vm:
                return v

    def load(self, program):
        data_size, code_size = program.size()

        allocation = self.memory.allocate_bytes(
            data_size + code_size + 2 * self.memory.block_size * constants.WORD_SIZE
        )

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
            interrupt_handlers.Incorrect_instruction_code,
            interrupt_handlers.Incorrect_operand,
            interrupt_handlers.Paging_error,
            interrupt_handlers.Stack_overflow
        ]
        si_handlers = [
            None,
            interrupt_handlers.Halt,
            interrupt_handlers.In,
            interrupt_handlers.Ini,
            interrupt_handlers.Out,
            interrupt_handlers.Outi,
            interrupt_handlers.Shread,
            interrupt_handlers.Shwrite,
            interrupt_handlers.Shlock,
            interrupt_handlers.Shunlock,
            interrupt_handlers.Led
        ]

        if (self._cpu._pi) > 0:
            pi_handlers[self._cpu._pi](self)
        elif (self._cpu._si) > 0:
            self._dump_registers()
            si_handlers[self._cpu._si](self)
        elif self._cpu._ti <= 0:
            interrupt_handlers.Timeout(self)

    def run(self):
        for vm, allocation in reversed(self._vms):
            print('Running {}'.format(vm.program.name))
            self._vm = vm

            while self._vm.running:
                # print('Memory dump:')
                # self.memory._dump(allocation)
                # print('Register dump:')
                # self._dump_registers()
                # pdb.set_trace()
                try:
                    instruction = self.memory.read_byte(allocation, self._vm.cpu.pc)
                    self._vm.cpu.pc += 1
                    # instruction = b'\xff'
                    instruction = self._cpu.instruction_set.find_by_code(instruction)()
                    if instruction.takes_arg:
                        instruction.arg = self.memory.read_word(allocation, self._vm.cpu.pc)
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


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument('files', nargs='+', type=open, metavar='FILE')

    args = parser.parse_args()

    rm = RM()
    assembler = Assembler(rm.cpu)

    for file in args.files:
        print('Loading {}'.format(file.name))
        rm.load(assembler.assemble(file))

    rm.run()
