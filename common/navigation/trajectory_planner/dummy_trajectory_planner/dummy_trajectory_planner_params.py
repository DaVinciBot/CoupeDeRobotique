from navigation.trajectory_planner.base_trajectory_planner.base_trajectory_planner_params import \
    BaseTrajectoryPlannerParams


class DummyTrajectoryPlannerParams(BaseTrajectoryPlannerParams):
    def __init__(self, step_sleep_delay: float = 0.0) -> None:
        self.step_sleep_delay: float = step_sleep_delay
        super().__init__()
