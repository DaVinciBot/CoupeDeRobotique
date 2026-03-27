"""LoRa serial communication helpers."""

import serial
from loggerplusplus import Logger
from serial import SerialException


class LoraCom:
    """Handle LoRa communication over a serial port."""

    def __init__(
        self,
        logger: Logger,
        port: str = "/dev/ttyAMA0",
        baudrate: int = 9600,
        timeout: float = 1,
    ) -> None:
        """Initialize the LoRa serial connection.

        Args:
            logger (Logger): Logger instance used for status messages.
            port (str, optional): Serial port device path. Defaults to "/dev/ttyAMA0".
            baudrate (int, optional): Serial baud rate. Defaults to 9600.
            timeout (float, optional): Read timeout in seconds. Defaults to 1.
        """
        self.ser = serial.Serial(
            port=port,
            baudrate=baudrate,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=timeout,
        )
        self.logger = logger

    def send(self, data: bytes) -> bool:
        """Send data over the serial link.

        Args:
            data (bytes): Raw payload to transmit.

        Returns:
            bool: True when all bytes are written, False otherwise.
        """
        try:
            written = self.ser.write(data)
            self.ser.flush()
        except (SerialException, OSError) as exc:
            self.logger.error(f"[LoraCom] Error send: {exc}")
            return False

        self.logger.info(f"[LoraCom] Sent {written} bytes: {data.hex()}")
        return written == len(data)

    def receive(self, size: int | None = None) -> bytes | None:
        """Receive data from the serial link.

        Args:
            size (int | None, optional): Number of bytes to read. When None, read
                all available bytes. Defaults to None.

        Returns:
            bytes | None: The received payload, or None if nothing is available.
        """
        self.logger.info("[LoraCom] Checking for incoming data...")
        try:
            available = self.ser.in_waiting

            if size is None:
                if not available:
                    self.logger.info("[LoraCom] No data available to read.")
                    return None
                data = self.ser.read(available)
            else:
                if available < size:
                    return None
                data = self.ser.read(size)
        except (SerialException, OSError) as exc:
            self.logger.error(f"[LoraCom] Error receive: {exc}")
            return None

        self.logger.info(f"[LoraCom] Received {len(data)} bytes: {data.hex()}")
        return data

    def close(self) -> None:
        """Close the serial connection if it is open."""
        if self.ser.is_open:
            self.ser.close()
