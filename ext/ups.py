import struct

import smbus2

from ext.log import logging

logger = logging.getLogger("ups.module")


class UPS:
    def __init__(self):
        self.bus = smbus2.SMBus(1)
        self.address = 0x36
        self.bus.write_word_data(self.address, 0x06, 0x4000)
        self.bus.write_word_data(self.address, 0xFE, 0x0054)


    def read_voltage(self):
        try:
            read = self.bus.read_word_data(self.address, 0x02)
            swapped = struct.unpack("<H", struct.pack(">H", read))[0]
            voltage = swapped * 1.25 / 1000 / 16
            return voltage
        except Exception as error:
            logging.error(f"Failed to read voltage from UPS: {type(error)}: {error}")


    def read_capacity(self):
        try:
            read = self.bus.read_word_data(self.address, 0x04)
            swapped = struct.unpack("<H", struct.pack(">H", read))[0]
            capacity = swapped / 256
            return capacity
        except Exception as error:
            logging.error(f"Failed to read capacity from UPS: {type(error)}: {error}")
