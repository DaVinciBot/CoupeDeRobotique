"""Serial port stub used for testing without hardware."""

from __future__ import annotations


class DummySerial:
    """A dummy serial communication class for testing purposes.

    This class simulates a serial port by maintaining input and output buffers,
    allowing data to be written and read in a controlled manner.
    """

    def __init__(self) -> None:
        """Initializes the DummySerial object with empty input and output buffers."""
        self.output_buffer = b""  # Stores data written to the serial port
        self.input_buffer = b""  # Stores incoming data for reading
        self.out_waiting = False  # Indicates if data is waiting to be sent

    def write(self, data: bytes) -> None:
        """Simulates writing data to the serial port.

        Args:
            data (bytes): The data to be written to the output buffer.
        """
        self.out_waiting = True
        self.output_buffer += data
        # Simulated delay can be added based on baud rate if necessary
        self.out_waiting = False

    def reset_output_buffer(self) -> None:
        """Clears the output buffer."""
        self.output_buffer = b""

    def read_until(self, signature: bytes) -> bytes:
        """Reads data from the input buffer up to a given signature.

        Args:
            signature (bytes): The delimiter indicating where to stop reading.

        Returns:
            bytes: Data read up to the given signature.
        """
        return self.input_buffer.split(signature)[0]

    def dummy_add_input(self, data: bytes) -> None:
        """Simulates incoming data by adding it to the input buffer.

        Args:
            data (bytes): The data to add to the input buffer.
        """
        self.input_buffer += data

    def reset_input_buffer(self) -> None:
        """Clears the input buffer."""
        self.input_buffer = b""
