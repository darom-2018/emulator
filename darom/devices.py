# © 2018 Edvinas Gervelis

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

import struct


class InputDevice():
    def __init__(self):
        self._memory = []

    def set_input(self, string):
        text = bytes(string, encoding='ascii')
        for byte in text:
            self._memory.append(struct.pack('>B', byte))

    @property
    def input(self):
        memory = self._memory
        self._memory = []
        return memory


class OutputDevice():
    def __init__(self):
        self._output = ''

    def set_output(self, data):
        for i in range(len(data)):
            self._output += data[i]

        print(self._output)

    @property
    def output(self):
        output = self._output
        self._output = ''
        return output


class LedDevice():
    def __init__(self):
        self._rgb = [0, 0, 0]

    def set_rgb(self, rgb):
        self._rgb = []
        for byte in rgb:
            self._rgb.append(
                int.from_bytes(
                    byte,
                    byteorder=constants.BYTE_ORDER))

        print(self._rgb)

    @property
    def rgb(self):
        color = '#'
        for byte in self._rgb:
            color += '{:02X}'.format(byte)
        return color
