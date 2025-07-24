class DummyDevice:
    """Dummy version of a GPIO device for simulation or testing."""

    def __init__(self) -> None:
        """Initialize the dummy GPIO device."""
        self.value = False
        self.is_pressed = False

    def on(self) -> None:
        """Set the device state to on (True)."""
        self.value = True

    def off(self) -> None:
        """Set the device state to off (False)."""
        self.value = False

    def toggle_input(self) -> None:
        """Toggle the input state of the device."""
        self.is_pressed = not self.is_pressed


class PIN:
    """Dummy version of a GPIO pin for simulation or testing."""

    def __init__(self, pin: int) -> None:
        """Initialize the dummy GPIO pin.

        Args:
            pin (int): Identifier of the pin.
        """
        self.pin = pin
        self.mode: str | None = None
        self.reverse_state: bool = False
        self.device: DummyDevice | None = None
        self.count: int = 0

    def setup(self, mode: str, reverse_state: bool = False) -> None:
        """Set up the pin with a mode and optional reverse state.

        Args:
            mode (str): Mode of the pin, e.g., 'input' or 'output'.
            reverse_state (bool, optional): If True, reverses the state of the pin. Defaults to False.
        """
        self.mode = mode.lower()
        self.reverse_state = reverse_state
        self.device = DummyDevice()

    def digital_write(self, state: bool) -> None:
        corrected: bool = self.__correct_state(state)
        self.device.value = corrected

    def digital_read(self) -> bool:
        if self.mode == "output":
            return self.__correct_state(self.device.value)
        return self.__correct_state(self.device.is_pressed)

    def safe_digital_read(self, n: int = 5) -> bool:
        """Read the digital value multiple times and return the majority value.

        Args:
            n (int, optional): Number of reads to perform. Defaults to 5.

        Returns:
            bool: The majority value read from the pin.
        """
        self.count += 1
        if self.count > 1500:
            self.count = 1000
            self.device.toggle_input()
        return sum([self.digital_read() for _ in range(n)]) / n >= 0.5

    def __correct_state(self, state: bool) -> bool:
        return not state if self.reverse_state else state
