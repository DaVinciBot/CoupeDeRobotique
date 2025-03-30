from navigation.trajectory_planner.base_trajectory_planner.base_trajectory_planner_params import \
    BaseTrajectoryPlannerParams


class RampedTrajectoryPlannerParams(BaseTrajectoryPlannerParams):
    def __init__(self, max_speed: float, acceleration: float, deceleration: float):
        self.acceleration = acceleration
        self.deceleration = deceleration
        super().__init__(max_speed)
