"""Base communication class for interacting with a Teensy over USB."""

from __future__ import annotations

from usb_com.python import Com
from usb_com.python.messages import Messages


class BaseComTeensy(Com):
    """Communication helper tailored for a Teensy microcontroller."""

    def reset(self) -> None:
        """Resets the Teensy device by sending a reset command."""
        self.send_bytes(data=Messages.RESET_TEENSY.to_bytes())
