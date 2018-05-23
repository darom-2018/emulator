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

import argparse
import sys
import tkinter
from tkinter import filedialog

from darom.assembler import Assembler
from darom.devices import StorageDevice
from darom.real_machine import RealMachine

from gui import real_machine as rm_gui
from gui import virtual_machine as vm_gui


def load_program(
        window,
        program_loading_window,
        real_machine_gui,
        real_machine,
        program):
    program_loading_window.destroy()

    real_machine.load(program)
    virtual_machine_id = real_machine.vm_count - 1

    code = real_machine.program_text(program)

    virtual_machine_gui = vm_gui.MachineFrame(
        window,
        real_machine_gui,
        virtual_machine_id,
        real_machine.last_vm,
        code)

    virtual_machine_gui.update()


def select_program(window, real_machine_gui, real_machine):
    program_loading_window = tkinter.Toplevel(window)
    program_loading_window.title('Choose a program to load…')
    program_loading_frame = tkinter.LabelFrame(
        program_loading_window, text='Programs', padx=5, pady=5)
    program_loading_frame.pack()
    program_list = tkinter.Listbox(program_loading_frame, width=50, height=20)
    program_list.pack()
    load_button = tkinter.Button(
        program_loading_frame,
        text='Load',
        command=lambda: load_program(
            window,
            program_loading_window,
            real_machine_gui,
            real_machine,
            program_list.selection_get()))
    load_button.pack(side='bottom')

    for program in real_machine.programs:
        program_list.insert('end', program)


def add_storage_device(window, real_machine_gui, real_machine):
    storage_device = filedialog.askopenfile(
        title='Choose a storage device to add…')
    if storage_device is None:
        return

    real_machine.add_storage_device(StorageDevice.from_file(storage_device))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('programs', nargs='*', metavar='PROGRAM')
    parser.add_argument('--cli', action='store_true')
    parser.add_argument('--storage-device', type=open)
    parser.add_argument('--input', action='store')

    args = parser.parse_args()
    real_machine = RealMachine()

    if args.cli:
        if not args.storage_device:
            print('No storage device specified, nothing to do')
            return

        real_machine.add_storage_device(
            StorageDevice.from_file(
                args.storage_device))

        for i, program in enumerate(args.programs):
            print('Loading', program)
            real_machine.load(program)
            print('Running', program)
            while real_machine.current_vm.running:
                real_machine.input_device.input = args.input
                real_machine.step(i)
    else:
        window = tkinter.Tk()
        window.title('Emulator')

        real_machine_gui = rm_gui.MachineFrame(window, real_machine)

        storage_device_button = tkinter.Button(
            window,
            text='Add a storage device',
            command=lambda: add_storage_device(
                window,
                real_machine_gui,
                real_machine))
        storage_device_button.pack(side='top')

        program_load_button = tkinter.Button(
            window, text='Load a program', command=lambda: select_program(
                window, real_machine_gui, real_machine))
        program_load_button.pack(side='bottom')

        window.mainloop()


if __name__ == '__main__':
    sys.exit(main())
