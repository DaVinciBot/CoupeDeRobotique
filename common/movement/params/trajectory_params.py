import math

from movement.params.speed_profile import SpeedProfile
from geometry import OrientedPoint, Point
from arena import BaseArenaZone


class TrajectoryParams:
    def __init__(
            self,
            speed_profile: SpeedProfile,
            goal: Point | OrientedPoint | BaseArenaZone | int,
            resolution: int,
            smooth_trajectory: bool = True,
            go_backwards: bool = False
    ) -> None:
        self.speed_profile: SpeedProfile = speed_profile
        self.goal: OrientedPoint | BaseArenaZone = goal
        self.resolution: int = resolution
        self.smooth_trajectory: bool = smooth_trajectory
        self.go_backwards: bool = go_backwards

        if self.go_backwards:
            OrientedPoint._id_to_attrs[str(id(self.goal))]["theta"] += math.pi

    def __str__(self):
        return (
            f"TrajectoryParams: speed_profile={self.speed_profile}, "
            f"goal={self.goal}, "
            f"resolution={self.resolution}, "
            f"smooth_trajectory={self.smooth_trajectory}, "
            f"go_backwards={self.go_backwards}"
        )

    def __eq__(self, other):
        if not isinstance(other, TrajectoryParams):
            return False
        return (
                self.speed_profile == other.speed_profile
                and self.goal == other.goal
                and self.resolution == other.resolution
                and self.smooth_trajectory == other.smooth_trajectory
                and self.go_backwards == other.go_backwards
        )

    def __ne__(self, other):
        return not self.__eq__(other)
