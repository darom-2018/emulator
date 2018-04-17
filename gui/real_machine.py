# © 2018 Tautvydas Baliukynas

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


import enum
import tkinter


class ProcessorFrame:
    class Registers(enum.Enum):
        PTR = enum.auto()
        PC = enum.auto()
        SP = enum.auto()
        SHM = enum.auto()
        FLAGS = enum.auto()
        MODE = enum.auto()
        SI = enum.auto()
        PI = enum.auto()
        TI = enum.auto()

    def __init__(self, window):
        self.registers = []

        self.frame = tkinter.LabelFrame(
            window, text="Processor", padx=5, pady=5, height=10)
        self.frame.pack(side="top")

        column = 0
        for register in range(1, len(self.Registers) + 1):
            column += 1
            label = tkinter.Label(
                self.frame, text="{}:".format(
                    self.Registers(register).name))
            label.grid(row=1, column=column)
            column += 1
            if register == self.Registers.PTR.value:
                entry = tkinter.Entry(self.frame, width=4)
            elif register < self.Registers.MODE.value:
                entry = tkinter.Entry(self.frame, width=2)
            else:
                entry = tkinter.Entry(self.frame, width=1)
            entry.grid(row=1, column=column)


class MemoryFrame:
    def __init__(self, window):
        self.frame = tkinter.LabelFrame(window, text="Memory", padx=5, pady=5)
        self.frame.pack(side="top")

        self.columns, self.rows = 32, 32
        self.cells = [None] * self.rows * self.columns

        for row in range(self.rows):
            for column in range(self.columns):
                entry = tkinter.Entry(self.frame, width=2)
                self.cells.append(entry)
                entry.grid(row=row, column=column)


class MachineFrame:
    def __init__(self, window, real_machine):
        self.real_machine = real_machine

        self.frame = tkinter.LabelFrame(
            window, text="Real Machine", padx=5, pady=5)
        self.frame.pack(side="top")
        self.processor_frame = ProcessorFrame(self.frame)
        self.memory_frame = MemoryFrame(self.frame)

        change_button = tkinter.Button(
            self.frame, text="Change memory & registers", command=self.update)
        change_button.pack(side="bottom")

    def update(self):
        pass
