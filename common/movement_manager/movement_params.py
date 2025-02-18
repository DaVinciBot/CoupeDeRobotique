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
