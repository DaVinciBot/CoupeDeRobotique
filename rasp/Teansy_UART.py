import serial
import serial.tools.list_ports
import struct
from typing import Any


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

    def send_bytes(self, data: bytes, end_bytes: bytes = b'\xBA\xDD\x1C\xC5'):
        self._teensy.reset_output_buffer()
        self._teensy.write(data + bytes([len(data)]) + end_bytes)
        while self._teensy.out_waiting:
            pass

    def read_bytes(self, end_bytes: bytes = b'\xBA\xDD\x1C\xC5') -> bytes:
        return self._teensy.read_until(end_bytes)

    def Go_To_Point(self, x: float, y: float, theta: float) -> None:
        msg = Command.GoToPoint + struct.pack(x, "f") + struct.pack(y, "f") + struct.pack(theta, "f")
        self.send_bytes(msg)
    
    def Set_Speed(self, speed : float) -> None:
        msg = Command.GoToPoint + struct.pack(speed, "f")
        self.send_bytes(msg)


