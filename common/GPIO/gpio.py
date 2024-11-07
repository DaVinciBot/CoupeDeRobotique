import RPi.GPIO as GPIO


class PIN:
    """
    Represents a GPIO pin.

    Args:
        pin (int): The pin number.

    Attributes:
        pin (int): The pin number.
        mode (str): The pin mode (input/output).
        reverse_state (bool): Whether to reverse the state of the pin.

    """

    def __init__(self, pin):
        self.pin = pin
        self.mode = None
        self.reverse_state = False

    def setup(self, mode, reverse_state=False):
        """
        Set up the pin.

        Args:
            mode (str): The pin mode (input/output).
            reverse_state (bool, optional): Whether to reverse the state of the pin. Defaults to False.

        """
        mode = mode.lower()
        self.mode = mode
        self.reverse_state = reverse_state
        GPIO.setmode(GPIO.BCM)

        if mode == "output":
            GPIO.setup(self.pin, GPIO.OUT)
        elif mode == "input":
            GPIO.setup(self.pin, GPIO.IN)
        elif mode == "input_pullup":
            GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        elif mode == "input_pulldown":
            GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    def digital_write(self, state: bool):
        """
        Write a digital state to the pin.

        Args:
            state (bool): The state to write (True/False).

        """
        GPIO.output(self.pin, self.__correct_state(state))

    def digital_read(self) -> bool:
        """
        Read the digital state of the pin.

        Returns:
            bool: The digital state of the pin (True/False).

        """
        return self.__correct_state(GPIO.input(self.pin))

    def safe_digital_read(self, n=5) -> bool:
        """
        Read multiple time the digital state of the pin.

        Returns:
            bool: The digital state of the pin (True/False).

        """
        return sum([self.digital_read() for _ in range(n)]) / n >= 0.5

    def __correct_state(self, state: bool) -> bool:
        """
        Correct the state of the pin based on the reverse_state attribute.

        Args:
            state (bool): The state to correct.

        Returns:
            bool: The corrected state.

        """
        return not state if self.reverse_state else state
