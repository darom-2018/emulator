# © 2018 Edvinas Gervelis, Ernestas Kulik

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

import re
import struct

from darom import constants


class InputDevice:
    def __init__(self):
        self._memory = []

    @property
    def input(self):
        memory = self._memory
        self._memory = []

        return memory

    @input.setter
    def input(self, string):
        self._memory = []
        text = bytes(string, encoding='ascii')
        for byte in text:
            self._memory.append(struct.pack('>B', byte))


class OutputDevice:
    def __init__(self):
        self._output = ''

    @property
    def output(self):
        output = self._output

        self._output = ''

        return output

    @output.setter
    def output(self, data):
        for datum in data:
            self._output += datum

        print(self._output)


class LedDevice:
    def __init__(self):
        self._rgb = [0, 0, 0]

    @property
    def rgb(self):
        color = '#'
        for byte in self._rgb:
            color += '{:02X}'.format(byte)

        return color

    @rgb.setter
    def rgb(self, value):
        self._rgb = []

        for byte in value:
            self._rgb.append(
                int.from_bytes(byte, byteorder=constants.BYTE_ORDER)
            )

        print(self._rgb)


class StorageDevice:
    def __init__(self, programs):
        self._programs = programs

    @property
    def programs(self):
        return self._programs

    @staticmethod
    def from_file(file):
        data = file.read()
        last_match = None
        programs = {}

        for match in re.finditer(r'(?i)\$PROGRAM', data):
            if last_match is not None:
                program = data[last_match.start():match.start()]
                program_name = re.search(
                    r'[^(?i)\$PROGRAM\s+]([^"]*)"', program)[1].upper()

                if program_name in programs:
                    raise Exception(
                        'Multiple programs named {} in {}'.format(
                            program_name, file))

                programs[program_name] = program

            last_match = match

        program = data[last_match.start():len(data)]
        program_name = re.search(
            r'[^(?i)\$PROGRAM\s+]([^"]*)"',
            program)[1].upper()

        if program_name in programs:
            raise Exception(
                'Multiple programs named {} in {}'.format(program_name, file)
            )

        programs[program_name] = program

        return StorageDevice(programs)
