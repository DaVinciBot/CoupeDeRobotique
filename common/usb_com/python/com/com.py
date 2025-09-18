"""USB communication helper with optional CRC and dummy mode."""

from __future__ import annotations

import threading
import time
from functools import wraps
from typing import TYPE_CHECKING, Any

import crc8
from serial import Serial
from serial.tools.list_ports import comports

from usb_com.python.com.dummy import DummySerial
from usb_com.python.com.exceptions import ComError
from usb_com.python.messages import END_BYTES_SIGNATURE, Messages

NACK_ID = 127

if TYPE_CHECKING:
    from collections.abc import Callable

    from loggerplusplus import Logger


class Com:
    """Handle USB exchanges with a Teensy microcontroller.

    Supports message transmission, CRC8 verification, and callback mechanisms.
    """

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
        """Initialize the USB communication instance.

        Args:
            logger (Logger): Logger instance for logging messages.
            serial_number (int): Serial number of the target device.
            vid (int): Vendor ID of the USB device.
            pid (int): Product ID of the USB device.
            baudrate (int): Baud rate for serial communication.
            enable_crc (bool, optional):
                Enables CRC8 checksum verification. Defaults to ``True``.
            enable_dummy (bool, optional):
                Enables dummy mode for testing. Defaults to ``False``.
        """
        # Initialize init variables
        self.logger: Logger = logger
        self.serial_number: int = serial_number
        self.vid: int = vid
        self.pid: int = pid
        self.baudrate: int = baudrate
        self.enable_crc: bool = enable_crc
        self.enable_dummy: bool = enable_dummy

        # Initialize usb com variables
        self._device: Serial | DummySerial = self._get_serial()
        self._crc8: crc8.crc8 = crc8.crc8()

        self.last_message: bytes | None = None
        self.message_id_callback: dict[int, Callable[[bytes], None]] = {}

        # Start the receiver thread (if not in dummy mode),
        # it is responsible for handling the received data
        self._receiver_thread: threading.Thread | None = self._start_receiver()

    # region ======= Private methods =======
    def _get_serial(self) -> Serial | DummySerial:
        """Detect and initialize the serial device or dummy mode.

        Returns:
            Serial | DummySerial:
                Initialized serial connection or dummy instance.

        Raises:
            ComError: If no device is found and dummy mode is disabled.
        """
        device_found: Serial | DummySerial | None = None

        for port in comports():
            if (
                port.vid == self.vid
                and port.pid == self.pid
                and port.serial_number is not None
                and port.serial_number == str(self.serial_number)
            ):
                device_found = Serial(port.device, baudrate=self.baudrate)
                break

        if device_found is None:
            if self.enable_dummy:
                self.logger.info("Dummy mode")
                device_found = DummySerial()
            else:
                msg = "No Device found!"
                self.logger.critical(msg)
                raise ComError(msg)

        return device_found

    def _start_receiver(self) -> threading.Thread | None:
        """Starts the receiver thread unless in dummy mode.

        Returns:
            threading.Thread | None: Receiver thread or None if dummy mode is enabled.
        """
        # If in dummy mode, do not start the receiver thread
        if self.enable_dummy:
            return None

        receiver = threading.Thread(target=self.__receiver, name="USBComReceiver")
        receiver.start()
        return receiver

    def __receiver(self) -> None:
        """Run in a thread and dispatch messages based on the protocol format.

        Format: ``msg_type | msg_data | msg_length | CRC8 | MSG_END_BYTES``
        with sizes ``1 | msg_length | 1 | 1 | 4`` bytes.
        """
        while True:
            try:
                msg = self.read_bytes()

                if self.enable_crc:
                    crc = msg[-5:-4]
                    msg = msg[:-5]
                    self._crc8.reset()
                    self._crc8.update(msg)
                    if self._crc8.digest() != crc:
                        self.logger.warning(f"Invalid CRC8, sending NACK ... [{crc}]")
                        self.send_bytes(Messages.NACK.to_bytes())  # send NACK
                        self._crc8.reset()
                        continue
                    self._crc8.reset()

                else:
                    msg = msg[:-4]

                len_msg = msg[-1]

                if len_msg > len(msg):
                    self.logger.warning(
                        "Received Teensy message that does not match declared length "
                        f"{msg.hex(sep=' ')}",
                    )
                    continue
                try:
                    if msg[0] == NACK_ID:
                        self.logger.warning("Received a NACK")
                        if self.last_message is not None:
                            self.send_bytes(self.last_message)
                            self.logger.info(
                                f"Sending back message : {self.last_message[0]}",
                            )
                            self.last_message = None
                    else:
                        self.message_id_callback.get(
                            msg[0],
                            lambda x: self.logger.error(
                                f"Unknown message type ! msg: {x}",
                            ),
                        )(msg[1:-1])

                except Exception as e:  # noqa: BLE001
                    self.logger.error(f"Received message handling crashed :\n{e}")
                    time.sleep(0.5)  # Wait to avoid spamming the logs

            except Exception as e:  # noqa: BLE001
                self.logger.critical(
                    f"Device connection seems to be closed, teensy crashed ? [{e}]",
                )
                time.sleep(0.5)  # Wait to avoid spamming the logs

    # endregion

    # region ======= Public methods =======
    @staticmethod
    def check_dummy(func: Callable[..., Any]) -> Callable[..., Any]:  # UNUSED
        """Decorator to cancel execution when in dummy mode.

        Args:
            func (Callable[..., Any]): Function to wrap.

        Returns:
            Callable[..., Any]:
                Wrapped function that returns ``None`` if dummy mode is enabled.
        """

        @wraps(func)
        def wrapper(  # UNUSED
            self: Com,
            *args: Any,  # noqa: ANN401
            **kwargs: Any,  # noqa: ANN401
        ) -> Any:  # noqa: ANN401
            # Check if the self.enable_dummy attribute is disabled (False)
            if self.enable_dummy:
                self.logger.debug(f"[DUMMY] {func.__name__} was called")
                return None  # Prevents the function from executing

            # Execute the function normally
            return func(self, *args, **kwargs)

        return wrapper

    def send_bytes(self, data: bytes) -> None:
        """Sends bytes over the serial connection.

        Args:
            data (bytes): Data to be transmitted.
        """
        self.last_message = data

        self._device.reset_output_buffer()
        msg = data + bytes([len(data)])
        if self.enable_crc:
            self._crc8.reset()
            self._crc8.update(msg)
            msg += self._crc8.digest()
            self._crc8.reset()

        self._device.write(msg + END_BYTES_SIGNATURE)
        while self._device.out_waiting:
            pass

    def read_bytes(self) -> bytes:
        """Reads bytes from the serial connection until the END_BYTES_SIGNATURE.

        Returns:
            bytes: Received data.
        """
        return self._device.read_until(END_BYTES_SIGNATURE)

    def add_callback(self, func: Callable[[bytes], None], iid: int) -> None:
        """Registers a callback for a specific message ID.

        Args:
            func (Callable[[bytes], None]): Callback function.
            iid (int): Message ID to associate with the callback.
        """
        if self.message_id_callback.get(iid) is not None:
            self.logger.warning(f"Callback for message id {iid} already exists !")

        self.message_id_callback[iid] = func

    # endregion
