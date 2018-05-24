# © 2018 Justinas Valatkevičius

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

from darom import resource
from darom import interrupt_handlers

import sys
import time
from enum import Enum

import pdb


class Status(Enum):
    RUN = 1
    READY = 2
    READYS = 3
    BLOCK = 4
    BLOCKS = 5


class Process:
    def __init__(
            self,
            priority,
            name=None,
            parent=None,
            owned_res=None,
            kernel=None):
        self._id = id(self)
        self._created_res = []
        self._status = Status.READY
        self._owned_res = [] if not owned_res else owned_res
        self._priority = priority
        self._parent = parent
        self._children = []
        self._name = name
        self._kernel = kernel

        self._instructions = []
        self._ic = 0

    def __str__(self):
        str = "name: {:<20} {:<20} priority: {}".format(
            self._name, self._status, self._priority)
        return str

    def _change_ic(self, ic):
        self._ic = ic

    @property
    def created_res(self):
        return self._created_res

    @property
    def kernel(self):
        return self._kernel

    @property
    def parent(self):
        return self._parent

    @property
    def children(self):
        return self._children

    @property
    def priority(self):
        return self._priority

    @property
    def name(self):
        return self._name

    @property
    def status(self):
        return self._status

    @property
    def owned_res(self):
        return self._owned_res

    @kernel.setter
    def kernel(self, kernel):
        self._kernel = kernel

    @parent.setter
    def parent(self, parent):
        self._parent = parent

    @status.setter
    def status(self, status):
        self._status = status

    def run(self):
        self._status = Status.RUN
        while self._status == Status.RUN:
            instr = self._instructions[self._ic]
            self._ic += 1
            if instr[1]:
                instr[0](*instr[1])
            else:
                instr[0]()

    def unblock(self):
        if self._status == Status.BLOCKS:
            self._status = Status.READYS
        else:
            self._status = Status.READY


class StartStop(Process):
    def __init__(self, kernel):
        super().__init__(kernel=kernel, priority=5, name='StartStop')
        self._kernel.processes.append(self)
        self._kernel.ready_procs.append(self)

        self._instructions.append((self._kernel.create_res, [resource.OS_END]))
        self._instructions.append(
            (self._kernel.create_res, [resource.FROM_UI]))
        self._instructions.append(
            (self._kernel.create_res, [
                resource.USER_INPUT]))
        self._instructions.append(
            (self._kernel.create_res, [
                resource.USER_MEMORY]))
        self._instructions.append(
            (self._kernel.create_res, [
                resource.TASK_IN_USER_MEMORY]))
        self._instructions.append(
            (self._kernel.create_res, [
                resource.INTERRUPT]))
        self._instructions.append(
            (self._kernel.create_res, [
                resource.FROM_INTERRUPT]))
        self._instructions.append(
            (self._kernel.create_res, [
                resource.CHANNEL_DEVICE]))
        self._instructions.append(
            (self._kernel.create_res, [
                resource.DATA_TRANSFER]))
        self._instructions.append(
            (self._kernel.create_res, [
                resource.FROM_CHANNEL_DEVICE]))

        self._instructions.append(
            (self._kernel.create_process, [
                Main(
                    kernel=self._kernel, priority=80)]))
        self._instructions.append(
            (self._kernel.create_process, [
                Loader(
                    kernel=self._kernel, priority=80)]))
        self._instructions.append(
            (self._kernel.create_process, [
                Interrupt(
                    kernel=self._kernel, priority=70)]))
        self._instructions.append(
            (self._kernel.create_process, [
                ChannelDevice(
                    kernel=self._kernel, priority=80)]))
        self._instructions.append(
            (self._kernel.request_res, [
                resource.OS_END, 1]))
        self._instructions.append((self._kernel.destroy_process, [self]))
        self._instructions.append((self.shutdown, [1]))

    def shutdown(self, arg):
        print("Shutting down OS")
        sys.exit(1)
        raise Exception("System shutdown")


class Main(Process):
    def __init__(self, kernel, priority):
        super().__init__(kernel=kernel, priority=priority, name="Main")

        self._instructions.append((
            self._kernel.request_res,
            [resource.TASK_IN_USER_MEMORY, 1])
        )
        self._instructions.append((self.inspect_resource, []))
        self._instructions.append((self._change_ic, [0]))

    def inspect_resource(self):
        res = self._owned_res[-1]
        if not isinstance(res.data, JobGovernor):
            self._kernel.create_process(
                JobGovernor(
                    kernel=self._kernel,
                    priority=60, vm=res.data
                )
            )
            self._owned_res.remove(res)
        else:
            self._kernel.destroy_process(res.data)


class Loader(Process):
    def __init__(self, kernel, priority):
        super().__init__(kernel=kernel, priority=priority, name="Loader")

        self._instructions.append(
            (self._kernel.request_res, [
                resource.FROM_UI, 1]))


