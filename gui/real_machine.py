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


class LEDFrame:
    def __init__(self, window):
        self.frame = tkinter.LabelFrame(
            window, text='LED', padx=5, pady=5, height=10)
        self.frame.pack(side='right')
        self.label = tkinter.Label(self.frame, width=2)
        self.label.grid(row=1, column=1)


class ProcessorFrame:
    def __init__(self, window):
        self.registers = []

        self.frame = tkinter.LabelFrame(
            window, text='Processor', padx=5, pady=5, height=10)
        self.frame.pack(side='left')

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
        self.frame.pack(side='top', fill='both', expand='true')

        vertical_scroll_bar = tkinter.Scrollbar(self.frame, orient='vertical')
        vertical_scroll_bar.pack(fill='y', side='right', expand='false')

        horizontal_scroll_bar = tkinter.Scrollbar(
            self.frame, orient='horizontal')
        horizontal_scroll_bar.pack(fill='x', side='bottom', expand='false')

        self._canvas = tkinter.Canvas(
            self.frame,
            bd=0,
            highlightthickness=0,
            yscrollcommand=vertical_scroll_bar.set,
            xscrollcommand=horizontal_scroll_bar.set)
        self._canvas.pack(fill='both', expand='true')

        vertical_scroll_bar.config(command=self._canvas.yview)
        horizontal_scroll_bar.config(command=self._canvas.xview)

        self._frame = tkinter.Frame(self._canvas)

        self._canvas.bind('<Configure>', self._canvas_configure)
        self._window = self._canvas.create_window(
            0, 0, window=self._frame, anchor='nw'
        )
        self._canvas.xview_moveto(0)
        self._canvas.yview_moveto(0)

        self.columns, self.rows = 32, 35
        self.cells = []

        for row in range(self.rows):
            self._frame.grid_rowconfigure(row, weight=1)
            for column in range(self.columns):
                self._frame.grid_columnconfigure(column, weight=1)
                entry = tkinter.Entry(
                    self._frame, width=4, font=(
                        'Consolas', 9))
                self.cells.append(entry)
                entry.grid(row=row, column=column)

    def _canvas_configure(self, event):
        self._canvas.update_idletasks()

        height_request = self._frame.winfo_reqheight()
        width_request = self._frame.winfo_reqwidth()
        canvas_height = self._canvas.winfo_height()
        canvas_width = self._canvas.winfo_width()

        self._canvas.itemconfigure(
            self._window,
            width=canvas_width,
            height=canvas_height)

        if canvas_height > height_request:
            self._canvas.itemconfigure(self._window, height=canvas_height)
            self._canvas.config(scrollregion='0 0 {} {}'.format(
                width_request, canvas_height)
            )
        else:
            self._canvas.itemconfigure(self._window, height=height_request)
            self._canvas.config(scrollregion='0 0 {} {}'.format(
                width_request, height_request)
            )

        if canvas_width > width_request:
            self._canvas.itemconfigure(self._window, width=canvas_width)
            self._canvas.config(scrollregion='0 0 {} {}'.format(
                canvas_width, height_request)
            )
        else:
            self._canvas.itemconfigure(self._window, width=width_request)
            self._canvas.config(scrollregion='0 0 {} {}'.format(
                width_request, height_request)
            )


class MachineFrame:
    def __init__(self, window, rm):
        self.rm = rm

        self.frame = tkinter.LabelFrame(
            window, text='Real Machine', padx=5, pady=5)
        self.frame.pack(side='top', fill='both', expand='true')
        self.top_frame = tkinter.Frame(self.frame)
        self.top_frame.pack(side='top')
        self.processor_frame = ProcessorFrame(self.top_frame)
        self.led_frame = LEDFrame(self.top_frame)
        self.memory_frame = MemoryFrame(self.frame)

        change_button = tkinter.Button(
            self.frame, text='Change memory & registers', command=self.modify)
        change_button.pack(side='bottom')

        self.update()

    def update(self):
        self.update_registers()
        self.update_memory()
        self.update_led()

    def update_registers(self):
        for register in self.processor_frame.registers:
            register.delete(0, 'end')

        if self.rm.current_vm:
            self.processor_frame.registers[Registers.PC.value].insert(
                0, format(self.rm.current_vm.cpu.pc, '04X'))
            self.processor_frame.registers[Registers.SP.value].insert(
                0, format(self.rm.current_vm.cpu.sp, '04X'))
            self.processor_frame.registers[Registers.FLAGS.value].insert(
                0, self.rm.current_vm.cpu.flags.hex().upper())
        else:
            self.processor_frame.registers[Registers.PC.value].insert(
                0, format(0, '04X'))
            self.processor_frame.registers[Registers.SP.value].insert(
                0, format(0, '04X'))
            self.processor_frame.registers[Registers.FLAGS.value].insert(
                0, format(0, '04X'))

        self.processor_frame.registers[Registers.PTR.value].insert(
            0, self.rm.cpu.ptr.hex().upper())
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
        for page in self.rm.memory._pages:
            for word in page:
                memory.append(word)

        for i in range(len(memory)):
            self.memory_frame.cells[i].delete(0, 'end')
            self.memory_frame.cells[i].insert(0, memory[i].hex())

    def update_led(self):
        self.led_frame.label.config(bg=self.rm.led_device.rgb)

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
            self.rm.current_vm.cpu.flags = bytearray(struct.pack('>H', int(
                self.processor_frame.registers[Registers.FLAGS.value].get(), 16)))
        self.rm.cpu.ptr = bytearray(struct.pack('>I', int(
            self.processor_frame.registers[Registers.PTR.value].get(), 16)))
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
