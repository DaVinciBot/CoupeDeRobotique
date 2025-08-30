"""Base communication class for interacting with a Teensy over USB."""

from loggerplusplus import Logger

from usb_com.python import Com
from usb_com.python.messages import Messages


class BaseComTeensy(Com):
    """Extends the ``Com`` class to provide specialized communication handling for a Teensy microcontroller."""

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
        """Initializes the communication parameters for the Teensy device.

        Args:
            logger (Logger): Logger instance to record communication logs.
            serial_number (int): Serial number of the Teensy device.
            vid (int): Vendor ID of the device.
            pid (int): Product ID of the device.
            baudrate (int): Baud rate for communication.
            enable_crc (bool, optional):
                Enables CRC error checking. Defaults to ``True``.
            enable_dummy (bool, optional):
                Enables dummy packet handling. Defaults to ``False``.

        """
        super().__init__(
            logger,
            serial_number,
            vid,
            pid,
            baudrate,
            enable_crc=enable_crc,
            enable_dummy=enable_dummy,
        )

    def reset(self) -> None:
        """Resets the Teensy device by sending a reset command."""
        self.send_bytes(data=Messages.RESET_TEENSY.to_bytes())
