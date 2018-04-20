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


class InputDevice():
    def __init__(self):
        self._memory = []

    def set_input(self, data):
        for i in range(len(data)):
            self._memory.append(str.encode(data[i]))

    def get_input(self):
        # input = "test"
        # for i in range(len(input)):
        #     self._memory.append(str.encode(input[i]))
        return self._memory


class OutputDevice():
    def __init__(self):
        self._output = ""

    def set_output(self, data):
        for i in range(len(data)):
            self._output += data[i]

        print(self._output)


class LedDevice():
    def __init__(self):
        self._rgb = []

    def set_RGB(self, rgb):
        for rgb in rgb:
            self._rgb.append(int.from_bytes(rgb, byteorder='little'))

        print(self._rgb)
