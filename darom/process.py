from darom import resource

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
        self._owned_res = owned_res
        self._priority = priority
        self._parent = parent
        self._children = []
        self._name = name
        self._kernel = kernel

    def __str__(self):
        str = "name: {}, id: {}, priority: {}".format(self._name, self._id, self._priority)
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
    def owned_res(self):
        return self._owned_res

    @kernel.setter
    def kernel(self, kernel):
        self._kernel = kernel

    @parent.setter
    def parent(self, parent):
        self._parent = parent

    def run(self):
        raise Exception("Abstract process run")

    def block(self):
        p = self._kernel.run_proc
        self._kernel.run_proc = None

class StartStop(Process):
    def __init__(self, kernel):
        super().__init__(kernel=kernel, priority=50, name='StartStop')
        self._kernel.processes.append(self)
        self._kernel.ready_procs.append(self)

    def run(self):
        self._kernel.create_res(resource.OS_END)

        self._kernel.create_process(Main(priority=80))
        self._kernel.create_process(Loader(priority=80))
        self._kernel.create_process(Interrupt(priority=80))
        self._kernel.create_process(ChannelDevice(priority=80))

        self._kernel.request_res(resource.OS_END)


class Main(Process):
    def __init__(self, priority):
        super().__init__(priority=priority, name="Main")

    def run(self):
        print("Running main")


class Loader(Process):
    def __init__(self, priority):
        super().__init__(priority=priority, name="Loader")

    def run(self):
        print("Running Loader")


class Interrupt(Process):
    def __init__(self, priority):
        super().__init__(priority=priority, name="Interrupt")

    def run(self):
        print("Interrupt")


class ChannelDevice(Process):
    def __init__(self, priority):
        super().__init__(priority=priority, name="ChannelDevice")

    def run(self):
        print("ChannelDevice")


class JobGovernor(Process):
    def __init__(self, priority):
        super().__init__(priority=priority, name="JobGovernor")

    def run(self):
        print("JobGovernor")


class VirtualMachine(Process):
    def __init__(self, priority):
        super().__init__(priority=priority, name="VirtualMachine")

    def run(self):
        print("VirtualMachine")
