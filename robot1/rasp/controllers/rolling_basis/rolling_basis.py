"""Rolling basis controller interfacing with the Teensy board."""

from __future__ import annotations

import atexit
import signal
import struct
import time
from pathlib import Path
from typing import TYPE_CHECKING, overload, override

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


class RollingBasis(BaseComTeensy):
    """Represents the rolling basis of the robot."""

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
        """Initialize the rolling basis controller."""
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

        self.linear_position_pid: PID = PID(0.0, 0.0, 0.0)
        self.angular_position_pid: PID = PID(0.0, 0.0, 0.0)

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
        """Handle PRINT messages from the Teensy."""
        text = msg.decode("ascii", errors="ignore")
        self._logger.info(f"[CTRL:RB:Teensy] {text}")

    def rcv_rolling_basis_state(self, msg: bytes) -> None:
        """Handle rolling basis odometry update messages from the Teensy."""
        self.odometrie = OrientedPoint(
            (struct.unpack("<d", msg[0:8])[0], struct.unpack("<d", msg[8:16])[0]),
            struct.unpack("<d", msg[16:24])[0],
        )
        self._debug_recorder.set_odometry(self.odometrie)
        self._debug_recorder.add_sample(event="odometry_update")

    def rcv_unknown_msg(self, msg: bytes) -> None:
        """Handle unknown messages from the Teensy."""
        self._logger.warning(f"[CTRL:RB:Teensy] Unknown message type: {msg.hex()}")

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
        self._logger.info(f"[CTRL:RB] Setting target pose: {cmd.position}")
        self.set_target_pose(cmd.position)

    def set_target_pose(self, pose: OrientedPoint) -> None:
        """Send a command to set the target pose."""
        msg = (
            Messages.SET_TARGET_POSE.to_bytes()
            + struct.pack("<d", pose.x)
            + struct.pack("<d", pose.y)
            + struct.pack("<d", pose.theta)
        )
        self.send_bytes(msg)
        self._debug_recorder.set_target(
            linear_speed=0.0,
            angular_speed=0.0,
            target_pose=pose,
        )
        self._debug_recorder.add_sample(event="target_pose")

    @log(param_logger="RollingBasis", log_level=LogLevels.INFO)
    def set_odometrie(self, odometrie: OrientedPoint) -> None:
        """Send a command to set rolling basis odometry."""
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
        """Send PID configuration data to the Teensy."""
        msg = Messages.SET_PID.to_bytes() + pid_id.to_bytes() + pid.to_bytes()
        self.send_bytes(msg)
        self._debug_recorder.add_sample(event=f"set_pid_{pid_id}", force=True)

    def get_debug_snapshot(self) -> dict[str, float | int | str | None]:
        """Return latest debug telemetry snapshot."""
        return self._debug_recorder.get_live_snapshot()

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

    def set_pids(
        self,
        linear_position_pid: dict[str, float],
        angular_position_pid: dict[str, float],
    ) -> None:
        """Configure all rolling basis position PID controllers."""
        self.set_linear_position_pid(**linear_position_pid)
        time.sleep(0.1)
        self.set_angular_position_pid(**angular_position_pid)
        time.sleep(0.1)

    def initialize_pids(self) -> None:
        """Initialize PID controllers from the configuration."""
        try:
            self.set_pids(
                linear_position_pid=CONFIG.ROLLING_BASIS_PIDS_LINEAR_POSITION,
                angular_position_pid=CONFIG.ROLLING_BASIS_PIDS_ANGULAR_POSITION,
            )
        except (ValueError, TypeError) as e:
            self._logger.error(f"[CTRL:RB] Failed to initialize PIDs: {e}")

    # endregion

    # region ====== Built-in methods ======

    @override
    def __eq__(self, other: object) -> bool:
        """Check equality between two RollingBasis instances."""
        if not isinstance(other, RollingBasis):
            return NotImplemented
        return (
            self.odometrie == other.odometrie
            and self.linear_position_pid == other.linear_position_pid
            and self.angular_position_pid == other.angular_position_pid
        )

    @override
    def __ne__(self, other: object) -> bool:
        """Check inequality between two RollingBasis instances."""
        return not self.__eq__(other)

    @override
    def __hash__(self) -> int:
        """Return a hash based on object identity."""
        return object.__hash__(self)

    # endregion
