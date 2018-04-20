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

WORD_SIZE = 2
WORD_MAX = (2 ** (8 * WORD_SIZE)) - 1
BLOCK_SIZE = 16 * WORD_SIZE

SRC_MEMORY = 1
SRC_SUPER_MEMORY = 2
SRC_HDD = 3
SRC_STDIN = 4
SRC_LED = 5

DST_MEMORY = 1
DST_SUPER_MEMORY = 2
DST_HDD = 3
DST_STDOUT = 4
DST_LED = 5
