"""Dummy rolling basis control for tests without hardware."""

from __future__ import annotations

import atexit
import math
import signal
import threading
import time
from pathlib import Path
from typing import TYPE_CHECKING, Any, overload, override

from loggerplusplus import log

from a_config_loader import CONFIG
from controllers.rolling_basis.debug_recorder import RollingBasisDebugRecorder
from controllers.rolling_basis.pids import PID, PidID
from geometry import OrientedPoint
from teensy import BaseComTeensy

if TYPE_CHECKING:
    from loggerplusplus import Logger

    from navigation.trajectory_planner import TrajectoryPlanCommand


class RollingBasisDummy(BaseComTeensy):
    """Simulated rolling basis used without hardware."""

    def __init__(
        self,
        logger: Logger,
        serial_number: int = CONFIG.ROLLING_BASIS_TEENSY_SER,
        vid: int = CONFIG.TEENSY_VID,
        pid: int = CONFIG.TEENSY_PID,
        baudrate: int = CONFIG.TEENSY_BAUDRATE,
        *,
        enable_crc: bool = CONFIG.TEENSY_CRC,
        enable_realtime_simulation: bool = True,
        realtime_period: float = 0.02,
        enable_debug_report: bool = False,
    ) -> None:
        """Initialize the dummy rolling basis."""
        self._debug_report_exported = False
        self._previous_signal_handlers: dict[int, object] = {}

        super().__init__(
            logger,
            serial_number,
            vid,
            pid,
            baudrate,
            enable_crc=enable_crc,
            enable_dummy=True,
        )

        self._debug_recorder = RollingBasisDebugRecorder(
            logger=logger,
            output_dir=Path(CONFIG.LOGGER_PATH) / "pid_debug",
            file_prefix="rolling_basis_dummy",
            enabled=enable_debug_report,
        )
        if enable_debug_report:
            atexit.register(self._export_debug_report_on_exit)
            self._install_signal_handlers()

        self.odometrie: OrientedPoint = OrientedPoint((0.0, 0.0), 0.0)
        self.target_position: OrientedPoint = OrientedPoint((0.0, 0.0), 0.0)
        self.linear_speed: float = 0.0
        self.angular_speed: float = 0.0
        self.left_wheel_position_cm: float = 0.0
        self.right_wheel_position_cm: float = 0.0
        self.left_wheel_target_cm: float = 0.0
        self.right_wheel_target_cm: float = 0.0

        self.linear_position_pid: PID = PID(0.0, 0.0, 0.0)
        self.angular_position_pid: PID = PID(0.0, 0.0, 0.0)
        self.left_wheel_position_pid: PID = PID(0.0, 0.0, 0.0)
        self.right_wheel_position_pid: PID = PID(0.0, 0.0, 0.0)

        self._enable_realtime_simulation = enable_realtime_simulation
        self._realtime_period = realtime_period
        self._stop_realtime = threading.Event()
        self._lock = threading.Lock()
        self._last_update_time = time.time()
        self._realtime_thread: threading.Thread | None = None
        if self._enable_realtime_simulation:
            self._realtime_thread = threading.Thread(
                target=self._realtime_loop,
                name="RollingBasisDummyRealtime",
                daemon=True,
            )
            self._realtime_thread.start()

    # region ====== Message Sending Methods ======

    @log(param_logger="RollingBasis")
    def set_trajectory_command(self, cmd: TrajectoryPlanCommand) -> None:
        """Apply a trajectory command to the simulated robot."""
        self.set_target_position(
            cmd.position,
            linear_speed=cmd.linear_speed,
            angular_speed=cmd.angular_speed,
        )

    def set_target_position(
        self,
        position: OrientedPoint,
        *,
        linear_speed: float = 0.0,
        angular_speed: float = 0.0,
    ) -> None:
        """Set the target position and simulated motion command."""
        now = time.time()
        with self._lock:
            dt = now - self._last_update_time
            if dt > 0.0:
                self._simulate_step_unlocked(dt)

            self.target_position = position
            self.linear_speed = linear_speed
            self.angular_speed = angular_speed
            self._last_update_time = now

            self._debug_recorder.set_target(
                linear_speed=linear_speed,
                angular_speed=angular_speed,
                target_position=position,
            )

        self._logger.debug(
            f"[CTRL:RB:Dummy] Set target position: {position} "
            f"cmd=({linear_speed}, {angular_speed})",
        )
        self._debug_recorder.add_sample(event="target_position")

    def simulate_step(self, dt: float) -> None:
        """Integrate the stored trajectory command over a timestep."""
        if dt <= 0.0:
            return

        with self._lock:
            self._simulate_step_unlocked(dt)
            self._last_update_time = time.time()

    def _simulate_step_unlocked(self, dt: float) -> None:
        """Integrate motion assuming the caller already holds the lock."""
        if dt <= 0.0:
            return

        if self.odometrie.theta is None:
            msg = "Cannot simulate motion with undefined theta."
            raise ValueError(msg)

        delta_distance = self.linear_speed * dt
        delta_theta = self.angular_speed * dt

        heading_mid = self.odometrie.theta + (delta_theta / 2.0)
        new_x = self.odometrie.x + math.cos(heading_mid) * delta_distance
        new_y = self.odometrie.y + math.sin(heading_mid) * delta_distance
        new_theta = self._normalize_angle(self.odometrie.theta + delta_theta)
        left_wheel_delta_cm = delta_distance - (delta_theta * 15.45)
        right_wheel_delta_cm = delta_distance + (delta_theta * 15.45)

        self.odometrie = OrientedPoint((new_x, new_y), new_theta)
        assert self.odometrie.theta is not None
        self.left_wheel_position_cm += left_wheel_delta_cm
        self.right_wheel_position_cm += right_wheel_delta_cm
        self.left_wheel_target_cm = self.left_wheel_position_cm
        self.right_wheel_target_cm = self.right_wheel_position_cm
        if self._debug_recorder.enabled:
            self._debug_recorder.set_odometry(
                self.odometrie,
                measured_linear_speed=self.linear_speed,
                measured_angular_speed=self.angular_speed,
            )
            dx = self.target_position.x - self.odometrie.x
            dy = self.target_position.y - self.odometrie.y
            linear_error = (
                math.cos(self.odometrie.theta) * dx
                + math.sin(self.odometrie.theta) * dy
            )
            target_theta = self.target_position.theta
            if target_theta is None:
                target_theta = self.odometrie.theta
            angular_error = self._normalize_angle(target_theta - self.odometrie.theta)
            self._debug_recorder.set_pid_telemetry(
                target_position=self.target_position,
                linear_error=linear_error,
                angular_error=angular_error,
                linear_output=delta_distance,
                angular_output=delta_theta,
                left_wheel_target_cm=self.left_wheel_target_cm,
                right_wheel_target_cm=self.right_wheel_target_cm,
                left_wheel_position_cm=self.left_wheel_position_cm,
                right_wheel_position_cm=self.right_wheel_position_cm,
                left_wheel_error_cm=0.0,
                right_wheel_error_cm=0.0,
                left_pwm=0,
                right_pwm=0,
                left_ticks=0,
                right_ticks=0,
                left_delta_ticks=0,
                right_delta_ticks=0,
            )
            self._debug_recorder.add_sample(event="simulation_step")

    def _realtime_loop(self) -> None:
        """Background loop that keeps odometry up-to-date in realtime."""
        while not self._stop_realtime.wait(self._realtime_period):
            now = time.time()
            with self._lock:
                dt = now - self._last_update_time
                if dt > 0.0:
                    self._simulate_step_unlocked(dt)
                    self._last_update_time = now

    @log("RollingBasis")
    def set_odometrie(self, odometrie: OrientedPoint) -> None:
        """Set rolling basis odometry."""
        if odometrie.theta is None:
            msg = (
                f"Odometrie theta must be defined, got None at "
                f"position ({odometrie.x}, {odometrie.y})"
            )
            raise ValueError(msg)

        with self._lock:
            self.odometrie = odometrie
            self.target_position = odometrie
            self.linear_speed = 0.0
            self.angular_speed = 0.0
            self.left_wheel_position_cm = 0.0
            self.right_wheel_position_cm = 0.0
            self.left_wheel_target_cm = 0.0
            self.right_wheel_target_cm = 0.0
            self._last_update_time = time.time()
        self._logger.info(f"[CTRL:RB:Dummy] Set odometry: {odometrie}")
        self._debug_recorder.set_odometry(odometrie)
        self._debug_recorder.add_sample(event="set_odometry", force=True)

    def _send_pid(self, pid_id: int, pid: PID) -> None:
        """Record PID configuration data in dummy mode."""
        self._logger.debug(f"[CTRL:RB:Dummy] Set PID {pid_id}: {pid}")
        self._debug_recorder.add_sample(event=f"set_pid_{pid_id}", force=True)

    def export_debug_report(self, *, reason: str = "manual") -> None:
        """Export static debug files (CSV + metadata)."""
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

    def get_debug_snapshot(self) -> dict[str, Any]:
        """Return latest debug telemetry snapshot."""
        return self._debug_recorder.get_live_snapshot()

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
        """Export debug artifacts and then terminate the process."""
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

    @staticmethod
    def _normalize_angle(angle: float) -> float:
        """Normalize angle to [-pi, pi)."""
        angle = math.fmod(angle + math.pi, 2.0 * math.pi)
        if angle < 0.0:
            angle += 2.0 * math.pi
        return angle - math.pi

    def stop_realtime_simulation(self) -> None:
        """Stop the realtime simulation thread if running."""
        if not self._enable_realtime_simulation or self._realtime_thread is None:
            self.export_debug_report(reason="stop_realtime")
            return
        now = time.time()
        with self._lock:
            dt = now - self._last_update_time
            if dt > 0.0:
                self._simulate_step_unlocked(dt)
                self._last_update_time = now
        self._stop_realtime.set()
        self._realtime_thread.join(timeout=1.0)
        self.export_debug_report(reason="stop_realtime")

    def __del__(self) -> None:
        """Ensure background thread is stopped when the object is deleted."""
        self.stop_realtime_simulation()
        self.export_debug_report(reason="object_deleted")

    # endregion

    # region ====== PID Configuration Methods ======

    @staticmethod
    def _load_pid(
        *args: float | dict[str, float],
        **kwargs: float,
    ) -> PID:
        """Load PID values from positional, dict, or keyword arguments."""
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
        """Configure the PID values for linear position control."""
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
        """Configure the PID values for angular position control."""
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
        """Configure all rolling basis position PID controllers."""
        self.set_linear_position_pid(**linear_position_pid)
        self.set_angular_position_pid(**angular_position_pid)
        self.set_left_wheel_position_pid(**left_wheel_position_pid)
        self.set_right_wheel_position_pid(**right_wheel_position_pid)

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
        """Check equality between two RollingBasisDummy instances."""
        if not isinstance(other, RollingBasisDummy):
            return NotImplemented
        return (
            self.odometrie == other.odometrie
            and self.linear_speed == other.linear_speed
            and self.angular_speed == other.angular_speed
            and self.linear_position_pid == other.linear_position_pid
            and self.angular_position_pid == other.angular_position_pid
            and self.left_wheel_position_pid == other.left_wheel_position_pid
            and self.right_wheel_position_pid == other.right_wheel_position_pid
        )

    @override
    def __ne__(self, other: object) -> bool:
        """Check inequality between two RollingBasisDummy instances."""
        return not self.__eq__(other)

    @override
    def __hash__(self) -> int:
        """Return a hash based on object identity."""
        return object.__hash__(self)

    # endregion
