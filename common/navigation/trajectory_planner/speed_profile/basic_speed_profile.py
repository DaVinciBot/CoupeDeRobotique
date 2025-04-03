# ====== Code Summary ======
# This module defines `BasicSpeedProfile`, a concrete implementation of the `BaseSpeedProfile` class.
# It provides constant-speed motion behavior by returning fixed values for speed, distance, and total duration
# calculations based on a uniform speed.

# ====== Internal Project Imports ======
from navigation.trajectory_planner.speed_profile.base_speed_profile import BaseSpeedProfile


class BasicSpeedProfile(BaseSpeedProfile):
    """
    Basic speed profile implementation using constant speed.

    All motion calculations assume uniform velocity with no acceleration or deceleration.
    """

    def __init__(self, speed: float):
        """
        Initialize the basic speed profile.

        Args:
            speed (float): Constant speed value used for calculations.
        """
        super().__init__(max_speed=speed)

    def get_speed(self, time_elapsed: float | None = None, distance: float | None = None) -> float:
        """
        Get constant speed at any given time or distance.

        Args:
            time_elapsed (float | None): Not used.
            distance (float | None): Not used.

        Returns:
            float: Constant speed.
        """
        return self.max_speed

    def get_distance(self, time_elapsed: float, distance: float | None = None) -> float:
        """
        Compute distance traveled given elapsed time.

        Args:
            time_elapsed (float): Elapsed time in seconds.
            distance (float | None): Not used.

        Returns:
            float: Distance = speed * time_elapsed
        """
        return self.max_speed * time_elapsed

    def get_total_duration(self, distance: float) -> float:
        """
        Compute total time required to cover a distance at constant speed.

        Args:
            distance (float): Distance to travel.

        Returns:
            float: Duration = distance / speed
        """
        return distance / self.max_speed
