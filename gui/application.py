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


import real_machine as rm
import virtual_machine as vm
import tkinter
from tkinter import filedialog


def start_virtual_machine(window, virtual_machine):
    program_file = filedialog.askopenfile(
        title="Choose a program to laod..."
    )
    code = program_file.read()
    vm.MachineFrame(window, virtual_machine, code)


def main():
    window = tkinter.Tk()
    window.resizable(width=False, height=False)
    window.title("Emulator")

    rm.MachineFrame(window, None)

    load_program_button = tkinter.Button(
        window, text="Load program", command=lambda: start_virtual_machine(
            window, None))
    load_program_button.pack(side="bottom")

    window.mainloop()


if __name__ == "__main__":
    main()
