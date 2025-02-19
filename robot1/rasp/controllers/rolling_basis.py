#!/usr/bin/env python3
"""
Module for handling communication with the Teensy microcontroller to control the robot's rolling basis.
It manages state updates, PID configuration, and sends/receives commands between the Raspberry Pi and Teensy.
"""

from config_loader import CONFIG

# ====== Standard Library Imports ======
from enum import Enum
from dataclasses import dataclass
import struct
from typing import Any, Dict

# ====== Internal Project Imports ======
from teensy_comms import Teensy
from geometry import OrientedPoint
from loggerplusplus import Logger, log


class Command(Enum):
    """
    Enumeration for command types exchanged between the Raspberry Pi and Teensy.

    Commands from Raspberry Pi to Teensy are in the range 0-127,
    while those from Teensy to Raspberry Pi are in the range 128-255.
    """
    # rasp -> teensy : 0-127 (Convention)
    SET_SPEED_AND_POSITION = 0
    SET_PID = 1
    SET_ODOMETRIE = 2
    RESET_TEENSY = 3

    # two ways : 127 (Convention)
    NACK = 127

    # teensy -> rasp : 128-255 (Convention)
    PRINT = 128
    UPDATE_ROLLING_BASIS = 129
    UNKNOWN_MSG_TYPE = 255

    # To use for message creation
    def to_bytes(self) -> bytes:
        """
        Converts the command to its byte representation.

        Returns:
            bytes: Single-byte representation of the command.
        """
        return bytes([self.value])


class PID_ID(Enum):
    """
    Identifiers for the different PID controllers.
    """
    LINEAR_SPEED = 0
    ANGULAR_SPEED = 1
    LINEAR_POSITION = 2
    ANGULAR_POSITION = 3


@dataclass
class PID:
    """
    Data class representing PID controller parameters.
    """
    kp: float
    ki: float
    kd: float

    def to_bytes(self) -> bytes:
        """
        Serialize the PID parameters into bytes.
        """
        return struct.pack("<fff", self.kp, self.ki, self.kd)

    @classmethod
    def from_dict(cls, pid_dict: Dict[str, Any]) -> 'PID':
        return cls(**pid_dict)

    @classmethod
    def from_tuple(cls, pid_tuple: tuple) -> 'PID':
        return cls(*pid_tuple)

    @classmethod
    def from_list(cls, pid_list: list) -> 'PID':
        return cls(*pid_list)