class Interrupt(Process):
    def __init__(self, kernel, priority):
        super().__init__(kernel=kernel, priority=priority, name="Interrupt")

        self._instructions.append(
            (self._kernel.request_res, [
                resource.INTERRUPT, 1]))
        self._instructions.append((self._identify_interrupt, []))
        self._instructions.append((self._change_ic, [0]))

    def _identify_interrupt(self):
        interrupt = self._owned_res[-1].data
        si, pi, ti = interrupt.get('si'), interrupt.get(
            'pi'), interrupt.get('ti')
        vm_id = interrupt.get('vm_id')
        if si > 0:
            if si == 1:
                self._release_interrupt_resource(vm_id, 'halt')
            else:
                self._release_interrupt_resource(vm_id, 'io', si)
        elif pi > 0:
            pass
        elif ti <= 0:
            self._release_interrupt_resource(vm_id, 'timeout')

    def _release_interrupt_resource(self, vm_id, type, si=None):
        self._kernel.release_res(
            resource.FROM_INTERRUPT,
            [{"vm_id": vm_id, "type": type, 'si': si}]
        )


class ChannelDevice(Process):
    def __init__(self, kernel, priority):
        super().__init__(kernel=kernel, priority=priority, name="ChannelDevice")

        self._instructions.append(
            (self._kernel.release_res, [
                resource.CHANNEL_DEVICE, []]))
        self._instructions.append(
            (self._kernel.request_res, [
                resource.DATA_TRANSFER, 1]))
        self._instructions.append((self._transfer_data, []))
        self._instructions.append(
            (self._kernel.release_res, [
                resource.FROM_CHANNEL_DEVICE, [1]]))
        self._instructions.append((self._change_ic, [1]))

    def _transfer_data(self):
        info = self._owned_res[-1].data
        dest = info.get('dest')
        if dest == 'led':
            led_device = self._kernel._rm.led_device
            led_device.rgb = info.get('rgb')


class JobGovernor(Process):
    def __init__(self, kernel, priority, vm):
        super().__init__(
            kernel=kernel,
            priority=priority,
            name="JobGovernor {}".format(
                vm.get('vm_id')))
        self._vm_id = vm.get('vm_id')

        self._pi_handlers = [
            None,
            interrupt_handlers.invalid_instruction_code,
            interrupt_handlers.invalid_operand,
            interrupt_handlers.page_fault,
            interrupt_handlers.stack_overflow
        ]
        self._si_handlers = [
            None,
            interrupt_handlers.halt,
            interrupt_handlers.in_,
            interrupt_handlers.ini,
            interrupt_handlers.out,
            interrupt_handlers.outi,
            interrupt_handlers.shread,
            interrupt_handlers.shwrite,
            interrupt_handlers.shlock,
            interrupt_handlers.shunlock,
            interrupt_handlers.led
        ]

        self._instructions.append(
            (
                self._kernel.create_process,
                [VirtualMachine(kernel=self._kernel, priority=40, vm=vm)]
            )
        )
        self._instructions.append(
            (self._kernel.request_res, [
                resource.FROM_INTERRUPT, 1, self._check_vm_id(
                    vm.get('vm_id'))]))
        self._instructions.append((self._inspect_from_interrupt, []))
        self._instructions.append((self._handle_input, []))
        self._instructions.append((self._change_ic, [1]))

    def _check_vm_id(self, vm_id):
        return lambda res_element: res_element.data.get("vm_id") == vm_id

    def _inspect_from_interrupt(self):
        from_interrupt = self._owned_res[-1]
        interrupt_type = from_interrupt.data.get('type')
        self._si = from_interrupt.data.get('si')
        self._vm_process = self._children[-1]
        if interrupt_type == 'timeout':
            self._kernel._rm._cpu.ti = 100
            self._kernel._rm.current_vm._cpu._halted = False
            self._vm_process._change_ic(0)
            self._vm_process._set_status(Status.READY)
        elif interrupt_type == 'io':
            if self._si == 2 or self._si == 3:
                self._kernel.request_res(
                    resource.USER_INPUT,
                    1,
                    cond=lambda elem: elem.data.get('vm_id') == self._vm_id
                )
                return
            else:
                self._si_handlers[self._si](self._kernel._rm)
            self._kernel._rm.current_vm._cpu._halted = False
            self._vm_process._change_ic(0)
            self._vm_process._set_status(Status.READY)
        elif interrupt_type == 'halt':
            self._kernel.release_res(resource.TASK_IN_USER_MEMORY, [self])
        self._ic += 1

    def _handle_input(self):
        from_input = self._owned_res[-1]
        vm_id = from_input.data.get('vm_id')
        self._kernel._rm.run(vm_id)
        self._si_handlers[self._si](self._kernel._rm)
        self._kernel._rm._vms[vm_id][0].cpu._halted = False
        self._vm_process._change_ic(0)
        self._vm_process._set_status(Status.READY)


class VirtualMachine(Process):
    def __init__(self, kernel, priority, vm):
        vm_id = vm.get('vm_id')
        super().__init__(
            kernel=kernel,
            priority=priority,
            name="VirtualMachine {}".format(vm_id))

        self._instructions.append((self._kernel._rm.run, [vm_id]))
        self._instructions.append((self._update_vm_gui, [vm.get('gui')]))
        self._instructions.append((self._set_status, [Status.BLOCK]))

    def _set_status(self, status):
        self.status = status

    def _update_vm_gui(self, gui):
        gui.update()


class Idle(Process):
    def __init__(self, kernel, priority):
        super().__init__(kernel=kernel, priority=priority, name="Idle")

        self._instructions.append((print, ["Idle"]))
        self._instructions.append((time.sleep, [1]))
        self._instructions.append((self.change_ic, [0]))
        self._instructions.append((self._kernel.planner, []))

    def change_ic(self, ic):
        self._ic = ic
