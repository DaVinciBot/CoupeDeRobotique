"""Rolling basis controller interfacing with the Teensy board."""

from __future__ import annotations

import struct
import time
from enum import Enum
from typing import TYPE_CHECKING, overload, override

import glob
import os

from loggerplusplus import LogLevels, log

from a_config_loader import CONFIG
from controllers.rolling_basis.pids import PID, PidID
from geometry import OrientedPoint
from teensy import BaseComTeensy
from usb_com.python import Messages

import re
import pandas as pd
import matplotlib.pyplot as plt

if TYPE_CHECKING:
    from loggerplusplus import Logger

    from navigation.trajectory_planner import TrajectoryPlanCommand


class RollingBasis(BaseComTeensy):
    """Represents the rolling basis of the robot.

    Inherits from Teensy to manage low-level communications and adds logic
    specific to the robot's state, PID configuration, and message messaging.
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
        """Initializes the RollingBasis class.

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

        # Initialize the parent-BaseComTeensy class
        super().__init__(
            logger,
            serial_number,
            vid,
            pid,
            baudrate,
            enable_crc=enable_crc,
            enable_dummy=enable_dummy,
        )

        # Robot state
        self.odometrie: OrientedPoint = OrientedPoint((0.0, 0.0), 0.0)

        # PID controllers
        self.linear_velocity_pid: PID = PID(0.0, 0.0, 0.0)
        self.angular_velocity_pid: PID = PID(0.0, 0.0, 0.0)

        self._live_counter = None
        self._live_data = None
        self.flag = True
        self._fig, self._axs = plt.subplots(4, 1, sharex=True)

        self._lines = {}

        """
        This is used to match a handling function to a message type.
        add_callback can also be used.
        """
        # Register message handlers
        self.add_callback(self.rcv_print, Messages.PRINT.value)
        self.add_callback(self.rcv_unknown_msg, Messages.UNKNOWN_MSG_TYPE.value)
        self.add_callback(
            self.rcv_rolling_basis_state,
            Messages.UPDATE_ROLLING_BASIS.value,
        )

        time.sleep(0.01)  # Avoid overload
        self.reset_teensy_and_reinit()

    # region ====== Message Receiving Handlers ======

    def rcv_print(self, msg: bytes) -> None:
        """Handles PRINT messages from the Teensy.

        Args:
            msg (bytes): The received message bytes.
        """
        line = msg.decode('ascii', errors='ignore')

        self._logger.info(f"[CTRL:RB:Teensy] {line}")

        self.update_live_plot_from_line(line)

    def rcv_rolling_basis_state(
        self,
        msg: bytes,
    ) -> None:  # TODO: teensy send correct odometrie / speed
        """Handles rolling basis state update messages from the Teensy.

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

    def rcv_unknown_msg(self, msg: bytes) -> None:
        """Handles unknown messages from the Teensy.

        Logs a warning indicating that the message type is not recognized.

        Args:
            msg (bytes): The received message bytes.
        """
        self._logger.warning(f"[CTRL:RB:Teensy] Unknown message type: {msg.hex()}")

    # endregion

    # region ====== Message Sending Methods ======

    class ControlMode(Enum):
        VELOCITY = 0
        POSITION = 1

    def reset_teensy_and_reinit(self, *, delay_s: float = 0.8) -> None:
        """Reset the Teensy and reinitialize rolling basis state."""
        self._logger.info("[CTRL:RB] Sending RESET_TEENSY")
        self.reset()
        time.sleep(delay_s)
        if not self.reconnect():
            return
        self.set_odometrie(OrientedPoint((0.0, 0.0), 0.0))
        msg = (
            Messages.SET_TARGET_VELOCITY.to_bytes()
            + struct.pack("<d", 0.0)
            + struct.pack("<d", 0.0)
        )
        self.send_bytes(msg)

    def set_control_mode(self, mode: ControlMode | int) -> None:
        """Set rolling basis control mode (velocity or position)."""
        mode_value = (
            mode.value if isinstance(mode, RollingBasis.ControlMode) else int(mode)
        )
        msg = Messages.SET_CONTROL_MODE.to_bytes() + bytes([mode_value])
        self.send_bytes(msg)

    # @log(param_logger="RollingBasis", log_level=LogLevels.INFO)
    def set_target_velocity(self, cmd: TrajectoryPlanCommand) -> None:
        """Send a command to set the target velocity of the rolling basis.

        Args:
            cmd (TrajectoryPlanCommand): The command containing target velocities
                (linear in cm/s, angular in rad/s).
        """
        self._logger.info(
            f"[CTRL:RB] Setting target velocities: "
            f"linear_speed={cmd.linear_speed}, angular_speed={cmd.angular_speed}",
        )
        msg = (
            Messages.SET_TARGET_VELOCITY.to_bytes()
            + struct.pack("<d", cmd.linear_speed)
            + struct.pack("<d", cmd.angular_speed)
        )

        # Send the composed message to the Teensy
        # https://docs.python.org/3/library/struct.html#format-characters
        self.send_bytes(msg)

    def set_target_pose(
        self,
        pose: OrientedPoint,
        linear_speed: float = 0.0,
        angular_speed: float = 0.0,
    ) -> None:
        """Send a command to set the target pose with optional feedforward."""
        msg = (
            Messages.SET_TARGET_POSE.to_bytes()
            + struct.pack("<d", pose.x)
            + struct.pack("<d", pose.y)
            + struct.pack("<d", pose.theta)
            + struct.pack("<d", linear_speed)
            + struct.pack("<d", angular_speed)
        )
        self.send_bytes(msg)

    @log(param_logger="RollingBasis", log_level=LogLevels.INFO)
    def set_odometrie(self, odometrie: OrientedPoint) -> None:
        """Sends a message to set the odometrie of the rolling basis.

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

    @log(
        param_logger="RollingBasis",
        log_level=LogLevels.INFO,
    )
    def _send_pid(self, pid_id: int, pid: PID) -> None:
        """Internal method to send PID configuration data to the Teensy.

        Args:
            pid_id (int): The identifier for the PID controller.
            pid (PID): The PID controller parameters.
        """
        msg = Messages.SET_PID.to_bytes() + pid_id.to_bytes() + pid.to_bytes()
        self.send_bytes(msg)

    # endregion

    # region ====== PID Configuration Methods ======

    @staticmethod
    def _load_pid(
        *args: float | dict[str, float],
        **kwargs: float,
    ) -> PID:
        """Load the PID values.

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
            pid = PID(*args)  # pyright: ignore[reportArgumentType] args are all float
        elif len(args) == 1 and isinstance(args[0], dict):
            pid = PID.from_dict(args[0])
        elif kwargs:
            pid = PID.from_dict(kwargs)
        else:
            msg = "Invalid arguments for PID configuration."
            raise ValueError(msg)
        return pid

    @overload
    def set_linear_velocity_pid(self, *args: float) -> None: ...

    @overload
    def set_linear_velocity_pid(self, pid_values: dict[str, float]) -> None: ...

    @overload
    def set_linear_velocity_pid(self, kp: float, ki: float, kd: float) -> None: ...

    def set_linear_velocity_pid(
        self,
        *args: float | dict[str, float],
        **kwargs: float,
    ) -> None:
        """Configure the PID values for linear position control.

        Overloads:
            - set_linear_velocity_pid(float, float, float) → None
            - set_linear_velocity_pid(dict[str, float]) → None
            - set_linear_velocity_pid(kp=float, ki=float, kd=float) → None

        Args:
            *args (float | dict[str, float]): Either three floats (kp, ki, kd) or a
                single dictionary with keys 'kp', 'ki', 'kd'.
            **kwargs (float): Keyword arguments mapping PID fields to values.
        """
        try:
            pid = self._load_pid(*args, **kwargs)
            self.linear_velocity_pid = pid
            self._send_pid(PidID.LINEAR_VELOCITY.value, pid)
        except (ValueError, TypeError) as e:
            self._logger.error(f"[CTRL:RB] Failed to set linear velocity PID: {e}")

    @overload
    def set_angular_velocity_pid(self, *args: float) -> None: ...

    @overload
    def set_angular_velocity_pid(self, pid_values: dict[str, float]) -> None: ...

    @overload
    def set_angular_velocity_pid(self, kp: float, ki: float, kd: float) -> None: ...

    def set_angular_velocity_pid(
        self,
        *args: float | dict[str, float],
        **kwargs: float,
    ) -> None:
        """Configure the PID values for angular velocity control.

        Overloads:
            - set_angular_velocity_pid(float, float, float) → None
            - set_angular_velocity_pid(dict[str, float]) → None
            - set_angular_velocity_pid(kp=float, ki=float, kd=float) → None

        Args:
            *args (float | dict[str, float]): Either three floats (kp, ki, kd) or
                a single dictionary with keys 'kp', 'ki', 'kd'.
            **kwargs (float): Keyword arguments mapping PID fields to values.
        """
        try:
            pid = self._load_pid(*args, **kwargs)
            self.angular_velocity_pid = pid
            self._send_pid(PidID.ANGULAR_VELOCITY.value, pid)
        except (ValueError, TypeError) as e:
            self._logger.error(f"[CTRL:RB] Failed to set angular velocity PID: {e}")

    def set_pids(
        self,
        linear_velocity_pid: dict[str, float],
        angular_velocity_pid: dict[str, float],
    ) -> None:
        """Configure all PID controllers using dictionaries for each.

        Args:
            linear_velocity_pid (dict[str, float]):
                PID configuration for linear velocity.
            angular_velocity_pid (dict[str, float]):
                PID configuration for angular velocity.
        """
        self.set_linear_velocity_pid(**linear_velocity_pid)
        time.sleep(0.1)  # Ensure the Teensy has time to process the first PID
        self.set_angular_velocity_pid(**angular_velocity_pid)
        time.sleep(0.1)  # Ensure the Teensy has time to process the second PID

    def initialize_pids(self) -> None:
        """Initialize PID controllers from the configuration."""
        try:
            self.set_pids(
                linear_velocity_pid=CONFIG.ROLLING_BASIS_PIDS_LINEAR_VELOCITY,
                angular_velocity_pid=CONFIG.ROLLING_BASIS_PIDS_ANGULAR_VELOCITY,
            )
        except (ValueError, TypeError) as e:
            self._logger.error(f"[CTRL:RB] Failed to initialize PIDs: {e}")

    # endregion

    # region ====== Built-in methods ======

    @override
    def __eq__(self, other: object) -> bool:
        """Check equality between two RollingBasis instances.

        Args:
            other (object): The other object to compare against.

        Returns:
            bool: ``True`` if the objects are equal, ``False`` otherwise.
        """
        if not isinstance(other, RollingBasis):
            return NotImplemented
        return (
            self.odometrie == other.odometrie
            and self.linear_velocity_pid == other.linear_velocity_pid
            and self.angular_velocity_pid == other.angular_velocity_pid
        )

    @override
    def __ne__(self, other: object) -> bool:
        """Check inequality between two RollingBasis instances.

        Args:
            other (object): The other object to compare against.

        Returns:
            bool: ``True`` if the objects are not equal, ``False`` otherwise.
        """
        return not self.__eq__(other)

    @override
    def __hash__(self) -> int:
        """Return a hash based on object identity.

        Returns:
            int: The hash value of the object.
        """
        return object.__hash__(self)

    # endregion

    # Temps functions do delete later

    def init_live_plot(self) -> None:
        self._live_data = {
            "t": [],
            "tv_lin": [],
            "v_lin": [],
            "e_lin": [],
            "pwm_l": [],
            "ticks_l": [],
        }

        self._live_counter = 0

        plt.ion()


        self._lines["tv_lin"], = self._axs[0].plot([], [], label="target")
        self._lines["v_lin"], = self._axs[0].plot([], [], label="measured")
        self._axs[0].legend()
        self._axs[0].set_title("Velocity")

        self._lines["e_lin"], = self._axs[1].plot([], [], label="error")
        self._axs[1].legend()
        self._axs[1].set_title("Error")

        self._lines["pwm_l"], = self._axs[2].plot([], [], label="PWM")
        self._axs[2].legend()
        self._axs[2].set_title("PWM")

        self._lines["ticks_l"], = self._axs[3].plot([], [], label="ticks")
        self._axs[3].legend()
        self._axs[3].set_title("Encoder")

        plt.show()

    def update_live_plot_from_line(self, line: str) -> None:
        pattern = re.compile(
            r"RB tv=(?P<tv_lin>-?\d+)/(?P<tv_ang>-?\d+)\s+"
            r"v=(?P<v_lin>-?\d+)/(?P<v_ang>-?\d+)\s+"
            r"e=(?P<e_lin>-?\d+)/(?P<e_ang>-?\d+)\s+"
            r"c=(?P<c_lin>-?\d+)/(?P<c_ang>-?\d+)\s+"
            r"pwm=(?P<pwm_l>-?\d+)/(?P<pwm_r>-?\d+)\s+"
            r"ticks=(?P<ticks_l>-?\d+)/(?P<ticks_r>-?\d+)"
        )

        match = pattern.search(line)
        if not match:
            return

        d = {k: int(v) for k, v in match.groupdict().items()}

        self._live_counter += 1
        t = self._live_counter

        self._live_data["t"].append(t)
        self._live_data["tv_lin"].append(d["tv_lin"])
        self._live_data["v_lin"].append(d["v_lin"])
        self._live_data["e_lin"].append(d["e_lin"])
        self._live_data["pwm_l"].append(d["pwm_l"])
        self._live_data["ticks_l"].append(d["ticks_l"])

        # Update lines
        for key in ["tv_lin", "v_lin", "e_lin", "pwm_l", "ticks_l"]:
            self._lines[key].set_data(
                self._live_data["t"],
                self._live_data[key],
            )

        # Rescale
        for ax in self._axs:
            ax.relim()
            ax.autoscale_view()

        self._fig.canvas.draw()
        self._fig.canvas.flush_events()

    def plot_rb_logs(
            self,
            log_file: str,
            *,
            use_real_time: bool = False,
    ) -> None:
        """Parse and plot rolling basis debug logs from a file.

        Args:
            log_file (str): Path to the log file.
            use_real_time (bool): If True, try to extract timestamps from logs.
        """

        pattern = re.compile(
            r"RB tv=(?P<tv_lin>-?\d+)/(?P<tv_ang>-?\d+)\s+"
            r"v=(?P<v_lin>-?\d+)/(?P<v_ang>-?\d+)\s+"
            r"e=(?P<e_lin>-?\d+)/(?P<e_ang>-?\d+)\s+"
            r"c=(?P<c_lin>-?\d+)/(?P<c_ang>-?\d+)\s+"
            r"pwm=(?P<pwm_l>-?\d+)/(?P<pwm_r>-?\d+)\s+"
            r"ticks=(?P<ticks_l>-?\d+)/(?P<ticks_r>-?\d+)"
        )

        data = []
        timestamps = []

        with open(log_file) as f:
            for i, line in enumerate(f):
                match = pattern.search(line)
                if not match:
                    continue

                values = {k: int(v) for k, v in match.groupdict().items()}
                data.append(values)

                if use_real_time:
                    # TODO: adapter si ton logger met un timestamp
                    timestamps.append(i)
                else:
                    timestamps.append(i)

        if not data:
            self._logger.warning("[CTRL:RB] No RB logs found in file")
            return

        df = pd.DataFrame(data)
        df["t"] = timestamps

        # ===== PLOTS =====

        fig, axs = plt.subplots(4, 1, sharex=True, figsize=(10, 8))

        # Velocity tracking
        axs[0].plot(df["t"], df["tv_lin"], label="target lin")
        axs[0].plot(df["t"], df["v_lin"], label="measured lin")
        axs[0].legend()
        axs[0].set_title("Linear velocity tracking")

        # Error
        axs[1].plot(df["t"], df["e_lin"], label="error lin")
        axs[1].plot(df["t"], df["e_ang"], label="error ang")
        axs[1].legend()
        axs[1].set_title("Error evolution")

        # PWM
        axs[2].plot(df["t"], df["pwm_l"], label="PWM left")
        axs[2].plot(df["t"], df["pwm_r"], label="PWM right")
        axs[2].legend()
        axs[2].set_title("Motor command")

        # Encoders
        axs[3].plot(df["t"], df["ticks_l"], label="ticks left")
        axs[3].plot(df["t"], df["ticks_r"], label="ticks right")
        axs[3].legend()
        axs[3].set_title("Encoder ticks")

        plt.xlabel("time (index or timestamp)")
        plt.tight_layout()
        plt.show()

        self._logger.info("[CTRL:RB] Log plots generated successfully")

    def plot_latest_rb_log(self, log_dir: str = "logs") -> None:
        files = glob.glob(os.path.join(log_dir, "*.log"))
        if not files:
            self._logger.warning("[CTRL:RB] No log files found")
            return

        latest = max(files, key=os.path.getmtime)
        self._logger.info(f"[CTRL:RB] Using latest log: {latest}")
        self.plot_rb_logs(latest)
