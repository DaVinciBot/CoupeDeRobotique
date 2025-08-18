"""Linear ramped speed profile for trapezoidal or triangular motion."""

from __future__ import annotations

from math import sqrt
from typing import override

from navigation.trajectory_planner.speed_profile.base_speed_profile import (
    BaseSpeedProfile,
)


class LinearRampedSpeedProfile(BaseSpeedProfile):
    """Speed profile with acceleration, cruise, and deceleration phases."""

    def __init__(
        self,
        acceleration: float,
        max_speed: float,
        deceleration: float,
    ) -> None:
        """Initialize with acceleration, max speed, and deceleration.

        Args:
            acceleration (float):
                The constant acceleration during the acceleration phase.
            max_speed (float): The maximum allowed cruising speed.
            deceleration (float):
                The constant deceleration during the deceleration phase.

        """
        super().__init__(max_speed=max_speed)
        self.acceleration = acceleration
        self.deceleration = deceleration

    def _compute_trapezoidal_params(
        self,
        departure_speed: float,
        arrival_speed: float,
    ) -> tuple[float, float, float, float]:
        """Computes trapezoidal motion parameters.

        Args:
            departure_speed (float): Speed at the beginning of the motion.
            arrival_speed (float): Speed at the end of the motion.

        Returns:
            tuple[float, float, float, float]: Time to accelerate, time to
                decelerate, distance during acceleration and distance during
                deceleration.

        """
        t_acc = (self._max_speed - departure_speed) / self.acceleration
        t_dec = (self._max_speed - arrival_speed) / self.deceleration
        d_acc = (self._max_speed**2 - departure_speed**2) / (2 * self.acceleration)
        d_dec = (self._max_speed**2 - arrival_speed**2) / (2 * self.deceleration)
        return t_acc, t_dec, d_acc, d_dec

    def _compute_triangular_peak_speed(
        self,
        distance: float,
        departure_speed: float,
        arrival_speed: float,
    ) -> float:
        """Calculate peak speed for triangular profile when no cruise phase.

        Args:
            distance (float): Total distance to travel.
            departure_speed (float): Speed at the start.
            arrival_speed (float): Speed at the end.

        Returns:
            float: Peak speed reached in the triangular profile.

        """
        v_peak_denom = (1 / (2 * self.acceleration)) + (1 / (2 * self.deceleration))
        v_peak_sq = (
            (departure_speed**2 / (2 * self.acceleration))
            + (arrival_speed**2 / (2 * self.deceleration))
            + distance
        ) / v_peak_denom
        return sqrt(v_peak_sq)

    def _speed_time(
        self,
        time_elapsed: float,
        t_acc: float,
        t_dec: float,
        departure_speed: float,
        arrival_speed: float,
    ) -> float:
        if time_elapsed < t_acc:
            return departure_speed + self.acceleration * time_elapsed
        if time_elapsed < t_acc + t_dec:
            return max(
                arrival_speed + self.deceleration * (t_acc + t_dec - time_elapsed),
                arrival_speed,
            )
        return arrival_speed

    def _speed_trapezoidal(
        self,
        time_elapsed: float,
        distance: float,
        t_acc: float,
        t_dec: float,
        d_acc: float,
        d_dec: float,
        departure_speed: float,
        arrival_speed: float,
    ) -> float:
        d_cruise = distance - (d_acc + d_dec)
        t_cruise = d_cruise / self._max_speed
        t_total = t_acc + t_cruise + t_dec
        if time_elapsed < t_acc:
            return departure_speed + self.acceleration * time_elapsed
        if time_elapsed < t_acc + t_cruise:
            return self._max_speed
        if time_elapsed < t_total:
            return max(
                self._max_speed - self.deceleration * (time_elapsed - t_acc - t_cruise),
                arrival_speed,
            )
        return arrival_speed

    def _speed_triangular(
        self,
        time_elapsed: float,
        distance: float,
        departure_speed: float,
        arrival_speed: float,
    ) -> float:
        v_peak = self._compute_triangular_peak_speed(
            distance,
            departure_speed,
            arrival_speed,
        )
        t_peak = (v_peak - departure_speed) / self.acceleration
        t_decel = (v_peak - arrival_speed) / self.deceleration
        t_total = t_peak + t_decel
        if time_elapsed < t_peak:
            return departure_speed + self.acceleration * time_elapsed
        if time_elapsed < t_total:
            return max(
                v_peak - self.deceleration * (time_elapsed - t_peak),
                arrival_speed,
            )
        return arrival_speed

    def _distance_time(
        self,
        time_elapsed: float,
        t_acc: float,
        t_dec: float,
        d_acc: float,
        d_dec: float,
        departure_speed: float,
        arrival_speed: float,
    ) -> float:
        t_total = t_acc + t_dec
        if time_elapsed < t_acc:
            return (
                departure_speed * time_elapsed
                + 0.5 * self.acceleration * time_elapsed**2
            )
        if time_elapsed < t_total:
            dt = time_elapsed - t_acc
            return (
                d_acc
                + arrival_speed * dt
                + self.deceleration
                * (t_total * dt - ((time_elapsed**2 - t_acc**2) / 2))
            )
        return d_acc + d_dec

    def _distance_trapezoidal(
        self,
        time_elapsed: float,
        distance: float,
        t_acc: float,
        t_dec: float,
        d_acc: float,
        d_dec: float,
        departure_speed: float,
        arrival_speed: float,
    ) -> float:
        d_cruise = distance - (d_acc + d_dec)
        t_cruise = d_cruise / self._max_speed
        t_total = t_acc + t_cruise + t_dec

        if time_elapsed < t_acc:
            return (
                departure_speed * time_elapsed
                + 0.5 * self.acceleration * time_elapsed**2
            )
        if time_elapsed < t_acc + t_cruise:
            return d_acc + self._max_speed * (time_elapsed - t_acc)
        if time_elapsed < t_total:
            dt = time_elapsed - (t_acc + t_cruise)
            return (
                d_acc
                + d_cruise
                + arrival_speed * dt
                + self.deceleration
                * (t_total * dt - ((time_elapsed**2 - (t_acc + t_cruise) ** 2) / 2))
            )
        return distance

    def _distance_triangular(
        self,
        time_elapsed: float,
        distance: float,
        departure_speed: float,
        arrival_speed: float,
    ) -> float:
        v_peak = self._compute_triangular_peak_speed(
            distance,
            departure_speed,
            arrival_speed,
        )
        t_peak = (v_peak - departure_speed) / self.acceleration
        t_decel = (v_peak - arrival_speed) / self.deceleration
        t_total = t_peak + t_decel
        if time_elapsed < t_peak:
            return (
                departure_speed * time_elapsed
                + 0.5 * self.acceleration * time_elapsed**2
            )
        if time_elapsed < t_total:
            dt = time_elapsed - t_peak
            d_acc_peak = (v_peak**2 - departure_speed**2) / (2 * self.acceleration)
            return (
                d_acc_peak
                + arrival_speed * dt
                + self.deceleration
                * (t_total * dt - ((time_elapsed**2 - t_peak**2) / 2))
            )
        return distance

    def get_speed(
        self,
        time_elapsed: float | None = None,
        distance: float | None = None,
        departure_speed: float = 0.0,
        arrival_speed: float = 0.0,
    ) -> float:
        """Return the speed at ``time_elapsed``.

        Args:
            time_elapsed (float | None, optional):
                Time since motion started. Defaults to None.
            distance (float | None, optional):
                Total distance to travel. Defaults to None.
            departure_speed (float, optional): Speed at the beginning. Defaults to 0.0.
            arrival_speed (float, optional): Speed at the end. Defaults to 0.0.

        Returns:
            float: Speed at the specified time.

        """
        if time_elapsed is None or time_elapsed < 0:
            return departure_speed

        t_acc, t_dec, d_acc, d_dec = self._compute_trapezoidal_params(
            departure_speed,
            arrival_speed,
        )

        if distance is None:
            return self._speed_time(
                time_elapsed,
                t_acc,
                t_dec,
                departure_speed,
                arrival_speed,
            )

        if distance >= d_acc + d_dec:
            return self._speed_trapezoidal(
                time_elapsed,
                distance,
                t_acc,
                t_dec,
                d_acc,
                d_dec,
                departure_speed,
                arrival_speed,
            )

        return self._speed_triangular(
            time_elapsed,
            distance,
            departure_speed,
            arrival_speed,
        )

    @override
    def get_distance(
        self,
        time_elapsed: float | None = None,
        distance: float | None = None,
        departure_speed: float = 0.0,
        arrival_speed: float = 0.0,
    ) -> float:
        """Return distance traveled at ``time_elapsed``.

        Args:
            time_elapsed (float | None): Elapsed time since start. Defaults to None.
            distance (float | None, optional): Total planned distance. Defaults to None.
            departure_speed (float, optional): Speed at start. Defaults to 0.0.
            arrival_speed (float, optional): Speed at end. Defaults to 0.0.

        Returns:
            float: Distance covered up to the specified time.

        """
        if time_elapsed is None or time_elapsed <= 0:
            return 0.0

        t_acc, t_dec, d_acc, d_dec = self._compute_trapezoidal_params(
            departure_speed,
            arrival_speed,
        )

        if distance is None:
            return self._distance_time(
                time_elapsed,
                t_acc,
                t_dec,
                d_acc,
                d_dec,
                departure_speed,
                arrival_speed,
            )

        if distance >= d_acc + d_dec:
            return self._distance_trapezoidal(
                time_elapsed,
                distance,
                t_acc,
                t_dec,
                d_acc,
                d_dec,
                departure_speed,
                arrival_speed,
            )

        return self._distance_triangular(
            time_elapsed,
            distance,
            departure_speed,
            arrival_speed,
        )

    @override
    def get_total_duration(
        self,
        distance: float,
        departure_speed: float = 0.0,
        arrival_speed: float = 0.0,
    ) -> float:
        """Calculates the total time required to travel the given distance.

        Args:
            distance (float): Total distance to be covered.
            departure_speed (float, optional): Speed at start. Defaults to 0.0.
            arrival_speed (float, optional): Speed at end. Defaults to 0.0.

        Returns:
            float: Total duration of the motion profile.

        """
        t_acc, t_dec, d_acc, d_dec = self._compute_trapezoidal_params(
            departure_speed,
            arrival_speed,
        )

        if distance >= d_acc + d_dec:
            d_cruise = distance - (d_acc + d_dec)
            t_cruise = d_cruise / self._max_speed
            return t_acc + t_cruise + t_dec
        v_peak = self._compute_triangular_peak_speed(
            distance,
            departure_speed,
            arrival_speed,
        )
        t_peak = (v_peak - departure_speed) / self.acceleration
        t_decel = (v_peak - arrival_speed) / self.deceleration
        return t_peak + t_decel
