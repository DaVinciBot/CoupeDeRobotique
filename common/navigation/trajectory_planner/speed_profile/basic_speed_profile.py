from navigation.trajectory_planner.speed_profile.base_speed_profile import BaseSpeedProfile


class BasicSpeedProfile(BaseSpeedProfile):
    def __init__(self, speed: float):
        super().__init__(
            max_speed=speed
        )

    def get_speed(self, time_elapsed: float | None = None, distance: float | None = None) -> float:
        return self.max_speed

    def get_distance(self, time_elapsed: float, distance: float | None = None) -> float:
        return self.max_speed * time_elapsed

    def get_total_duration(self, distance: float) -> float:
        return distance / self.max_speed
