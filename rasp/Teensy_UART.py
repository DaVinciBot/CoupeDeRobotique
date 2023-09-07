import serial
import serial.tools.list_ports
import struct
from typing import Any
import threading
import time


class Command:
    GoToPoint = b"\x00"
    SetSpeed = b"\x01"


class Teensy:
    def __init__(self, vid: int = 0x16C0, pid: int = 0x0483, baudrate: int = 115200):
        self._teensy = None
        for port in serial.tools.list_ports.comports():
            if port.vid == vid and port.pid == pid:
                self._teensy = serial.Serial(port.device, baudrate=baudrate)
                break
        if self._teensy == None:
            raise Exception("No Device found!")
        self.odometrie = [0.0, 0.0, 0.0]
        self._reciever = threading.Thread(
            target=self.__receiver__, name="TeensyReceiver")
        self._reciever.start()

    def send_bytes(self, data: bytes, end_bytes: bytes = b'\xBA\xDD\x1C\xC5'):
        self._teensy.reset_output_buffer()
        self._teensy.write(data + bytes([len(data)]) + end_bytes)
        while self._teensy.out_waiting:
            pass

    def read_bytes(self, end_bytes: bytes = b'\xBA\xDD\x1C\xC5') -> bytes:
        return self._teensy.read_until(end_bytes)

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
        msg = Command.GoToPoint + \
            struct.pack("<f", x) + \
            struct.pack("<f", y) + \
            struct.pack("<?", direction) + \
            speed + \
            struct.pack("<H", next_position_delay) + \
            struct.pack("<H", action_error_auth) + \
            struct.pack("<H", traj_precision)
        # https://docs.python.org/3/library/struct.html#format-characters
        print(msg.hex(sep="|"))
        self.send_bytes(msg)

    def Set_Speed(self, speed: float) -> None:
        msg = Command.GoToPoint + struct.pack(speed, "f")
        self.send_bytes(msg)

    def __receiver__(self) -> None:
        while True:
            msg = self.read_bytes()
            print(msg.hex(sep="|"))
            print(msg[-5])
            msg = msg[:-5]
            self.odometrie = [struct.unpack("f", msg[1:5]),
                              struct.unpack("f", msg[5:9]),
                              struct.unpack("f", msg[9:13])]            # time.sleep(0.1)
