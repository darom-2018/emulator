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

from darom import constants


class ChannelDevice():
    def __init__(self, real_machine):
        self._real_machine = real_machine

    def read_stdinput(self, convert_to_int=False):
        # TODO: fix the case when no input has been provided prior to calling
        #       this by either blocking or using magic.
        device_input = self._real_machine.input_device.input

        if convert_to_int:
            string = ''

            for byte in device_input:
                string += byte.decode()

            word = int(string).to_bytes(
                constants.WORD_SIZE,
                byteorder=constants.BYTE_ORDER
            )

            return word

        return device_input

    def write_stdoutput(self, data):
        self._real_machine.output_device.output = data

    def write_led(self, rgb):
        self._real_machine.led_device.rgb = rgb
