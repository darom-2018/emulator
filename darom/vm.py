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


class CPU:
    def __init__(self):
        self.pc = 0
        self.sp = 0
        self.ds = 0
        self.flags = bytearray(2)
        self._halted = False

    @property
    def halted(self):
            return self._halted

    def halt(self):
        self._halted = True

    def test_flags(self):
        return self.flags[0], self.flags[1] & 0x10, self.flags[1] & 1


class VM:
    def __init__(self, program, rm):
        self._cpu = CPU()
        self._program = program
        self._rm = rm

    @property
    def cpu(self):
        return self._cpu

    @property
    def memory(self):
        return self.rm.get_memory_allocation_for_vm(self)

    @property
    def program(self):
        return self._program

    @property
    def rm(self):
        return self._rm

    @property
    def running(self):
        return not self._cpu.halted

    def stack_pop(self):
        allocation = self.memory
        self.cpu.sp -= constants.WORD_SIZE
        head = self.rm.memory.read_word(allocation, self.cpu.sp)
        return head

    def stack_push(self, word):
        allocation = self.memory
        try:
            head = self.rm.memory.write_word(allocation, self.cpu.sp, word)
        except exceptions.PagingError:
            self._rm.cpu.pi = 4
        self.cpu.sp += constants.WORD_SIZE
