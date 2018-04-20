# © 2018 Justinas Valatkevicius

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

import pdb


class ChannelDevice():
    def __init__(self, rm):
        self._rm = rm

    def read_stdinput(self, convert_to_int=False):
        device_input = self._rm.input_device.input
        if convert_to_int:
            string = ""
            for byte in device_input:
                string += byte.decode()
            word = int(string).to_bytes(2, byteorder='little')
            return word
        return device_input

    def write_stdoutput(self, data):
        self._rm.output_device.set_output(data)

    def write_led(self, RGB):
        self._rm.led_device.set_RGB(RGB)
