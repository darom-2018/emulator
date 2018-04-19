

class InputDevice():
    def __init__(self):
        self.memory =  bytearray()

    def setInput(self, data):
        for i in range(len(data)):
            self.memory.extend(str.encode(data[i]))

    def getInput(self):
        return self.memory


class outputDevice():
    def __init__(self):
        self.output = ""

    def getOutput(self, data):
        for i in range(len(data)):
            self.output += data[i].to_bytes(1, byteorder='little' )
        return self.output

class ledDevice():
    def __init__(self):
        self.rgb = []

    def getRgb(self, rgb):
        for rgb in rgb:
            self.rgb.append(int.from_bytes(rgb,  byteorder='little'))
        return self.rgb
