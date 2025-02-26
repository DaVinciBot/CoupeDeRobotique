from movement.trajectory_computer.speed_profile import SpeedProfile
from geometry import OrientedPoint, Point
from arena import BaseArenaZone


class TrajectoryParams:
    def __init__(
            self,
            speed_profile: SpeedProfile,
            goal: Point | OrientedPoint | BaseArenaZone,
            resolution: int,
            smooth_trajectory: bool = True,
    ) -> None:
        self.speed_profile: SpeedProfile = speed_profile
        self.goal: OrientedPoint | BaseArenaZone = goal
        self.resolution: int = resolution
        self.smooth_trajectory: bool = smooth_trajectory
