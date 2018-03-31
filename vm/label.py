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


from . import cpu


class Label(cpu.Instruction):
    def __init__(self, label, instruction):
        cpu.Instruction.__init__(self,
                                 instruction.code,
                                 instruction.mnemonic,
                                 takes_args=instruction.takes_args,
                                 arg=instruction.arg,
                                 length=instruction.length)
        self._label = label

    @property
    def label(self):
        return self._label
