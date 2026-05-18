"""GPIO wrapper built upon gpiozero."""

from __future__ import annotations

from gpiozero import LED, Button, Device
from gpiozero.exc import BadPinFactory

MAJORITY_RATIO = 0.5
GPIO_BACKEND_ERROR = (
    "GPIO backend unavailable. Install/enable a Raspberry Pi GPIO backend "
    "or run with access to /dev/gpiomem. On the robot, try running as root "
    "or adding the user to the gpio group, then restart the session."
)


class PIN:
    """Represent a GPIO pin."""

    def __init__(self, pin: int) -> None:
        """Initialize the pin.

        Args:
            pin (int): The pin number.
        """
        self.pin = pin
        self.mode = None
        self.reverse_state = False
        self.device: Device | None = None

    def setup(self, mode: str, *, reverse_state: bool = False) -> None:
        """Set up the pin.

        Args:
            mode (str): The pin mode (output/input/input_pullup/input_pulldown).
            reverse_state (bool, optional):
                Whether to reverse the state of the pin. Defaults to ``False``.

        Raises:
            RuntimeError: If no Raspberry Pi GPIO backend is available.
        """
        mode = mode.lower()
        self.mode = mode
        self.reverse_state = reverse_state

        try:
            if mode == "output":
                self.device = LED(self.pin)
                self.device.off()
            elif mode == "input":
                self.device = Button(self.pin)
            elif mode == "input_pullup":
                self.device = Button(
                    self.pin,
                    pull_up=True,
                )
            elif mode == "input_pulldown":
                self.device = Button(
                    self.pin,
                    pull_up=False,
                )
        except BadPinFactory:
            raise RuntimeError(GPIO_BACKEND_ERROR) from None

    def digital_write(self, *, state: bool) -> None:
        """Write a digital state to the pin.

        Args:
            state (bool): The state to write (``True``/``False``).

        Raises:
            TypeError: If the pin is not set up for output mode.
        """
        if not isinstance(self.device, LED):
            msg = "Pin not set up for output mode."
            raise TypeError(msg)
        self.device.value = self.__correct_state(state=state)

    def digital_read(self) -> bool:
        """Read the digital state of the pin.

        Returns:
            bool: The digital state of the pin (``True``/``False``).

        Raises:
            RuntimeError: If the pin is not set up.
        """
        if self.device is None:
            msg = "Pin not set up. Call setup() first."
            raise RuntimeError(msg)

        return (
            self.__correct_state(state=bool(self.device.value))
            if self.mode == "output"
            else self.__correct_state(state=self.device.is_pressed)  # pyright: ignore[reportAttributeAccessIssue] self.device is Button
        )

    def safe_digital_read(self, n: int = 5) -> bool:
        """Read multiple times the digital state of the pin and take a majority vote.

        Args:
            n (int, optional): Number of samples to read. Defaults to 5.

        Returns:
            bool:
                The averaged digital state.
                ``True`` if the majority of samples are ``True``, otherwise ``False``.
        """
        return sum(self.digital_read() for _ in range(n)) / n >= MAJORITY_RATIO

    def __correct_state(self, *, state: bool) -> bool:
        """Correct the state of the pin based on the reverse_state attribute.

        Args:
            state (bool): The state to correct.

        Returns:
            bool: The corrected state.
        """
        return not state if self.reverse_state else state
