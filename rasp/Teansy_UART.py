import serial
import serial.tools.list_ports

class Teensy:
    def __init__(self,vid : int , pid : int):
        self._teensy = None
        for port in serial.tools.list_ports.comports():
            if port.vid == vid and port.pid == pid:
                self._teensy = serial.Serial(port.device)
                break
        if self._teensy == None :
            raise Exception("No Device found!")
                
    def send_bytes(self,data : bytearray, end_bytes : bytearray = b'0xDEADBEEF') :
        self._teensy.reset_output_buffer()
        self._teensy.write(data.append(len(data),end_bytes))
        while self._teensy.out_waiting :
            pass
        
    def read_bytes(self,end_bytes : bytearray = b'0xDEADBEEF') -> bytearray:
        return self._teensy.read_until(end_bytes)