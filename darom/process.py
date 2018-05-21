from darom import resource

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
    '''
    process_list - procesų sąrašas, kuriam priklauso procesas
    created_res - proceso sukurtu resursu sarasas
    owned_res - procesui kurimo metu paduoti resursai
    name - proceso isorinis vardas
    '''
    def __init__(self, priority, name=None, parent=None, owned_res=None, kernel=None):
        # self._process_list = kernel.ready_procs
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
        # instruction counter
        self._ic = 0

    def __str__(self):
        str = "name: {:<20} {:<20} priority: {}".format(self._name, self._status, self._priority)
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
                # print("{:<15} : {}({})".format(self.__class__.__name__, instr[0].__name__, *instr[1]))
                instr[0](*instr[1])
            else:
                # print("{:<15} : {}()".format(self.__class__.__name__, instr[0].__name__))
                instr[0]()

        # self._kernel.planner()

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
        self._instructions.append((self._kernel.create_res, [resource.FROM_UI]))
        self._instructions.append((self._kernel.create_res, [resource.USER_MEMORY]))
        self._instructions.append((self._kernel.create_res, [resource.TASK_IN_USER_MEMORY]))
        self._instructions.append((self._kernel.create_res, [resource.INTERRUPT]))
        self._instructions.append((self._kernel.create_res, [resource.FROM_INTERRUPT]))
        self._instructions.append((self._kernel.create_res, [resource.CHANNEL_DEVICE]))
        self._instructions.append((self._kernel.create_res, [resource.DATA_TRANSFER]))
        self._instructions.append((self._kernel.create_res, [resource.FROM_CHANNEL_DEVICE]))

        self._instructions.append((self._kernel.create_process, [Main(kernel=self._kernel, priority=80)]             ))
        self._instructions.append((self._kernel.create_process, [Loader(kernel=self._kernel, priority=80)]           ))
        self._instructions.append((self._kernel.create_process, [Interrupt(kernel=self._kernel, priority=80)]        ))
        self._instructions.append((self._kernel.create_process, [ChannelDevice(kernel=self._kernel, priority=80)]    ))
        # self._instructions.append((self._kernel.create_process, [Idle(kernel=self._kernel, priority=80)]             ))
        self._instructions.append((self._kernel.request_res, [resource.OS_END, 1]               ))
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

        self._instructions.append((self._kernel.request_res, [resource.FROM_UI, 1]))


class Interrupt(Process):
    def __init__(self, kernel, priority):
        super().__init__(kernel=kernel, priority=priority, name="Interrupt")

        self._instructions.append((self._kernel.request_res, [resource.INTERRUPT, 1] ))
        self._instructions.append((self._identify_interrupt, []))
        self._instructions.append((self._change_ic, [0]))

    def _identify_interrupt(self):
        interrupt = self._owned_res[-1].data
        vm_id = interrupt.get('vm_id')
        if interrupt.get('ti') == 0:
            self._release_interrupt_resource(vm_id, 'timeout')
        elif interrupt.get('si') > 0:
            if interrupt.get('si') == 1:
                self._release_interrupt_resource(vm_id, 'halt')
            else:
                self._release_interrupt_resource(vm_id, 'io')

    def _release_interrupt_resource(self, vm_id, type):
        self._kernel.release_res(
            resource.FROM_INTERRUPT,
            [{"vm_id": vm_id, "type": type}]
        )


class ChannelDevice(Process):
    def __init__(self, kernel, priority):
        super().__init__(kernel=kernel, priority=priority, name="ChannelDevice")

        self._instructions.append((self._kernel.request_res, [resource.DATA_TRANSFER, 1] ))


class JobGovernor(Process):
    def __init__(self, kernel, priority, vm):
        super().__init__(kernel=kernel, priority=priority, name="JobGovernor {}".format(vm.get('vm_id')))

        self._instructions.append(
            (
                self._kernel.create_process,
                [VirtualMachine(kernel=self._kernel, priority=40, vm=vm)]
            )
        )
        self._instructions.append(
            (self._kernel.request_res, [resource.FROM_INTERRUPT, 1, self._check_vm_id(vm.get('vm_id'))])
        )
        self._instructions.append((self._inspect_from_interrupt, []))
        self._instructions.append((self._change_ic, [1]))

    def _check_vm_id(self, vm_id):
        return lambda res_element: res_element.data.get("vm_id") == vm_id

    def _inspect_from_interrupt(self):
        from_interrupt = self._owned_res[-1]
        interrupt_type = from_interrupt.data.get('type')
        vm = self._children[-1]
        if interrupt_type == 'timeout':
            self._kernel._rm._cpu.reset_registers()
            self._kernel._rm.current_vm._cpu._halted = False
            vm._change_ic(0)
            vm._set_status(Status.READY)
        elif interrupt_type == 'halt':
            self._kernel.release_res(resource.TASK_IN_USER_MEMORY, [self])


class VirtualMachine(Process):
    def __init__(self, kernel, priority, vm):
        vm_id = vm.get('vm_id')
        super().__init__(kernel=kernel, priority=priority, name="VirtualMachine {}".format(vm_id))

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

        self._instructions.append((print , ["Idle"]))
        self._instructions.append((time.sleep, [1]))
        self._instructions.append((self.change_ic, [0]))
        self._instructions.append((self._kernel.planner, []))

    def change_ic(self, ic):
        self._ic = ic
