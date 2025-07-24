from gpiozero import LED, Button
from gpiozero.pins.lgpio import LGPIOFactory


class PIN:
    """Represents a GPIO pin.

    Args:
        pin (int): The pin number.
    """

    def __init__(self, pin: int) -> None:
        self.pin = pin
        self.mode = None
        self.reverse_state = False
        self.device = None

    def setup(self, mode: str, reverse_state: bool = False) -> None:
        """Set up the pin.

        Args:
            mode (str): The pin mode (output/input/input_pullup/input_pulldown).
            reverse_state (bool, optional): Whether to reverse the state of the pin. Defaults to `False`.
        """
        mode = mode.lower()
        self.mode = mode
        self.reverse_state = reverse_state

        if mode == "output":
            self.device = LED(self.pin, pin_factory=LGPIOFactory())
            self.device.off()
        elif mode == "input":
            self.device = Button(self.pin, pin_factory=LGPIOFactory())
        elif mode == "input_pullup":
            self.device = Button(
                self.pin,
                pull_up=True,
                pin_factory=LGPIOFactory(),
            )
        elif mode == "input_pulldown":
            self.device = Button(
                self.pin,
                pull_up=False,
                pin_factory=LGPIOFactory(),
            )

    def digital_write(self, state: bool) -> None:
        """Write a digital state to the pin.

        Args:
            state (bool): The state to write (`True`/`False`).
        """
        self.device.value = self.__correct_state(state)

    def digital_read(self) -> bool:
        """Read the digital state of the pin.

        Returns:
            bool: The digital state of the pin (`True`/`False`).

        """
        return (
            self.__correct_state(self.device.value)
            if self.mode == "output"
            else self.__correct_state(self.device.is_pressed)
        )

    def safe_digital_read(self, n: int = 5) -> bool:
        """Read multiple times the digital state of the pin and take a majority vote.

        Args:
            n (int, optional): Number of samples to read. Defaults to 5.

        Returns:
            bool: The averaged digital state. `True` if the majority of samples are `True`, otherwise `False`.

        """
        return sum([self.digital_read() for _ in range(n)]) / n >= 0.5

    def __correct_state(self, state: bool) -> bool:
        """Correct the state of the pin based on the reverse_state attribute.

        Args:
            state (bool): The state to correct.

        Returns:
            bool: The corrected state.

        """
        return not state if self.reverse_state else state
