from navigation.trajectory_planner.speed_profile.base_speed_profile import BaseSpeedProfile


class BasicSpeedProfile(BaseSpeedProfile):
    def __init__(self, speed: float):
        super().__init__(
            max_speed=speed
        )

    def get_speed(self, time_elapsed: float | None = None, distance: float | None = None) -> float:
        return self.max_speed
