from config_loader import CONFIG

# ====== Standard Library Imports ======
import struct
import numpy as np
import time
import matplotlib.pyplot as plt

# ====== Third-party library imports ======
from loggerplusplus import Logger, log, LogLevels

# ====== Local Library Imports ======
from geometry import OrientedPoint
from usb_com.python import Messages
from teensy import BaseComTeensy

# ====== Internal Project Imports ======
from controllers.rolling_basis.pids import PID, PID_ID


# ====== Class Part ======
class RollingBasis(BaseComTeensy):
    """
    Represents the rolling basis of the robot.

    Inherits from Teensy to manage low-level communications and adds logic specific to the robot's state,
    PID configuration, and message messaging.
    """

    def __init__(
        self,
        logger: Logger,
        serial_number=CONFIG.ROLLING_BASIS_TEENSY_SER,
        vid=CONFIG.TEENSY_VID,
        pid=CONFIG.TEENSY_PID,
        baudrate=CONFIG.TEENSY_BAUDRATE,
        enable_crc=CONFIG.TEENSY_CRC,
        enable_dummy=CONFIG.TEENSY_DUMMY,
    ):
        self.flag = True
        # Initialize the parent-BaseComTeensy class
        super().__init__(
            logger, serial_number, vid, pid, baudrate, enable_crc, enable_dummy
        )

        # Robot state
        self.odometrie: OrientedPoint = OrientedPoint((0.0, 0.0), 0.0)

        # PID controllers
        self.linear_position_pid: PID = PID(0.0, 0.0, 0.0)
        self.angular_position_pid: PID = PID(0.0, 0.0, 0.0)

        """
        This is used to match a handling function to a message type.
        add_callback can also be used.
        """
        # Register message handlers
        self.add_callback(self.rcv_print, Messages.PRINT.value)
        self.add_callback(self.rcv_unknown_msg, Messages.UNKNOWN_MSG_TYPE.value)
        self.add_callback(
            self.rcv_rolling_basis_state, Messages.UPDATE_ROLLING_BASIS.value
        )

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
        # Temp to debug logs
        self.logger.info(
            "Teensy Rolling Basis says: " + msg.decode("ascii", errors="ignore")
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
        # Position / odometrie
        self.odometrie = OrientedPoint(
            (struct.unpack("<d", msg[0:8])[0], struct.unpack("<d", msg[8:16])[0]),
            struct.unpack("<d", msg[16:24])[0],
        )

    def rcv_unknown_msg(self, msg: bytes):
        """
        Handles unknown messages from the Teensy.

        Logs a warning indicating that the message type is not recognized.

        Args:
            msg (bytes): The received message bytes.
        """
        self.logger.warning(f"Teensy Motors does not know the message {msg.hex()}")

    ####################################
    # Message Sending Methods          #
    ####################################
    # @log(param_logger="RollingBasis", log_level=LogLevels.INFO)
    def set_target_position(
        self,
        target_position: OrientedPoint,
    ) -> None:
        """
        Sends a message to set the target speed and position of the rolling basis.

        Args:
            target_linear_speed (float): Target linear speed.
            target_angular_speed (float): Target angular speed.
            target_position (OrientedPoint): Target position and orientation.
        """
        msg = (
            Messages.SET_TARGET_POSITION.to_bytes()
            + struct.pack("<d", target_position.x)
            + struct.pack("<d", target_position.y)
            + struct.pack("<d", target_position.theta)
        )

        # Send the composed message to the Teensy
        # https://docs.python.org/3/library/struct.html#format-characters
        self.send_bytes(msg)

    @log(param_logger="RollingBasis", log_level=LogLevels.INFO)
    def set_odometrie(self, odometrie: OrientedPoint) -> None:
        """
        Sends a message to set the odometrie of the rolling basis.

        Args:
            odometrie (OrientedPoint): The new odometrie values.
        """
        msg = (
            Messages.SET_ODOMETRIE.to_bytes()
            + struct.pack("<d", odometrie.x)
            + struct.pack("<d", odometrie.y)
            + struct.pack("<d", odometrie.theta)
        )

        self.send_bytes(msg)

    @log(
        param_logger="RollingBasis",
        log_level=LogLevels.INFO,
    )
    def _send_pid(self, pid_id: int, pid: PID) -> None:
        """
        Internal method to send PID configuration data to the Teensy.

        Args:
            pid_id (int): The identifier for the PID controller.
            pid (PID): The PID controller parameters.
        """
        msg = Messages.SET_PID.to_bytes() + pid_id.to_bytes() + pid.to_bytes()
        self.send_bytes(msg)

    ####################################
    # PID Configuration Methods        #
    ####################################
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
                raise ValueError(
                    "Invalid arguments for linear position PID configuration."
                )
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
                raise ValueError(
                    "Invalid arguments for angular position PID configuration."
                )
            self.angular_position_pid = pid
            self._send_pid(PID_ID.ANGULAR_POSITION.value, pid)
        except Exception as e:
            self.logger.error(f"Failed to set angular position PID: {e}")

    def set_pids(
        self,
        linear_position_pid: dict[str, float],
        angular_position_pid: dict[str, float],
    ) -> None:
        """
        Configure all PID controllers using dictionaries for each.
        """
        self.set_linear_position_pid(**linear_position_pid)
        time.sleep(0.1)  # Ensure the Teensy has time to process the first PID
        self.set_angular_position_pid(**angular_position_pid)
        time.sleep(0.1)  # Ensure the Teensy has time to process the second PID

    def _initialize_pids(self) -> None:
        """
        Initialize PID controllers from the configuration.
        """
        try:
            self.set_pids(
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
            self.odometrie == other.odometrie
            and self.linear_position_pid == other.linear_position_pid
            and self.angular_position_pid == other.angular_position_pid
        )

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)
