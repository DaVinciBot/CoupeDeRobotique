from config_loader import CONFIG

from boombot_strategy.tasks.navigation_tasks import NavigationTask
from navigation import (
    StopAndWaitAvoidanceParams,
    BasicPathPlannerParams,
    SequentialTrajectoryPlannerParams,
    Direction,
    TrajectoryPlanCommand,
)
from navigation.avoidance.acs_detection_profiles.rectangular_projection_acs_detection_profile import (
    RectangularProjectionAcsDetectionProfileParams,
)
import time


class GoToColorReservedZoneToFinishGame(NavigationTask):
    def __init__(self, color_reserved_zone_id: int):
        super().__init__(
            goal=color_reserved_zone_id,
            path_planner_params=BasicPathPlannerParams(),
            trajectory_planner_params=SequentialTrajectoryPlannerParams(),
            speed_profiler=CONFIG.ROLLING_BASIS_DEFAULT_SPEED_PROFILER,  # Be fast to finish the game
            avoidance_params=StopAndWaitAvoidanceParams(timeout=30),
            acs_detection_profile_params=RectangularProjectionAcsDetectionProfileParams(
                acs_distance=50, width_view=40
            ),
        )


class GoToColorReservedZoneToConstruct(NavigationTask):
    def __init__(self, color_reserved_zone_id: int):
        super().__init__(
            goal=color_reserved_zone_id,
            path_planner_params=BasicPathPlannerParams(),
            trajectory_planner_params=SequentialTrajectoryPlannerParams(),
            speed_profiler=CONFIG.ROLLING_BASIS_DEFAULT_SPEED_PROFILER,  # Be careful to construct
            avoidance_params=StopAndWaitAvoidanceParams(timeout=30),
            acs_detection_profile_params=RectangularProjectionAcsDetectionProfileParams(
                acs_distance=50, width_view=40
            ),
        )

    def handle(self, ctx):
        if not self._is_initialized:
            self._initialize(ctx)

        cmd: TrajectoryPlanCommand = self.navigator_task.handle(
            ally_zone=ctx.arena.ally_zone,
            enemy_zone=ctx.arena.enemy_zone,
        )

        ctx.rolling_basis.set_target_position(cmd.get_position_command())
        if not self.navigator_task.state.is_finished():
            return False
        else:
            time.sleep(1)
            return True
