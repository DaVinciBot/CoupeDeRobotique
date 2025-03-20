# ====== Code Summary ======
# This module defines the `BaseComTeensy` class, which extends `Com` to provide
# communication functionality with a Teensy microcontroller over USB.
# It initializes communication settings, including serial number, VID, PID, baud rate,
# and optional CRC and dummy packet support.

# ====== Standard Library import ======
from typing import Callable

# ====== Third-Party Library Imports ======
from loggerplusplus import Logger

# ====== Local Library Imports ======
from usb_com.python import Com
from usb_com.python.messages import Messages


# ====== Class Part ======
class BaseComTeensy(Com):
    """
    Extends the `Com` class to provide specialized communication handling for a Teensy microcontroller.

    Attributes:
        logger (Logger): Logger instance for logging communication events.
        serial_number (int): Unique serial number of the USB device.
        vid (int): Vendor ID of the USB device.
        pid (int): Product ID of the USB device.
        baudrate (int): Communication baud rate.
        enable_crc (bool): Flag to enable CRC error checking (default: True).
        enable_dummy (bool): Flag to enable dummy packets (default: False).
    """

    def __init__(
            self,
            logger: Logger,
            serial_number: int,
            vid: int,
            pid: int,
            baudrate: int,
            enable_crc: bool = True,
            enable_dummy: bool = False
    ):
        """
        Initializes the communication parameters for the Teensy device.

        Args:
            logger (Logger): Logger instance to record communication logs.
            serial_number (int): Serial number of the Teensy device.
            vid (int): Vendor ID of the device.
            pid (int): Product ID of the device.
            baudrate (int): Baud rate for communication.
            enable_crc (bool, optional): Enables CRC error checking. Defaults to True.
            enable_dummy (bool, optional): Enables dummy packet handling. Defaults to False.
        """
        super().__init__(logger, serial_number, vid, pid, baudrate, enable_crc, enable_dummy)

    def reset(self, message_id_callback: dict[int, Callable[[bytes], None]]) -> None:
        """
        Resets the Teensy device by sending a reset command.
        Then kill the receiver thread of the Com and reinitialized the Com.
        Reput the message callback in the new Com object
        """
        self.send_bytes(
            data=Messages.RESET_TEENSY.to_bytes()
        )
        self._end_receiver()
        super().__init__(self.logger, self.serial_number, self.vid, self.pid, 
                         self.baudrate, self.enable_crc, self.enable_dummy)
        self.message_id_callback = message_id_callback
