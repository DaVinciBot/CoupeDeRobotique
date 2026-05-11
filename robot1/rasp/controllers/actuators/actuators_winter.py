"""Hardware actuator implementation used during demonstrations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from a_config_loader import CONFIG
from controllers.actuators.base.actuators import Actuators

if TYPE_CHECKING:
    from loggerplusplus import Logger


R_ARM_SERVO_PIN = CONFIG.R_ARM_PIN
L_ARM_SERVO_PIN = CONFIG.L_ARM_PIN
CURSOR_SERVO_PIN = CONFIG.CURSOR_PIN


@dataclass
class Servo:
    """Description of a generic servo angle configuration.

    Attributes:
        retract_angle (int): Retract angle for the servo (in degrees).
        max_angle (int): Maximum angle for the servo (in degrees).
    """

    retract_angle: int
    """Default angle for the servo (in degrees)."""

    extend_angle: int
    """Angle to extend the servo (in degrees)."""

    max_angle: int
    """Maximum angle for the servo (in degrees)."""


class ActuatorsWinter(Actuators):
    """Implementation of actuators for the winter mode.

    Inherits from :class:`Actuators` and overrides its methods to provide
    hardware-specific functionality.
    """

    def __init__(
        self,
        logger: Logger,
        serial_number: int = CONFIG.ACTUATOR_TEENSY_SER,
        vid: int = CONFIG.TEENSY_VID,
        pid: int = CONFIG.TEENSY_PID,
        baudrate: int = CONFIG.TEENSY_BAUDRATE,
        *,
        enable_crc: bool = CONFIG.TEENSY_CRC,
        enable_dummy: bool = CONFIG.ACTUATORS_DUMMY,
    ) -> None:
        """Initialize the ``ActuatorsWinter`` class.

        Args:
            logger (Logger): The logger instance for logging.
            serial_number (int, optional):
                The serial number of the Teensy. Defaults to CONFIG.ACTUATOR_TEENSY_SER.
            vid (int, optional):
                The vendor ID of the Teensy. Defaults to CONFIG.TEENSY_VID.
            pid (int, optional):
                The product ID of the Teensy. Defaults to CONFIG.TEENSY_PID.
            baudrate (int, optional): The baud rate for serial communication.
                Defaults to CONFIG.TEENSY_BAUDRATE.
            enable_crc (bool, optional):
                Whether to enable CRC checks. Defaults to CONFIG.TEENSY_CRC.
            enable_dummy (bool, optional):
                Whether to enable dummy mode. Defaults to CONFIG.ACTUATORS_DUMMY.
        """
        super().__init__(
            logger=logger,
            serial_number=serial_number,
            vid=vid,
            pid=pid,
            baudrate=baudrate,
            enable_crc=enable_crc,
            enable_dummy=enable_dummy,
        )  # Call the parent constructor
        self.folded: bool = True  # Indicates if the actuators are folded
        self.elevator_ticks: int = 0
        self.servos: dict[int, Servo] = {}
        self.pumps: list[int] = CONFIG.ACTUATOR_PUMPS_PINS
        self.pump_driver: str = CONFIG.ACTUATOR_PUMPS_CONFIG.get("driver", "relay")
        self.pump_mosfet_power: int = CONFIG.ACTUATOR_PUMPS_CONFIG.get(
            "mosfet_power",
            255,
        )

        for pin_str, cfg in CONFIG.ACTUATOR_SERVOS_CONFIG.items():
            pin = int(pin_str)
            self.servos[pin] = Servo(
                retract_angle=cfg["retract_angle"],
                extend_angle=cfg.get("extend_angle", cfg.get("deploy_angle")),
                max_angle=cfg["max_angle"],
            )

    def _check_pin(self, pin: int) -> bool:
        """Checks if the specified pin is a valid servo pin.

        Args:
            pin (int): The pin number to check.

        Returns:
            bool: ``True`` if the pin is a valid servo pin, ``False`` otherwise.
        """
        if pin not in self.servos:
            self._logger.warning(
                f"[CTRL:ACT] Invalid servo pin {pin}, not configured",
            )
            return False
        return True

    # Public methods
    def extend(self, pin: int) -> None:
        """Extend the servo connected to the specified pin.

        Args:
            pin (int): The pin number of the servo to extend.
        """
        if self._check_pin(pin):
            self.set_servo_angle(pin, self.servos[pin].extend_angle, max_angle=self.servos[pin].max_angle)

    def retract(self, pin: int) -> None:
        """Retract the servo connected to the specified pin.

        Args:
            pin (int): The pin number of the servo to retract.

        """
        if self._check_pin(pin):
            self.set_servo_angle(
                pin,
                self.servos[pin].retract_angle,
                max_angle=self.servos[pin].max_angle,
            )

    def extend_arm(self) -> None:
        """Extend the specified servos to their extend angle.

        This method sets the specified servos to their extend angle, effectively
        extending the servo arm.
        """
        pins = [R_ARM_SERVO_PIN, L_ARM_SERVO_PIN]
        for pin in pins:
            self.extend(pin)

    def set_arm_angles(
        self,
        left_angle: int,
        right_angle: int,
        *,
        max_angle: int | None = None,
    ) -> None:
        """Set both arm servos to explicit debug angles."""
        for pin, angle in (
            (L_ARM_SERVO_PIN, left_angle),
            (R_ARM_SERVO_PIN, right_angle),
        ):
            servo_max_angle = max_angle or self.servos[pin].max_angle
            self.set_servo_angle(pin, angle, max_angle=servo_max_angle)

    def retract_arm(self) -> None:
        """Retract the specified servos to their retract angle.

        This method sets the specified servos to their retract angle, effectively
        retracting the servo arm.
        """
        pins = [R_ARM_SERVO_PIN, L_ARM_SERVO_PIN]
        for pin in pins:
            self.retract(pin)

    def extend_cursor(self) -> None:
        """Deploy the cursor by setting the specified servo to its deployment angle.

        This method sets the specified servo to its deployment angle, effectively
        deploying the cursor.
        """
        self.extend(CURSOR_SERVO_PIN)

    def retract_cursor(self) -> None:
        """Retract the cursor by setting the specified servo to its retract angle.

        This method sets the specified servo to its retract angle, effectively
        retracting the cursor.
        """
        self.retract(CURSOR_SERVO_PIN)

    def extend_all(self) -> None:
        """Extend all servos to their extend angle.

        This method sets all configured servos to their extend angle, effectively
        extending all servo arms.
        """
        for i in self.servos:
            self.extend(i)

    def retract_all(self) -> None:
        """Retract all servos to their retract angle.

        This method sets all configured servos to their retract angle, effectively
        retracting all servo arms.
        """
        for i in self.servos:
            self.retract(i)

    def suck_jenga(
        self,
        pins: int | list[int] | None = None,
        *,
        use_mosfet: bool | None = None,
        power: int | None = None,
    ) -> None:
        """Activate the suction mechanism to pick up Jenga pieces.

        If specific pins are provided, the suction will be activated for those pins.
        If no pins are provided, the suction will be activated for all configured
        pump pins.

        Args:
            pins (int | list[int] | None): The pin(s) to activate for suction. Can be
                a single integer, a list of integers, or None to activate all.
        """
        if pins is not None:
            if isinstance(pins, int):
                pins = [pins]
            for pin in pins:
                self.suck(pin, use_mosfet=use_mosfet, power=power)
        else:
            for pin in self.pumps:
                self.suck(pin, use_mosfet=use_mosfet, power=power)

    def _use_pump_mosfet(self, *, use_mosfet: bool | None = None) -> bool:
        """Return whether the pump should use MOSFET mode."""
        if use_mosfet is not None:
            return use_mosfet
        return self.pump_driver == "mosfet"

    def suck(
        self,
        pin: int,
        *,
        use_mosfet: bool | None = None,
        power: int | None = None,
    ) -> None:
        """Activate one pump pin."""
        if self._use_pump_mosfet(use_mosfet=use_mosfet):
            self.set_pump_mosfet_power(
                pin,
                self.pump_mosfet_power if power is None else power,
            )
        else:
            self.set_pump_pin_state(pin, state=True)

    def release_jenga(
        self,
        pins: int | list[int] | None = None,
        *,
        use_mosfet: bool | None = None,
    ) -> None:
        """Deactivate the suction mechanism to release Jenga pieces.

        If specific pins are provided, the suction will be deactivated for those
        pins. If no pins are provided, the suction will be deactivated for all
        configured pump pins.

        Args:
            pins (int | list[int] | None): The pin(s) to deactivate for suction. Can
                be a single integer, a list of integers, or None to deactivate all.
        """
        if pins is not None:
            if isinstance(pins, int):
                pins = [pins]
            for pin in pins:
                self.release(pin, use_mosfet=use_mosfet)
        else:
            for pin in self.pumps:
                self.release(pin, use_mosfet=use_mosfet)

    def release(self, pin: int, *, use_mosfet: bool | None = None) -> None:
        """Deactivate one pump pin."""
        if self._use_pump_mosfet(use_mosfet=use_mosfet):
            self.set_pump_mosfet_power(pin, 0)
        else:
            self.set_pump_pin_state(pin, state=False)

    def pickup(
        self,
        pins: int | list[int] | None = None,
        *,
        use_mosfet: bool | None = None,
        power: int | None = None,
    ) -> None:
        """Perform the sequence to pick up Jenga pieces using the suction mechanism.
        This method first releases any active suction, then extends the arm, and
        finally activates the suction for the specified pins. If no pins are
        provided, it activates suction for all configured pump pins.

        Args:
            pins (int | list[int] | None): The pin(s) to activate for suction. Can be a
            single integer, a list of integers, or None to activate all.

        Returns:
            None
        """
        self.release_jenga(use_mosfet=use_mosfet)
        self.extend_arm()
        if pins is not None:
            if isinstance(pins, int):
                pins = [pins]
            for pin in pins:
                self.suck(pin, use_mosfet=use_mosfet, power=power)
        else:
            self.suck_jenga(use_mosfet=use_mosfet, power=power)

        self.retract_arm()

    def deposit(
        self,
        pins: int | list[int] | None = None,
        *,
        use_mosfet: bool | None = None,
    ) -> None:
        """Perform the sequence to deposit Jenga pieces using the suction mechanism.
        This method first retracts the arm, then releases any active suction for
        the specified pins. If no pins are provided, it releases suction for all
        configured pump pins.

        Args:
            pins (int | list[int] | None): The pin(s) to deactivate for suction. Can be a
            single integer, a list of integers, or None to deactivate all.

        Returns:
            None
        """
        self.extend_arm()
        self.release_jenga(pins, use_mosfet=use_mosfet)
