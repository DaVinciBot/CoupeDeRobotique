from movement.params.trajectory_params import TrajectoryParams

from geometry import OrientedPoint
from arena import BaseArenaZone


class GoToParams:
    def __init__(
            self,
            trajectory_params: TrajectoryParams,
            acs_distance: float,
            path_finder_recompute_distance: float,
            timeout: float = -1.0,
            is_mandatory: bool = False,
            goal_tolerance: float = 0.1,
            distance_to_goal_to_dont_recompute_path: float = 0.0,
    ) -> None:
        self.trajectory_params: TrajectoryParams = trajectory_params
        self.acs_distance: float = acs_distance
        self.timeout: float = timeout
        self.is_mandatory: bool = is_mandatory
        self.path_finder_recompute_distance: float = path_finder_recompute_distance
        self.goal_tolerance: float = goal_tolerance
        self.distance_to_goal_to_dont_recompute_path: float = distance_to_goal_to_dont_recompute_path

    def __str__(self):
        return (
            f"GoToParams: trajectory_params={self.trajectory_params}, "
            f"acs_distance={self.acs_distance}, "
            f"path_finder_recompute_distance={self.path_finder_recompute_distance}, "
            f"timeout={self.timeout}, "
            f"is_mandatory={self.is_mandatory}, "
            f"goal_tolerance={self.goal_tolerance}, "
            f"distance_to_goal_to_dont_recompute_path={self.distance_to_goal_to_dont_recompute_path}"
        )

    def __eq__(self, other):
        if not isinstance(other, GoToParams):
            return False
        return (
                self.trajectory_params == other.trajectory_params
                and self.acs_distance == other.acs_distance
                and self.timeout == other.timeout
                and self.is_mandatory == other.is_mandatory
                and self.path_finder_recompute_distance == other.path_finder_recompute_distance
                and self.goal_tolerance == other.goal_tolerance
                and self.distance_to_goal_to_dont_recompute_path == other.distance_to_goal_to_dont_recompute_path
        )

    def __ne__(self, other):
        return not self.__eq__(other)
