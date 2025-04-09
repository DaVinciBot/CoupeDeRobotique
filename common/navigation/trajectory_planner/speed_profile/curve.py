class Curve:
    """
    Represents a trajectory curve with three phases: departure, max speed, and arrival.
    """

    def __init__(
        self,
        departure_speed: float,
        max_speed: float,
        arrival_speed: float,
        total_distance: float,
        acceleration_max: float,
        deceleration_max: float,
    ) -> None:
        """
        Initializes the Curve object with the given parameters.

        Args:
            departure_speed (float): Initial speed at the start of the trajectory.
            max_speed (float): Maximum speed during the trajectory.
            arrival_speed (float): Final speed at the end of the trajectory.
            total_distance (float): Total distance to be covered.
            acceleration_max (float): Maximum acceleration during the departure phase.
            deceleration_max (float): Maximum deceleration during the arrival phase.
        """
        self._acceleration_rate = acceleration_max
        self._deceleration_rate = deceleration_max

        self._departure_speed = departure_speed
        self._cruise_speed = max_speed
        self._arrival_speed = arrival_speed

        self._total_distance = total_distance
        self._distance_to_accelerate = (max_speed**2 - departure_speed**2) / (
            2 * acceleration_max
        )
        self._distance_to_decelerate = (max_speed**2 - arrival_speed**2) / (
            2 * deceleration_max
        )
        self._cruise_distance = (
            self._total_distance
            - self._distance_to_accelerate
            - self._distance_to_decelerate
        )

        self._time_to_accelerate = (
            self._cruise_speed - self._departure_speed
        ) / self._acceleration_rate
        self._cruise_time = self._cruise_distance / self._cruise_speed
        self._time_to_decelerate = (
            self._cruise_speed - self._arrival_speed
        ) / self._deceleration_rate
        self._total_time = (
            self._time_to_accelerate + self._cruise_time + self._time_to_decelerate
        )

    def _compute_departure_speed_at_t(self, t) -> float:
        """
        Computes the speed during the departure phase at a given time.

        Args:
            t (float): Time elapsed since the start of the trajectory.

        Returns:
            float: Speed at time t during the departure phase.
        """
        return self._departure_speed + self._acceleration_rate * t

    def _compute_arrival_speed_at_t(self, t) -> float:
        """
        Computes the speed during the arrival phase at a given time.

        Args:
            t (float): Time elapsed since the start of the trajectory.

        Returns:
            float: Speed at time t during the arrival phase.
        """
        return self._arrival_speed + self._deceleration_rate * (self._total_time - t)

    def get_speed(self, t) -> float:
        """
        Retrieves the current speed at a given time based on the trajectory plan.

        Args:
            t (float): Time elapsed since the start of the trajectory.

        Returns:
            float: Current speed at time t.
        """
        if t < self._total_time:
            speeds = [
                self._compute_departure_speed_at_t(t),
                self._cruise_speed,
                self._compute_arrival_speed_at_t(t),
            ]
            return min([i for i in speeds if i >= 0])

        return self._arrival_speed

    def get_distance(self, t) -> float:
        """
        Computes the current position at a given time based on the trajectory plan.

        Args:
            t (float): Time elapsed since the start of the trajectory.

        Returns:
            float: Current position at time t.
        """
        if t <= self._time_to_accelerate:
            return self._departure_speed * t + 0.5 * self._acceleration_rate * t**2
        if t <= self._time_to_accelerate + self._cruise_time:
            dt = t - self._time_to_accelerate
            return self._distance_to_accelerate + self._cruise_speed * dt
        # Intégrale de la vitesse : v(τ) = arrival_speed + deceleration_rate * (total_time - τ)
        # sur l'intervalle τ ∈ [t0, t].
        #
        # Formule :
        # dist_decel = ∫[t0->t] [arrival_speed + deceleration_rate * (total_time - τ)] dτ
        #            = arrival_speed * (t - t0)
        #
        if t <= self._total_time:
            t0 = self._time_to_accelerate + self._cruise_time
            dt = t - t0
            return (
                self._distance_to_accelerate
                + self._cruise_distance
                + self._arrival_speed * dt
                + self._deceleration_rate
                * (self._total_time * dt - ((t**2 - t0**2) / 2))
            )

        return self._total_distance

    def get_total_duration(self) -> float:
        """
        Retrieves the total time required to complete the trajectory.

        Returns:
            float: Total time of the trajectory.
        """
        return self._total_time
