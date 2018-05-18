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

    def __str__(self):
        str = "name: {:<20} {:<20} wait_list_len: {:<5} elements_len: {:<5}".format(
            self._name, self._parent.name, len(self._wait_list), len(self._elements)
        )
        return str

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

    def get_elements(self, amount):
        elems = random.sample(self._elements, amount)
        for e in elems:
            self._elements.remove(e)
        return elems

# Klase, resurso prasymui aprasyti
class ResourceRequest:
    '''
    proc - resurso prasantis procesas
    amount - prasomu resurso elementu skaicius
    '''
    def __init__(self, proc, amount):
        self._proc = proc
        self._amount = amount

    @property
    def proc(self):
        return self._proc

    @property
    def amount(self):
        return self._amount
