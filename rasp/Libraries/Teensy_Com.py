# autopep8: off
# import os 
# import sys
# sys.path.append(os.getcwd())
# autopep8: on

import serial
import serial.tools.list_ports
from typing import Any, Callable
import threading
import time
import logging
import crc8
import struct


class TeensyException(Exception):
    pass


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
            raise TeensyException("No Device !")
        self.messagetype = {}
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

            lenmsg = msg[-1]

            if lenmsg > len(msg):
                logging.warn(
                    "Received Teensy message that does not match declared length " + msg.hex(sep = " "))
                continue
            try:
                if msg[0] != 128 :
                    print(msg)
                self.messagetype[msg[0]](msg[1:-1])
            except Exception as e:
                logging.error("Received message handling crashed :\n" + e.args)
                time.sleep(0.5)


class Rolling_basis(Teensy):
    ######################
    # Rolling basis init #
    ######################

    def __init__(self, vid: int = 5824, pid: int = 1155, baudrate: int = 115200, crc: bool = True):
        super().__init__(vid, pid, baudrate, crc)
        # All position are in the form tuple(X, Y, THETA)
        self.odometrie = (0.0, 0.0, 0.0)
        self.position_offset = (0.0, 0.0, 0.0)
        self.action_finished = False
        """
        This is used to match a handling function to a message type.
        add_callback can also be used.
        """
        self.messagetype = {
            128: self.rcv_odometrie,  # \x80
            129: self.rcv_action_finish  # \x45
        }

    #####################
    # Position handling #
    #####################

    def true_pos(self, position: list[float, float, float]) -> tuple[float, float, float]:
        ret = []
        for i in range(3):
            ret.append(position[i] + self.position_offset[i])
        return ret

    #############################
    # Received message handling #
    #############################

    def rcv_odometrie(self, msg: bytes):
        # print(msg.hex(sep =  " "))
        self.odometrie = (struct.unpack("<f", msg[0:4])[0],
                          struct.unpack("<f", msg[4:8])[0],
                          struct.unpack("<f", msg[8:12])[0])

    def rcv_action_finish(self, msg: bytes):
        print(msg.hex())
        self.action_finished = True

    #########################
    # User facing functions #
    #########################

    class Command:
        GoToPoint = b"\x00"
        SetSpeed = b"\x01"
        KeepCurrentPosition = b'\02'
        DisablePid = b'\03'
        EnablePid = b'\04'

    def Go_To(self, position: list[float, float, float], direction: bool = False, speed: bytes = b'\x64', next_position_delay: int = 100, action_error_auth: int = 20, traj_precision: int = 50) -> None:
        """Got to a point

        Args:
            x (float): x coordinate
            y (float): y coordinate
            direction (bool, optional): whether to go backwards or forwards. Defaults to False.
            next_position_delay (int, optional): _description_. Defaults to 100.
            action_error_auth (int, optional): _description_. Defaults to 20.
            traj_precision (int, optional): _description_. Defaults to 50.
        """

        pos = self.true_pos(position)
        msg = self.Command.GoToPoint + \
            struct.pack("<f", pos[0]) + \
            struct.pack("<f", pos[1]) + \
            struct.pack("<?", direction) + \
            speed + \
            struct.pack("<H", next_position_delay) + \
            struct.pack("<H", action_error_auth) + \
            struct.pack("<H", traj_precision)
        # https://docs.python.org/3/library/struct.html#format-characters

        self.send_bytes(msg)
        self.action_finished = True

    def Set_Speed(self, speed: float) -> None:
        msg = self.Command.GoToPoint + struct.pack(speed, "f")
        self.send_bytes(msg)

    def Keep_Current_Position(self):
        msg = self.Command.KeepCurrentPosition
        self.send_bytes(msg)

    def Disable_Pid(self):
        msg = self.Command.DisablePid
        self.send_bytes(msg)

    def Enable_Pid(self):
        msg = self.Command.EnablePid
        self.send_bytes(msg)

    def Home_Position(self, timeout: float = 1, epsilon: float = 1):
        pos = self.odometrie[0]
        self.Go_To([-100, 0, 0], True, b'\x0A')
        timer = time.time()
        offset = [0.0, 0.0, 0.0]

        while True:
            if abs(pos - self.odometrie[0]) > epsilon:
                pos = self.odometrie[0]
                timer = time.time()
                continue
            if time.time() - timer > timeout:
                offset[0] = self.odometrie[0]
                offset[2] = self.odometrie[2]
                break

        self.Go_To([0, 0, 0])
        while not self.action_finished:
            time.sleep(0.1)
        # time.sleep(5)

        pos = self.odometrie[1]
        self.Go_To([0, -100, 0], False, b'\x0A')
        timer = time.time()

        while True:
            if abs(pos - self.odometrie[1]) > epsilon:
                pos = self.odometrie[1]
                timer = time.time()
                continue
            if time.time() - timer > timeout:
                offset[1] = self.odometrie[1]
                break

        self.position_offset = offset
        self.Go_To([30, 30, 0])
        while not self.action_finished:
            time.sleep(0.1)
        # time.sleep(5)
