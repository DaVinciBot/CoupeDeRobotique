"""Constant speed profile implementation."""

from __future__ import annotations

from typing import override

from navigation.trajectory_planner.speed_profile.base_speed_profile import (
    BaseSpeedProfile,
)


class BasicSpeedProfile(BaseSpeedProfile):
    """Basic speed profile assuming uniform velocity."""

    def __init__(self, speed: float) -> None:
        """Initialize with the constant ``speed``.

        Args:
            speed (float): Constant speed value used for calculations.
        """
        super().__init__(max_speed=speed)

    @override
    def get_speed(
        self,
        time_elapsed: float | None = None,
        distance: float | None = None,
        departure_speed: float = 0.0,
        arrival_speed: float = 0.0,
    ) -> float:
        """Return constant speed regardless of inputs.

        Args:
            time_elapsed (float | None, optional): Not used. Defaults to None.
            distance (float | None, optional): Not used. Defaults to None.
            departure_speed (float, optional):
                Accepted for compatibility; not used. Defaults to 0.0.
            arrival_speed (float, optional):
                Accepted for compatibility; not used. Defaults to 0.0.

        Returns:
            float: The constant speed value.
        """
        if time_elapsed is None or time_elapsed <= 0:
            return 0.0

        return self._max_speed

    @override
    def get_distance(
        self,
        time_elapsed: float | None = None,
        distance: float | None = None,
        departure_speed: float = 0.0,
        arrival_speed: float = 0.0,
    ) -> float:
        """Compute distance as ``speed * time_elapsed``.

        Args:
            time_elapsed (float | None): Elapsed time in seconds. Defaults to None.
            distance (float | None, optional): Not used. Defaults to None.
            departure_speed (float, optional):
                Accepted for compatibility; not used. Defaults to 0.0.
            arrival_speed (float, optional):
                Accepted for compatibility; not used. Defaults to 0.0.

        Returns:
            float: Distance covered.
        """
        if time_elapsed is None or time_elapsed <= 0:
            return 0.0

        return self._max_speed * time_elapsed

    @override
    def get_total_duration(
        self,
        distance: float,
        departure_speed: float = 0.0,
        arrival_speed: float = 0.0,
    ) -> float:
        """Return duration to travel ``distance`` at constant speed.

        Args:
            distance (float): Distance to travel.
            departure_speed (float, optional):
                Accepted for compatibility; not used. Defaults to 0.0.
            arrival_speed (float, optional):
                Accepted for compatibility; not used. Defaults to 0.0.

        Returns:
            float: Duration of the motion.
        """
        return distance / self._max_speed
