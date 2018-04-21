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
import struct
from darom import constants


class Registers(enum.Enum):
    PC = 0
    SP = 1
    FLAGS = 2
    PTR = 3
    SHM = 4
    MODE = 5
    SI = 6
    PI = 7
    TI = 8


class ProcessorFrame:

    def __init__(self, window):
        self.registers = []

        self.frame = tkinter.LabelFrame(
            window, text='Processor', padx=5, pady=5, height=10)
        self.frame.pack(side='top')

        column = 0
        for register in range(len(Registers)):
            column += 1
            label = tkinter.Label(
                self.frame, text='{}:'.format(
                    Registers(register).name))
            label.grid(row=1, column=column)
            column += 1
            if register == Registers.PTR.value:
                entry = tkinter.Entry(
                    self.frame, width=8, font=('Consolas', 9))
            elif register < Registers.MODE.value:
                entry = tkinter.Entry(
                    self.frame, width=4, font=('Consolas', 9))
            else:
                entry = tkinter.Entry(
                    self.frame, width=2, font=('Consolas', 9))
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
                entry = tkinter.Entry(
                    self.frame, width=4, font=(
                        'Consolas', 9))
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

        if self.rm.current_vm:
            self.processor_frame.registers[Registers.PC.value].insert(
                0, format(self.rm.current_vm.cpu.pc, '04X'))
            self.processor_frame.registers[Registers.SP.value].insert(
                0, format(self.rm.current_vm.cpu.sp, '04X'))
            self.processor_frame.registers[Registers.FLAGS.value].insert(
                0, format(self.rm.current_vm.cpu.flags, '04X'))
        else:
            self.processor_frame.registers[Registers.PC.value].insert(
                0, format(0, '04X'))
            self.processor_frame.registers[Registers.SP.value].insert(
                0, format(0, '04X'))
            self.processor_frame.registers[Registers.FLAGS.value].insert(
                0, format(0, '04X'))

        self.processor_frame.registers[Registers.PTR.value].insert(
            0, format(self.rm.cpu.ptr, '08X'))
        self.processor_frame.registers[Registers.SHM.value].insert(
            0, format(self.rm.cpu.shm, '04X'))
        self.processor_frame.registers[Registers.MODE.value].insert(
            0, format(self.rm.cpu.mode, '02X'))
        self.processor_frame.registers[Registers.SI.value].insert(
            0, format(self.rm.cpu.si, '02X'))
        self.processor_frame.registers[Registers.PI.value].insert(
            0, format(self.rm.cpu.pi, '02X'))
        self.processor_frame.registers[Registers.TI.value].insert(
            0, format(self.rm.cpu.ti, '02X'))

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
        self.update()

    def set_registers(self):
        if self.rm.current_vm:
            self.rm.current_vm.cpu.pc = int(
                self.processor_frame.registers[Registers.PC.value].get(), 16)
            self.rm.current_vm.cpu.sp = int(
                self.processor_frame.registers[Registers.SP.value].get(), 16)
            self.rm.current_vm.cpu.set_flags(struct.pack('<H', int(
                self.processor_frame.registers[Registers.FLAGS.value].get(), 16)))
        self.rm.cpu.ptr = int(
            self.processor_frame.registers[Registers.PTR.value].get(), 16)
        self.rm.cpu.shm = int(
            self.processor_frame.registers[Registers.SHM.value].get(), 16)
        self.rm.cpu.mode = int(
            self.processor_frame.registers[Registers.MODE.value].get(), 16)
        self.rm.cpu.si = int(
            self.processor_frame.registers[Registers.SI.value].get(), 16)
        self.rm.cpu.pi = int(
            self.processor_frame.registers[Registers.PI.value].get(), 16)
        self.rm.cpu.ti = int(
            self.processor_frame.registers[Registers.TI.value].get(), 16)

    def set_memory(self):
        for i in range(len(self.memory_frame.cells)):
            self.rm.memory.write_word(
                i * 2, struct.pack('>H', int(self.memory_frame.cells[i].get(), 16)))
