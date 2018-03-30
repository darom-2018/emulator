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


class Program():
    def __init__(self, name, data, code):
        self._name = name
        self._data = data
        self._code = code

    def __str__(self):
        string = '''Program “{}”:
    Data:
        {}
    Code:
        {}'''.format(self.name, self.data, self.code)

        return string

    @property
    def name(self):
        return self._name

    @property
    def data(self):
        return self._data

    @property
    def code(self):
        return self._code
