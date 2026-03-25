import serial


class LoraCom:
    """
    Class to handle LoRa communication via a serial interface.
    It provides methods to send and receive data, as well as to manage the serial connection.
    """

    def __init__(self, port="/dev/ttyAMA0", baudrate=9600, timeout=1):
        """
        Initialize the LoRa communication interface.
        Args:
            port (str): The serial port to which the LoRa module is connected. Defaults to "/dev/ttyAMA0".
            baudrate (int): The baud rate for serial communication. Defaults to 9600.
            timeout (int): The timeout for serial communication in seconds. Defaults to 1.
        """
        self.ser = serial.Serial(
            port=port,
            baudrate=baudrate,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=timeout
        )

    def send(self, data: bytes) -> bool:
        """
        Send data over the LoRa communication channel.
        Args:
            data (bytes): The data to be sent.
        Returns:
            bool: True if the data was sent successfully, False otherwise.
        """
        try:
            written = self.ser.write(data)
            self.ser.flush()
            return written == len(data)
        except Exception as e:
            print(f"[LoraCom] Error send : {e}")
            return False

    def receive(self, size: int = None) -> bytes | None:
        """
        Receive data from the LoRa communication channel.
        Args:
            size (int, optional): The number of bytes to read. If None, reads all available bytes.
        Returns:
            bytes | None: The received data as bytes, or None if no data is available or an error occurs.
        """
        try:
            available = self.ser.in_waiting
            if size is None and available > 0:
                return self.ser.read(available)
            if size is not None and available >= size:
                return self.ser.read(size)
            return None
        except Exception as e:
            print(f"[LoraCom] Error receive : {e}")
            return None

    def close(self) -> None:
        """
        Close the serial connection if it is open.
        Returns:
            None
        """
        if self.ser.is_open:
            self.ser.close()
