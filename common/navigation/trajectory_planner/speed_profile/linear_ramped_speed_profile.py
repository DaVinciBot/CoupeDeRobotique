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
from navigation.trajectory_planner.speed_profile.base_speed_profile import BaseSpeedProfile


class LinearRampedSpeedProfile(BaseSpeedProfile):
    """
    Speed profile with linear acceleration and deceleration, optionally constrained by total distance.

    Supports both trapezoidal and triangular profiles depending on whether the maximum speed can be reached
    within the specified distance.

    Attributes:
        acceleration (float): Acceleration rate (m/s²).
        max_speed (float): Maximum speed (m/s).
        deceleration (float): Time duration (s) used to compute deceleration rate or deceleration phase.
    """

    def __init__(self, acceleration: float, max_speed: float, deceleration: float):
        """
        Initialize the LinearRampedSpeedProfile instance.

        Args:
            acceleration (float): Acceleration rate in m/s².
            max_speed (float): Maximum speed in m/s.
            deceleration (float): Duration in seconds for deceleration phase.
        """
        super().__init__(max_speed=max_speed)
        self.acceleration = acceleration
        self.deceleration = deceleration

        # --- Precomputed attributes for efficiency ---
        self._t_acc = max_speed / acceleration  # Time to reach max speed
        self._decel_rate = max_speed / deceleration  # Deceleration rate
        self._d_acc_full = 0.5 * max_speed ** 2 / acceleration  # Distance covered during full acceleration
        self._d_decel_full = 0.5 * max_speed * deceleration  # Distance covered during full deceleration
        self._v_peak_denom = (1 / (2 * acceleration)) + (deceleration / (2 * max_speed))  # Denominator for v_peak calc

    def get_speed(self, time_elapsed: float | None = None, distance: float | None = None) -> float:
        """
        Compute the speed at a given time, with optional distance constraint for trapezoidal or triangular profiles.

        Args:
            time_elapsed (float | None): Time elapsed since motion start in seconds.
            distance (float | None): Total planned distance in meters (optional).

        Returns:
            float: Speed at the given time in meters per second.
        """
        if time_elapsed is None or time_elapsed < 0:
            return 0.0

        # --- Mode without distance constraint ---
        if distance is None:
            if time_elapsed < self._t_acc:
                return self.acceleration * time_elapsed  # Still accelerating

            t_total = self._t_acc + self.deceleration
            if time_elapsed < t_total:
                return max(self.max_speed - self._decel_rate * (time_elapsed - self._t_acc), 0.0)  # Decelerating

            return 0.0  # Motion complete

        # --- Mode with distance constraint ---
        if distance >= self._d_acc_full + self._d_decel_full:
            # Trapezoidal profile: has cruising phase
            d_cruise = distance - (self._d_acc_full + self._d_decel_full)
            t_cruise = d_cruise / self.max_speed
            t_total = self._t_acc + t_cruise + self.deceleration

            if time_elapsed < self._t_acc:
                return self.acceleration * time_elapsed  # Accelerating
            elif time_elapsed < self._t_acc + t_cruise:
                return self.max_speed  # Cruising
            elif time_elapsed < t_total:
                return max(self.max_speed - self._decel_rate * (time_elapsed - self._t_acc - t_cruise),
                           0.0)  # Decelerating
            else:
                return 0.0  # Motion complete

        else:
            # Triangular profile: distance too short to reach max speed
            v_peak = (distance / self._v_peak_denom) ** 0.5
            t_peak = v_peak / self.acceleration
            t_decel = v_peak / self._decel_rate
            t_total = t_peak + t_decel

            if time_elapsed < t_peak:
                return self.acceleration * time_elapsed  # Accelerating to peak
            elif time_elapsed < t_total:
                return max(v_peak - self._decel_rate * (time_elapsed - t_peak), 0.0)  # Decelerating from peak
            else:
                return 0.0  # Motion complete

    def get_distance(self, time_elapsed: float, distance: float | None = None) -> float:
        """
        Compute the cumulative distance traveled from time 0 to t.

        Args:
            time_elapsed (float): Time instant (s).
            distance (float | None): Optional total planned distance in meters.

        Returns:
            float: Cumulative distance traveled (m).
        """
        if time_elapsed <= 0:
            return 0.0

        # --- Unconstrained profile (distance is None) ---
        if distance is None:
            T_total = self._t_acc + self.deceleration
            if time_elapsed < self._t_acc:
                # Accelerating phase: d = 0.5 * a * t^2
                return 0.5 * self.acceleration * time_elapsed ** 2
            elif time_elapsed < T_total:
                # Decelerating phase: add full accel distance and integrate deceleration
                dt = time_elapsed - self._t_acc
                return self._d_acc_full + dt * self.max_speed - 0.5 * self._decel_rate * dt ** 2
            else:
                # Motion complete
                return self._d_acc_full + self._d_decel_full

        # --- Constrained profile ---
        # Check if we have a trapezoidal profile (enough distance to cruise)
        if distance >= self._d_acc_full + self._d_decel_full:
            T_acc = self._t_acc
            d_acc = self._d_acc_full
            d_decel = self._d_decel_full
            t_cruise = (distance - (d_acc + d_decel)) / self.max_speed
            T_total = T_acc + t_cruise + self.deceleration

            if time_elapsed < T_acc:
                # Accelerating phase
                return 0.5 * self.acceleration * time_elapsed ** 2
            elif time_elapsed < T_acc + t_cruise:
                # Cruising phase: full accel distance + constant speed segment
                return d_acc + self.max_speed * (time_elapsed - T_acc)
            elif time_elapsed < T_total:
                # Decelerating phase
                dt = time_elapsed - (T_acc + t_cruise)
                return d_acc + self.max_speed * t_cruise + dt * self.max_speed - 0.5 * self._decel_rate * dt ** 2
            else:
                # Completed trajectory
                return distance
        else:
            # Triangular profile: cannot reach max_speed; uses v_peak instead
            v_peak = (distance / self._v_peak_denom) ** 0.5
            T_peak = v_peak / self.acceleration
            T_decel = v_peak / self._decel_rate
            T_total = T_peak + T_decel

            if time_elapsed < T_peak:
                # Accelerating phase
                return 0.5 * self.acceleration * time_elapsed ** 2
            elif time_elapsed < T_total:
                dt = time_elapsed - T_peak
                d_acc_peak = 0.5 * self.acceleration * T_peak ** 2
                return d_acc_peak + dt * v_peak - 0.5 * self._decel_rate * dt ** 2
            else:
                return distance

    def get_total_duration(self, distance: float) -> float:
        # Trapezoidal profile: distance is sufficient to reach maximum speed
        if distance >= self._d_acc_full + self._d_decel_full:
            d_cruise = distance - (self._d_acc_full + self._d_decel_full)
            t_cruise = d_cruise / self.max_speed
            return self._t_acc + t_cruise + self.deceleration
        else:
            # Triangular profile: distance is too short to reach maximum speed
            v_peak = (distance / self._v_peak_denom) ** 0.5
            t_peak = v_peak / self.acceleration
            t_decel = v_peak / self._decel_rate
            return t_peak + t_decel
