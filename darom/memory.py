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

import random

from darom import constants
from darom import util
from darom.exceptions import PageFaultError


class Memory:
    def __init__(self, page_count, cpu):
        self._available_pages = [i for i in range(page_count)]
        self._pages = [[
            bytearray(constants.WORD_SIZE) for j in range(constants.PAGE_SIZE)
        ] for i in range(page_count)]
        self._cpu = cpu

    def allocate(self, page_count):
        if page_count <= 0:
            raise Exception('Allocation needs to have a size')

        pages_available = len(self._available_pages)
        if pages_available < page_count:
            raise Exception(
                '{} pages requested while {} are available'.format(
                    page_count, pages_available
                )
            )

        random.shuffle(self._available_pages)

        pages = self._available_pages[:page_count]
        del self._available_pages[:page_count]

        return pages

    def dump(self):
        for i, page in enumerate(self._pages):
            print('P{:02d}: '.format(i), end='')
            for word in page:
                print('{:02x} {:02x} | '.format(word[0], word[1]), end='')
            print()

    def flatten(self):
        return [word for words in self._pages for word in words]

    def read_byte(self, byte_address, virtual=False):
        page, word, byte = util.to_relative_address(byte_address)

        if virtual:
            if page not in range(self._cpu.ptr[1]):
                raise PageFaultError()
            byte_address = util.to_byte_address(self._cpu.ptr[2], page)

            # Calling read_word() without enabling identity paging
            # would cause an infinite loop.
            page = int.from_bytes(
                self.read_word(byte_address, virtual=False),
                byteorder=constants.BYTE_ORDER
            )

        return self._pages[page][word][byte]

    def read_word(self, byte_address, virtual=False):
        word = bytearray(constants.WORD_SIZE)

        for i in range(constants.WORD_SIZE):
            word[i] = self.read_byte(byte_address + i, virtual)

        return word

    def write_byte(self, byte_address, data, virtual=False):
        page, word, byte = util.to_relative_address(byte_address)

        if virtual:
            if page not in range(self._cpu.ptr[1]):
                raise PageFaultError()
            byte_address = util.to_byte_address(self._cpu.ptr[2], page)

            page = int.from_bytes(
                self.read_word(byte_address, virtual=False),
                byteorder=constants.BYTE_ORDER
            )

        self._pages[page][word][byte] = data

    def write_word(self, byte_address, data, virtual=False):
        for i in range(constants.WORD_SIZE):
            self.write_byte(byte_address + i, data[i], virtual)
