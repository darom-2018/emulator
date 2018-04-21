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


class Instruction():
    def __init__(self, code, mnemonic, takes_arg=False):
        self.arg = None
        self._code = code
        self._mnemonic = mnemonic
        self._takes_arg = takes_arg

    @property
    def code(self):
        return self._code

    @property
    def length(self):
        length = len(self.code)
        if self.takes_arg:
            length += constants.WORD_SIZE
        return length

    @property
    def mnemonic(self):
        return self._mnemonic

    @property
    def takes_arg(self):
        return self._takes_arg

    def execute(self, vm):
        pass


class Label(Instruction):
    def __init__(self, label, instruction):
        super().__init__(
            instruction.code,
            instruction.mnemonic,
            takes_arg=instruction.takes_arg,
        )
        self.arg = instruction.arg
        self._label = label

    @property
    def label(self):
        return self._label


class BinaryOperation(Instruction):
    def __init__(self, code, mnemonic, operator):
        super().__init__(code, mnemonic)

        self._operator = operator

    def execute(self, vm):
        lhs = int.from_bytes(vm.stack_pop(), byteorder='little')
        rhs = int.from_bytes(vm.stack_pop(), byteorder='little')

        try:
            result = self._operator(lhs, rhs)

            cf = result < 0 or result > constants.WORD_MAX
            pf = (result % 2) == 0

            result = result & constants.WORD_MAX

            # This is intentional, as the result can overflow
            zf = result == 0

            vm.cpu.set_flags(((cf & 1), ((pf & 1) << 4) | (zf & 1)))

            vm.stack_push(
                result.to_bytes(
                    constants.WORD_SIZE,
                    byteorder='little'))
        except ZeroDivisionError:
            vm.rm.cpu.pi = 2


class IOInstruction(Instruction):
    def __init__(self, code, mnemonic):
        super().__init__(code, mnemonic)
