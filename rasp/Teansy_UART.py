import serial
import serial.tools.list_ports


class Teensy:
    def __init__(self, vid: int = 0x16C0, pid: int = 0x0483, baudrate: int = 115200):
        self._teensy = None
        for port in serial.tools.list_ports.comports():
            if port.vid == vid and port.pid == pid:
                self._teensy = serial.Serial(port.device, baudrate=baudrate)
                break
        if self._teensy == None:
            raise Exception("No Device found!")

    def send_bytes(self, data: bytes, end_bytes: bytes = b'\xDE\xAD\xBE\xEF'):
        self._teensy.reset_output_buffer()
        self._teensy.write(data + bytes([len(data)]) + end_bytes)
        while self._teensy.out_waiting:
            pass

    def read_bytes(self, end_bytes: bytes = b'\xDE\xAD\xBE\xEF') -> bytes:
        return self._teensy.read_until(end_bytes)
