"""Communication helper adding GPIO control for a Teensy device."""

from __future__ import annotations

from typing import TYPE_CHECKING

from teensy.tools import GPIOManager
from usb_com.python import Com

if TYPE_CHECKING:
    from loggerplusplus import Logger


class GPIOComTeensy(Com):
    """Provide GPIO management for a Teensy microcontroller."""

    def __init__(
        self,
        logger: Logger,
        serial_number: int,
        vid: int,
        pid: int,
        baudrate: int,
        *,
        enable_crc: bool = True,
        enable_dummy: bool = False,
    ) -> None:
        """Initialize GPIO management for the Teensy and its communication settings.

        Args:
            logger (Logger): Logger instance for debugging and event tracking.
            serial_number (int): Serial number of the Teensy device.
            vid (int): Vendor ID of the Teensy device.
            pid (int): Product ID of the Teensy device.
            baudrate (int): Baud rate for serial communication.
            enable_crc (bool, optional):
                Enables cyclic redundancy check. Defaults to ``True``.
            enable_dummy (bool, optional):
                Enables dummy mode for testing. Defaults to ``False``.
        """
        # Initialize variables dedicated to Teensy's GPIO management
        # I2C pins
        self.scl: int = 19  # Serial Clock Line (SCL) assigned to pin 19
        self.sda: int = 18  # Serial Data Line (SDA) assigned to pin 18

        # GPIO attribution manager to handle up to 41 GPIO pins
        self.gpio_manager: GPIOManager = GPIOManager(logger=logger, nb_pin=41)

        # Initialize the parent-Com class
        super().__init__(
            logger,
            serial_number,
            vid,
            pid,
            baudrate,
            enable_crc=enable_crc,
            enable_dummy=enable_dummy,
        )
