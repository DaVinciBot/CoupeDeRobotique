"""Base interfaces for speed profile strategies."""

from __future__ import annotations

from abc import ABC, abstractmethod


class BaseSpeedProfile(ABC):
    """Interface to compute speed and distance along a path."""

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
            time_elapsed (float | None, optional):
                Time since motion started (in seconds). Defaults to None.
            distance (float | None, optional):
                Total path distance (in meters or appropriate unit). Defaults to None.
            departure_speed (float, optional):
                Speed at the start of motion. Defaults to 0.0.
            arrival_speed (float, optional):
                Speed at the end of motion. Defaults to 0.0.

        Returns:
            float: Speed at the current time/distance.

        """

    @abstractmethod
    def get_distance(
        self,
        time_elapsed: float | None = None,
        distance: float | None = None,
        departure_speed: float = 0.0,
        arrival_speed: float = 0.0,
    ) -> float:
        """Get distance traveled given elapsed time.

        This method computes how far the object has traveled over time
        using motion dynamics defined by the specific speed profile.

        Args:
            time_elapsed (float | None): Elapsed time in seconds. Defaults to None.
            distance (float | None, optional):
                Total path distance (optional). Defaults to None.
            departure_speed (float, optional):
                Speed at the beginning of motion. Defaults to 0.0.
            arrival_speed (float, optional):
                Speed at the end of motion. Defaults to 0.0.

        Returns:
            float: Distance traveled so far.

        """

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
            departure_speed (float, optional):
                Speed at the beginning of motion. Defaults to 0.0.
            arrival_speed (float, optional):
                Speed at the end of motion. Defaults to 0.0.

        Returns:
            float: Time needed to complete the distance.

        """
