"""Dummy rolling basis control for tests without hardware."""

from __future__ import annotations

from typing import overload, override

from loggerplusplus import Logger, log

from a_config_loader import CONFIG
from controllers.rolling_basis.pids import PID, PidID
from geometry import OrientedPoint
from teensy import BaseComTeensy


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
        self.linear_speed: float = 0.0
        self.angular_speed: float = 0.0

        # PID controllers
        self.linear_speed_pid: PID = PID(0.0, 0.0, 0.0)
        self.angular_speed_pid: PID = PID(0.0, 0.0, 0.0)
        self.linear_position_pid: PID = PID(0.0, 0.0, 0.0)
        self.angular_position_pid: PID = PID(0.0, 0.0, 0.0)

        # Initialize PID controllers from configuration
        # self._initialize_pids()

    # region ====== Message Sending Methods ======

    @log(param_logger="RollingBasis")
    def set_target_position(
        self,
        target_position: OrientedPoint,
    ) -> None:
        """Sends a message to set the target speed and position of the rolling basis.

        Args:
            target_position (OrientedPoint): Target position and orientation.

        Raises:
            ValueError: If target_position.theta is None.
        """
        if target_position.theta is None:
            msg = (
                f"Target position theta must be defined, got None at "
                f"position ({target_position.x}, {target_position.y})"
            )
            raise ValueError(msg)

        self.odometrie = target_position

        self._logger.debug(f"[DUMMY] Set speed and position: {target_position}")

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

        self.odometrie = odometrie
        self._logger.info(f"[DUMMY] Set odometrie: {odometrie}")

    def _send_pid(self, pid_id: int, pid: PID) -> None:
        """Internal method to send PID configuration data to the Teensy.

        Args:
            pid_id (int): The identifier for the PID controller.
            pid (PID): The PID controller parameters.
        """
        self._logger.debug(f"[DUMMY] Set PID: {pid_id}, {pid}")

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
            self._logger.error(f"Failed to set linear position PID: {e}")

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
            self._logger.error(f"Failed to set angular position PID: {e}")

    def set_pids(
        self,
        linear_position_pid: dict[str, float],
        angular_position_pid: dict[str, float],
    ) -> None:
        """Configure all PID controllers using dictionaries for each.

        Args:
            linear_position_pid (dict[str, float]):
                PID configuration for linear position.
            angular_position_pid (dict[str, float]):
                PID configuration for angular position.
        """
        self.set_linear_position_pid(**linear_position_pid)
        self.set_angular_position_pid(**angular_position_pid)

    def initialize_pids(self) -> None:
        """Initialize PID controllers from the configuration."""
        try:
            self.set_pids(
                linear_position_pid=CONFIG.ROLLING_BASIS_PIDS_LINEAR_POSITION,
                angular_position_pid=CONFIG.ROLLING_BASIS_PIDS_ANGULAR_POSITION,
            )
        except (ValueError, TypeError) as e:
            self._logger.error(f"Failed to initialize PIDs: {e}")

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
            and self.linear_speed_pid == other.linear_speed_pid
            and self.angular_speed_pid == other.angular_speed_pid
            and self.linear_position_pid == other.linear_position_pid
            and self.angular_position_pid == other.angular_position_pid
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
