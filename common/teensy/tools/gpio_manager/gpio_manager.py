"""Utility to track and validate Teensy GPIO pin usage."""

from __future__ import annotations

from typing import TYPE_CHECKING, override

from teensy.tools.gpio_manager.actuators_type import ActuatorType

if TYPE_CHECKING:
    from loggerplusplus import Logger


class GPIOManager:
    """Manages GPIO pins and their associated actuator types."""

    def __init__(self, logger: Logger, nb_pin: int) -> None:
        """Initializes the GPIOManager with a logger and the number of available pins.

        Args:
            logger (Logger): Logger instance for logging events.
            nb_pin (int): The maximum number of available GPIO pins.
        """
        self.logger: Logger = logger
        self.nb_pin: int = nb_pin
        self.gpios: dict[int, ActuatorType] = {}

    @override
    def __str__(self) -> str:
        """Return a string representation of the mapped GPIOs.

        Returns:
            str: String representation of the GPIO manager.
        """
        return f"GPIOManager: {self.gpios}"

    def is_declared_gpio(self, pin: int) -> bool:
        """Check if a GPIO pin is already declared.

        Args:
            pin (int): The GPIO pin-number to check.

        Returns:
            bool:
                ``True`` if the pin is declared (currently in use), ``False`` otherwise.
        """
        return pin in self.gpios

    def is_valid_gpio(
        self,
        pin: int,
        type_actuator: ActuatorType = ActuatorType.UNKNOWN,
    ) -> bool:
        """Check if a GPIO pin is valid and matches the expected actuator type.

        Args:
            pin (int): The GPIO pin-number to validate.
            type_actuator (ActuatorType, optional):
                The expected actuator type. Defaults to ActuatorType.UNKNOWN.

        Returns:
            bool:
                ``True`` if the pin is declared and matches the expected actuator type,
                ``False`` otherwise.
        """
        return pin in self.gpios and self.gpios[pin] == type_actuator

    def add_gpio(
        self,
        pin: int,
        type_actuator: ActuatorType = ActuatorType.UNKNOWN,
    ) -> bool:
        """Add a new GPIO pin with a specified actuator type if it is valid.

        Args:
            pin (int): The GPIO pin-number to add.
            type_actuator (ActuatorType, optional):
                The type of actuator associated with the pin.
                Defaults to ActuatorType.UNKNOWN.

        Returns:
            bool: ``True`` if the pin was successfully added, ``False`` otherwise.
        """
        if self.is_declared_gpio(pin) or pin < 0 or pin > self.nb_pin:
            self.logger.warning(f"Failed to add pin {pin}: Invalid or already declared")
            return False

        self.gpios[pin] = type_actuator
        self.logger.info(f"Added pin {pin} with type {type_actuator}")
        return True

    def get_type_gpio(self, pin: int) -> ActuatorType | None:
        """Retrieve the actuator type associated with a GPIO pin.

        Args:
            pin (int): The GPIO pin-number to query.

        Returns:
            ActuatorType | None:
                The actuator type if the pin is declared, None otherwise.
        """
        type_found: ActuatorType | None = self.gpios.get(pin, None)

        if type_found is None:
            self.logger.error(f"Pin {pin} is not used")

        return type_found
