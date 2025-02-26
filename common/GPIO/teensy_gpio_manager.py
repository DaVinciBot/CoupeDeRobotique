from enum import Enum

# from logger import Logger, LogLevels


class TeensyGpioManager:

    class TypeActuator(Enum):
        UNKNOWN = 0
        SERVO = 1
        STEPPER = 2
        LCD = 3

    def __init__(self, nb_pin: int, logger):
        self.logger = logger
        self.nb_pin = nb_pin
        self.gpios = {}

    def __str__(self):
        return f"TeensyGpioManager : {self.gpios}"

    def is_declared_gpio(self, pin: int):
        """
        Check if a GPIO pin is already declared.

        Args:
            pin (int): The GPIO pin number to check.

        Returns:
            bool: True if the pin is declared (currently in use), False otherwise.
        """
        return pin in self.gpios

    def is_valid_gpio(
        self, pin: int, type_actuator: TypeActuator = TypeActuator.UNKNOWN
    ):
        if not pin in self.gpios or self.gpios[pin] != type_actuator:
            return False
        return True

    def add_gpio(self, pin: int, type_actuator: TypeActuator = TypeActuator.UNKNOWN):
        if self.is_declared_gpio(pin) or pin < 0 or pin > self.nb_pin:
            return False
        self.gpios[pin] = type_actuator
        return True

    def get_type_gpio(self, pin: int):
        if pin in self.gpios:
            return self.gpios[pin]
        else:
            # self.logger.log(f"Pin {pin} is not used", LogLevels.ERROR)
            return None
