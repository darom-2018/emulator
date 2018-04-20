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
        self._pc = 0
        self._sp = 0
        self._ds = 0
        self._flags = bytearray(2)
        self._halted = False

    @property
    def pc(self):
        return self._pc

    @pc.setter
    def pc(self, value):
        self._pc = value

    @property
    def sp(self):
        return self._sp

    @sp.setter
    def sp(self, value):
        self._sp = value

    @property
    def ds(self):
        return self._ds

    @ds.setter
    def ds(self, value):
        self._ds = value

    @property
    def flags(self):
        return int.from_bytes(self._flags, byteorder='little')

    def set_flags(self, value):
        self._flags[0] = value[0]
        self._flags[1] = value[1]

    def test_flags(self):
        return self._flags[0], self._flags[1] & 0x10, self._flags[1] & 1

    @property
    def halted(self):
        return self._halted

    def halt(self):
        self._halted = True


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
