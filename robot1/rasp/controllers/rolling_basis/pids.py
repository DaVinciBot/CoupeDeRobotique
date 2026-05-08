"""PID constants and identifiers for the rolling basis controller."""

from __future__ import annotations

import struct
from dataclasses import dataclass
from enum import Enum
from typing import override


class PidID(Enum):
    """Identifiers for the different PID controllers.

    Attributes:
        LINEAR_POSITION: Identifier for linear position PID control.
        ANGULAR_POSITION: Identifier for angular position PID control.
        LEFT_WHEEL_POSITION: Identifier for left wheel position PID control.
        RIGHT_WHEEL_POSITION: Identifier for right wheel position PID control.
    """

    LINEAR_POSITION = 0
    """Identifier for linear position PID control."""
    ANGULAR_POSITION = 1
    """Identifier for angular position PID control."""
    LEFT_WHEEL_POSITION = 2
    """Identifier for left wheel position PID control."""
    RIGHT_WHEEL_POSITION = 3
    """Identifier for right wheel position PID control."""


@dataclass
class PID:
    """Data class representing PID controller parameters.

    Attributes:
        kp (float): Proportional coefficient.
        ki (float): Integral coefficient.
        kd (float): Derivative coefficient.
    """

    kp: float
    """Proportional coefficient."""
    ki: float
    """Integral coefficient."""
    kd: float
    """Derivative coefficient."""

    def to_bytes(self) -> bytes:
        """Serialize the PID parameters into bytes.

        Returns:
            bytes: The serialized PID coefficients.
        """
        return struct.pack("<fff", self.kp, self.ki, self.kd)

    @classmethod
    def from_dict(cls, pid_dict: dict[str, float]) -> PID:
        """Initialize a PID instance from a dictionary.

        Args:
            pid_dict (dict[str, float]): A dictionary containing PID parameters.

        Returns:
            PID: An instance of the PID class.
        """
        return cls(**pid_dict)

    @classmethod
    def from_tuple(cls, pid_tuple: tuple[float, float, float]) -> PID:
        """Initialize a PID instance from a tuple.

        Args:
            pid_tuple (tuple[float, float, float]):
                A tuple containing PID parameters (kp, ki, kd).

        Returns:
            PID: An instance of the PID class.
        """
        return cls(*pid_tuple)

    @classmethod
    def from_list(cls, pid_list: list[float]) -> PID:
        """Initialize a PID instance from a list.

        Args:
            pid_list (list[float]): A list containing PID parameters (kp, ki, kd).

        Returns:
            PID: An instance of the PID class.
        """
        return cls(*pid_list)

    @override
    def __str__(self) -> str:
        """String representation of the PID parameters.

        Returns:
            str: A string in the format "PID(kp=..., ki=..., kd=...)".
        """
        return f"PID(kp={self.kp}, ki={self.ki}, kd={self.kd})"
