

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
