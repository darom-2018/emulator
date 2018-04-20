

class InputDevice():
    def __init__(self):
        self._memory = bytearray()

    def set_input(self, data):
        for i in range(len(data)):
            self._memory.extend(str.encode(data[i]))

    @property
    def input(self):
        return self._memory


class OutputDevice():
    def __init__(self):
        self._output = ""

    def set_output(self, data):
        for i in range(len(data)):
            self._output += data[i].to_bytes(1, byteorder='little')

    @property
    def output(self):
        return self._output


class LedDevice():
    def __init__(self):
        self._rgb = []

    def set_rgb(self, rgb):
        for rgb in rgb:
            self._rgb.append(int.from_bytes(rgb, byteorder='little'))

    @property
    def rgb(self):
        return self._rgb
