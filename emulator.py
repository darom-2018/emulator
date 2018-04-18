#!/usr/bin/env python3

# © 2018 Ernestas Kulik, Tautvydas Baliukynas

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

import sys
import tkinter
from tkinter import filedialog
from gui import real_machine as rm_gui
from gui import virtual_machine as vm_gui
from darom import rm


def start_virtual_machine(window, real_machine_gui, real_machine, assembler):
    virtual_machine_id = real_machine.vm_count

    program_file = filedialog.askopenfile(
        title='Choose a program to laod...'
    )
    code = program_file.read()
    program_file.close()
    program_file = open(program_file.name, 'r')

    real_machine.load(assembler.assemble(program_file))

    virutal_machine_gui = vm_gui.MachineFrame(
        window,
        real_machine_gui,
        virtual_machine_id,
        real_machine.last_vm,
        code)

    virutal_machine_gui.update()


def main():
    window = tkinter.Tk()
    window.resizable(width=False, height=False)
    window.title('Emulator')

    real_machine = rm.RM()
    assembler = rm.Assembler(real_machine.cpu)

    real_machine_gui = rm_gui.MachineFrame(window, real_machine)

    load_program_button = tkinter.Button(
        window, text='Load program', command=lambda: start_virtual_machine(
            window, real_machine_gui, real_machine, assembler))
    load_program_button.pack(side='bottom')

    window.mainloop()


if __name__ == '__main__':
    sys.exit(main())
