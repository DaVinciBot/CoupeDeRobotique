"""Base communication class for interacting with a Teensy over USB."""

from __future__ import annotations

import time

from usb_com.python import Com
from usb_com.python.messages import Messages


class BaseComTeensy(Com):
    """Communication helper tailored for a Teensy microcontroller."""

    def reset(self) -> None:
        """Resets the Teensy device by sending a reset command."""
        self.send_bytes(data=Messages.RESET_TEENSY.to_bytes())

    def reset_and_reconnect(self, *, delay_s: float = 0.8) -> bool:
        """Reset the Teensy and attempt to reconnect.

        Args:
            delay_s (float):
                Time to wait after resetting before trying to reconnect.
                Defaults to 0.8.

        Returns:
            bool: True if reconnection was successful, False otherwise.
        """
        self.reset()
        time.sleep(delay_s)
        return self.reconnect()
