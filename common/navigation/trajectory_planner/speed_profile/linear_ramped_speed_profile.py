# ====== Code Summary ======
# This module defines a `LinearRampedSpeedProfile` class that generates speed profiles
# with linear acceleration and deceleration.
# It supports both unconstrained motion (no distance limit) and constrained motion
# where the total distance limits the velocity profile.
# The profile can take either a trapezoidal form (with cruising) or triangular form
# (no cruising) depending on the distance.

# ====== Standard Library Imports ======
from math import sqrt

# ====== Third-Party Library Imports ======
# (None)

# ====== Internal Project Imports ======
from navigation.trajectory_planner.speed_profile.base_speed_profile import (
    BaseSpeedProfile,
)


# ====== Linear Ramped Speed Profile Class ======
class LinearRampedSpeedProfile(BaseSpeedProfile):
    """
    Speed profile with linear acceleration and deceleration.

    Supports both trapezoidal and triangular profiles depending on whether the maximum speed
    can be reached within the specified distance.
    """

    def __init__(self, acceleration: float, max_speed: float, deceleration: float):
        """
        Initialize the LinearRampedSpeedProfile instance with constant acceleration and deceleration rates.

        Args:
            acceleration (float): Maximum acceleration rate for the departure phase.
            max_speed (float): Maximum (cruise) speed achievable in the mid phase.
            deceleration (float): Maximum deceleration rate for the arrival phase.
        """
        super().__init__(max_speed=max_speed)
        self._acceleration_rate = acceleration
        self._deceleration_rate = deceleration

    def _compute_profile_params(
        self,
        distance: float | None = None,
        departure_speed: float = 0.0,
        arrival_speed: float = 0.0,
    ) -> dict:
        """
        Compute the times and distances for each phase of the motion profile (accelerate, cruise, decelerate).

        The returned dictionary includes:
            - t_to_accelerate (float): time to accelerate from departure_speed to max_speed.
            - t_to_decelerate (float): time to decelerate from max_speed to arrival_speed.
            - t_cruise (float): cruising duration (may be 0 if triangular).
            - t_total (float): total time.
            - d_to_accelerate (float): distance covered during acceleration.
            - d_to_decelerate (float): distance covered during deceleration.
            - d_cruise (float): distance covered during cruise phase.
            - v_cruise (float): cruise speed.

        Args:
            distance (float | None, optional): Total planned distance to cover. Defaults to None.
            departure_speed (float, optional): Speed at the start of the motion. Defaults to 0.0.
            arrival_speed (float, optional): Speed at the end of the motion. Defaults to 0.0.

        Returns:
            dict: A dictionary of profile parameters.
        """
        d_to_accelerate = (self._max_speed**2 - departure_speed**2) / (
            2 * self._acceleration_rate
        )
        d_to_decelerate = (self._max_speed**2 - arrival_speed**2) / (
            2 * self._deceleration_rate
        )

        if distance is None:
            distance = d_to_accelerate + d_to_decelerate

        t_to_accelerate = (
            (self._max_speed - departure_speed) / self._acceleration_rate
            if self._max_speed > departure_speed
            else 0.0
        )
        t_to_decelerate = (
            (self._max_speed - arrival_speed) / self._deceleration_rate
            if self._max_speed > arrival_speed
            else 0.0
        )

        d_needed_for_full = d_to_accelerate + d_to_decelerate
        if distance >= d_needed_for_full:
            d_cruise = distance - d_needed_for_full
            t_cruise = d_cruise / self._max_speed
            v_cruise = self._max_speed
        else:
            v_peak = sqrt(
                2 * distance * self._acceleration_rate * self._deceleration_rate
                + self._acceleration_rate * (arrival_speed**2)
                + self._deceleration_rate * (departure_speed**2)
            ) / sqrt(self._acceleration_rate + self._deceleration_rate)

            t_to_accelerate = (
                (v_peak - departure_speed) / self._acceleration_rate
                if v_peak > departure_speed
                else 0.0
            )
            t_to_decelerate = (
                (v_peak - arrival_speed) / self._deceleration_rate
                if v_peak > arrival_speed
                else 0.0
            )

            d_to_accelerate = (v_peak**2 - departure_speed**2) / (
                2 * self._acceleration_rate
            )
            d_to_decelerate = (v_peak**2 - arrival_speed**2) / (
                2 * self._deceleration_rate
            )

            d_cruise = 0.0
            t_cruise = 0.0
            v_cruise = v_peak

        t_total = t_to_accelerate + t_cruise + t_to_decelerate

        return {
            "t_to_accelerate": t_to_accelerate,
            "t_to_decelerate": t_to_decelerate,
            "t_cruise": t_cruise,
            "t_total": t_total,
            "d_to_accelerate": d_to_accelerate,
            "d_to_decelerate": d_to_decelerate,
            "d_cruise": d_cruise,
            "v_cruise": v_cruise,
        }

    def get_speed(
        self,
        time_elapsed: float | None = None,
        distance: float | None = None,
        departure_speed: float = 0.0,
        arrival_speed: float = 0.0,
    ) -> float:
        """
        Compute the speed at a given time.

        Args:
            time_elapsed (float | None, optional): Time since motion start. Defaults to None.
            distance (float | None, optional): Total planned distance to cover. Defaults to None.
            departure_speed (float, optional): Speed at the start of the motion. Defaults to 0.0.
            arrival_speed (float, optional): Speed at the end of the motion. Defaults to 0.0.

        Returns:
            float: The current speed at 'time_elapsed'.
        """
        if time_elapsed is None or time_elapsed < 0:
            return departure_speed

        params = self._compute_profile_params(distance, departure_speed, arrival_speed)
        t_to_accelerate = params["t_to_accelerate"]
        t_cruise = params["t_cruise"]
        t_total = params["t_total"]
        v_cruise = params["v_cruise"]

        if time_elapsed >= t_total:
            return arrival_speed

        if time_elapsed < t_to_accelerate:
            return departure_speed + self._acceleration_rate * time_elapsed

        if time_elapsed < t_to_accelerate + t_cruise:
            return v_cruise

        return max(
            arrival_speed + self._deceleration_rate * (t_total - time_elapsed), 0.0
        )

    def get_distance(
        self,
        time_elapsed: float,
        distance: float | None = None,
        departure_speed: float = 0.0,
        arrival_speed: float = 0.0,
    ) -> float:
        """
        Compute the traveled distance at a given time.

        Args:
            time_elapsed (float): Time since motion started.
            distance (float | None, optional): Total planned distance. Defaults to None.
            departure_speed (float, optional): Initial speed at the start. Defaults to 0.0.
            arrival_speed (float, optional): Final speed at the end. Defaults to 0.0.

        Returns:
            float: Cumulative distance traveled from t=0 to t='time_elapsed'.
        """
        if time_elapsed <= 0:
            return 0.0

        params = self._compute_profile_params(distance, departure_speed, arrival_speed)
        t_to_accelerate = params["t_to_accelerate"]
        t_cruise = params["t_cruise"]
        t_total = params["t_total"]
        d_to_accelerate = params["d_to_accelerate"]
        d_to_decelerate = params["d_to_decelerate"]
        d_cruise = params["d_cruise"]
        v_cruise = params["v_cruise"]

        if time_elapsed >= t_total:
            return min(distance, d_to_accelerate + d_cruise + d_to_decelerate)

        if time_elapsed < t_to_accelerate:
            return (
                departure_speed * time_elapsed
                + 0.5 * self._acceleration_rate * time_elapsed**2
            )

        t2 = time_elapsed - t_to_accelerate
        if t2 < t_cruise:
            return d_to_accelerate + v_cruise * t2

        t3 = t2 - t_cruise
        return (
            d_to_accelerate
            + d_cruise
            + arrival_speed * t3
            + self._deceleration_rate
            * (
                t_total * t3
                - ((time_elapsed**2 - (t_to_accelerate + t_cruise) ** 2) / 2)
            )
        )

    def get_total_duration(
        self,
        distance: float | None = None,
        departure_speed: float = 0.0,
        arrival_speed: float = 0.0,
    ) -> float:
        """
        Compute the total time required to complete the motion over a given distance,
        from 'departure_speed' to 'arrival_speed', respecting the maximum speed and
        the acceleration/deceleration rates.

        Args:
            distance (float | None, optional): Total planned distance to cover. Defaults to None.
            departure_speed (float, optional): Speed at the start of the motion. Defaults to 0.0.
            arrival_speed (float, optional): Speed at the end of the motion. Defaults to 0.0.

        Returns:
            float: Total time (seconds) to finish the trajectory. Returns 0.0 if distance <= 0.
        """
        params = self._compute_profile_params(distance, departure_speed, arrival_speed)
        return params["t_total"]
