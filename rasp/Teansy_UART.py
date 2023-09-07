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
        self._reciever = threading.Thread(target=self.__receiver__, name= "TeensyReceiver")
        self._reciever.start()

    def send_bytes(self, data: bytes, end_bytes: bytes = b'\xBA\xDD\x1C\xC5'):
        self._teensy.reset_output_buffer()
        self._teensy.write(data + bytes([len(data)]) + end_bytes)
        while self._teensy.out_waiting:
            pass

    def read_bytes(self, end_bytes: bytes = b'\xBA\xDD\x1C\xC5') -> bytes:
        return self._teensy.read_until(end_bytes)

    def Go_To_Point(self, x: float, y: float, theta: float) -> None:
        msg = Command.GoToPoint + struct.pack("f",x) + struct.pack("f",y) + struct.pack("f",theta)
        print(msg.hex(sep="|"))
        self.send_bytes(msg)
    
    def Set_Speed(self, speed : float) -> None:
        msg = Command.GoToPoint + struct.pack(speed, "f")
        self.send_bytes(msg)

    def __receiver__(self) -> None :
        while True :
            msg = self.read_bytes()
            print(msg.hex(sep="|"))
            print(msg[-5])
            msg = msg [:-5]
            print(struct.unpack("f",msg[-4:]))
            print(struct.unpack("f",msg[-8:-4]))
            print(struct.unpack("f",msg[-12:-8]))
            # time.sleep(0.1)
