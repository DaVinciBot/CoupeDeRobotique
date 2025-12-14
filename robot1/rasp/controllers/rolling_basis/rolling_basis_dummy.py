"""Dummy rolling basis control for tests without hardware."""

from __future__ import annotations

import math
import threading
import time
from typing import TYPE_CHECKING, overload, override

from loggerplusplus import log

from a_config_loader import CONFIG
from controllers.rolling_basis.pids import PID, PidID
from geometry import OrientedPoint
from teensy import BaseComTeensy

if TYPE_CHECKING:
    from loggerplusplus import Logger

    from navigation.trajectory_planner import TrajectoryPlanCommand


class RollingBasisDummy(BaseComTeensy):
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
        enable_realtime_simulation: bool = True,
        realtime_period: float = 0.02,
    ) -> None:
        """Initializes the RollingBasisDummy class.

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
            enable_realtime_simulation (bool, optional):
                If ``True``, odometry is integrated continuously in a background loop.
                Defaults to ``True``.
            realtime_period (float, optional):
                Sleep duration between realtime integration steps. Defaults to 0.02s.
        """
        # Initialize the parent-BaseComTeensy class
        super().__init__(
            logger,
            serial_number,
            vid,
            pid,
            baudrate,
            enable_crc=enable_crc,
            enable_dummy=True,
        )

        # Robot state
        self.odometrie: OrientedPoint = OrientedPoint((0.0, 0.0), 0.0)
        self.target_position: OrientedPoint = OrientedPoint((0.0, 0.0), 0.0)
        self.linear_speed: float = 0.0
        self.angular_speed: float = 0.0

        # PID controllers
        self.linear_velocity_pid: PID = PID(0.0, 0.0, 0.0)
        self.angular_velocity_pid: PID = PID(0.0, 0.0, 0.0)

        # Realtime simulation bookkeeping
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
    def set_target_velocity(self, cmd: TrajectoryPlanCommand) -> None:
        """Sends a message to set the target speed and position of the rolling basis.

        Args:
            cmd (TrajectoryPlanCommand): The command containing target velocities.
        """
        now = time.time()
        with self._lock:
            dt = now - self._last_update_time
            if dt > 0.0:
                self._simulate_step_unlocked(dt)

            self.linear_speed, self.angular_speed = (
                cmd.linear_speed,
                cmd.angular_speed,
            )
            self.target_position = cmd.position
            self._last_update_time = now

        self._logger.debug(f"[CTRL:RB:Dummy] Set target velocity: {cmd}")

    def simulate_step(self, dt: float) -> None:
        """Integrate the stored target speeds over a timestep to update odometry.

        Mirrors the kinematics used in the Teensy C++ code: apply the linear and
        angular speeds during ``dt`` to compute the new pose.

        Args:
            dt (float): Elapsed time in seconds. Non-positive values are ignored.

        Raises:
            ValueError: If odometrie.theta is None.
        """
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

        self.odometrie = OrientedPoint((new_x, new_y), new_theta)

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

        with self._lock:
            self.odometrie = odometrie
            self._last_update_time = time.time()
        self._logger.info(f"[CTRL:RB:Dummy] Set odometry: {odometrie}")

    def _send_pid(self, pid_id: int, pid: PID) -> None:
        """Internal method to send PID configuration data to the Teensy.

        Args:
            pid_id (int): The identifier for the PID controller.
            pid (PID): The PID controller parameters.
        """
        self._logger.debug(f"[CTRL:RB:Dummy] Set PID {pid_id}: {pid}")

    @staticmethod
    def _normalize_angle(angle: float) -> float:
        """Normalize angle to [-pi, pi) similar to the C++ implementation.

        Args:
            angle (float): The angle in radians to normalize.

        Returns:
            float: The normalized angle in radians.
        """
        angle = math.fmod(angle + math.pi, 2.0 * math.pi)
        if angle < 0.0:
            angle += 2.0 * math.pi
        return angle - math.pi

    def stop_realtime_simulation(self) -> None:
        """Stop the realtime simulation thread if running."""
        if not self._enable_realtime_simulation or self._realtime_thread is None:
            return
        self._stop_realtime.set()
        self._realtime_thread.join(timeout=1.0)

    def __del__(self) -> None:
        """Ensure background thread is stopped when the object is deleted."""
        self.stop_realtime_simulation()

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
        """Configure the PID values for linear velocity control.

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
        self.set_angular_velocity_pid(**angular_velocity_pid)

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
        if not isinstance(other, RollingBasisDummy):
            return NotImplemented
        return (
            self.odometrie == other.odometrie
            and self.linear_speed == other.linear_speed
            and self.angular_speed == other.angular_speed
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
