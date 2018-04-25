# © 2018 Ernestas Kulik

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


def to_page_count(byte_count):
    # Round to the nearest word count
    word_count = (byte_count + (constants.WORD_SIZE - 1)) // constants.WORD_SIZE
    # Round to the nearest page count
    page_count = (word_count + (constants.PAGE_SIZE - 1)) // constants.PAGE_SIZE

    return page_count


def to_byte_address(page, word):
    return (
        (page * constants.PAGE_SIZE * constants.WORD_SIZE) +
        (word * constants.WORD_SIZE)
    )


def to_relative_address(byte_address):
    page = byte_address // constants.PAGE_SIZE // constants.WORD_SIZE
    word = (byte_address % (constants.PAGE_SIZE * constants.WORD_SIZE)) // constants.WORD_SIZE
    byte = (byte_address % (constants.PAGE_SIZE * constants.WORD_SIZE)) % constants.WORD_SIZE

    return page, word, byte