class RollingBasis(Teensy):
    """
    Represents the rolling basis of the robot.

    Inherits from Teensy to manage low-level communications and adds logic specific to the robot's state,
    PID configuration, and command messaging.
    """

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
        """
        Initializes the RollingBasis instance.

        Args:
            logger (Logger): Logger instance for logging messages.
            ser (int): Serial port identifier for Teensy communication.
            crc (bool): Whether to use CRC for message validation.
            vid (int): Vendor ID of the Teensy device.
            pid (int): Product ID of the Teensy device.
            baudrate (int): Communication baud rate.
            dummy (bool): Whether to use dummy mode (for testing purposes).
        """
        super().__init__(logger, ser=ser, vid=vid, pid=pid, baudrate=baudrate, crc=crc, dummy=dummy)

        # Robot state
        self.odometrie: OrientedPoint = OrientedPoint((0.0, 0.0), 0.0)
        self.linear_speed: float = 0.0
        self.angular_speed: float = 0.0

        # PID controllers
        self.linear_speed_pid: PID = PID(0.0, 0.0, 0.0)
        self.angular_speed_pid: PID = PID(0.0, 0.0, 0.0)
        self.linear_position_pid: PID = PID(0.0, 0.0, 0.0)
        self.angular_position_pid: PID = PID(0.0, 0.0, 0.0)

        """
        This is used to match a handling function to a message type.
        add_callback can also be used.
        """
        # self.messagetype = {
        #     128: self.rcv_print,
        #     129: self.rcv_rolling_basis_state,
        #     255: self.rcv_unknown_msg,
        # }

        # Register message handlers
        self.add_callback(self.rcv_print, Command.PRINT.value)
        self.add_callback(self.rcv_unknown_msg, Command.UNKNOWN_MSG_TYPE.value)
        self.add_callback(self.rcv_rolling_basis_state, Command.UPDATE_ROLLING_BASIS.value)

        # Initialize PID controllers from configuration
        self._initialize_pids()

    ####################################
    # Message Receiving Handlers       #
    ####################################
    def rcv_print(self, msg: bytes):
        """
        Handles PRINT messages from the Teensy.

        Args:
            msg (bytes): The received message bytes.
        """
        self.logger.info(
            "Teensy says: " + msg.decode("ascii", errors="ignore")
        )

    def rcv_rolling_basis_state(self, msg: bytes):
        """
        Handles rolling basis state update messages from the Teensy.

        The message contains:
        - float x: X-coordinate of the position (4 bytes).
        - float y: Y-coordinate of the position (4 bytes).
        - float theta: Orientation (4 bytes).
        - float current_linear_speed: Current linear speed (4 bytes).
        - float current_angular_speed: Current angular speed (4 bytes).

        Args:
            msg (bytes): The received message bytes.
        """
        # Position / odometry
        self.odometrie = OrientedPoint(
            (struct.unpack("<f", msg[0:4])[0], struct.unpack("<f", msg[4:8])[0]),
            struct.unpack("<f", msg[8:12])[0],
        )
        # Speeds
        self.linear_speed = struct.unpack("<f", msg[12:16])[0]
        self.angular_speed = struct.unpack("<f", msg[16:20])[0]

    def rcv_unknown_msg(self, msg: bytes):
        """
        Handles unknown messages from the Teensy.

        Logs a warning indicating that the message type is not recognized.

        Args:
            msg (bytes): The received message bytes.
        """
        self.logger.warning(
            f"Teensy does not know the command {msg.hex()}"
        )

    ####################################
    # Message Sending Methods          #
    ####################################
    @log(param_logger="RollingBasis")
    def set_speed_and_position(
            self,
            target_linear_speed: float,
            target_angular_speed: float,
            target_position: OrientedPoint,
    ) -> None:
        """
        Sends a command to set the target speed and position of the rolling basis.

        Args:
            target_linear_speed (float): Target linear speed.
            target_angular_speed (float): Target angular speed.
            target_position (OrientedPoint): Target position and orientation.
        """
        msg = (
                Command.SET_SPEED_AND_POSITION.to_bytes()
                + struct.pack("<f", target_linear_speed)
                + struct.pack("<f", target_angular_speed)
                + struct.pack("<f", target_position.x)
                + struct.pack("<f", target_position.y)
                + struct.pack("<f", target_position.theta)
        )
        # Send the composed message to the Teensy
        # https://docs.python.org/3/library/struct.html#format-characters
        self.send_bytes(msg)

    @log("RollingBasis")
    def set_odometrie(self, odometrie: OrientedPoint) -> None:
        """
        Sends a command to set the odometrie of the rolling basis.

        Args:
            odometrie (OrientedPoint): The new odometrie values.
        """
        msg = (
                Command.SET_ODOMETRIE.to_bytes()
                + struct.pack("<f", odometrie.x)
                + struct.pack("<f", odometrie.y)
                + struct.pack("<f", odometrie.theta)
        )
        self.send_bytes(msg)

    def _send_pid(self, pid_id: int, pid: PID) -> None:
        """
        Internal method to send PID configuration data to the Teensy.

        Args:
            pid_id (int): The identifier for the PID controller.
            pid (PID): The PID controller parameters.
        """
        msg = (
                Command.SET_PID.to_bytes()
                + pid_id.to_bytes()
                + pid.to_bytes()
        )
        self.send_bytes(msg)

    ####################################
    # PID Configuration Methods        #
    ####################################
    def set_linear_speed_pid(self, *args, **kwargs) -> None:
        """
        Configure the PID values for linear speed control.

        Accepts either three positional arguments (kp, ki, kd),
        a single dictionary, or keyword arguments.
        """
        try:
            if len(args) == 3:
                pid = PID(*args)
            elif len(args) == 1 and isinstance(args[0], dict):
                pid = PID.from_dict(args[0])
            elif kwargs:
                pid = PID.from_dict(kwargs)
            else:
                raise ValueError("Invalid arguments for linear speed PID configuration.")
            self.linear_speed_pid = pid
            self._send_pid(PID_ID.LINEAR_SPEED.value, pid)
        except Exception as e:
            self.logger.error(f"Failed to set linear speed PID: {e}")

    def set_angular_speed_pid(self, *args, **kwargs) -> None:
        """
        Configure the PID values for angular speed control.

        Accepts either three positional arguments (kp, ki, kd),
        a single dictionary, or keyword arguments.
        """
        try:
            if len(args) == 3:
                pid = PID(*args)
            elif len(args) == 1 and isinstance(args[0], dict):
                pid = PID.from_dict(args[0])
            elif kwargs:
                pid = PID.from_dict(kwargs)
            else:
                raise ValueError("Invalid arguments for angular speed PID configuration.")
            self.angular_speed_pid = pid
            self._send_pid(PID_ID.ANGULAR_SPEED.value, pid)
        except Exception as e:
            self.logger.error(f"Failed to set angular speed PID: {e}")

    def set_linear_position_pid(self, *args, **kwargs) -> None:
        """
        Configure the PID values for linear position control.

        Accepts either three positional arguments (kp, ki, kd),
        a single dictionary, or keyword arguments.
        """
        try:
            if len(args) == 3:
                pid = PID(*args)
            elif len(args) == 1 and isinstance(args[0], dict):
                pid = PID.from_dict(args[0])
            elif kwargs:
                pid = PID.from_dict(kwargs)
            else:
                raise ValueError("Invalid arguments for linear position PID configuration.")
            self.linear_position_pid = pid
            self._send_pid(PID_ID.LINEAR_POSITION.value, pid)
        except Exception as e:
            self.logger.error(f"Failed to set linear position PID: {e}")

    def set_angular_position_pid(self, *args, **kwargs) -> None:
        """
        Configure the PID values for angular position control.

        Accepts either three positional arguments (kp, ki, kd),
        a single dictionary, or keyword arguments.
        """
        try:
            if len(args) == 3:
                pid = PID(*args)
            elif len(args) == 1 and isinstance(args[0], dict):
                pid = PID.from_dict(args[0])
            elif kwargs:
                pid = PID.from_dict(kwargs)
            else:
                raise ValueError("Invalid arguments for angular position PID configuration.")
            self.angular_position_pid = pid
            self._send_pid(PID_ID.ANGULAR_POSITION.value, pid)
        except Exception as e:
            self.logger.error(f"Failed to set angular position PID: {e}")

    def set_pids(
            self,
            linear_speed_pid: dict[str, float],
            angular_speed_pid: dict[str, float],
            linear_position_pid: dict[str, float],
            angular_position_pid: dict[str, float],
    ) -> None:
        """
        Configure all PID controllers using dictionaries for each.
        """
        self.set_linear_speed_pid(**linear_speed_pid)
        self.set_angular_speed_pid(**angular_speed_pid)
        self.set_linear_position_pid(**linear_position_pid)
        self.set_angular_position_pid(**angular_position_pid)

    def _initialize_pids(self) -> None:
        """
        Initialize PID controllers from the configuration.
        """
        try:
            self.set_pids(
                linear_speed_pid=CONFIG.ROLLING_BASIS_PIDS_LINEAR_SPEED,
                angular_speed_pid=CONFIG.ROLLING_BASIS_PIDS_ANGULAR_SPEED,
                linear_position_pid=CONFIG.ROLLING_BASIS_PIDS_LINEAR_POSITION,
                angular_position_pid=CONFIG.ROLLING_BASIS_PIDS_ANGULAR_POSITION,
            )
        except Exception as e:
            self.logger.error(f"Failed to initialize PIDs: {e}")

    ####################################
    # Equality Comparison              #
    ####################################
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, RollingBasis):
            return NotImplemented
        return (
                self.odometrie == other.odometrie and
                self.linear_speed == other.linear_speed and
                self.angular_speed == other.angular_speed and
                self.linear_speed_pid == other.linear_speed_pid and
                self.angular_speed_pid == other.angular_speed_pid and
                self.linear_position_pid == other.linear_position_pid and
                self.angular_position_pid == other.angular_position_pid
        )

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)


