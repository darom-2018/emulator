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
from darom import constants


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
            window, text='Processor', padx=5, pady=5, height=10)
        self.frame.pack(side='top')

        column = 0
        for register in range(1, len(self.Registers) + 1):
            column += 1
            label = tkinter.Label(
                self.frame, text='{}:'.format(
                    self.Registers(register).name))
            label.grid(row=1, column=column)
            column += 1
            if register == self.Registers.PTR.value:
                entry = tkinter.Entry(self.frame, width=8)
            elif register < self.Registers.MODE.value:
                entry = tkinter.Entry(self.frame, width=4)
            else:
                entry = tkinter.Entry(self.frame, width=2)
            self.registers.append(entry)
            entry.grid(row=1, column=column)


class MemoryFrame:
    def __init__(self, window):
        self.frame = tkinter.LabelFrame(window, text='Memory', padx=5, pady=5)
        self.frame.pack(side='top')

        self.columns, self.rows = 32, 33
        self.cells = []

        for row in range(self.rows):
            for column in range(self.columns):
                entry = tkinter.Entry(self.frame, width=4)
                self.cells.append(entry)
                entry.grid(row=row, column=column)


class MachineFrame:
    def __init__(self, window, rm):
        self.rm = rm

        self.frame = tkinter.LabelFrame(
            window, text='Real Machine', padx=5, pady=5)
        self.frame.pack(side='top')
        self.processor_frame = ProcessorFrame(self.frame)
        self.memory_frame = MemoryFrame(self.frame)

        change_button = tkinter.Button(
            self.frame, text='Change memory & registers', command=self.modify)
        change_button.pack(side='bottom')

        self.update()

    def update(self):
        self.update_registers()
        self.update_memory()

    def update_registers(self):
        for register in self.processor_frame.registers:
            register.delete(0, 'end')

        self.processor_frame.registers[0].insert(0, self.rm.cpu.ptr)
        self.processor_frame.registers[1].insert(0, self.rm.cpu.pc)
        self.processor_frame.registers[2].insert(0, self.rm.cpu.sp)
        self.processor_frame.registers[3].insert(0, self.rm.cpu.shm)
        self.processor_frame.registers[4].insert(0, self.rm.cpu.flags.hex())
        self.processor_frame.registers[5].insert(0, self.rm.cpu.mode)
        self.processor_frame.registers[6].insert(0, self.rm.cpu.si)
        self.processor_frame.registers[7].insert(0, self.rm.cpu.pi)
        self.processor_frame.registers[8].insert(0, self.rm.cpu.ti)

    def update_memory(self):
        memory = []
        for i in range(0, len(self.rm.memory.data), 2):
            word = bytes()
            word += self.rm.memory.data[i] + self.rm.memory.data[i + 1]
            memory.append(word)

        for i in range(len(memory)):
            self.memory_frame.cells[i].delete(0, 'end')
            self.memory_frame.cells[i].insert(0, memory[i].hex())

    def modify(self):
        self.set_registers()
        self.set_memory()

    def set_registers(self):
        pass

    def set_memory(self):
        # struct.pack('<B', 5)
        pass
