import serial
from loggerplusplus import Logger


class LoraCom:
    def __init__(self, logger: Logger, port="/dev/ttyAMA0", baudrate=9600, timeout=1):
        self.ser = serial.Serial(
            port=port,
            baudrate=baudrate,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=timeout
        )
        self.logger = logger

    def send(self, data: bytes) -> bool:
        try:
            written = self.ser.write(data)
            self.ser.flush()

            self.logger.info(f"[LoraCom] Sent {written} bytes: {data.hex()}")
            return written == len(data)

        except Exception as e:
            self.logger.error(f"[LoraCom] Error send: {e}")
            return False

    def receive(self, size: int = None) -> bytes | None:
        self.logger.info("[LoraCom] Checking for incoming data...")
        try:
            available = self.ser.in_waiting

            if size is None:
                if available == 0:
                    self.logger.info("[LoraCom] No data available to read.")
                    return None

                data = self.ser.read(available)

            else:
                if available < size:
                    return None

                data = self.ser.read(size)

            self.logger.info(f"[LoraCom] Received {len(data)} bytes: {data.hex()}")
            return data

        except Exception as e:
            self.logger.error(f"[LoraCom] Error receive: {e}")
            return None

    def close(self) -> None:
        if self.ser.is_open:
            self.ser.close()