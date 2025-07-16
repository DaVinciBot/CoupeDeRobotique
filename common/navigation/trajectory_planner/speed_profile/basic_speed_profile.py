# ====== Code Summary ======
# This module defines `BasicSpeedProfile`, a concrete implementation of the `BaseSpeedProfile` class.
# It provides constant-speed motion behavior by returning fixed values for speed, distance, and total duration
# calculations based on a uniform speed. Additional parameters such as departure and arrival speeds are accepted
# for interface compatibility but not used in calculations due to the constant-speed assumption.

from navigation.trajectory_planner.speed_profile.base_speed_profile import (
    BaseSpeedProfile,
)


class BasicSpeedProfile(BaseSpeedProfile):
    """Basic speed profile implementation using constant speed.

    All motion calculations assume uniform velocity with no acceleration or deceleration.
    """

    def __init__(self, speed: float) -> None:
        """Initialize the basic speed profile.

        Args:
            speed (float): Constant speed value used for calculations.
        """
        super().__init__(max_speed=speed)

    def get_speed(
        self,
        time_elapsed: float | None = None,
        distance: float | None = None,
        departure_speed: float = 0.0,
        arrival_speed: float = 0.0,
    ) -> float:
        """Get constant speed at any given time or distance.

        Args:
            time_elapsed (float | None): Not used.
            distance (float | None): Not used.
            departure_speed (float): Accepted for compatibility; not used.
            arrival_speed (float): Accepted for compatibility; not used.

        Returns:
            float: Constant speed.
        """
        return self._max_speed

    def get_distance(
        self,
        time_elapsed: float,
        distance: float | None = None,
        departure_speed: float = 0.0,
        arrival_speed: float = 0.0,
    ) -> float:
        """Compute distance traveled given elapsed time.

        Args:
            time_elapsed (float): Elapsed time in seconds.
            distance (float | None): Not used.
            departure_speed (float): Accepted for compatibility; not used.
            arrival_speed (float): Accepted for compatibility; not used.

        Returns:
            float: Distance = speed * time_elapsed
        """
        return self._max_speed * time_elapsed

    def get_total_duration(
        self,
        distance: float,
        departure_speed: float = 0.0,
        arrival_speed: float = 0.0,
    ) -> float:
        """Compute total time required to cover a distance at constant speed.

        Args:
            distance (float): Distance to travel.
            departure_speed (float): Accepted for compatibility; not used.
            arrival_speed (float): Accepted for compatibility; not used.

        Returns:
            float: Duration = distance / speed
        """
        return distance / self._max_speed
