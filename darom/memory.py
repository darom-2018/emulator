# © 2018 Justinas Valatkevičius, Ernestas Kulik

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
from . import exceptions

import random


class Allocation:
    def __init__(self, block_count, translation_table):
        self._block_count = block_count
        self._translation_table = translation_table

    @property
    def block_count(self):
        return self._block_count

    def translate(self, block):
        if block not in range(self._block_count):
            raise exceptions.PagingError(
                'Accessing block {} when {} were allocated'.format(
                    block, self._block_count))
        return self._translation_table[block]


class Memory:
    def __init__(self, block_count, block_size):
        self._block_count = block_count
        self._block_size = block_size

        self._allocation_table = {i: None for i in range(self._block_count)}
        self._data = [
            [
                b'\x00' for j in range(self._block_size * constants.WORD_SIZE)
            ] for i in range(self._block_count)
        ]

    @property
    def block_count(self):
        return self._block_count

    @property
    def block_size(self):
        return self._block_size

    @property
    def data(self):
        # Flatten the matrix that represents the memory
        return [cell for block in self._data for cell in block]

    def write_byte(self, address, value):
        self._data[address //
                   (self._block_size *
                    constants.WORD_SIZE)][address %
                                          (self._block_size *
                                           constants.WORD_SIZE)] = value

    def write_word(self, address, value):
        word = (value[:1], value[1:])
        for i in range(constants.WORD_SIZE):
            self.write_byte(address + i, word[i])

    def allocate(self, block_count):
        available_blocks = []

        for k, v in self._allocation_table.items():
            if v is None:
                available_blocks.append(k)

        if block_count > len(available_blocks):
            raise Exception(
                'Not enough memory ({} blocks requested, {} available)'.format(
                    block_count, len(available_blocks)
                )
            )

        chosen_blocks = random.sample(available_blocks, block_count)
        translation_table = {}

        for i in range(block_count):
            translation_table[i] = chosen_blocks[i]

        allocation = Allocation(block_count, translation_table)

        for block in chosen_blocks:
            self._allocation_table[block] = allocation

        return allocation

    def allocate_bytes(self, size):
        # Round to the nearest word count
        word_count = (size + (constants.WORD_SIZE - 1)) // constants.WORD_SIZE
        # Round to the nearest block count
        block_count = (word_count + (self._block_size - 1)) // self._block_size

        return self.allocate(block_count)

    def free(self, allocation):
        for k, v in self._allocation_table.items():
            if v is allocation:
                self._allocation_table[k] = None

    def read_virtual_byte(self, allocation, address):
        block = address // self._block_size // constants.WORD_SIZE
        translated_block = allocation.translate(block)
        byte = address % (self._block_size * constants.WORD_SIZE)

        return self._data[translated_block][byte]

    def read_virtual_word(self, allocation, address):
        word = bytes()

        for i in range(constants.WORD_SIZE):
            byte = self.read_virtual_byte(allocation, address + i)
            word += byte

        return word

    def translate_address(self, block, word):
        address = block * self._block_size * constants.WORD_SIZE
        address += word * constants.WORD_SIZE
        return address

    def write_virtual_byte(self, allocation, address, data):
        block = address // self._block_size // constants.WORD_SIZE
        translated_block = allocation.translate(block)
        byte = address % (self._block_size * constants.WORD_SIZE)

        self._data[translated_block][byte] = data

    def write_virtual_word(self, allocation, address, data):
        for i in range(constants.WORD_SIZE):
            self.write_virtual_byte(allocation, address + i, bytes([data[i]]))

    def _dump(self, allocation):
        for i in range(allocation.block_count):
            print(self._data[allocation.translate(i)])
