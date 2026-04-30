"""Module for managing the asservissement of the rolling basis of the robot."""

from __future__ import annotations

import struct
import time
from typing import TYPE_CHECKING, Any, overload, override

import matplotlib.pyplot as plt
from loggerplusplus import LogLevels, log

from a_config_loader import CONFIG
from controllers.rolling_basis.pids import PID, PidID
from geometry import OrientedPoint
from teensy import BaseComTeensy
from usb_com.python import Messages

if TYPE_CHECKING:
    from loggerplusplus import Logger

    from navigation.trajectory_planner import TrajectoryPlanCommand


class AsservissementRollingBasis(
    BaseComTeensy,
):  # FIXME: à la fin de la tache, continue de tourner au lieu de s'arreter
    """Represents the rolling basis of the robot.

    Inherits from Teensy to manage low-level communications and adds logic specific
    to the robot's state,
    PID configuration, and message messaging.
    Automatically logs target vs actual odometry on each send.
    """

    def __init__(
        self,
        logger: Logger,
        serial_number: int = CONFIG.ROLLING_BASIS_TEENSY_SER,
        vid: int = CONFIG.TEENSY_VID,
        pid: int = CONFIG.TEENSY_PID,
        baudrate: int = CONFIG.TEENSY_BAUDRATE,
        *,
        enable_crc: bool = CONFIG.TEENSY_CRC,
        enable_dummy: bool = CONFIG.ROLLING_BASIS_DUMMY,
    ) -> None:
        """Initializes the AsservissementRollingBasis class.

        Args:
            logger (Logger): The logger instance for logging.
            serial_number (int, optional): The serial number of the Teensy.
                Defaults to CONFIG.ROLLING_BASIS_TEENSY_SER.
            vid (int, optional):
                The vendor ID of the Teensy. Defaults to CONFIG.TEENSY_VID.
            pid (int, optional):
                The product ID of the Teensy. Defaults to CONFIG.TEENSY_PID.
            baudrate (int, optional): The baud rate for serial communication.
                Defaults to CONFIG.TEENSY_BAUDRATE.
            enable_crc (bool, optional):
                Whether to enable CRC checks. Defaults to CONFIG.TEENSY_CRC.
            enable_dummy (bool, optional):
                Whether to enable dummy mode. Defaults to CONFIG.ROLLING_BASIS_DUMMY.
        """
        # Initialize state and log storage
        self._logger = logger
        self.odometrie: OrientedPoint = OrientedPoint((0.0, 0.0), 0.0)
        self._last_target: OrientedPoint = OrientedPoint((0.0, 0.0), 0.0)
        self._logs: list[dict[str, Any]] = []  # store dicts of time, target, actual

        # Initialize parent
        super().__init__(
            logger,
            serial_number,
            vid,
            pid,
            baudrate,
            enable_crc=enable_crc,
            enable_dummy=enable_dummy,
        )

        # PID controllers
        self.linear_position_pid: PID = PID(0.0, 0.0, 0.0)
        self.angular_position_pid: PID = PID(0.0, 0.0, 0.0)
        self.left_wheel_position_pid: PID = PID(0.0, 0.0, 0.0)
        self.right_wheel_position_pid: PID = PID(0.0, 0.0, 0.0)

        # Register message handlers
        self.add_callback(self.rcv_print, Messages.PRINT.value)
        self.add_callback(self.rcv_unknown_msg, Messages.UNKNOWN_MSG_TYPE.value)
        self.add_callback(
            self.rcv_rolling_basis_state,
            Messages.UPDATE_ROLLING_BASIS.value,
        )

        self.initialize_pids()
        self.reset_teensy_and_reinit()

    # region ====== Message Receiving Handlers ======

    def rcv_print(self, msg: bytes) -> None:
        """Handle PRINT messages from the Teensy.

        Args:
            msg (bytes): The received message bytes.
        """
        self._logger.info(
            f"[CTRL:RB] Teensy says: {msg.decode('ascii', errors='ignore')}",
        )

    def rcv_rolling_basis_state(self, msg: bytes) -> None:
        """Handle rolling basis odometry update messages from the Teensy.

        The message contains:
        - float x: X-coordinate of the position (4 bytes).
        - float y: Y-coordinate of the position (4 bytes).
        - float theta: Orientation (4 bytes).
        - float current_linear_speed: Current linear speed (4 bytes).
        - float current_angular_speed: Current angular speed (4 bytes).

        Args:
            msg (bytes): The received message bytes.
        """
        # Unpack new odometry
        self.odometrie = OrientedPoint(
            (struct.unpack("<d", msg[0:8])[0], struct.unpack("<d", msg[8:16])[0]),
            struct.unpack("<d", msg[16:24])[0],
        )
        # After receiving actual state, log entry
        self._log_entry()

    def rcv_unknown_msg(self, msg: bytes) -> None:
        """Handle unknown messages from the Teensy.

        Args:
            msg (bytes): The received message bytes.
        """
        self._logger.warning(f"[CTRL:RB] Teensy unknown message: {msg.hex()}")

    # endregion

    # region ====== Message Sending Methods ======

    def reset_teensy_and_reinit(self, *, delay_s: float = 0.8) -> None:
        """Reset the Teensy and reinitialize rolling basis state."""
        self._logger.info("[CTRL:RB] Sending RESET_TEENSY")
        self.reset()
        time.sleep(delay_s)
        if not self.reconnect():
            return
        self.set_odometrie(OrientedPoint((0.0, 0.0), 0.0))
        self.set_target_pose(OrientedPoint((0.0, 0.0), 0.0))

    def set_trajectory_command(self, cmd: TrajectoryPlanCommand) -> None:
        """Send the target pose from a trajectory command."""
        self.set_target_pose(cmd.position)

    def set_target_pose(
        self,
        pose: OrientedPoint,
    ) -> None:
        """Send a command to set the target position of the rolling basis.

        Linear speed is expressed in cm/s and angular speed in rad/s.

        Args:
            pose (OrientedPoint): Desired position and orientation.
        """
        # Store for logging
        self._last_target = pose

        # Build and send message
        msg = (
            Messages.SET_TARGET_POSE.to_bytes()
            + struct.pack("<d", pose.x)
            + struct.pack("<d", pose.y)
            + struct.pack("<d", pose.theta)
        )
        self.send_bytes(msg)

    @log(param_logger="RollingBasis", log_level=LogLevels.INFO)
    def set_odometrie(self, odometrie: OrientedPoint) -> None:
        """Send a message to set the odometrie of the rolling basis.

        Args:
            odometrie (OrientedPoint): The new odometrie values.

        Raises:
            ValueError: If odometrie.theta is None.
        """
        if odometrie.theta is None:
            msg = (
                f"Odometrie theta must be defined, got None at "
                f"position ({odometrie.x}, {odometrie.y})"
            )
            raise ValueError(msg)

        msg = (
            Messages.SET_ODOMETRIE.to_bytes()
            + struct.pack("<d", odometrie.x)
            + struct.pack("<d", odometrie.y)
            + struct.pack("<d", odometrie.theta)
        )
        self.send_bytes(msg)

    @log(param_logger="RollingBasis", log_level=LogLevels.INFO)
    def _send_pid(self, pid_id: int, pid: PID) -> None:
        """Internal method to send PID configuration data to the Teensy.

        Args:
            pid_id (int): The identifier for the PID controller.
            pid (PID): The PID controller parameters.
        """
        msg = Messages.SET_PID.to_bytes() + pid_id.to_bytes() + pid.to_bytes()
        self.send_bytes(msg)

    # endregion

    # region ====== Logging Methods ======

    def _log_entry(self) -> None:
        """Record timestamp, last target, and latest odometry."""
        self._logs.append(
            {
                "time": time.time(),
                "target_x": self._last_target.x,
                "target_y": self._last_target.y,
                "target_theta": self._last_target.theta,
                "actual_x": self.odometrie.x,
                "actual_y": self.odometrie.y,
                "actual_theta": self.odometrie.theta,
            },
        )

    def get_logs(self) -> list[dict[str, Any]]:
        """Return the recorded log entries.

        Each entry is a dictionary with keys ``time``, ``target_x``, ``target_y``,
        ``target_theta``, ``actual_x``, ``actual_y`` and ``actual_theta``.

        Returns:
            list[dict[str, Any]]: The stored log entries.
        """
        return self._logs

    def clear_logs(self) -> None:
        """Clear stored log entries."""
        self._logs.clear()

    def plot_logs(self) -> None:
        """Plot target vs actual odometry for X, Y, and Theta using stored logs.

        Ensures all series have the same length before plotting.
        """
        if not self._logs:
            self._logger.warning("[CTRL:RB] No position-control logs to plot")
            return

        t0 = self._logs[0]["time"]
        times = [entry["time"] - t0 for entry in self._logs]

        _, axs = plt.subplots(3, 1, figsize=(10, 8), sharex=True)

        axs[0].plot(
            times,
            [entry["target_x"] for entry in self._logs],
            label="Consigne X",
        )
        axs[0].plot(times, [entry["actual_x"] for entry in self._logs], label="Reel X")
        axs[0].set_ylabel("X (cm)")
        axs[0].legend()

        axs[1].plot(
            times,
            [entry["target_y"] for entry in self._logs],
            label="Consigne Y",
        )
        axs[1].plot(times, [entry["actual_y"] for entry in self._logs], label="Reel Y")
        axs[1].set_ylabel("Y (cm)")
        axs[1].legend()

        axs[2].plot(
            times,
            [entry["target_theta"] for entry in self._logs],
            label="Consigne theta",
        )
        axs[2].plot(
            times,
            [entry["actual_theta"] for entry in self._logs],
            label="Reel theta",
        )
        axs[2].set_ylabel("theta (rad)")
        axs[2].set_xlabel("Temps (s)")
        axs[2].legend()

        plt.tight_layout()
        plt.show()

    # endregion

    # region ====== PID Configuration Methods ======

    @staticmethod
    def _load_pid(
        *args: float | dict[str, float],
        **kwargs: float,
    ) -> PID:
        """Load the PID values.

        Overloads:
            - set_linear_position_pid(float, float, float) → None
            - set_linear_position_pid(dict[str, float]) → None
            - set_linear_position_pid(kp=float, ki=float, kd=float) → None

        Args:
            *args (float | dict[str, float]): Either three floats (kp, ki, kd) or a
                single dictionary with keys 'kp', 'ki', 'kd'.
            **kwargs (float): Keyword arguments mapping PID fields to values.

        Returns:
            PID: The configured PID instance.

        Raises:
            ValueError: If the arguments do not match any expected format.
        """
        if len(args) == 3 and all(isinstance(arg, float) for arg in args):  # noqa: PLR2004
            pid = PID(*args)  # pyright: ignore[reportArgumentType]
        elif len(args) == 1 and isinstance(args[0], dict):
            pid = PID.from_dict(args[0])
        elif kwargs:
            pid = PID.from_dict(kwargs)
        else:
            msg = "Invalid arguments for PID configuration."
            raise ValueError(msg)
        return pid

    @overload
    def set_linear_position_pid(self, *args: float) -> None: ...

    @overload
    def set_linear_position_pid(self, pid_values: dict[str, float]) -> None: ...

    @overload
    def set_linear_position_pid(self, kp: float, ki: float, kd: float) -> None: ...

    def set_linear_position_pid(
        self,
        *args: float | dict[str, float],
        **kwargs: float,
    ) -> None:
        """Configure the PID values for linear position control.

        Overloads:
            - set_linear_position_pid(float, float, float) → None
            - set_linear_position_pid(dict[str, float]) → None
            - set_linear_position_pid(kp=float, ki=float, kd=float) → None

        Args:
            *args (float | dict[str, float]): Either three floats (kp, ki, kd) or a
                single dictionary with keys 'kp', 'ki', 'kd'.
            **kwargs (float): Keyword arguments mapping PID fields to values.
        """
        try:
            pid = self._load_pid(*args, **kwargs)
            self.linear_position_pid = pid
            self._send_pid(PidID.LINEAR_POSITION.value, pid)
        except (ValueError, TypeError) as e:
            self._logger.error(f"[CTRL:RB] Failed to set linear position PID: {e}")

    @overload
    def set_angular_position_pid(self, *args: float) -> None: ...

    @overload
    def set_angular_position_pid(self, pid_values: dict[str, float]) -> None: ...

    @overload
    def set_angular_position_pid(self, kp: float, ki: float, kd: float) -> None: ...

    def set_angular_position_pid(
        self,
        *args: float | dict[str, float],
        **kwargs: float,
    ) -> None:
        """Configure the PID values for angular position control.

        Overloads:
            - set_angular_position_pid(float, float, float) → None
            - set_angular_position_pid(dict[str, float]) → None
            - set_angular_position_pid(kp=float, ki=float, kd=float) → None

        Args:
            *args (float | dict[str, float]): Either three floats (kp, ki, kd) or a
                single dictionary with keys 'kp', 'ki', 'kd'.
            **kwargs (float): Keyword arguments mapping PID fields to values.
        """
        try:
            pid = self._load_pid(*args, **kwargs)
            self.angular_position_pid = pid
            self._send_pid(PidID.ANGULAR_POSITION.value, pid)
        except (ValueError, TypeError) as e:
            self._logger.error(f"[CTRL:RB] Failed to set angular position PID: {e}")

    @overload
    def set_left_wheel_position_pid(self, *args: float) -> None: ...

    @overload
    def set_left_wheel_position_pid(self, pid_values: dict[str, float]) -> None: ...

    @overload
    def set_left_wheel_position_pid(self, kp: float, ki: float, kd: float) -> None: ...

    def set_left_wheel_position_pid(
        self,
        *args: float | dict[str, float],
        **kwargs: float,
    ) -> None:
        """Configure the PID values for left wheel position control."""
        try:
            pid = self._load_pid(*args, **kwargs)
            self.left_wheel_position_pid = pid
            self._send_pid(PidID.LEFT_WHEEL_POSITION.value, pid)
        except (ValueError, TypeError) as e:
            self._logger.error(f"[CTRL:RB] Failed to set left wheel PID: {e}")

    @overload
    def set_right_wheel_position_pid(self, *args: float) -> None: ...

    @overload
    def set_right_wheel_position_pid(self, pid_values: dict[str, float]) -> None: ...

    @overload
    def set_right_wheel_position_pid(self, kp: float, ki: float, kd: float) -> None: ...

    def set_right_wheel_position_pid(
        self,
        *args: float | dict[str, float],
        **kwargs: float,
    ) -> None:
        """Configure the PID values for right wheel position control."""
        try:
            pid = self._load_pid(*args, **kwargs)
            self.right_wheel_position_pid = pid
            self._send_pid(PidID.RIGHT_WHEEL_POSITION.value, pid)
        except (ValueError, TypeError) as e:
            self._logger.error(f"[CTRL:RB] Failed to set right wheel PID: {e}")

    def set_pids(
        self,
        linear_position_pid: dict[str, float],
        angular_position_pid: dict[str, float],
        left_wheel_position_pid: dict[str, float],
        right_wheel_position_pid: dict[str, float],
    ) -> None:
        """Configure all PID controllers.

        Args:
            linear_position_pid (dict[str, float]):
                PID values for linear position control.
            angular_position_pid (dict[str, float]):
                PID values for angular position control.
        """
        self.set_linear_position_pid(**linear_position_pid)
        time.sleep(0.1)
        self.set_angular_position_pid(**angular_position_pid)
        time.sleep(0.1)
        self.set_left_wheel_position_pid(**left_wheel_position_pid)
        time.sleep(0.1)
        self.set_right_wheel_position_pid(**right_wheel_position_pid)
        time.sleep(0.1)

    def initialize_pids(self) -> None:
        """Initialize PID controllers from the configuration."""
        try:
            self.set_pids(
                linear_position_pid=CONFIG.ROLLING_BASIS_PIDS_LINEAR_POSITION,
                angular_position_pid=CONFIG.ROLLING_BASIS_PIDS_ANGULAR_POSITION,
                left_wheel_position_pid=CONFIG.ROLLING_BASIS_PIDS_LEFT_WHEEL_POSITION,
                right_wheel_position_pid=CONFIG.ROLLING_BASIS_PIDS_RIGHT_WHEEL_POSITION,
            )
        except (ValueError, TypeError) as e:
            self._logger.error(f"[CTRL:RB] Failed to initialize PIDs: {e}")

    def _initialize_pids(self) -> None:
        """Backward-compatible alias for PID initialization."""
        self.initialize_pids()

    # endregion

    # region ====== Built-in methods ======

    @override
    def __hash__(self) -> int:
        """Compute a hash for the AsservissementRollingBasis instance.

        Returns:
            int: The hash value.
        """
        return hash((
            self.odometrie,
            self.linear_position_pid,
            self.angular_position_pid,
            self.left_wheel_position_pid,
            self.right_wheel_position_pid,
        ))

    @override
    def __eq__(self, other: object) -> bool:
        """Check equality of two AsservissementRollingBasis instances."""
        if not isinstance(other, AsservissementRollingBasis):
            return NotImplemented
        return (
            self.odometrie == other.odometrie
            and self.linear_position_pid == other.linear_position_pid
            and self.angular_position_pid == other.angular_position_pid
            and self.left_wheel_position_pid == other.left_wheel_position_pid
            and self.right_wheel_position_pid == other.right_wheel_position_pid
        )

    @override
    def __ne__(self, other: object) -> bool:
        """Check inequality of two AsservissementRollingBasis instances.

        Args:
            other (object): The other instance to compare against.

        Returns:
            bool: ``True`` if the instances are not equal, ``False`` otherwise.
        """
        return not self.__eq__(other)

    # endregion
