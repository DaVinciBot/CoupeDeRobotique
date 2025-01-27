# ====== Code Summary ======
# This code defines a system for communication between a Raspberry Pi and a Teensy microcontroller.
# It includes a `Command` enumeration for message types, and a `RollingBasis` class for managing
# the state and behavior of a rolling robot basis. The `RollingBasis` class handles received messages
# and sends commands, encapsulating robot state updates and messaging logic.

from config_loader import CONFIG

# ====== Standard Library Imports ======
from enum import Enum
import struct
from typing import Callable

# ====== Internal Project Imports ======
from teensy_comms import Teensy
from geometry import OrientedPoint
from logger import Logger, LogLevels


class Command(Enum):
    """
    Defines the command protocol between the Raspberry Pi and the Teensy microcontroller.
    """

    # rasp -> teensy : 0-127 (Convention)
    SET_SPEED_AND_POSITION = 0
    SET_PID = 1

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


class RollingBasis(Teensy):
    """
    Represents the rolling basis of a robot, managing communication, state, and behavior.

    Inherits from Teensy to handle low-level communication. This class adds logic specific
    to the rolling basis of the robot.
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
        # self.messagetype = {
        #     128: self.rcv_print,
        #     129: self.rcv_rolling_basis_state,
        #     255: self.rcv_unknown_msg,
        # }

        # Register message handlers for different command types
        self.add_callback(self.rcv_print, Command.PRINT.value)
        self.add_callback(self.rcv_unknown_msg, Command.UNKNOWN_MSG_TYPE.value)
        self.add_callback(
            self.rcv_rolling_basis_state, Command.UPDATE_ROLLING_BASIS.value
        )
        self.__init_set_pids()

    #############################
    # Received message handling #
    #############################
    def rcv_print(self, msg: bytes):
        """
        Handles PRINT messages from the Teensy.

        Args:
            msg (bytes): The received message bytes.
        """
        self.logger.log(
            "Teensy says: " + msg.decode("ascii", errors="ignore"), LogLevels.INFO
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

    @Logger
    def __set_pid(self, pid_id: int, kp: float, ki: float, kd: float) -> None:
        """
        Sends a command to set the PID values for the linear speed control.

        Args:
            kp (float): Proportional gain.
            ki (float): Integral gain.
            kd (float): Derivative gain.
        """
        msg = (
            Command.SET_PID.to_bytes()
            + pid_id.to_bytes()
            + struct.pack("<f", kp)
            + struct.pack("<f", ki)
            + struct.pack("<f", kd)
        )
        self.send_bytes(msg)

    def set_linear_speed_pid(self, kp: float, ki: float, kd: float) -> None:
        """
        Sets the PID values for the linear speed control.

        Args:
            kp (float): Proportional gain.
            ki (float): Integral gain.
            kd (float): Derivative gain.
        """
        self.linear_speed_kp = kp
        self.linear_speed_ki = ki
        self.linear_speed_kd = kd
        self.__set_pid(CONFIG.LINEAR_SPEED_PID, kp, ki, kd)

    def set_angular_speed_pid(self, kp: float, ki: float, kd: float) -> None:
        """
        Sets the PID values for the angular speed control.

        Args:
            kp (float): Proportional gain.
            ki (float): Integral gain.
            kd (float): Derivative gain.
        """
        self.angular_speed_kp = kp
        self.angular_speed_ki = ki
        self.angular_speed_kd = kd
        self.__set_pid(CONFIG.ANGULAR_SPEED_PID, kp, ki, kd)

    def set_linear_position_pid(self, kp: float, ki: float, kd: float) -> None:
        """
        Sets the PID values for the linear position control.

        Args:
            kp (float): Proportional gain.
            ki (float): Integral gain.
            kd (float): Derivative gain.
        """
        self.linear_position_kp = kp
        self.linear_position_ki = ki
        self.linear_position_kd = kd
        self.__set_pid(CONFIG.LINEAR_DISTANCE_PID, kp, ki, kd)

    def set_angular_position_pid(self, kp: float, ki: float, kd: float) -> None:
        """
        Sets the PID values for the angular position control.

        Args:
            kp (float): Proportional gain.
            ki (float): Integral gain.
            kd (float): Derivative gain.
        """
        self.angular_position_kp = kp
        self.angular_position_ki = ki
        self.angular_position_kd = kd
        self.__set_pid(CONFIG.ANGULAR_DISTANCE_PID, kp, ki, kd)

    def set_pids(
        self,
        kp_linear_speed,
        ki_linear_speed,
        kd_linear_speed,
        kp_angular_speed,
        ki_angular_speed,
        kd_angular_speed,
        kp_linear_position,
        ki_linear_position,
        kd_linear_position,
        kp_angular_position,
        ki_angular_position,
        kd_angular_position,
    ):
        self.set_linear_speed_pid(kp_linear_speed, ki_linear_speed, kd_linear_speed)
        self.set_angular_speed_pid(kp_angular_speed, ki_angular_speed, kd_angular_speed)
        self.set_linear_position_pid(
            kp_linear_position, ki_linear_position, kd_linear_position
        )
        self.set_angular_position_pid(
            kp_angular_position, ki_angular_position, kd_angular_position
        )

    def __init_set_pids(self):
        self.set_pids(
            **CONFIG.LINEAR_SPEED_PID,
            **CONFIG.ANGULAR_SPEED_PID,
            **CONFIG.LINEAR_DISTANCE_PID,
            **CONFIG.ANGULAR_DISTANCE_PID,
        )


class RollingBasisDummy:
    """
    A dummy version of the RollingBasis class.

    This dummy class mimics the interface of the real RollingBasis class
    but does not establish any actual hardware communication or process
    real data. It is useful for testing and simulations, where you do not
    have a Teensy device or hardware connected.
    """

    def __init__(
        self,
        logger,
        ser: int = None,
        crc: bool = False,
        vid: int = None,
        pid: int = None,
        baudrate: int = None,
        dummy: bool = True,
    ):
        """
        Initializes the dummy RollingBasis instance.

        Args:
            logger: Logger instance for logging messages (dummy in this case).
            ser (int): Serial port identifier (not used in the dummy class).
            crc (bool): Whether to use CRC (not used in the dummy class).
            vid (int): Vendor ID of the device (not used in the dummy class).
            pid (int): Product ID of the device (not used in the dummy class).
            baudrate (int): Communication baud rate (not used in the dummy class).
            dummy (bool): Indicates that this is a dummy setup (always True here).
        """
        self.logger = logger
        self.ser = ser
        self.crc = crc
        self.vid = vid
        self.pid = pid
        self.baudrate = baudrate
        self.dummy = dummy

        # States of the robot (dummy state)
        self.odometrie: OrientedPoint = OrientedPoint((0.0, 0.0), 0.0)
        self.linear_speed: float = 0.0
        self.angular_speed: float = 0.0

        # Dictionary to store callbacks for different message types (optional).
        # You can use add_callback to register your own handlers.
        self.messagetype_callbacks = {}

        # Register dummy handlers as an example
        self.add_callback(self.rcv_print, Command.PRINT.value)
        self.add_callback(self.rcv_unknown_msg, Command.UNKNOWN_MSG_TYPE.value)
        self.add_callback(
            self.rcv_rolling_basis_state, Command.UPDATE_ROLLING_BASIS.value
        )

    def add_callback(self, callback_func: Callable, cmd_type: int) -> None:
        """
        Registers a callback function for a given command type (dummy implementation).

        Args:
            callback_func (Callable): The function to call when `cmd_type` is received.
            cmd_type (int): The command type for which the callback is registered.
        """
        self.messagetype_callbacks[cmd_type] = callback_func

    #############################
    # Received message handling #
    #############################

    def rcv_print(self, msg: bytes):
        """
        Dummy handler for PRINT messages.

        Args:
            msg (bytes): The received message bytes.
        """
        decoded_msg = msg.decode("ascii", errors="ignore")
        self.logger.log(
            f"Dummy RollingBasis received a PRINT message: {decoded_msg}",
            LogLevels.INFO,
        )

    def rcv_rolling_basis_state(self, msg: bytes):
        """
        Dummy handler for rolling basis state update messages.

        The expected structure in the real system would be:
        - float x
        - float y
        - float theta
        - float current_linear_speed
        - float current_angular_speed

        Args:
            msg (bytes): The received message bytes.
        """
        # Since this is a dummy method, we'll just log the raw data
        # rather than unpack and update real state.
        raw_data_hex = msg.hex()
        self.logger.log(
            f"Dummy RollingBasis received a state update: {raw_data_hex}",
            LogLevels.INFO,
        )

    def rcv_unknown_msg(self, msg: bytes):
        """
        Dummy handler for unknown messages.

        Args:
            msg (bytes): The received message bytes.
        """
        self.logger.log(
            f"Dummy RollingBasis received an unknown message: {msg.hex()}",
            LogLevels.WARNING,
        )

    ###################
    # Message to send #
    ###################

    @Logger
    def set_speed_and_position(
        self,
        target_linear_speed: float,
        target_angular_speed: float,
        target_position: OrientedPoint,
    ) -> None:
        """
        Dummy method to set the target speed and position of the rolling basis.

        In the real implementation, this would send a message to the Teensy
        containing the desired linear speed, angular speed, and target position.

        Args:
            target_linear_speed (float): Target linear speed.
            target_angular_speed (float): Target angular speed.
            target_position (OrientedPoint): Target position and orientation.
        """
        # This is where you'd normally pack data and send it over serial
        # or another communication interface. We just log it here.
        self.odometrie = target_position
        self.linear_speed = target_linear_speed
        self.angular_speed = target_angular_speed
        self.logger.log(
            f"[DUMMY] Setting speed to linear={target_linear_speed}, "
            f"angular={target_angular_speed}, "
            f"position=({target_position.x}, {target_position.y}, {target_position.theta})",
            LogLevels.INFO,
        )

    def send_bytes(self, msg: bytes):
        """
        Dummy method to send bytes to the device.
        In the real class, this would handle serial communication.

        Args:
            msg (bytes): The message to send.
        """
        # No real sending performed; simply log the attempt.
        self.logger.log(f"[DUMMY] Sending bytes: {msg.hex()}", LogLevels.INFO)
