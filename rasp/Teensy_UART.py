import serial
import serial.tools.list_ports
import struct
from typing import Any
import threading
import time
import logging


class Teensy:
    #############
    # Internals #
    #############

    MSG_END_BYTES = b'\xBA\xDD\x1C\xC5'

    def __init__(self, vid: int = 0x16C0, pid: int = 0x0483, baudrate: int = 115200):
        self._teensy = None
        for port in serial.tools.list_ports.comports():
            if port.vid == vid and port.pid == pid:
                self._teensy = serial.Serial(port.device, baudrate=baudrate)
                break
        if self._teensy == None:
            logging.error("No Teensy found!", stack_info=True)
        self.odometrie = [0.0, 0.0, 0.0]
        self._reciever = threading.Thread(
            target=self.__receiver__, name="TeensyReceiver")
        self._reciever.start()

    def send_bytes(self, data: bytes, end_bytes: bytes = MSG_END_BYTES):
        self._teensy.reset_output_buffer()
        self._teensy.write(data + bytes([len(data)]) + end_bytes)
        while self._teensy.out_waiting:
            pass

    def read_bytes(self, end_bytes: bytes = MSG_END_BYTES) -> bytes:
        return self._teensy.read_until(end_bytes)

    def __receiver__(self) -> None:
        """This is started as a thread, handles the data acording to the decided format :

        msg_type | msg_data | msg_length | MSG_END_BYTES
        size : 1 | msg_length | 1 | 4

        The size is in bytes.
        It will call the corresponding function 
        """
        while True:
            msg = self.read_bytes()
            lenmsg = msg[-5]
            if lenmsg + 5 > len(msg):
                logging.warn(
                    "Received Teensy message does not match declared length")
                continue
            try:
                self.messagetype[msg[0]](msg[1:-5])
            except Exception as e:
                logging.error("Received message handling crashed \n" + str(e))

    #############################
    # Received message handling #
    #############################

    def rcv_odometrie(self, msg: bytes):
        self.odometrie = [struct.unpack("<f", msg[0:4]),
                          struct.unpack("<f", msg[4:8]),
                          struct.unpack("<f", msg[8:12])]

    """
    This is used to match a handling function to a message type.
    """
    messagetype = {
        b'\x80': rcv_odometrie
    }

    #########################
    # User facing functions #
    #########################

    class Command:
        GoToPoint = b"\x00"
        SetSpeed = b"\x01"

    def Go_To(self, x: float, y: float, direction: bool = False, speed: bytes = b'\xFF', next_position_delay: int = 100, action_error_auth: int = 20, traj_precision: int = 50) -> None:
        """Got to a point

        Args:
            x (float): x coordinate
            y (float): y coordinate
            direction (bool, optional): whether to go backwards or forwards. Defaults to False.
            next_position_delay (int, optional): _description_. Defaults to 100.
            action_error_auth (int, optional): _description_. Defaults to 20.
            traj_precision (int, optional): _description_. Defaults to 50.
        """
        msg = self.Command.GoToPoint + \
            struct.pack("<f", x) + \
            struct.pack("<f", y) + \
            struct.pack("<?", direction) + \
            speed + \
            struct.pack("<H", next_position_delay) + \
            struct.pack("<H", action_error_auth) + \
            struct.pack("<H", traj_precision)
        # https://docs.python.org/3/library/struct.html#format-characters
        # print(msg.hex(sep="|"))
        self.send_bytes(msg)

    def Set_Speed(self, speed: float) -> None:
        msg = self.Command.GoToPoint + struct.pack(speed, "<f")
        self.send_bytes(msg)
