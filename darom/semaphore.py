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


class Semaphore():
    def __init__(self, init_value):
        self._value = init_value

    @property
    def value(self):
        return self._value

    def p(self):
        if self._value > 0:
            self._value -= 1
            return True
        else:
            # print("Waiting for semaphore to unlock")
            return False

    def v(self):
        self._value += 1
