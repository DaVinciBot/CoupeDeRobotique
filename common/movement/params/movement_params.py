from rolling_basis_handler import SpeedProfile
from geometry import OrientedPoint
from arena import BaseArenaZone


class GoToParams:
    def __init__(
            self,
            initial_linear_speed: float,
            initial_angular_speed: float,
            speed_profile: SpeedProfile,
            goal: OrientedPoint,
            acs_distance: float,
            path_finder_recompute_distance: float,
            timeout: float = -1.0,
            is_mandatory: bool = False,
            smooth_trajectory: bool = True,
            goal_tolerance: float = 0.1,
    ) -> None:
        self.initial_linear_speed: float = initial_linear_speed
        self.initial_angular_speed: float = initial_angular_speed
        self.speed_profile: SpeedProfile = speed_profile
        self.acs_distance: float = acs_distance
        self.timeout: float = timeout
        self.goal: OrientedPoint | BaseArenaZone = goal
        self.is_mandatory: bool = is_mandatory
        self.smooth_trajectory: bool = smooth_trajectory
        self.path_finder_recompute_distance: float = path_finder_recompute_distance
        self.goal_tolerance: float = goal_tolerance

    def __str__(self):
        return (
            f"GoToParams: initial_linear_speed={self.initial_linear_speed}, "
            f"initial_angular_speed={self.initial_angular_speed}, "
            f"speed_profile={self.speed_profile}, goal={self.goal}, "
            f"acs_distance={self.acs_distance}, "
            f"path_finder_recompute_distance={self.path_finder_recompute_distance}, "
            f"timeout={self.timeout}, "
            f"is_mandatory={self.is_mandatory}, "
            f"smooth_trajectory={self.smooth_trajectory}, "
            f"goal_tolerance={self.goal_tolerance}"
        )

    def __eq__(self, other):
        if not isinstance(other, GoToParams):
            return False
        return (
                self.initial_linear_speed == other.initial_linear_speed
                and self.initial_angular_speed == other.initial_angular_speed
                and self.speed_profile == other.speed_profile
                and self.goal == other.goal
                and self.acs_distance == other.acs_distance
                and self.timeout == other.timeout
                and self.is_mandatory == other.is_mandatory
                and self.smooth_trajectory == other.smooth_trajectory
                and self.path_finder_recompute_distance == other.path_finder_recompute_distance
                and self.goal_tolerance == other.goal_tolerance
        )

    def __ne__(self, other):
        return not self.__eq__(other)
