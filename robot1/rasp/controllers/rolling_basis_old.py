# ====== Code Summary ======
# This code defines a system for communication between a Raspberry Pi and a Teensy microcontroller.
# It includes a `Command` enumeration for message types, and a `RollingBasis` class for managing
# the state and behavior of a rolling robot basis. The `RollingBasis` class handles received messages
# and sends commands, encapsulating robot state updates and messaging logic.

from config_loader import CONFIG

# ====== Standard Library Imports ======
from enum import Enum
from dataclasses import dataclass
import struct
from typing import Callable

# ====== Internal Project Imports ======
from teensy_comms import Teensy
from geometry import OrientedPoint
from loggerplusplus import Logger, log


class Command(Enum):
    """
       Defines the command protocol between the Raspberry Pi and the Teensy microcontroller.
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
    linear_speed_pid_id = 0
    angular_speed_pid_id = 1
    linear_position_pid_id = 2
    angular_position_pid_id = 3


@dataclass
class PID:
    kp: float
    ki: float
    kd: float

    @classmethod
    def from_dict(cls, pid_dict):
        return cls(**pid_dict)

    @classmethod
    def from_tuple(cls, pid_tuple):
        return cls(*pid_tuple)


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

        # PID values for speed and position control
        self.linear_speed_pid: PID = PID(0, 0, 0)
        self.angular_speed_pid: PID = PID(0, 0, 0)

        self.linear_position_pid: PID = PID(0, 0, 0)
        self.angular_position_pid: PID = PID(0, 0, 0)

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
        self.add_callback(self.rcv_rolling_basis_state, Command.UPDATE_ROLLING_BASIS.value)

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

    ###################
    # Message to send #
    ###################
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

    @log("RollingBasis")
    def __set_pid(self, pid_id: int, pid: PID) -> None:
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
                + struct.pack("<f", pid.kp)
                + struct.pack("<f", pid.ki)
                + struct.pack("<f", pid.kd)
        )
        self.send_bytes(msg)

    def set_linear_speed_pid(self, *args, **kwargs) -> None:
        """
        Sets the PID values for the linear speed control.

        Args:
            kp (float): Proportional gain.
            ki (float): Integral gain.
            kd (float): Derivative gain.
        """
        if len(args) == 3:
            self.linear_speed_pid: PID = PID(*args)
        elif len(args) == 1:
            self.linear_speed_pid: PID = PID.from_dict(args[0])
        elif kwargs:
            self.linear_speed_pid: PID = PID.from_dict(kwargs)
        else:
            self.logger.error(f"Invalid arguments for set_linear_speed_pid: args:{args}, kwargs{kwargs}")

        self.__set_pid(PID_ID.linear_speed_pid_id.value, self.linear_speed_pid)

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
        self.__set_pid(PID_ID.angular_speed_pid_id.value, kp, ki, kd)

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
        self.__set_pid(PID_ID.linear_position_pid_id.value, kp, ki, kd)

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
        self.__set_pid(PID_ID.linear_position_pid_id.value, kp, ki, kd)

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
            **CONFIG.ROLLING_BASIS_PIDS_LINEAR_SPEED.values(),
            **CONFIG.ANGULAR_SPEED_PID,
            **CONFIG.LINEAR_POSITION_PID,
            **CONFIG.ANGULAR_POSITION_PID,
        )

    def __eq__(self, other):
        if not isinstance(other, RollingBasisDummy):
            return False
        return (
                self.odometrie == other.odometrie
                and self.linear_speed == other.linear_speed
                and self.angular_speed == other.angular_speed
                and self.linear_speed_kp == other.linear_speed_kp
                and self.linear_speed_ki == other.linear_speed_ki
                and self.linear_speed_kd == other.linear_speed_kd
                and self.angular_speed_kp == other.angular_speed_kp
                and self.angular_speed_ki == other.angular_speed_ki
                and self.angular_speed_kd == other.angular_speed_kd
                and self.linear_position_kp == other.linear_position_kp
                and self.linear_position_ki == other.linear_position_ki
                and self.linear_position_kd == other.linear_position_kd
                and self.angular_position_kp == other.angular_position_kp
                and self.angular_position_ki == other.angular_position_ki
                and self.angular_position_kd == other.angular_position_kd
        )

    def __ne__(self, other):
        return not self.__eq__(other)


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

        # PID values for speed and position control
        self.linear_speed_kp = 0.0
        self.linear_speed_ki = 0.0
        self.linear_speed_kd = 0.0

        self.angular_speed_kp = 0.0
        self.angular_speed_ki = 0.0
        self.angular_speed_kd = 0.0

        self.linear_position_kp = 0.0
        self.linear_position_ki = 0.0
        self.linear_position_kd = 0.0

        self.angular_position_kp = 0.0
        self.angular_position_ki = 0.0
        self.angular_position_kd = 0.0

        # Dictionary to store callbacks for different message types (optional).
        # You can use add_callback to register your own handlers.
        self.messagetype_callbacks = {}

        # Register dummy handlers as an example
        self.add_callback(self.rcv_print, Command.PRINT.value)
        self.add_callback(self.rcv_unknown_msg, Command.UNKNOWN_MSG_TYPE.value)
        self.add_callback(self.rcv_rolling_basis_state, Command.UPDATE_ROLLING_BASIS.value)

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
        self.logger.info(f"Dummy RollingBasis received a PRINT message: {decoded_msg}")

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
        self.logger.info(f"Dummy RollingBasis received a state update: {raw_data_hex}")

    def rcv_unknown_msg(self, msg: bytes):
        """
        Dummy handler for unknown messages.

        Args:
            msg (bytes): The received message bytes.
        """
        self.logger.warning(
            f"Dummy RollingBasis received an unknown message: {msg.hex()}"
        )

    ###################
    # Message to send #
    ###################

    @log("RollingBasis")
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
        self.logger.info(
            f"[DUMMY] Setting speed to linear={target_linear_speed}, "
            f"angular={target_angular_speed}, "
            f"position=({target_position.x}, {target_position.y}, {target_position.theta})"
        )

    @log("RollingBasis")
    def set_odometrie(self, odometrie: OrientedPoint) -> None:
        """
        Sends a command to set the odometrie of the rolling basis.

        Args:
            odometrie (OrientedPoint): The new odometrie values.
        """
        self.odometrie = odometrie

        self.logger.info(
            f"[DUMMY] Setting odometrie={odometrie}, "
        )

    @log("RollingBasis")
    def __set_pid(self, pid_id: int, kp: float, ki: float, kd: float) -> None:
        """
        Sends a command to set the PID values for the linear speed control.

        Args:
            kp (float): Proportional gain.
            ki (float): Integral gain.
            kd (float): Derivative gain.
        """
        if pid_id == PID_ID.linear_speed_pid_id.value:
            self.linear_speed_kp = kp
            self.linear_speed_ki = ki
            self.linear_speed_kd = kd
            self.logger.info(
                f"[DUMMY] Setting Linear Speed PID=({kp},{ki},{kd}), "
            )
        elif pid_id == PID_ID.angular_speed_pid_id.value:
            self.angular_speed_kp = kp
            self.angular_speed_ki = ki
            self.angular_speed_kd = kd
            self.logger.info(
                f"[DUMMY] Setting Angular Speed PID=({kp},{ki},{kd}), "
            )
        elif pid_id == PID_ID.linear_position_pid_id.value:
            self.linear_position_kp = kp
            self.linear_position_ki = ki
            self.linear_position_kd = kd
            self.logger.info(
                f"[DUMMY] Setting Linear Position PID=({kp},{ki},{kd}), "
            )
        elif pid_id == PID_ID.angular_position_pid_id.value:
            self.angular_position_kp = kp
            self.angular_position_ki = ki
            self.angular_position_kd = kd
            self.logger.info(
                f"[DUMMY] Setting Angular Position PID=({kp},{ki},{kd}), "
            )

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
        self.__set_pid(PID_ID.linear_speed_pid_id.value, kp, ki, kd)

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
        self.__set_pid(PID_ID.angular_speed_pid_id.value, kp, ki, kd)

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
        self.__set_pid(PID_ID.linear_position_pid_id.value, kp, ki, kd)

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
        self.__set_pid(PID_ID.linear_position_pid_id.value, kp, ki, kd)

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
            **CONFIG.LINEAR_POSITION_PID,
            **CONFIG.ANGULAR_POSITION_PID,
        )

    def send_bytes(self, msg: bytes):
        """
        Dummy method to send bytes to the device.
        In the real class, this would handle serial communication.

        Args:
            msg (bytes): The message to send.
        """
        # No real sending performed; simply log the attempt.
        self.logger.info(f"[DUMMY] Sending bytes: {msg.hex()}")

    def __eq__(self, other):
        if not isinstance(other, RollingBasisDummy):
            return False
        return (
                self.odometrie == other.odometrie
                and self.linear_speed == other.linear_speed
                and self.angular_speed == other.angular_speed
                and self.linear_speed_kp == other.linear_speed_kp
                and self.linear_speed_ki == other.linear_speed_ki
                and self.linear_speed_kd == other.linear_speed_kd
                and self.angular_speed_kp == other.angular_speed_kp
                and self.angular_speed_ki == other.angular_speed_ki
                and self.angular_speed_kd == other.angular_speed_kd
                and self.linear_position_kp == other.linear_position_kp
                and self.linear_position_ki == other.linear_position_ki
                and self.linear_position_kd == other.linear_position_kd
                and self.angular_position_kp == other.angular_position_kp
                and self.angular_position_ki == other.angular_position_ki
                and self.angular_position_kd == other.angular_position_kd
        )

    def __ne__(self, other):
        return not self.__eq__(other)


import math
import time
from typing import Callable


########################
# CLASSE DE SIMULATION #
########################

class RollingBasisSimulationDummy:
    """
    Une version plus sophistiquée d'un "dummy" pour votre RollingBasis,
    qui simule grossièrement le comportement d'un robot différentiel
    asservi en vitesse et/ou en position via des PID.
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
            simulation_dt: float = 0.01,
    ):
        """
        Args:
            simulation_dt (float): pas de temps pour la simulation (en secondes).
                                   Détermine la vitesse à laquelle on "avance" dans
                                   la physique simulée.
        """
        # On peut reprendre une bonne partie de l'init du RollingBasisDummy classique :
        self.logger = logger
        self.ser = ser
        self.crc = crc
        self.vid = vid
        self.pid = pid
        self.baudrate = baudrate
        self.dummy = dummy

        # ---- États du robot ----
        self.odometrie: OrientedPoint = OrientedPoint(0.0, 0.0, 0.0)  # (x, y, theta)
        self.current_linear_speed = 0.0  # Vitesse linéaire réelle
        self.current_angular_speed = 0.0  # Vitesse angulaire réelle

        # ---- Consignes ----
        # Consigne de vitesse (peut être mise à jour par set_speed_and_position, ou autre).
        self.target_linear_speed = 0.0
        self.target_angular_speed = 0.0

        # Consigne de position (peut être mise à jour par set_speed_and_position).
        self.target_position = OrientedPoint((0.0, 0.0), 0.0)

        # Indicateurs : veut-on asservir la position ?
        # (si oui, on active un PID position qui génère une consigne de vitesse)
        self.enable_position_control = True

        # ---- PID (valeurs Kp, Ki, Kd) ----
        # Vitesse linéaire
        self.linear_speed_kp = 0.0
        self.linear_speed_ki = 0.0
        self.linear_speed_kd = 0.0

        # Vitesse angulaire
        self.angular_speed_kp = 0.0
        self.angular_speed_ki = 0.0
        self.angular_speed_kd = 0.0

        # Position linéaire
        self.linear_position_kp = 0.0
        self.linear_position_ki = 0.0
        self.linear_position_kd = 0.0

        # Position angulaire
        self.angular_position_kp = 0.0
        self.angular_position_ki = 0.0
        self.angular_position_kd = 0.0

        # ---- États internes du PID (intégrale, erreur précédente) ----
        self._lin_speed_integral = 0.0
        self._lin_speed_prev_error = 0.0

        self._ang_speed_integral = 0.0
        self._ang_speed_prev_error = 0.0

        self._lin_pos_integral = 0.0
        self._lin_pos_prev_error = 0.0

        self._ang_pos_integral = 0.0
        self._ang_pos_prev_error = 0.0

        # Pour stocker les callbacks
        self.messagetype_callbacks = {}

        # On les enregistre
        self.add_callback(self.rcv_print, Command.PRINT)
        self.add_callback(self.rcv_unknown_msg, Command.UNKNOWN_MSG_TYPE)
        self.add_callback(self.rcv_rolling_basis_state, Command.UPDATE_ROLLING_BASIS)

        # ---- Paramètres de simulation ----
        self.simulation_dt = simulation_dt  # pas de temps
        self.last_update_time = time.time()  # pour si on veut un loop auto
        self.logger.info("[DUMMY SIM] RollingBasisSimulationDummy initialized.")

    def add_callback(self, callback_func: Callable, cmd_type: int) -> None:
        self.messagetype_callbacks[cmd_type] = callback_func

    #############################
    # Callbacks / Handlers etc #
    #############################

    def rcv_print(self, msg: bytes):
        decoded_msg = msg.decode("ascii", errors="ignore")
        self.logger.info(f"Dummy RollingBasis received a PRINT message: {decoded_msg}")

    def rcv_rolling_basis_state(self, msg: bytes):
        raw_data_hex = msg.hex()
        self.logger.info(f"Dummy RollingBasis received a state update: {raw_data_hex}")

    def rcv_unknown_msg(self, msg: bytes):
        self.logger.warning(
            f"Dummy RollingBasis received an unknown message: {msg.hex()}"
        )

    ###################
    # Méthodes "send" #
    ###################
    def send_bytes(self, msg: bytes):
        # Dans la vraie vie, on enverrait sur le port série. Ici on log simplement.
        self.logger.info(f"[DUMMY SIM] Sending bytes: {msg.hex()}")

    #####################
    # SET / GET PIDs    #
    #####################

    def __set_pid(self, pid_id: int, kp: float, ki: float, kd: float) -> None:
        """Similaire à votre code RollingBasisDummy, sans le décorateur log."""
        if pid_id == PID_ID.linear_speed_pid_id.value:
            self.linear_speed_kp = kp
            self.linear_speed_ki = ki
            self.linear_speed_kd = kd
            self.logger.info(f"[DUMMY SIM] Setting Linear Speed PID=({kp},{ki},{kd})")
        elif pid_id == PID_ID.angular_speed_pid_id.value:
            self.angular_speed_kp = kp
            self.angular_speed_ki = ki
            self.angular_speed_kd = kd
            self.logger.info(f"[DUMMY SIM] Setting Angular Speed PID=({kp},{ki},{kd})")
        elif pid_id == PID_ID.linear_position_pid_id.value:
            self.linear_position_kp = kp
            self.linear_position_ki = ki
            self.linear_position_kd = kd
            self.logger.info(f"[DUMMY SIM] Setting Linear Position PID=({kp},{ki},{kd})")
        elif pid_id == PID_ID.angular_position_pid_id.value:
            self.angular_position_kp = kp
            self.angular_position_ki = ki
            self.angular_position_kd = kd
            self.logger.info(f"[DUMMY SIM] Setting Angular Position PID=({kp},{ki},{kd})")

    def set_linear_speed_pid(self, kp: float, ki: float, kd: float) -> None:
        self.__set_pid(PID_ID.linear_speed_pid_id.value, kp, ki, kd)

    def set_angular_speed_pid(self, kp: float, ki: float, kd: float) -> None:
        self.__set_pid(PID_ID.angular_speed_pid_id.value, kp, ki, kd)

    def set_linear_position_pid(self, kp: float, ki: float, kd: float) -> None:
        self.__set_pid(PID_ID.linear_position_pid_id.value, kp, ki, kd)

    def set_angular_position_pid(self, kp: float, ki: float, kd: float) -> None:
        self.__set_pid(PID_ID.angular_position_pid_id.value, kp, ki, kd)

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
        self.set_linear_position_pid(kp_linear_position, ki_linear_position, kd_linear_position)
        self.set_angular_position_pid(kp_angular_position, ki_angular_position, kd_angular_position)

    ###################
    # Ordres de base  #
    ###################

    @log("RollingBasis")
    def set_speed_and_position(
            self,
            target_linear_speed: float,
            target_angular_speed: float,
            target_position: OrientedPoint,
    ) -> None:
        """
        En mode normal, on reçoit un ordre (v_lin, v_ang, position).
        Dans cette simulation, on va considérer qu'on veut à la fois
        atteindre la vitesse ET la position (si enable_position_control=True).
        """
        # Consignes
        self.target_linear_speed = target_linear_speed
        self.target_angular_speed = target_angular_speed
        self.target_position = target_position

        self.logger.info(
            f"[DUMMY SIM] Consigne => Vlin={target_linear_speed}, "
            f"Vang={target_angular_speed}, Pos=({target_position.x}, "
            f"{target_position.y}, {target_position.theta})"
        )

    @log("RollingBasis")
    def set_odometrie(self, odometrie: OrientedPoint) -> None:
        """
        Permet de "forcer" la position (par ex. re-calage).
        """
        self.odometrie = odometrie
        self.logger.info(f"[DUMMY SIM] Setting odometrie => {odometrie.x}, {odometrie.y}, {odometrie.theta}")

    #############################################
    # Fonction de MISE A JOUR de la SIMULATION  #
    #############################################

    def update_simulation(self, dt: float = None):
        """
        Met à jour l'état du robot (position, vitesse), en tenant compte
        des PID vitesse et position. À appeler régulièrement (par exemple
        dans un thread, ou dans la boucle principale).

        Args:
            dt (float): si None, on recalcule un dt en fonction du temps réel.
                        sinon, on utilise la valeur donnée.
        """
        if dt is None:
            current_time = time.time()
            dt = current_time - self.last_update_time
            self.last_update_time = current_time

        if dt <= 0:
            return

        # --- 1) PID POSITION => génère la consigne de vitesse (optionnel) ---
        if self.enable_position_control:
            # -> Contrôle en X/Y
            # distance à la cible
            dx = self.target_position.x - self.odometrie.x
            dy = self.target_position.y - self.odometrie.y
            distance = math.sqrt(dx * dx + dy * dy)

            # Erreur linéaire = distance
            # On calcule un angle desired pour pointer vers la cible
            desired_angle = math.atan2(dy, dx)
            angle_error = self._angle_diff(desired_angle, self.odometrie.theta)

            # Contrôle PIDs position : (simplement sur la distance et l'erreur d'angle)
            # => On veut en sortir une "vitesse linéaire" et "vitesse angulaire" cibles.
            lin_pos_error = distance
            # PID lin position
            (lin_pos_pid_out,
             self._lin_pos_integral,
             self._lin_pos_prev_error) = self._apply_pid(
                lin_pos_error,
                self._lin_pos_integral,
                self._lin_pos_prev_error,
                self.linear_position_kp,
                self.linear_position_ki,
                self.linear_position_kd,
                dt
            )

            ang_pos_error = angle_error
            # PID ang position
            (ang_pos_pid_out,
             self._ang_pos_integral,
             self._ang_pos_prev_error) = self._apply_pid(
                ang_pos_error,
                self._ang_pos_integral,
                self._ang_pos_prev_error,
                self.angular_position_kp,
                self.angular_position_ki,
                self.angular_position_kd,
                dt
            )

            # On limite la consigne si on veut (ex: pour éviter d'aller trop vite en mode position)
            # ou on la mixe avec la consigne de vitesse imposée par l'utilisateur
            # par ex: self.target_linear_speed = ...
            # Dans cet exemple, on va admettre que la position a la priorité,
            # donc c'est elle qui fixe la target speed.
            # On peut faire un "mix" : target_v = min(lin_pos_pid_out, self.target_linear_speed)
            # Pour la démo, on écrase tout simplement la consigne de vitesse par la sortie PID position.
            self.target_linear_speed = lin_pos_pid_out
            self.target_angular_speed = ang_pos_pid_out

        # --- 2) PID VITESSE => met à jour la vitesse réelle (accélération) ---
        # Contrôle la vitesse linéaire
        lin_speed_error = self.target_linear_speed - self.current_linear_speed
        (lin_speed_pid_out,
         self._lin_speed_integral,
         self._lin_speed_prev_error) = self._apply_pid(
            lin_speed_error,
            self._lin_speed_integral,
            self._lin_speed_prev_error,
            self.linear_speed_kp,
            self.linear_speed_ki,
            self.linear_speed_kd,
            dt
        )
        # Cette sortie de PID peut être vue comme une "accélération" (selon un modèle simpliste).
        # On met à jour la vitesse réelle :
        self.current_linear_speed += lin_speed_pid_out * dt

        # Contrôle la vitesse angulaire
        ang_speed_error = self.target_angular_speed - self.current_angular_speed
        (ang_speed_pid_out,
         self._ang_speed_integral,
         self._ang_speed_prev_error) = self._apply_pid(
            ang_speed_error,
            self._ang_speed_integral,
            self._ang_speed_prev_error,
            self.angular_speed_kp,
            self.angular_speed_ki,
            self.angular_speed_kd,
            dt
        )
        self.current_angular_speed += ang_speed_pid_out * dt

        # --- 3) Mise à jour de la position (odometrie) ---
        # On fait une intégration sur dt, dans le repère du robot différentiel
        # Simplification : le robot avance dans la direction de son orientation
        # => x += v_lin * cos(theta) * dt
        # => y += v_lin * sin(theta) * dt
        # => theta += v_ang * dt
        theta = self.odometrie.theta
        self.odometrie.x += self.current_linear_speed * math.cos(theta) * dt
        self.odometrie.y += self.current_linear_speed * math.sin(theta) * dt
        self.odometrie.theta = self._normalize_angle(theta + self.current_angular_speed * dt)

    #######################################
    # Petites fonctions utilitaires PID   #
    #######################################

    def _apply_pid(self, error, integral, prev_error, kp, ki, kd, dt):
        """
        Calcule la sortie d'un PID discret (Euler) simple.
        Renvoie (output, new_integral, new_prev_error).
        """
        # Somme d'erreur
        new_integral = integral + error * dt
        # Terme dérivé
        derivative = (error - prev_error) / dt if dt > 0 else 0.0

        output = kp * error + ki * new_integral + kd * derivative
        new_prev_error = error
        return output, new_integral, new_prev_error

    def _normalize_angle(self, angle):
        """Ramène un angle dans [-pi, pi)."""
        while angle >= math.pi:
            angle -= 2.0 * math.pi
        while angle < -math.pi:
            angle += 2.0 * math.pi
        return angle

    def _angle_diff(self, a, b):
        """Renvoie la différence d'angle a - b ramenée dans [-pi, pi)."""
        diff = a - b
        return self._normalize_angle(diff)
