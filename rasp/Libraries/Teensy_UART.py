import serial
import serial.tools.list_ports
from typing import Any, Callable
import threading
import time
import logging
import crc8


class Teensy():
    def __init__(self, vid: int = 0x16C0, pid: int = 0x0483, baudrate: int = 115200, crc: bool = True):
        self._teensy = None
        self.crc = crc
        self._crc8 = crc8.crc8()

        for port in serial.tools.list_ports.comports():
            if port.vid == vid and port.pid == pid:
                self._teensy = serial.Serial(port.device, baudrate=baudrate)
                break
        if self._teensy == None:
            raise Exception("No Device found!")
        self.messagetype = {}
        self.odometrie = [0.0, 0.0, 0.0]
        self._reciever = threading.Thread(
            target=self.__receiver__, name="TeensyReceiver")
        self._reciever.start()

    def send_bytes(self, data: bytes, end_bytes: bytes = b'\xBA\xDD\x1C\xC5'):
        self._teensy.reset_output_buffer()
        msg = data + bytes([len(data)])
        if self.crc:
            self._crc8.update(msg)
            msg += self._crc8.digest()

        self._teensy.write(msg + end_bytes)
        while self._teensy.out_waiting:
            pass

    def read_bytes(self, end_bytes: bytes = b'\xBA\xDD\x1C\xC5') -> bytes:
        return self._teensy.read_until(end_bytes)

    def add_callback(self, func: Callable[[bytes], None], id: int):
        self.messagetype[id] = func

    def __receiver__(self) -> None:
        """This is started as a thread, handles the data acording to the decided format :

        msg_type | msg_data | msg_length | CRC8 (optional) |MSG_END_BYTES
        size : 1 | msg_length | 1 | 1 | 4

        The size is in bytes.
        It will call the corresponding function 
        """
        while True:
            msg = self.read_bytes()

            if (self.crc):
                crc = msg[-5:-5]
                msg = msg[:-5]
                self._crc8.update(msg)
                if (self._crc8.digest() != crc):
                    logging.warn(
                        "Inivalid CRC8 skipping message"
                    )
                self._crc8.reset()
            else:
                msg = msg[:-4]

            lenmsg = msg[:-1]
            if lenmsg + 5 > len(msg):
                logging.warn(
                    "Received Teensy message does not match declared length")
                continue
            try:
                self.messagetype[msg[0]](msg=msg[1:-6])
            except Exception as e:
                logging.error("Received message handling crashed :\n" + e.args)
                time.sleep(0.5)
