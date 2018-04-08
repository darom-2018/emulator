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

    def size(self):
        data_size = 0
        for datum in self.data:
            data_size += len(datum)

        code_size = 0
        for instruction in self.code:
            code_size += instruction.length

        return data_size, code_size

    def as_bytes(self):
        data_bytes = bytes()
        for datum in self.data:
            data_bytes += datum

        code_bytes = bytes()
        for instruction in self.code:
            code_bytes += instruction.code
            if instruction.takes_arg:
                code_bytes += instruction.arg

        return data_bytes, code_bytes
