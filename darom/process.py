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
    def __init__(self, priority, name=None, parent=None, owned_res=[], kernel=None):
        # self._process_list = kernel.ready_procs
        self._id = id(self)
        self._created_res = []
        self._status = Status.READY
        self._owned_res = owned_res
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
            print("{:<15} : {}({})".format(self.__class__.__name__, instr[0].__name__, *instr[1]))
            instr[0](*instr[1])

        self._kernel.planner()

    def unblock(self):
        if self._status == Status.BLOCKS:
            self._status = Status.READYS
        else:
            self._status = Status.READY

class StartStop(Process):
    def __init__(self, kernel):
        super().__init__(kernel=kernel, priority=50, name='StartStop')
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

        self._instructions.append((self.shutdown, [1]))

    def shutdown(self, arg):
        sys.exit(1)
        raise Exception("System shutdown")

class Main(Process):
    def __init__(self, kernel, priority):
        super().__init__(kernel=kernel, priority=priority, name="Main")

        self._instructions.append((self._kernel.request_res, [resource.TASK_IN_USER_MEMORY, 1]))


class Loader(Process):
    def __init__(self, kernel, priority):
        super().__init__(kernel=kernel, priority=priority, name="Loader")

        self._instructions.append((self._kernel.request_res, [resource.FROM_UI, 1]))


class Interrupt(Process):
    def __init__(self, kernel, priority):
        super().__init__(kernel=kernel, priority=priority, name="Interrupt")

        self._instructions.append((self._kernel.request_res, [resource.INTERRUPT, 1] ))


class ChannelDevice(Process):
    def __init__(self, kernel, priority):
        super().__init__(kernel=kernel, priority=priority, name="ChannelDevice")

        self._instructions.append((self._kernel.request_res, [resource.DATA_TRANSFER, 1] ))


class JobGovernor(Process):
    def __init__(self, kernel, priority):
        super().__init__(kernel=kernel, priority=priority, name="JobGovernor")

        self._instructions.append((self._kernel.request_res, [resource.FROM_INTERRUPT, 1] ))


class VirtualMachine(Process):
    def __init__(self, kernel, priority):
        super().__init__(kernel=kernel, priority=priority, name="VirtualMachine")

        self._instructions.append((print, ["VirtualMachine"] ))


class Idle(Process):
    def __init__(self, kernel, priority):
        super().__init__(kernel=kernel, priority=priority, name="Idle")

        self._instructions.append((print , ["Idle"]))
        self._instructions.append((time.sleep, [1]))
        self._instructions.append((self.change_ic, [0]))
        self._instructions.append((self._kernel.planner, []))

    def change_ic(self, ic):
        self._ic = ic
