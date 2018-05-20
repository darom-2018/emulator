import random

OS_END = "OSEnd"
FROM_UI = "FromUI"
USER_MEMORY = "Memory"
TASK_IN_USER_MEMORY = "TaskInUserMemory"
INTERRUPT = "Interrupt"
FROM_INTERRUPT = "FromInterrupt"
CHANNEL_DEVICE = "ChannelDevice"
DATA_TRANSFER = "DataTransfer"
FROM_CHANNEL_DEVICE = "FromChannelDevice"


class Resource:
    '''
    parent - resursa sukures procesas
    elements - resurso elementu sarasas
    wait_list - resurso laukianciu procesu sarasas
    '''
    def __init__(self, parent, name):
        self._parent = parent
        self._name = name
        self._id = id(self)
        self._elements = []
        self._wait_list = []

    # def __str__(self):
    #     str = "---------------RESOURCE {} --------------\n".format(self._name)
    #     str += "waiting proceses: \n"
    #     for req in self._wait_list:
    #         str += "{:>20}\n".format(req.proc.name)
    #     str += "available elements:\n"
    #     for elem in self._elements:
    #         str += "\t{}\n".format(elem)
    #     str += "----------------------------------------\n"
    #     return str

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, parent):
        self._parent = parent

    @property
    def elements(self):
        return self._elements

    @property
    def wait_list(self):
        return self._wait_list

    @property
    def name(self):
        return self._name

    def elements_available(self, amount, cond):
        if cond:
            elems = [elem for elem in self._elements if cond(elem)]
        else:
            elems = self._elements
        if len(elems) >= amount:
            return True
        return False

    def get_elements(self, amount, cond):
        if cond:
            candidate = [elem for elem in self._elements if cond(elem)]
        else:
            candidate = self._elements
        elems = random.sample(candidate, amount)
        for e in elems:
            self._elements.remove(e)
        return elems

# Klase, resurso prasymui aprasyti
class ResourceRequest:
    '''
    proc - resurso prasantis procesas
    amount - prasomu resurso elementu skaicius
    cond - funckija, leidzianti atlikti papildomus resurso identifikavimo veiksmus
    '''
    def __init__(self, proc, amount, cond):
        self._proc = proc
        self._amount = amount
        self._cond = cond

    @property
    def proc(self):
        return self._proc

    @property
    def amount(self):
        return self._amount

    @property
    def cond(self):
        return self._cond


class ResourceElement:
    def __init__(self, name, data):
        self._name = name
        self._data = data

    def __repr__(self):
        return "{}: {}".format(self._name, self._data)

    @property
    def name(self):
        return self._name

    @property
    def data(self):
        return self._data
