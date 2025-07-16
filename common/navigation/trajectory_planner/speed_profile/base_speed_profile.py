# ====== Code Summary ======
# This module defines `BaseSpeedProfile`, an abstract base class
# for speed profile strategies used in trajectory planning.
# It specifies the interface for calculating speed, distance
# traveled, and total duration based on motion parameters.

from abc import ABC, abstractmethod


class BaseSpeedProfile(ABC):
    """Abstract base class for speed profile models.

    Defines an interface for retrieving dynamic motion properties such as speed,
    distance traveled, and time duration, based on elapsed time and path distance.
    """

    def __init__(self, max_speed: float) -> None:
        """Initialize the base speed profile with a maximum speed.

        Args:
            max_speed (float): The maximum speed for the profile.
        """
        self._max_speed: float = max_speed

    @abstractmethod
    def get_speed(
        self,
        time_elapsed: float | None = None,
        distance: float | None = None,
        departure_speed: float = 0.0,
        arrival_speed: float = 0.0,
    ) -> float:
        """Get current speed based on elapsed time or distance.

        Implementations should use the provided motion parameters
        to calculate the current speed at a given point in the trajectory.

        Args:
            time_elapsed (float | None): Time since motion started (in seconds).
            distance (float | None): Total path distance (in meters or appropriate unit).
            departure_speed (float): Speed at the start of motion.
            arrival_speed (float): Speed at the end of motion.

        Returns:
            float: Speed at the current time/distance.
        """
        ...

    @abstractmethod
    def get_distance(
        self,
        time_elapsed: float,
        distance: float | None = None,
        departure_speed: float = 0.0,
        arrival_speed: float = 0.0,
    ) -> float:
        """Get distance traveled given elapsed time.

        This method computes how far the object has traveled over time
        using motion dynamics defined by the specific speed profile.

        Args:
            time_elapsed (float): Elapsed time in seconds.
            distance (float | None): Total path distance (optional).
            departure_speed (float): Speed at the beginning of motion.
            arrival_speed (float): Speed at the end of motion.

        Returns:
            float: Distance traveled so far.
        """
        ...

    @abstractmethod
    def get_total_duration(
        self,
        distance: float,
        departure_speed: float = 0.0,
        arrival_speed: float = 0.0,
    ) -> float:
        """Get total duration required to travel a given distance.

        This method estimates how long it will take to complete the
        entire trajectory based on the profile's speed characteristics.

        Args:
            distance (float): Distance to travel.
            departure_speed (float): Speed at the beginning of motion.
            arrival_speed (float): Speed at the end of motion.

        Returns:
            float: Time needed to complete the distance.
        """
        ...
