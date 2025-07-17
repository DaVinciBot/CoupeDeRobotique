import struct
from dataclasses import dataclass
from enum import Enum


class PID_ID(Enum):
    """Identifiers for the different PID controllers.

    Attributes:
        LINEAR_POSITION (int): Identifier for linear position PID control.
        ANGULAR_POSITION (int): Identifier for angular position PID control.
    """

    LINEAR_POSITION: int = 0
    ANGULAR_POSITION: int = 1


@dataclass
class PID:
    """Data class representing PID controller parameters.

    Attributes:
        kp (float): Proportional coefficient.
        ki (float): Integral coefficient.
        kd (float): Derivative coefficient.
    """

    kp: float
    ki: float
    kd: float

    def to_bytes(self) -> bytes:
        """Serialize the PID parameters into bytes.

        Returns:
            bytes: The serialized PID coefficients.
        """
        return struct.pack("<fff", self.kp, self.ki, self.kd)

    @classmethod
    def from_dict(cls, pid_dict: dict[str, any]) -> "PID":
        """Initialize a PID instance from a dictionary.

        Args:
            pid_dict (dict[str, any]): A dictionary containing PID parameters.

        Returns:
            PID: An instance of the PID class.
        """
        return cls(**pid_dict)

    @classmethod
    def from_tuple(cls, pid_tuple: tuple) -> "PID":
        """Initialize a PID instance from a tuple.

        Args:
            pid_tuple (tuple): A tuple containing PID parameters (kp, ki, kd).

        Returns:
            PID: An instance of the PID class.
        """
        return cls(*pid_tuple)

    @classmethod
    def from_list(cls, pid_list: list) -> "PID":
        """Initialize a PID instance from a list.

        Args:
            pid_list (list): A list containing PID parameters (kp, ki, kd).

        Returns:
            PID: An instance of the PID class.
        """
        return cls(*pid_list)
