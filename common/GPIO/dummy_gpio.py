class DummyDevice:
    def __init__(self) -> None:
        self.value = False
        self.is_pressed = False

    def on(self) -> None:
        self.value = True

    def off(self) -> None:
        self.value = False


class PIN:
    """Dummy version of a GPIO pin for simulation or testing."""

    def __init__(self, pin: int) -> None:
        """Initialize the dummy GPIO pin.

        Args:
            pin (int): Identifier of the pin.
        """
        self.pin = pin
        self.mode = None
        self.reverse_state = False
        self.device = None

    def setup(self, mode, reverse_state=False) -> None:
        self.mode = mode.lower()
        self.reverse_state = reverse_state
        self.device = DummyDevice()

    def digital_write(self, state: bool) -> None:
        corrected = self.__correct_state(state)
        self.device.value = corrected

    def digital_read(self) -> bool:
        if self.mode == "output":
            return self.__correct_state(self.device.value)
        return self.__correct_state(self.device.is_pressed)

    def safe_digital_read(self, n=5) -> bool:
        return sum([self.digital_read() for _ in range(n)]) / n >= 0.5

    def __correct_state(self, state: bool) -> bool:
        return not state if self.reverse_state else state
