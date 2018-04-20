from . import constants

import pdb

class ChannelDevice():
    def __init__(self, rm):
        self._rm = rm
    #     self._sb = 0
    #     self._db = 0
    #     self._sc = 0
    #     self._dc = 0
    #     self._byte_count = 0
    #     self._buffer = []
    #     self._address = 0
    #
    # @property
    # def sb(self):
    #     return self._sb
    #
    # @property
    # def db(self):
    #     return self._db
    #
    # @property
    # def sc(self):
    #     return self._sc
    #
    # @property
    # def dc(self):
    #     return self._dc
    #
    # @property
    # def byte_count(self):
    #     return self._byte_count
    #
    # @property
    # def buffer(self):
    #     return self._buffer
    #
    # @property
    # def address(self):
    #     return self._address
    #
    # @sb.setter
    # def sb(self, value):
    #     self._sb = value
    #
    # @db.setter
    # def db(self, value):
    #     self._db = value
    #
    # @sc.setter
    # def sc(self, value):
    #     self._sc = value
    #
    # @dc.setter
    # def dc(self, value):
    #     self._dc = value
    #
    # @byte_count.setter
    # def byte_count(self, value):
    #     self._byte_count = value
    #
    # @buffer.setter
    # def buffer(self, value):
    #     self._buffer = value
    #
    # @address.setter
    # def address(self, value):
    #     self._address = value

    def read_stdinput(self, convert_to_int=False):
        bytes = self._rm.input_device.get_input()
        if convert_to_int:
            string = ""
            for byte in bytes:
                string += byte.decode()
            word = int(string).to_bytes(2, byteorder='little')
            return word
        return bytes

    def write_stdoutput(self, data):
        self._rm.output_device.set_output(data)

    def write_led(self, RGB):
        self._rm.led_device.set_RGB(RGB)

    # def transfer_data(self, convert_to_int=False):
    #     dest = self._dc
    #     if dest == constants.DST_MEMORY:
    #         self._load_from_device(convert_to_int)
    #         self._transfer_to_memory()
    #     elif dest == constants.DST_STDOUT:
    #         self._transfer_to_stdout()
    #     elif dest == constants.DST_LED:
    #         self._transfer_to_led()
    #
    # def _transfer_to_memory(self):
    #     for i, byte in enumerate(self._buffer):
    #         print(byte)
    #         self._rm.memory.write_byte(self._rm._vm.memory, self._address + i, byte)
    #
    # def _transfer_to_stdout(self):
    #     self._rm.output_device.set_output(self._buffer)
    #
    # def _transfer_to_led(self):
    #     self._rm.led_device.set_RGB(self._buffer)
    #
    # def _load_from_device(self, convert_to_int):
    #     if self._sc == constants.SRC_STDIN:
    #         self._buffer = self._rm.input_device.get_input()
    #         if convert_to_int:
    #             string = ""
    #             for byte in self._buffer:
    #                 string += byte.decode()
    #             integer = int(string).to_bytes(2, byteorder='little')
    #             self._buffer = []
    #             for byte in integer:
    #                 self._buffer.append(byte.to_bytes(1, byteorder='little'))

    # def load_data(self):
    #     src = self._sc
    #     if src == constants.SRC_MEMORY:
    #         self.load_from_memory()
    #     elif src == constants.SRC_STDIN:
    #         self.load_from_stdin()
    #     elif src == constants.SRC_LED:
    #         pass
    #
    # def load_from_memory(self):
    #     for i in range(self._byte_count):
    #         self._buffer.append(self._rm.memory.read_byte(self._rm._vm.memory, self._address + i))
    #     # self._buffer = self._buffer[:self._byte_count]
    #
    # def load_from_stdin(self):
    #     # for i in range(constants.BLOCK_SIZE * constants.WORD_SIZE):
    #     #     self._buffer.append(self._rm.memory.read_byte(self._rm._vm.memory, i))
    #     self._buffer = [b'h', b'h', b'h', b'h']

    # def store_data(self):
    #     dest = self._dc
    #     if dest == constants.DST_MEMORY:
    #         self.store_to_memory()
    #     elif dest == constants.DST_STDOUT:
    #         self.store_to_stdout()
    #     elif dest == constants.DST_LED:
    #         self.store_to_led()
