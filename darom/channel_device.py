from . import constants

import pdb


class ChannelDevice():
    def __init__(self, rm):
        self._rm = rm

    def read_stdinput(self, convert_to_int=False):
        bytes = self._rm.input_device.get_input()
        if convert_to_int:
            string = ""
            for byte in bytes:
                string += byte.decode()
            word = int(string).to_bytes(2, byteorder='little')
            return word
        return bytes

    def write_stdoutput(self, data):
        self._rm.output_device.set_output(data)

    def write_led(self, RGB):
        self._rm.led_device.set_RGB(RGB)
