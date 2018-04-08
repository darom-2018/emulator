# © 2018 Justinas Valatkevičius

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


class Memory:
    def __init__(self):
        self._blocks = 66
        self._words = 16
        self._bytes_in_word = 2
        self._bytes = self._words * self._bytes_in_word
        self._memory = [
            [None for x in range(self._bytes)] for y in range(self._blocks)
        ]

    @property
    def blocks(self):
        return self._blocks

    @property
    def words(self):
        return self._words

    @property
    def bytes(self):
        return self._bytes

    @property
    def word_size(self):
        return self._bytes_in_word

    @property
    def block_size(self):
        return self._bytes

    def dump(self, blocks=64):
        print("=====================================")
        for i in range(blocks):
            print('%d(%02xh):\t' % (i, i * self._bytes), end=' ')
            for j in range(self._bytes):
                data = self._memory[i][j]
                if isinstance(data, bytes):
                    print("{}h".format(data.hex().upper()), end=' ')
                else:
                    print(data, end=' ')
            print()
        print("=====================================")

    def write(self, address, data):
        block = address // self.bytes
        byte = address % self.bytes
        self._memory[block][byte] = data

    def read(self, address):
        block = address // self.bytes
        byte = address % self.bytes
        return self._memory[block][byte]
