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

from enum import auto
from enum import Enum
from enum import unique


@unique
class TokenType(Enum):
    # Sections
    PROGRAM = auto()
    DATA = auto()
    CODE = auto()

    LITERAL = auto()

    # Instructions
    NOP = auto()
    HALT = auto()
    DUP = auto()
    POP = auto()
    POPM = auto()
    PUSH = auto()
    PUSHM = auto()
    PUSHF = auto()
    PUSHDS = auto()
    ADD = auto()
    CMP = auto()
    DEC = auto()
    DIV = auto()
    INC = auto()
    MUL = auto()
    SUB = auto()
    AND = auto()
    NOT = auto()
    OR = auto()
    XOR = auto()
    JMP = auto()
    JC = auto()
    JE = auto()
    JG = auto()
    JGE = auto()
    JL = auto()
    JLE = auto()
    JNC = auto()
    JNE = auto()
    JNP = auto()
    JP = auto()
    LOOP = auto()
    IN = auto()
    INI = auto()
    OUT = auto()
    OUTI = auto()
    SHREAD = auto()
    SHWRITE = auto()
    SHLOCK = auto()
    LED = auto()

token_dict = {
    '$PROGRAM': TokenType.PROGRAM,
    '$DATA': TokenType.DATA,
    '$CODE': TokenType.CODE,
    'NOP': TokenType.NOP,
    'HALT': TokenType.HALT,
    'DUP': TokenType.DUP,
    'POP': TokenType.POP,
    'POPM': TokenType.POPM,
    'PUSH': TokenType.PUSH,
    'PUSHM': TokenType.PUSHM,
    'PUSHF': TokenType.PUSHF,
    'PUSHDS': TokenType.PUSHDS,
    'ADD': TokenType.ADD,
    'CMP': TokenType.CMP,
    'DEC': TokenType.DEC,
    'DIV': TokenType.DIV,
    'INC': TokenType.INC,
    'MUL': TokenType.MUL,
    'SUB': TokenType.SUB,
    'AND': TokenType.AND,
    'NOT': TokenType.NOT,
    'OR': TokenType.OR,
    'XOR': TokenType.XOR,
    'JMP': TokenType.JMP,
    'JC': TokenType.JC,
    'JE': TokenType.JE,
    'JG': TokenType.JG,
    'JGE': TokenType.JGE,
    'JL': TokenType.JL,
    'JLE': TokenType.JLE,
    'JNC': TokenType.JNC,
    'JNE': TokenType.JNE,
    'JNP': TokenType.JNP,
    'JP': TokenType.JP,
    'LOOP': TokenType.LOOP,
    'IN': TokenType.IN,
    'INI': TokenType.INI,
    'OUT': TokenType.OUT,
    'OUTI': TokenType.OUTI,
    'SHREAD': TokenType.SHREAD,
    'SHWRITE': TokenType.SHWRITE,
    'SHLOCK': TokenType.SHLOCK,
    'LED': TokenType.LED,
}


class Token():
    def __repr__(self):
        return "({}, {})".format(self.type, self.value)

    def __init__(self, type, value):
        self._type = type
        self._value = value

    @property
    def type(self):
        return self._type

    @property
    def value(self):
        return self._value


def scan(file):
    tokens = []

    for line in file:
        for word in line.strip().split():
            type = token_dict.get(word.upper(), TokenType.LITERAL)

            tokens.append(Token(type, word))

    return tokens
