# ====== Code Summary ======
# This module defines a `LinearRampedSpeedProfile` class that generates speed profiles
# with linear acceleration and deceleration.
# It supports both unconstrained motion (no distance limit) and constrained motion
# where the total distance limits the velocity profile.
# The profile can take either a trapezoidal form (with cruising) or triangular form
# (no cruising) depending on the distance.

# ====== Standard Library Imports ======
# (None)

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

    def get_speed(
        self,
        time_elapsed: float | None = None,
        distance: float | None = None,
        departure_speed: float = 0.0,
        arrival_speed: float = 0.0,
    ) -> float:
        """
        Compute the speed at a given time, using a three-phase motion plan:
        (departure, cruising, arrival). This accounts for the desired departure speed
        and final arrival speed.

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

        t_to_accelerate = (self._max_speed - departure_speed) / self._acceleration_rate
        t_to_decelerate = (self._max_speed - arrival_speed) / self._deceleration_rate

        # --- Mode without distance constraint ---
        if distance is None:
            if time_elapsed < t_to_accelerate:
                return departure_speed + self._acceleration_rate * time_elapsed

            t_total = t_to_accelerate + t_to_decelerate
            if time_elapsed < t_total:
                return max(
                    self._max_speed
                    - self._deceleration_rate * (time_elapsed - t_to_accelerate),
                    0.0,
                )

            return arrival_speed

        # --- Mode with distance constraint ---
        d_to_accelerate = (self._max_speed**2 - departure_speed**2) / (
            2 * self._acceleration_rate
        )
        d_to_decelerate = (self._max_speed**2 - arrival_speed**2) / (
            2 * self._deceleration_rate
        )

        if distance >= d_to_accelerate + d_to_decelerate:
            # Trapezoidal profile: has cruising phase
            d_cruise = distance - (d_to_accelerate + d_to_decelerate)
            t_cruise = d_cruise / self._max_speed
            t_total = t_to_accelerate + t_cruise + t_to_decelerate

            if time_elapsed < t_total:
                speeds = [
                    departure_speed + self._acceleration_rate * time_elapsed,
                    self._max_speed,
                    arrival_speed + self._deceleration_rate * (t_total - time_elapsed),
                ]
                return min([i for i in speeds if i >= 0])
            return arrival_speed

        # Triangular profile: distance too short to reach max speed
        v_at_peak = (
            (
                2 * distance * self._acceleration_rate * self._deceleration_rate
                + self._acceleration_rate * (arrival_speed**2)
                + self._deceleration_rate * (departure_speed**2)
            )
            / (self._acceleration_rate + self._deceleration_rate)
        ) ** 0.5
        t_to_peak = (v_at_peak - departure_speed) / self._acceleration_rate
        t_to_decelerate = (v_at_peak - arrival_speed) / self._deceleration_rate
        t_total = t_to_peak + t_to_decelerate

        if time_elapsed < t_to_peak:
            return (
                departure_speed + self._acceleration_rate * time_elapsed
            )  # Accelerating to peak
        if time_elapsed < t_total:
            # return max(
            #     v_at_peak - self._deceleration_rate * (time_elapsed - t_to_peak), 0.0
            # )  # Decelerating from peak
            return max(
                arrival_speed + self._deceleration_rate * (t_total - time_elapsed), 0.0
            )

        return arrival_speed

    def get_distance(
        self,
        time_elapsed: float,
        distance: float | None = None,
        departure_speed: float = 0.0,
        arrival_speed: float = 0.0,
    ) -> float:
        """
        Compute the traveled distance at a given time, using the same three-phase approach
        (departure, cruising, arrival). The distance returned is the position along the
        trajectory from t=0 to t='time_elapsed'.

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

        t_to_accelerate = (self._max_speed - departure_speed) / self._acceleration_rate
        t_to_decelerate = (self._max_speed - arrival_speed) / self._deceleration_rate

        d_to_accelerate = (self._max_speed**2 - departure_speed**2) / (
            2 * self._acceleration_rate
        )
        d_to_decelerate = (self._max_speed**2 - arrival_speed**2) / (
            2 * self._deceleration_rate
        )

        # --- Unconstrained profile (distance is None) ---
        if distance is None:
            t_total = t_to_accelerate + t_to_decelerate
            if time_elapsed < t_to_accelerate:
                # Accelerating phase: d = v * t + 0.5 * a * t^2
                return (
                    departure_speed * time_elapsed
                    + 0.5 * self._acceleration_rate * time_elapsed**2
                )
            if time_elapsed < t_total:
                # Decelerating phase: add full accel distance and integrate deceleration
                dt = time_elapsed - t_to_accelerate
                # return d_to_accelerate - 0.5 * self._deceleration_rate * dt**2
                return (
                    d_to_accelerate
                    + arrival_speed * dt
                    + self._deceleration_rate
                    * (t_total * dt - ((time_elapsed**2 - t_to_accelerate**2) / 2))
                )

            return d_to_accelerate + d_to_decelerate

        # --- Constrained profile ---
        # Check if we have a trapezoidal profile (enough distance to cruise)
        if distance >= d_to_accelerate + d_to_decelerate:
            d_cruise = distance - (d_to_accelerate + d_to_decelerate)
            t_cruise = d_cruise / self._max_speed
            t_total = t_to_accelerate + t_cruise + t_to_decelerate

            if time_elapsed < t_to_accelerate:
                # Accelerating phase
                return (
                    departure_speed * time_elapsed
                    + 0.5 * self._acceleration_rate * time_elapsed**2
                )
            if time_elapsed < t_to_accelerate + t_cruise:
                # Cruising phase: full accel distance + constant speed segment
                return d_to_accelerate + self._max_speed * (
                    time_elapsed - t_to_accelerate
                )
            if time_elapsed < t_total:
                # Decelerating phase
                t0 = t_to_accelerate + t_cruise
                dt = time_elapsed - t0
                # return (
                #     d_to_accelerate
                #     + self._max_speed * t_cruise
                #     + dt * self._max_speed
                #     - 0.5 * self._deceleration_rate * dt**2
                # )
                return (
                    d_to_accelerate
                    + d_cruise
                    + arrival_speed * dt
                    + self._deceleration_rate
                    * (t_total * dt - ((time_elapsed**2 - t0**2) / 2))
                )
            return distance

        # Triangular profile: cannot reach max_speed; uses v_peak instead
        v_at_peak = (
            (
                2 * distance * self._acceleration_rate * self._deceleration_rate
                + self._acceleration_rate * (arrival_speed**2)
                + self._deceleration_rate * (departure_speed**2)
            )
            / (self._acceleration_rate + self._deceleration_rate)
        ) ** 0.5
        t_to_peak = (v_at_peak - departure_speed) / self._acceleration_rate
        t_to_decelerate = v_at_peak / self._deceleration_rate
        t_total = t_to_peak + t_to_decelerate

        if time_elapsed < t_to_peak:
            # Accelerating phase
            return (
                departure_speed * time_elapsed
                + 0.5 * self._acceleration_rate * time_elapsed**2
            )
        if time_elapsed < t_total:
            dt = time_elapsed - t_to_peak
            d_to_peak = (
                departure_speed * t_to_peak
                + 0.5 * self._acceleration_rate * t_to_peak**2
            )
            return (
                d_to_peak
                + arrival_speed * dt
                + self._deceleration_rate
                * (t_total * dt - ((time_elapsed**2 - t_to_peak**2) / 2))
            )

            # return d_to_peak + dt * v_at_peak - 0.5 * self._deceleration_rate * dt**2

        return distance

    def get_total_duration(
        self,
        distance: float,
        departure_speed: float = 0.0,
        arrival_speed: float = 0.0,
    ) -> float:
        """
        Compute the total time required to complete the motion over a given distance,
        from the specified departure speed down to the arrival speed, respecting
        the maximum speed, acceleration, and deceleration.

        Args:
            distance (float): Total distance to travel.
            departure_speed (float, optional): Speed at the start of the motion. Defaults to 0.0.
            arrival_speed (float, optional): Speed at the end of the motion. Defaults to 0.0.

        Returns:
            float: Total time (seconds) to finish the trajectory.
        """
        d_to_accelerate = (self._max_speed**2 - departure_speed**2) / (
            2 * self._acceleration_rate
        )
        d_to_decelerate = (self._max_speed**2 - arrival_speed**2) / (
            2 * self._deceleration_rate
        )
        d_cruise = distance - (d_to_accelerate + d_to_decelerate)

        t_to_accelerate = (self._max_speed - departure_speed) / self._acceleration_rate
        t_to_decelerate = (self._max_speed - arrival_speed) / self._deceleration_rate
        t_cruise = d_cruise / self._max_speed

        # Trapezoidal profile: distance is sufficient to reach maximum speed
        if distance >= d_to_accelerate + d_to_decelerate:
            return t_to_accelerate + t_cruise + t_to_decelerate

        # Triangular profile: distance is too short to reach maximum speed
        v_at_peak = (
            (
                2 * distance * self._acceleration_rate * self._deceleration_rate
                + self._acceleration_rate * (arrival_speed**2)
                + self._deceleration_rate * (departure_speed**2)
            )
            / (self._acceleration_rate + self._deceleration_rate)
        ) ** 0.5
        t_to_peak = (v_at_peak - departure_speed) / self._acceleration_rate
        t_to_decelerate = v_at_peak / self._deceleration_rate
        t_total = t_to_peak + t_to_decelerate
        return t_total
