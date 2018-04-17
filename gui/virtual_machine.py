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
from tkinter import scrolledtext
from darom import constants


class ProcessorFrame:
    class Registers(enum.Enum):
        PC = enum.auto()
        SP = enum.auto()
        DS = enum.auto()
        FLAGS = enum.auto()

    def __init__(self, window):
        self.frame = tkinter.LabelFrame(
            window, text="Processor", padx=5, pady=5, height=10)
        self.frame.pack(side="top")
        self.registers = []

        column = 0
        for register in range(1, len(self.Registers) + 1):
            column += 1
            label = tkinter.Label(
                self.frame, text="{}:".format(
                    self.Registers(register).name))
            label.grid(row=1, column=column)
            column += 1
            entry = tkinter.Entry(self.frame, width=4)
            self.registers.append(entry)
            entry.grid(row=1, column=column)


class MemoryFrame:
    def __init__(self, window):
        self.frame = tkinter.LabelFrame(window, text="Memory", padx=5, pady=5)
        self.frame.pack(side="top")

        self.columns, self.rows = 16, 16
        self.cells = []

        for row in range(self.rows):
            for column in range(self.columns):
                entry = tkinter.Entry(self.frame, width=4)
                self.cells.append(entry)
                entry.grid(row=row, column=column)


class IOFrame:
    def __init__(self, window):
        self.frame = tkinter.LabelFrame(
            window, text="I/O", padx=5, pady=5)
        self.frame.pack(side="top")

        self.input_frame = tkinter.LabelFrame(
            self.frame, text="Input", padx=5, pady=5)
        self.input_frame.pack(side="top")

        self.output_frame = tkinter.LabelFrame(
            self.frame, text="Output", padx=5, pady=5)
        self.output_frame.pack(side="top")

        self.input_entry = tkinter.Entry(self.input_frame, width=45)
        self.input_entry.pack(side="top")

        self.output_label = scrolledtext.ScrolledText(
            self.output_frame, width=32, height=5)
        self.output_label.pack(side="top")
        self.output_label.config(state=tkinter.DISABLED)


class ProgramFrame:
    def __init__(self, window, code):
        self.frame = tkinter.LabelFrame(
            window, text="Program", padx=5, pady=5)
        self.frame.pack(side="top")

        code_box = scrolledtext.ScrolledText(
            self.frame, width=80, height=37)
        code_box.pack(side="top")

        code = code.split('\n')
        text = ""
        for i in range(len(code)):
            text += "{:02X}: {}\n".format(i, code[i])
        code_box.insert(tkinter.END, text)
        code_box.config(state=tkinter.DISABLED)


class MachineFrame:
    def __init__(self, window, rm_gui, vm_id, vm, code):
        window = tkinter.Toplevel(window)

        self.rm_gui = rm_gui
        self.vm_id = vm_id
        self.vm = vm
        self.rm = self.vm.rm
        self.code = code

        self.frame = tkinter.LabelFrame(
            window, text="Virtual Machine", padx=5, pady=5)
        self.frame.pack(side="left")

        self.io_frame = IOFrame(self.frame)
        self.processor_frame = ProcessorFrame(self.frame)
        self.memory_frame = MemoryFrame(self.frame)
        self.program_frame = ProgramFrame(window, code)

        input_button = tkinter.Button(
            self.io_frame.input_frame,
            text="Input",
            command=self.input)
        input_button.pack(side="bottom")

        step_button = tkinter.Button(
            self.program_frame.frame,
            text="Step",
            command=self.step)
        step_button.pack(side="right")

        run_buton = tkinter.Button(
            self.program_frame.frame,
            text="Run",
            command=self.run)
        run_buton.pack(side="right")

        change_button = tkinter.Button(
            self.frame, text="Change memory & registers", command=self.modify)
        change_button.pack(side="bottom")

        self.update()

    def input(self):
        pass

    def output(self):
        self.io_frame.output_label.config(state=tkinter.NORMAL)
        self.io_frame.output_label.config(state=tkinter.DISABLED)

    def step(self):
        pass

    def run(self):
        self.rm.run(self.vm_id)
        self.update()

    def update(self):
        self.update_registers()
        self.update_memory()
        self.rm_gui.update_registers()
        self.rm_gui.update_memory()

    def update_registers(self):
        for register in self.processor_frame.registers:
            register.delete(0, "end")

        self.processor_frame.registers[0].insert(0, self.vm.cpu.pc)
        self.processor_frame.registers[1].insert(0, self.vm.cpu.sp)
        self.processor_frame.registers[2].insert(0, self.vm.cpu.ds)
        self.processor_frame.registers[3].insert(0, self.vm.cpu.flags.hex())

        self.vm.rm.cpu.pc = self.vm.cpu.pc
        self.vm.rm.cpu.sp = self.vm.cpu.sp
        self.vm.rm.cpu.flags = self.vm.cpu.flags

    def update_memory(self):
        memory_allocation = self.vm.memory
        memory = []
        for i in range(0,
                       memory_allocation.block_count * constants.BLOCK_SIZE,
                       constants.WORD_SIZE):
            word = self.vm.rm.memory.read_word(memory_allocation, i)
            memory.append(word)

        for i in range(len(memory)):
            self.memory_frame.cells[i].delete(0, "end")
            self.memory_frame.cells[i].insert(0, memory[i].hex())

    def modify(self):
        self.set_registers()
        self.set_memory()

    def set_registers(self):
        pass

    def set_memory(self):
        # struct.pack("<B", 5)
        pass
