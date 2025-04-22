# ====== Standard Library Imports ======
from enum import Enum
from dataclasses import dataclass
import struct


class PID_ID(Enum):
    """
    Identifiers for the different PID controllers.
    """

    LINEAR_SPEED = 0
    ANGULAR_SPEED = 1
    LINEAR_POSITION = 2
    ANGULAR_POSITION = 3


@dataclass
class PID:
    """
    Data class representing PID controller parameters.
    """

    kp: float
    ki: float
    kd: float

    def to_bytes(self) -> bytes:
        """
        Serialize the PID parameters into bytes.
        """
        return struct.pack("<fff", self.kp, self.ki, self.kd)

    @classmethod
    def from_dict(cls, pid_dict: dict[str, any]) -> "PID":
        return cls(**pid_dict)

    @classmethod
    def from_tuple(cls, pid_tuple: tuple) -> "PID":
        return cls(*pid_tuple)

    @classmethod
    def from_list(cls, pid_list: list) -> "PID":
        return cls(*pid_list)
