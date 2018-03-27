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

from unittest import mock
from vm.assembler import scanner
from vm.assembler.scanner import Token
from vm.assembler.scanner import TokenType

import unittest


class TestScanner(unittest.TestCase):
    def test_scan(self):
        read_data = '''
            $PROGRAM
            TEST
            $DATA
            $CODE
            HALT
            $END
        '''
        tokens = [
            Token(TokenType.PROGRAM, '$PROGRAM'),
            Token(TokenType.LITERAL, 'TEST'),
            Token(TokenType.DATA, '$DATA'),
            Token(TokenType.CODE, '$CODE'),
            Token(TokenType.HALT, 'HALT'),
            Token(TokenType.END, '$END')
        ]

        file = unittest.mock.MagicMock()
        file.__iter__.return_value = iter(read_data.split())

        self.assertEqual(scanner.scan(file), tokens)

if __name__ == '__main__':
    unittest.main()
