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


from . import assembler
from . import cpu
from . import memory

import argparse
import sys


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument('files',
                        nargs='+',
                        type=open,
                        metavar='FILE')

    args = parser.parse_args()

    for file in args.files:
        mem = memory.Memory()
        hlp = cpu.HLP(mem)
        hlp.run(assembler.Assembler(hlp).assemble(file))
