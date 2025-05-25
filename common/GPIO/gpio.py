# import RPi.GPIO as GPIO
from gpiozero import LED, Button
from gpiozero.pins.rpigpio import RPiGPIOFactory


class PIN:
    """
    Represents a GPIO pin.

    Args:
        pin (int): The pin number.

    Attributes:
        pin (int): The pin number.
        mode (str): The pin mode (input/output).
        reverse_state (bool): Whether to reverse the state of the pin.
        device : The GPIO device associated with the pin.
    """

    def __init__(self, pin):
        self.pin = pin
        self.mode = None
        self.reverse_state = False
        self.device = None

    def setup(self, mode, reverse_state=False):
        """
        Set up the pin.

        Args:
            mode (str): The pin mode (input/output).
            reverse_state (bool, optional): Whether to reverse the state of the pin. Defaults to False.

        """
        mode = mode.lower()
        self.mode = mode
        self.reverse_state = reverse_state

        if mode == "output":
            self.device = LED(self.pin, pin_factory=RPiGPIOFactory())
            self.device.off()
        elif mode == "input":
            self.device = Button(self.pin, pin_factory=RPiGPIOFactory())
        elif mode == "input_pullup":
            self.device = Button(
                self.pin,
                pull_up=True,
                pin_factory=RPiGPIOFactory(),
            )
        elif mode == "input_pulldown":
            self.device = Button(
                self.pin,
                pull_up=False,
                pin_factory=RPiGPIOFactory(),
            )

    def digital_write(self, state: bool):
        """
        Write a digital state to the pin.

        Args:
            state (bool): The state to write (True/False).

        """
        self.device.value = self.__correct_state(state)

    def digital_read(self) -> bool:
        """
        Read the digital state of the pin.

        Returns:
            bool: The digital state of the pin (True/False).

        """
        return (
            self.__correct_state(self.device.value)
            if self.mode == "output"
            else self.__correct_state(self.device.is_pressed)
        )

    def safe_digital_read(self, n=5) -> bool:
        """
        Read multiple time the digital state of the pin.

        Returns:
            bool: The digital state of the pin (True/False).

        """
        return sum([self.digital_read() for _ in range(n)]) / n >= 0.5

    def __correct_state(self, state: bool) -> bool:
        """
        Correct the state of the pin based on the reverse_state attribute.

        Args:
            state (bool): The state to correct.

        Returns:
            bool: The corrected state.

        """
        return not state if self.reverse_state else state
