from config_loader import CONFIG

# Import from common
from teensy_comms import Teensy
from geometry import OrientedPoint, Point, distance
from logger import Logger, LogLevels

import struct
import math
import asyncio
from enum import Enum
from dataclasses import dataclass
import time

from enum import Enum

class Command(Enum):
    # rasp -> teensy : 0-127 (Convention)
    SET_SPEED_AND_POSITION = b"\x00"  # 0
    
    # two ways : 127 (Convention)
    NACK = b"\x7F"  # 127
    
    # teensy -> rasp : 128-255 (Convention)
    PRINT = b"\x80"  # 128
    UPDATE_ROLLING_BASIS = b"\x81"  # 129
    UNKNOWN_MSG_TYPE = b"\xFF"  # 255


class RollingBasis(Teensy):
    ######################
    # Rolling basis init #
    ######################
    def __init__(
        self,
        logger: Logger,
        ser: int = CONFIG.ROLLING_BASIS_TEENSY_SER,
        crc: bool = CONFIG.TEENSY_CRC,
        vid: int = CONFIG.TEENSY_VID,
        pid: int = CONFIG.TEENSY_PID,
        baudrate: int = CONFIG.TEENSY_BAUDRATE,
        dummy: bool = CONFIG.TEENSY_DUMMY,
    ):
        super().__init__(
            logger, ser=ser, vid=vid, pid=pid, baudrate=baudrate, crc=crc, dummy=dummy
        )
        
        # States of the robot
        self.odometrie: OrientedPoint = OrientedPoint((0.0, 0.0), 0.0)
        self.linear_speed: float = 0.0
        self.angular_speed: float = 0.0
        
        """
        This is used to match a handling function to a message type.
        add_callback can also be used.
        """
        self.add_callback(self.rcv_print, Command.PRINT.value)
        self.add_callback(self.rcv_unknown_msg, Command.UNKNOWN_MSG_TYPE.value)
        self.add_callback(self.rcv_rolling_basis_state, Command.UPDATE_ROLLING_BASIS.value)
    
    #############################
    # Received message handling #
    #############################
    def rcv_print(self, msg: bytes):
        self.logger.log(
            "Teensy says : " + msg.decode("ascii", errors="ignore"), LogLevels.INFO
        )

    def rcv_rolling_basis_state(self, msg: bytes):
        """
        Rolling basis update message:
        - float x (4 bytes)
        - float y (4 bytes)
        - float theta (4 bytes)
        - float current_linear_speed (4 bytes)
        - float current_angular_speed (4 bytes) 
        """
        # Position / odometrie
        self.odometrie = OrientedPoint(
            (struct.unpack("<f", msg[0:4])[0], struct.unpack("<f", msg[4:8])[0]),
            struct.unpack("<f", msg[8:12])[0],
        )
        # Speeds
        self.linear_speed = struct.unpack("<f", msg[12:16])[0]
        self.angular_speed = struct.unpack("<f", msg[16:20])[0]

    def rcv_unknown_msg(self, msg: bytes):
        self.logger.log(
            f"Teensy does not know the command {msg.hex()}", LogLevels.WARNING
        )
        
    ###################
    # Message to send #
    ###################
    @Logger
    def set_speed_and_position(
        self,
        target_linear_speed: float,
        target_angular_speed: float,
        target_position: OrientedPoint
    ) -> None:
        self.logger.log(
            f"Setting speed and position to:\n"
            f"Linear speed: {target_linear_speed}\n"
            f"Angular speed: {target_angular_speed}\n"
            f"Position: {target_position}",
            LogLevels.DEBUG
        )
        msg = (
            Command.SET_SPEED_AND_POSITION.value
            + struct.pack("<f", target_linear_speed)
            + struct.pack("<f", target_angular_speed)
            + struct.pack("<f", target_position.x)
            + struct.pack("<f", target_position.y)
            + struct.pack("<f", target_position.theta)
        )
        # https://docs.python.org/3/library/struct.html#format-characters
        
        self.send_bytes(msg)
        
