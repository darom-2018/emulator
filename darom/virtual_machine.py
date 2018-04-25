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

from darom import constants
from darom import exceptions


class CPU:
    def __init__(self):
        self.pc = 0
        self.sp = 0
        self.ds = 0
        self.flags = bytearray(2)
        self._halted = False

    def test_flags(self):
        return self.flags[0], self.flags[1] & 0x10, self.flags[1] & 1

    @property
    def halted(self):
        return self._halted

    def halt(self):
        self._halted = True


class VirtualMachine:
    def __init__(self, program, real_machine):
        self._cpu = CPU()
        self._program = program
        self._real_machine = real_machine

    @property
    def cpu(self):
        return self._cpu

    @property
    def program(self):
        return self._program

    @property
    def real_machine(self):
        return self._real_machine

    @property
    def running(self):
        return not self._cpu.halted

    def stack_pop(self):
        self.cpu.sp -= constants.WORD_SIZE
        head = self.real_machine.memory.read_word(self.cpu.sp, virtual=True)
        return head

    def stack_push(self, word):
        try:
            head = self.real_machine.memory.write_word(
                self.cpu.sp,
                word,
                virtual=True
            )
        except exceptions.PageFaultError:
            self.real_machine.cpu.pi = 4
        self.cpu.sp += constants.WORD_SIZE