class RollingBasisDummy:
    """
    Represents the rolling basis of the robot.

    Inherits from Teensy to manage low-level communications and adds logic specific to the robot's state,
    PID configuration, and command messaging.
    """

    def __init__(
            self,
            logger: Logger,
    ):
        """
        Initializes the RollingBasis instance.

        Args:
            logger (Logger): Logger instance for logging messages.
        """
        self.logger = logger

        # Robot state
        self.odometrie: OrientedPoint = OrientedPoint((0.0, 0.0), 0.0)
        self.linear_speed: float = 0.0
        self.angular_speed: float = 0.0

        # PID controllers
        self.linear_speed_pid: PID = PID(0.0, 0.0, 0.0)
        self.angular_speed_pid: PID = PID(0.0, 0.0, 0.0)
        self.linear_position_pid: PID = PID(0.0, 0.0, 0.0)
        self.angular_position_pid: PID = PID(0.0, 0.0, 0.0)

        # Initialize PID controllers from configuration
        self._initialize_pids()

    ####################################
    # Message Sending Methods          #
    ####################################
    @log(param_logger="RollingBasis")
    def set_speed_and_position(
            self,
            target_linear_speed: float,
            target_angular_speed: float,
            target_position: OrientedPoint,
    ) -> None:
        """
        Sends a command to set the target speed and position of the rolling basis.

        Args:
            target_linear_speed (float): Target linear speed.
            target_angular_speed (float): Target angular speed.
            target_position (OrientedPoint): Target position and orientation.
        """
        self.linear_speed = target_linear_speed
        self.angular_speed = target_angular_speed
        self.odometrie = target_position

        self.logger.debug(
            f"[DUMMY] Set speed and position: "
            f"{target_linear_speed}, {target_angular_speed}, {target_position}"
        )

    @log("RollingBasis")
    def set_odometrie(self, odometrie: OrientedPoint) -> None:
        """
        Sends a command to set the odometrie of the rolling basis.

        Args:
            odometrie (OrientedPoint): The new odometrie values.
        """
        self.odometrie = odometrie
        self.logger.debug(
            f"[DUMMY] Set odometrie: {odometrie}"
        )

    def _send_pid(self, pid_id: int, pid: PID) -> None:
        """
        Internal method to send PID configuration data to the Teensy.

        Args:
            pid_id (int): The identifier for the PID controller.
            pid (PID): The PID controller parameters.
        """
        self.logger.debug(
            f"[DUMMY] Set PID: {pid_id}, {pid}"
        )

    ####################################
    # PID Configuration Methods        #
    ####################################
    def set_linear_speed_pid(self, *args, **kwargs) -> None:
        """
        Configure the PID values for linear speed control.

        Accepts either three positional arguments (kp, ki, kd),
        a single dictionary, or keyword arguments.
        """
        try:
            if len(args) == 3:
                pid = PID(*args)
            elif len(args) == 1 and isinstance(args[0], dict):
                pid = PID.from_dict(args[0])
            elif kwargs:
                pid = PID.from_dict(kwargs)
            else:
                raise ValueError("Invalid arguments for linear speed PID configuration.")
            self.linear_speed_pid = pid
            self._send_pid(PID_ID.LINEAR_SPEED.value, pid)
        except Exception as e:
            self.logger.error(f"Failed to set linear speed PID: {e}")

    def set_angular_speed_pid(self, *args, **kwargs) -> None:
        """
        Configure the PID values for angular speed control.

        Accepts either three positional arguments (kp, ki, kd),
        a single dictionary, or keyword arguments.
        """
        try:
            if len(args) == 3:
                pid = PID(*args)
            elif len(args) == 1 and isinstance(args[0], dict):
                pid = PID.from_dict(args[0])
            elif kwargs:
                pid = PID.from_dict(kwargs)
            else:
                raise ValueError("Invalid arguments for angular speed PID configuration.")
            self.angular_speed_pid = pid
            self._send_pid(PID_ID.ANGULAR_SPEED.value, pid)
        except Exception as e:
            self.logger.error(f"Failed to set angular speed PID: {e}")

    def set_linear_position_pid(self, *args, **kwargs) -> None:
        """
        Configure the PID values for linear position control.

        Accepts either three positional arguments (kp, ki, kd),
        a single dictionary, or keyword arguments.
        """
        try:
            if len(args) == 3:
                pid = PID(*args)
            elif len(args) == 1 and isinstance(args[0], dict):
                pid = PID.from_dict(args[0])
            elif kwargs:
                pid = PID.from_dict(kwargs)
            else:
                raise ValueError("Invalid arguments for linear position PID configuration.")
            self.linear_position_pid = pid
            self._send_pid(PID_ID.LINEAR_POSITION.value, pid)
        except Exception as e:
            self.logger.error(f"Failed to set linear position PID: {e}")

    def set_angular_position_pid(self, *args, **kwargs) -> None:
        """
        Configure the PID values for angular position control.

        Accepts either three positional arguments (kp, ki, kd),
        a single dictionary, or keyword arguments.
        """
        try:
            if len(args) == 3:
                pid = PID(*args)
            elif len(args) == 1 and isinstance(args[0], dict):
                pid = PID.from_dict(args[0])
            elif kwargs:
                pid = PID.from_dict(kwargs)
            else:
                raise ValueError("Invalid arguments for angular position PID configuration.")
            self.angular_position_pid = pid
            self._send_pid(PID_ID.ANGULAR_POSITION.value, pid)
        except Exception as e:
            self.logger.error(f"Failed to set angular position PID: {e}")

    def set_pids(
            self,
            linear_speed_pid: dict[str, float],
            angular_speed_pid: dict[str, float],
            linear_position_pid: dict[str, float],
            angular_position_pid: dict[str, float],
    ) -> None:
        """
        Configure all PID controllers using dictionaries for each.
        """
        self.set_linear_speed_pid(**linear_speed_pid)
        self.set_angular_speed_pid(**angular_speed_pid)
        self.set_linear_position_pid(**linear_position_pid)
        self.set_angular_position_pid(**angular_position_pid)

    def _initialize_pids(self) -> None:
        """
        Initialize PID controllers from the configuration.
        """
        try:
            self.set_pids(
                linear_speed_pid=CONFIG.ROLLING_BASIS_PIDS_LINEAR_SPEED,
                angular_speed_pid=CONFIG.ROLLING_BASIS_PIDS_ANGULAR_SPEED,
                linear_position_pid=CONFIG.ROLLING_BASIS_PIDS_LINEAR_POSITION,
                angular_position_pid=CONFIG.ROLLING_BASIS_PIDS_ANGULAR_POSITION,
            )
        except Exception as e:
            self.logger.error(f"Failed to initialize PIDs: {e}")

    ####################################
    # Equality Comparison              #
    ####################################
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, RollingBasis):
            return NotImplemented
        return (
                self.odometrie == other.odometrie and
                self.linear_speed == other.linear_speed and
                self.angular_speed == other.angular_speed and
                self.linear_speed_pid == other.linear_speed_pid and
                self.angular_speed_pid == other.angular_speed_pid and
                self.linear_position_pid == other.linear_position_pid and
                self.angular_position_pid == other.angular_position_pid
        )

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)
