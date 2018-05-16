OS_END = "OSEnd"
FROM_UI = "FromUI"
MEMORY = "Memory"

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
        str = "name: {}, id: {}, parent: {}, wait_list_len: {}, elements_len: {}\n".format(
            self._name, self._id, self._parent.name, len(self._wait_list), len(self._elements)
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
