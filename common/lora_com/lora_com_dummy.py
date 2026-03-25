# Je peux rien faire tant que l'élek est pas fixée, flemme de coder dans le vide si une librairie fait le taff
from common.lora_com import LoraCom
from typing import override


class LoraComDummy(LoraCom):
    def __init__(self, port="/dev/ttyAMA0", baudrate=9600, timeout=1):
        """
        Initialize the dummy LoRa communication interface.
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout

    @override
    def send(self, data: bytes) -> bool:
        """
        Simulate sending data over the LoRa communication channel.
        Args:
            data (bytes): The data to be sent.
        Returns:
            bool: Always returns True to indicate successful sending in dummy mode.
        """
        return True

    @override
    def receive(self, size: int = None) -> bytes | None:
        """
        Simulate receiving data over the LoRa communication channel.
        Args:
            size (int, optional): The number of bytes to read. If None, simulates receiving all available bytes.
        Returns:
            bytes | None: Simulated received data as bytes, or None if no data is available.
        """
        return b""

    @override
    def close(self) -> None:
        """
        Close the dummy connection (no actual connection to close).
         Returns:
             None
         """
        return None
