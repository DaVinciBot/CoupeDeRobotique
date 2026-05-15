"""Rolling basis controller interfacing with the Teensy board."""

from __future__ import annotations

import atexit
import signal
import struct
import time
from pathlib import Path
from typing import TYPE_CHECKING, Any, overload, override

from loggerplusplus import LogLevels, log

from a_config_loader import CONFIG
from controllers.rolling_basis.debug_recorder import RollingBasisDebugRecorder
from controllers.rolling_basis.pids import PID, PidID
from geometry import OrientedPoint
from teensy import BaseComTeensy
from usb_com.python import Messages

if TYPE_CHECKING:
    from loggerplusplus import Logger

    from navigation.trajectory_planner import TrajectoryPlanCommand


_LEGACY_ROLLING_BASIS_STATE = struct.Struct("<ddd")
_EXTENDED_ROLLING_BASIS_STATE = struct.Struct("<" + "d" * 16 + "hhiiii")
_EXTENDED_ROLLING_BASIS_FIELDS = (
    "x",
    "y",
    "theta",
    "target_x",
    "target_y",
    "target_theta",
    "linear_error",
    "angular_error",
    "linear_output",
    "angular_output",
    "left_wheel_target_cm",
    "right_wheel_target_cm",
    "left_wheel_position_cm",
    "right_wheel_position_cm",
    "left_wheel_error_cm",
    "right_wheel_error_cm",
    "left_pwm",
    "right_pwm",
    "left_ticks",
    "right_ticks",
    "left_delta_ticks",
    "right_delta_ticks",
)


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
        self.flag = True
        self._debug_report_exported = False
        self._previous_signal_handlers: dict[int, object] = {}

        super().__init__(
            logger,
            serial_number,
            vid,
            pid,
            baudrate,
            enable_crc=enable_crc,
            enable_dummy=enable_dummy,
        )

        self._debug_recorder = RollingBasisDebugRecorder(
            logger=logger,
            output_dir=Path(CONFIG.LOGGER_PATH) / "pid_debug",
            file_prefix="rolling_basis",
            enabled=True,
        )
        atexit.register(self._export_debug_report_on_exit)
        self._install_signal_handlers()

        self.odometrie: OrientedPoint = OrientedPoint((0.0, 0.0), 0.0)

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

        time.sleep(0.01)
        self.reset_teensy_and_reinit()

    # region ====== Message Receiving Handlers ======

    def rcv_print(self, msg: bytes) -> None:
        """Handle PRINT messages from the Teensy.

        Args:
            msg (bytes): The received message bytes.
        """
        text = msg.decode("ascii", errors="ignore")
        # self._logger.info(f"[CTRL:RB:Teensy] {text}")

    def rcv_rolling_basis_state(self, msg: bytes) -> None:
        """Handle rolling basis odometry update messages from the Teensy.

        The message contains:
        - float x: X-coordinate of the position (4 bytes).
        - float y: Y-coordinate of the position (4 bytes).
        - float theta: Orientation (4 bytes).
        - float current_linear_speed: Current linear speed (4 bytes).
        - float current_angular_speed: Current angular speed (4 bytes).
        - float target_x: Target X-coordinate (4 bytes).
        - float target_y: Target Y-coordinate (4 bytes).
        - float target_theta: Target orientation (4 bytes).
        - float linear_error: Linear position error (4 bytes).
        - float angular_error: Angular position error (4 bytes).
        - float linear_output: Linear output from the PID controller (4 bytes).
        - float angular_output: Angular output from the PID controller (4 bytes).
        - float left_wheel_target_cm: Target position for the left wheel in cm (4 bytes).
        - float right_wheel_target_cm: Target position for the right wheel in cm (4
            bytes).
        - float left_wheel_position_cm: Current position of the left wheel in cm (4 bytes).
        - float right_wheel_position_cm: Current position of the right wheel in cm (4 bytes).
        - float left_wheel_error_cm: Position error for the left wheel in cm (4 bytes).
        - float right_wheel_error_cm: Position error for the right wheel in cm (4 bytes).
        - int16 left_pwm: Current PWM value for the left motor (2 bytes).
        - int16 right_pwm: Current PWM value for the right motor (2 bytes).
        - int32 left_ticks: Current encoder ticks for the left wheel (4 bytes).
        - int32 right_ticks: Current encoder ticks for the right wheel (4 bytes).
        - int32 left_delta_ticks: Change in encoder ticks for the left wheel since the last update (4 bytes).
        - int32 right_delta_ticks: Change in encoder ticks for the right wheel since the last update (4 bytes).

        Args:
            msg (bytes): The received message bytes.
        """
        if len(msg) < _LEGACY_ROLLING_BASIS_STATE.size:
            self._logger.warning(
                f"[CTRL:RB:Teensy] Invalid rolling basis state size: {len(msg)}",
            )
            return

        x, y, theta = _LEGACY_ROLLING_BASIS_STATE.unpack_from(msg)
        self.odometrie = OrientedPoint(
            (x, y),
            theta,
        )
        self._debug_recorder.set_odometry(self.odometrie)

        if len(msg) >= _EXTENDED_ROLLING_BASIS_STATE.size:
            telemetry = dict(
                zip(
                    _EXTENDED_ROLLING_BASIS_FIELDS,
                    _EXTENDED_ROLLING_BASIS_STATE.unpack_from(msg),
                    strict=True,
                ),
            )
            self._debug_recorder.set_pid_telemetry(
                target_position=OrientedPoint(
                    (telemetry["target_x"], telemetry["target_y"]),
                    telemetry["target_theta"],
                ),
                linear_error=telemetry["linear_error"],
                angular_error=telemetry["angular_error"],
                linear_output=telemetry["linear_output"],
                angular_output=telemetry["angular_output"],
                left_wheel_target_cm=telemetry["left_wheel_target_cm"],
                right_wheel_target_cm=telemetry["right_wheel_target_cm"],
                left_wheel_position_cm=telemetry["left_wheel_position_cm"],
                right_wheel_position_cm=telemetry["right_wheel_position_cm"],
                left_wheel_error_cm=telemetry["left_wheel_error_cm"],
                right_wheel_error_cm=telemetry["right_wheel_error_cm"],
                left_pwm=int(telemetry["left_pwm"]),
                right_pwm=int(telemetry["right_pwm"]),
                left_ticks=int(telemetry["left_ticks"]),
                right_ticks=int(telemetry["right_ticks"]),
                left_delta_ticks=int(telemetry["left_delta_ticks"]),
                right_delta_ticks=int(telemetry["right_delta_ticks"]),
            )

        self._debug_recorder.add_sample(event="odometry_update")

    def rcv_unknown_msg(self, msg: bytes) -> None:
        """Handle unknown messages from the Teensy.

        Logs a warning indicating that the message type is not recognized.

        Args:
            msg (bytes): The received message bytes.
        """
        self._logger.warning(f"[CTRL:RB:Teensy] Unknown message type: {msg.hex()}")

    # endregion

    # region ====== Message Sending Methods ======

    def reset_teensy_and_reinit(self, *, delay_s: float = 0.8) -> None:
        """Reset the Teensy and reinitialize rolling basis state.

        Args:
            delay_s (float, optional):
                Time to wait after resetting before trying to reconnect.
                Defaults to 0.8.
        """
        self._logger.info("[CTRL:RB] Sending RESET_TEENSY")
        self.reset()
        time.sleep(delay_s)
        if not self.reconnect():
            return
        self.set_odometrie(OrientedPoint((0.0, 0.0), 0.0))
        self.set_target_position(OrientedPoint((0.0, 0.0), 0.0))

    def set_trajectory_command(self, cmd: TrajectoryPlanCommand) -> None:
        """Send the target position from a trajectory command.

        Args:
            cmd (TrajectoryPlanCommand):
                The trajectory command containing the target position
                and motion parameters.
        """
        self._logger.info(f"[CTRL:RB] Setting target position: {cmd.position}")
        self.set_target_position(cmd.position)

    def set_target_position(self, position: OrientedPoint) -> None:
        """Sends a message to set the target speed and position of the rolling basis.

        Args:
            position (OrientedPoint): Target position and orientation.
        """
        msg = (
            Messages.SET_TARGET_POSITION.to_bytes()
            + struct.pack("<d", position.x)
            + struct.pack("<d", position.y)
            + struct.pack("<d", position.theta)
        )
        self.send_bytes(msg)
        self._debug_recorder.set_target(
            linear_speed=0.0,
            angular_speed=0.0,
            target_position=position,
        )
        self._debug_recorder.add_sample(event="target_position")

    def set_motors_pwm(
        self,
        *,
        left_pwm: int,
        right_pwm: int,
        duration_ms: int,
    ) -> None:
        """Temporarily command raw motor PWM on the rolling basis.

        Args:
            left_pwm (int): PWM value for the left motor (-255 to 255).
            right_pwm (int): PWM value for the right motor (-255 to 255).
            duration_ms (int): Duration to apply the PWM values in milliseconds.
        """
        safe_duration_ms = max(0, min(int(duration_ms), 5000))
        safe_left_pwm = max(-240, min(int(left_pwm), 240))
        safe_right_pwm = max(-240, min(int(right_pwm), 240))
        msg = Messages.SET_MOTORS_PWM.to_bytes() + struct.pack(
            "<hhI",
            safe_left_pwm,
            safe_right_pwm,
            safe_duration_ms,
        )
        self.send_bytes(msg)
        self._debug_recorder.add_sample(event="set_motors_pwm", force=True)

    @log(param_logger="RollingBasis", log_level=LogLevels.INFO)
    def set_odometrie(self, odometrie: OrientedPoint) -> None:
        """Send a command to set rolling basis odometry.

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
        self._debug_recorder.set_odometry(odometrie)
        self._debug_recorder.add_sample(event="set_odometry", force=True)

    @log(param_logger="RollingBasis", log_level=LogLevels.INFO)
    def _send_pid(self, pid_id: int, pid: PID) -> None:
        """Internal method to send PID configuration data to the Teensy.

        Args:
            pid_id (int): The identifier for the PID controller.
            pid (PID): The PID controller parameters.
        """
        msg = Messages.SET_PID.to_bytes() + pid_id.to_bytes() + pid.to_bytes()
        self.send_bytes(msg)
        self._debug_recorder.add_sample(event=f"set_pid_{pid_id}", force=True)

    def get_debug_snapshot(self) -> dict[str, Any]:
        """Return latest debug telemetry snapshot.

        Returns:
            dict[str, Any]: A dictionary containing the latest debug telemetry data.
        """
        return self._debug_recorder.get_live_snapshot()

    def export_debug_report(self, *, reason: str = "manual") -> None:
        """Export static debug files (CSV + metadata).

        Args:
            reason (str, optional):
                Reason for exporting the report, used for logging. Defaults to "manual".
        """
        if self._debug_report_exported:
            return

        artifacts = self._debug_recorder.export_report(reason=reason)
        if artifacts is None:
            return

        self._debug_report_exported = True
        self._logger.info(f"[CTRL:RB:Debug] CSV exported: {artifacts['csv']}")
        self._logger.info(
            f"[CTRL:RB:Debug] Metadata exported: {artifacts['metadata']}",
        )

    def _export_debug_report_on_exit(self) -> None:
        """Best effort debug export when process exits."""
        self.export_debug_report(reason="process_exit")

    def _install_signal_handlers(self) -> None:
        """Install signal handlers to export debug artifacts on termination."""
        for signum in (signal.SIGTERM, signal.SIGINT):
            try:
                previous = signal.getsignal(signum)
                signal.signal(signum, self._handle_termination_signal)
            except (OSError, ValueError):
                continue
            self._previous_signal_handlers[signum] = previous

    def _handle_termination_signal(self, signum: int, _frame: object) -> None:
        """Export debug artifacts and then terminate the process.

        Args:
            signum (int): The signal number received.
            _frame (object): The current stack frame (unused).

        Raises:
            SystemExit:
                After handling the signal and exporting debug data,
                the process will exit.
        """
        try:
            signal_name = signal.Signals(signum).name.lower()
        except ValueError:
            signal_name = str(signum)

        self.export_debug_report(reason=f"signal_{signal_name}")

        previous = self._previous_signal_handlers.get(signum)
        if callable(previous):
            previous(signum, _frame)
            return
        if previous == signal.SIG_IGN:
            return
        raise SystemExit(0)

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
            *args (float | dict[str, float]): Either three floats (kp, ki, kd) or
                a single dictionary with keys 'kp', 'ki', 'kd'.
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
        """Configure the PID values for left wheel position control.

        Overloads:
            - set_left_wheel_position_pid(float, float, float) → None
            - set_left_wheel_position_pid(dict[str, float]) → None
            - set_left_wheel_position_pid(kp=float, ki=float, kd=float) → None

        Args:
            *args (float | dict[str, float]): Either three floats (kp, ki, kd) or a
                single dictionary with keys 'kp', 'ki', 'kd'.
            **kwargs (float): Keyword arguments mapping PID fields to values.
        """
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
        """Configure the PID values for right wheel position control.

        Overloads:
            - set_right_wheel_position_pid(float, float, float) → None
            - set_right_wheel_position_pid(dict[str, float]) → None
            - set_right_wheel_position_pid(kp=float, ki=float, kd=float) → None

        Args:
            *args (float | dict[str, float]): Either three floats (kp, ki, kd) or a
                single dictionary with keys 'kp', 'ki', 'kd'.
            **kwargs (float): Keyword arguments mapping PID fields to values.
        """
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
        """Configure all rolling basis position PID controllers.

        Args:
            linear_position_pid (dict[str, float]):
                PID parameters for linear position control.
            angular_position_pid (dict[str, float]):
                PID parameters for angular position control.
            left_wheel_position_pid (dict[str, float]):
                PID parameters for left wheel position control.
            right_wheel_position_pid (dict[str, float]):
                PID parameters for right wheel position control.
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
            and self.linear_position_pid == other.linear_position_pid
            and self.angular_position_pid == other.angular_position_pid
            and self.left_wheel_position_pid == other.left_wheel_position_pid
            and self.right_wheel_position_pid == other.right_wheel_position_pid
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
