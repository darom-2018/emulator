class Semaphore():
    def __init__(self, init_value):
        self._value = init_value

    @property
    def value(self):
        return self._value

    def p(self):
        if self._value > 0:
            self._value -= 1
            return True
        else:
            # print("Waiting for semaphore to unlock")
            return False

    def v(self):
        self._value += 1
