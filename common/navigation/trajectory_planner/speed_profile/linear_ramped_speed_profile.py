# ====== Code Summary ======
# This module defines the LinearRampedSpeedProfile class, which extends a base speed profile
# to generate a trapezoidal or triangular velocity profile for motion planning. It handles
# acceleration, cruising, and deceleration phases, computing speed, distance traveled,
# and total duration based on elapsed time and specified constraints. This is commonly used
# in robotics and autonomous navigation systems to manage smooth and time-efficient motion.

# ====== Standard Library Imports ======
from math import sqrt

# ====== Third-party Library Imports ======
# (None)

# ====== Internal Project Imports ======
from navigation.trajectory_planner.speed_profile.base_speed_profile import (
    BaseSpeedProfile,
)


class LinearRampedSpeedProfile(BaseSpeedProfile):
    """
    Implements a linear ramped speed profile using either trapezoidal or triangular motion profiles
    depending on available distance and speed constraints.
    """

    def __init__(self, acceleration: float, max_speed: float, deceleration: float):
        """
        Initializes the profile with acceleration, max speed, and deceleration.

        Args:
            acceleration (float): The constant acceleration during the acceleration phase.
            max_speed (float): The maximum allowed cruising speed.
            deceleration (float): The constant deceleration during the deceleration phase.
        """
        super().__init__(max_speed=max_speed)
        self.acceleration = acceleration
        self.deceleration = deceleration

    def _compute_trapezoidal_params(self, departure_speed, arrival_speed):
        """
        Computes parameters used in trapezoidal motion profile.

        Args:
            departure_speed (float): Speed at the beginning of the motion.
            arrival_speed (float): Speed at the end of the motion.

        Returns:
            tuple: Time to accelerate, time to decelerate, distance during acceleration
            and distance during deceleration.
        """
        t_acc = (self._max_speed - departure_speed) / self.acceleration
        t_dec = (self._max_speed - arrival_speed) / self.deceleration
        d_acc = (self._max_speed**2 - departure_speed**2) / (2 * self.acceleration)
        d_dec = (self._max_speed**2 - arrival_speed**2) / (2 * self.deceleration)
        return t_acc, t_dec, d_acc, d_dec

    def _compute_triangular_peak_speed(self, distance, departure_speed, arrival_speed):
        """
        Calculates peak speed for triangular profile when cruising is not possible.

        Args:
            distance (float): Total distance to travel.
            departure_speed (float): Speed at the start.
            arrival_speed (float): Speed at the end.
            decel_rate (float): Computed deceleration rate.

        Returns:
            float: Computed peak speed.
        """
        v_peak_denom = (1 / (2 * self.acceleration)) + (1 / (2 * self.deceleration))
        v_peak_sq = (
            (departure_speed**2 / (2 * self.acceleration))
            + (arrival_speed**2 / (2 * self.deceleration))
            + distance
        ) / v_peak_denom
        return sqrt(v_peak_sq)

    def get_speed(
        self, time_elapsed=None, distance=None, departure_speed=0.0, arrival_speed=0.0
    ) -> float:
        """
        Returns the speed at a given time and distance using either trapezoidal or triangular profile.

        Args:
            time_elapsed (float, optional): Time since motion started.
            distance (float, optional): Total distance to travel.
            departure_speed (float): Speed at the beginning.
            arrival_speed (float): Speed at the end.

        Returns:
            float: Current speed at the specified time.
        """
        if time_elapsed is None or time_elapsed < 0:
            return departure_speed

        t_acc, t_dec, d_acc, d_dec = self._compute_trapezoidal_params(
            departure_speed, arrival_speed
        )

        if distance is None:
            # Time-based profile without distance limit
            if time_elapsed < t_acc:
                return departure_speed + self.acceleration * time_elapsed
            elif time_elapsed < t_acc + t_dec:
                return max(
                    arrival_speed + self.deceleration * (t_acc + t_dec - time_elapsed),
                    arrival_speed,
                )

            else:
                return arrival_speed

        if distance >= d_acc + d_dec:
            # Full trapezoidal profile with cruising
            d_cruise = distance - (d_acc + d_dec)
            t_cruise = d_cruise / self._max_speed
            t_total = t_acc + t_cruise + t_dec

            if time_elapsed < t_acc:
                return departure_speed + self.acceleration * time_elapsed
            elif time_elapsed < t_acc + t_cruise:
                return self._max_speed
            elif time_elapsed < t_total:
                return max(
                    self._max_speed
                    - self.deceleration * (time_elapsed - t_acc - t_cruise),
                    arrival_speed,
                )
            else:
                return arrival_speed
        else:
            # Triangular profile (no cruising)
            v_peak = self._compute_triangular_peak_speed(
                distance, departure_speed, arrival_speed
            )
            t_peak = (v_peak - departure_speed) / self.acceleration
            t_decel = (v_peak - arrival_speed) / self.deceleration
            t_total = t_peak + t_decel

            if time_elapsed < t_peak:
                return departure_speed + self.acceleration * time_elapsed
            elif time_elapsed < t_total:
                return max(
                    v_peak - self.deceleration * (time_elapsed - t_peak), arrival_speed
                )
            else:
                return arrival_speed

    def get_distance(
        self, time_elapsed, distance=None, departure_speed=0.0, arrival_speed=0.0
    ) -> float:
        """
        Calculates distance traveled at a given time.

        Args:
            time_elapsed (float): Elapsed time since start.
            distance (float, optional): Total planned distance.
            departure_speed (float): Speed at start.
            arrival_speed (float): Speed at end.

        Returns:
            float: Distance covered up to the specified time.
        """
        if time_elapsed <= 0:
            return 0.0

        t_acc, t_dec, d_acc, d_dec = self._compute_trapezoidal_params(
            departure_speed, arrival_speed
        )

        if distance is None:
            # Time-based profile without distance constraint
            t_total = t_acc + t_dec
            if time_elapsed < t_acc:
                return (
                    departure_speed * time_elapsed
                    + 0.5 * self.acceleration * time_elapsed**2
                )
            elif time_elapsed < t_total:
                dt = time_elapsed - t_acc
                return (
                    d_acc
                    + arrival_speed * dt
                    + self.deceleration
                    * (t_total * dt - ((time_elapsed**2 - t_acc**2) / 2))
                )
            else:
                return d_acc + d_dec

        if distance >= d_acc + d_dec:
            # Full trapezoidal profile with cruise
            d_cruise = distance - (d_acc + d_dec)
            t_cruise = d_cruise / self._max_speed
            t_total = t_acc + t_cruise + t_dec

            if time_elapsed < t_acc:
                return (
                    departure_speed * time_elapsed
                    + 0.5 * self.acceleration * time_elapsed**2
                )
            elif time_elapsed < t_acc + t_cruise:
                return d_acc + self._max_speed * (time_elapsed - t_acc)
            elif time_elapsed < t_total:
                dt = time_elapsed - (t_acc + t_cruise)
                return (
                    d_acc
                    + d_cruise
                    + arrival_speed * dt
                    + self.deceleration
                    * (t_total * dt - ((time_elapsed**2 - (t_acc + t_cruise) ** 2) / 2))
                )
            else:
                return distance
        else:
            # Triangular profile
            v_peak = self._compute_triangular_peak_speed(
                distance, departure_speed, arrival_speed
            )
            t_peak = (v_peak - departure_speed) / self.acceleration
            t_decel = (v_peak - arrival_speed) / self.deceleration
            t_total = t_peak + t_decel

            if time_elapsed < t_peak:
                return (
                    departure_speed * time_elapsed
                    + 0.5 * self.acceleration * time_elapsed**2
                )
            elif time_elapsed < t_total:
                dt = time_elapsed - t_peak
                d_acc_peak = (v_peak**2 - departure_speed**2) / (2 * self.acceleration)
                return (
                    d_acc_peak
                    + arrival_speed * dt
                    + self.deceleration
                    * (t_total * dt - ((time_elapsed**2 - t_peak**2) / 2))
                )
            else:
                return distance

    def get_total_duration(
        self, distance, departure_speed=0.0, arrival_speed=0.0
    ) -> float:
        """
        Calculates the total time required to travel the given distance.

        Args:
            distance (float): Total distance to be covered.
            departure_speed (float): Speed at start.
            arrival_speed (float): Speed at end.

        Returns:
            float: Total duration of the motion profile.
        """
        t_acc, t_dec, d_acc, d_dec = self._compute_trapezoidal_params(
            departure_speed, arrival_speed
        )

        if distance >= d_acc + d_dec:
            d_cruise = distance - (d_acc + d_dec)
            t_cruise = d_cruise / self._max_speed
            return t_acc + t_cruise + t_dec
        else:
            v_peak = self._compute_triangular_peak_speed(
                distance, departure_speed, arrival_speed
            )
            t_peak = (v_peak - departure_speed) / self.acceleration
            t_decel = (v_peak - arrival_speed) / self.deceleration
            return t_peak + t_decel
