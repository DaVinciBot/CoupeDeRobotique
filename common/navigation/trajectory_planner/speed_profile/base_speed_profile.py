# ====== Code Summary ======
# This module defines `BaseSpeedProfile`, an abstract base class
# for speed profile strategies used in trajectory planning.
# It specifies the interface for calculating speed, distance
# traveled, and total duration based on motion parameters.

# ====== Standard Library Imports ======
from abc import ABC, abstractmethod


class BaseSpeedProfile(ABC):
    """
    Abstract base class for speed profile models.

    Defines an interface for retrieving dynamic motion properties such as speed,
    distance traveled, and time duration, based on elapsed time and path distance.
    """

    def __init__(self, max_speed: float):
        """
        Initialize the base speed profile with a maximum speed.

        Args:
            max_speed (float): The maximum speed for the profile.
        """
        self._max_speed: float = max_speed

    @abstractmethod
    def get_speed(
        self, time_elapsed: float | None = None, distance: float | None = None
    ) -> float:
        """
        Get current speed based on elapsed time or distance.

        Args:
            time_elapsed (float | None): Time since motion started.
            distance (float | None): Total distance of motion.

        Returns:
            float: Speed at the current time/distance.
        """
        ...

    @abstractmethod
    def get_distance(self, time_elapsed: float, distance: float | None = None) -> float:
        """
        Get distance traveled given elapsed time.

        Args:
            time_elapsed (float): Elapsed time in seconds.
            distance (float | None): Total distance of motion.

        Returns:
            float: Distance traveled so far.
        """
        ...

    @abstractmethod
    def get_total_duration(self, distance: float) -> float:
        """
        Get total duration required to travel a given distance.

        Args:
            distance (float): Distance to travel.

        Returns:
            float: Time needed to complete the distance.
        """
        ...
