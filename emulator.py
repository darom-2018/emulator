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


def start_virtual_machine(window, real_machine_gui, real_machine):
    virtual_machine_id = real_machine.vm_count

    program_file = filedialog.askopenfile(title='Choose a program to load…')
    if program_file is None:
        return

    code = program_file.read()
    program_file.close()
    program_file = open(program_file.name, 'r')

    real_machine.add_storage_device(StorageDevice.from_file(program_file))

    raise NotImplementedError('Storage devices not yet supported')

    virtual_machine_gui = vm_gui.MachineFrame(
        window,
        real_machine_gui,
        virtual_machine_id,
        real_machine.last_vm,
        code)

    virtual_machine_gui.update()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('programs', nargs='*', metavar='PROGRAM')
    parser.add_argument('--cli', action='store_true')
    parser.add_argument('--storage-device', type=open)

    args = parser.parse_args()
    real_machine = RealMachine()

    if args.cli:
        if not args.storage_device:
            print('No storage device specified, nothing to do')
            return

        real_machine.add_storage_device(StorageDevice.from_file(args.storage_device))

        for i, program in enumerate(args.programs):
            print('Loading', program)
            real_machine.load(program)
            print('Running', program)
            real_machine.run(i)
    else:
        window = tkinter.Tk()
        window.title('Emulator')

        real_machine_gui = rm_gui.MachineFrame(window, real_machine)

        load_program_button = tkinter.Button(
            window, text='Load program', command=lambda: start_virtual_machine(
                window, real_machine_gui, real_machine))
        load_program_button.pack(side='bottom')

        window.mainloop()


if __name__ == '__main__':
    sys.exit(main())
