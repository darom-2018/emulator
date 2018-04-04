class Memory:
    def __init__(self):
        self._blocks = 66
        self._words = 16
        self._memory = [
            [None for x in range(self._words)] for y in range(self._blocks)
        ]

    @property
    def blocks(self):
        return self._blocks

    @property
    def words(self):
        return self._words

    def dump(self, blocks=64):
        print("=====================================")
        for i in range(blocks):
            print(i, end=' ')
            for j in range(self._words):
                data = self._memory[i][j]
                if isinstance(data, bytes):
                    print("{}h".format(data.hex().upper()), end=' ')
                else:
                    print(data, end=' ')
            print()
        print("=====================================")

    def write(self, address, data):
        block = address // self.words
        word = address % self.words
        self._memory[block][word] = data

    def read(self, address):
        block = address // self.words
        word = address % self.words
        return self._memory[block][word]
