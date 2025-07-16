# ====== Code Summary ======
# This module defines the GPIOComTeensy class, which extends the Com class to provide
# GPIO management functionality specifically for the Teensy microcontroller. It initializes
# I2C pins and integrates a GPIO manager to handle up to 41 GPIO pins.

from loggerplusplus import Logger

from teensy.tools import GPIOManager
from usb_com.python import Com


class GPIOComTeensy(Com):
    """Extends the Com class to provide GPIO management for a Teensy microcontroller.

    Attributes:
        scl (int): I2C clock pin (SCL) assigned to pin 19.
        sda (int): I2C data pin (SDA) assigned to pin 18.
        gpio_manager (GPIOManager): Manages GPIO pin allocation (up to 41 pins).
    """

    def __init__(
        self,
        logger: Logger,
        serial_number: int,
        vid: int,
        pid: int,
        baudrate: int,
        enable_crc: bool = True,
        enable_dummy: bool = False,
    ):
        """Initializes GPIO management for the Teensy microcontroller and its communication settings.

        Args:
            logger (Logger): Logger instance for debugging and event tracking.
            serial_number (int): Serial number of the Teensy device.
            vid (int): Vendor ID of the Teensy device.
            pid (int): Product ID of the Teensy device.
            baudrate (int): Baud rate for serial communication.
            enable_crc (bool, optional): Enables cyclic redundancy check. Defaults to True.
            enable_dummy (bool, optional): Enables dummy mode for testing. Defaults to False.
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
            enable_crc,
            enable_dummy,
        )
