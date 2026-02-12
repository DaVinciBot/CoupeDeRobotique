"""Navigation task to reach a color-reserved zone."""

from __future__ import annotations

from typing import TYPE_CHECKING

from a_config_loader import CONFIG
from boombot_strategy.tasks.navigation_tasks.navigation_task import NavigationTask
from navigation.avoidance.acs_detection_profiles.rectangular_projection_acs_detection_profile import (  # noqa: E501
    RectangularProjectionAcsDetectionProfileParams,
)
from navigation.avoidance.stop_and_wait_avoidance import StopAndWaitAvoidanceParams
from navigation.path_planner.astar_path_planner import AStarPathPlannerParams
from navigation.path_planner.structs import Direction
from navigation.trajectory_planner.sequential_trajectory_planner import (
    SequentialTrajectoryPlannerParams,
)

if TYPE_CHECKING:
    from boombot_strategy.winter_game_context import WinterGameContext as GameContext


class GoToColorReservedZoneToFinishGame(NavigationTask):
    """Task to navigate to a color reserved zone to finish the game."""

    def __init__(self, color_reserved_zone_id: int, ctx: GameContext) -> None:
        """Initialize the GoToColorReservedZoneToFinishGame task.

        Args:
            color_reserved_zone_id (int): The ID of the target color reserved zone.
            ctx (GameContext): The current game context.

        Raises:
            ValueError: If the provided color_reserved_zone_id is invalid.
        """
        goal = ctx.arena.compute_goal_position(color_reserved_zone_id)

        if goal is None:
            msg = f"Invalid color reserved zone ID: {color_reserved_zone_id}"
            raise ValueError(msg)

        super().__init__(
            goal=goal,
            path_planner_params=AStarPathPlannerParams(
                grid=ctx.arena.grid_manager.get_static_and_dynamic_grid(),
                path_resolution=5,
                chunk_size=CONFIG.ARENA_CHUNK_SIZE,
                start=ctx.arena.ally_zone.point,
                goal=goal,
                direction=Direction.FORWARD,
            ),
            trajectory_planner_params=SequentialTrajectoryPlannerParams(),
            speed_profiler=CONFIG.ROLLING_BASIS_DEFAULT_SPEED_PROFILER,
            avoidance_params=StopAndWaitAvoidanceParams(timeout=30),
            acs_detection_profile_params=RectangularProjectionAcsDetectionProfileParams(
                acs_distance=50,
                width_view=40,
            ),
            stabilization_delay=0.5,
        )


class GoToColorReservedZoneToConstruct(NavigationTask):
    """Task to navigate to a color reserved zone to construct."""

    def __init__(self, color_reserved_zone_id: int, ctx: GameContext) -> None:
        """Initialize the GoToColorReservedZoneToConstruct task.

        Args:
            color_reserved_zone_id (int): The ID of the target color reserved zone.
            ctx (GameContext): The current game context.

        Raises:
            ValueError: If the provided color_reserved_zone_id is invalid.
        """
        goal = ctx.arena.compute_goal_position(color_reserved_zone_id)

        if goal is None:
            msg = f"Invalid color reserved zone ID: {color_reserved_zone_id}"
            raise ValueError(msg)

        super().__init__(
            goal=goal,
            path_planner_params=AStarPathPlannerParams(
                grid=ctx.arena.grid_manager.get_static_and_dynamic_grid(),
                path_resolution=5,
                chunk_size=CONFIG.ARENA_CHUNK_SIZE,
                start=ctx.arena.ally_zone.point,
                goal=goal,
                direction=Direction.FORWARD,
            ),
            trajectory_planner_params=SequentialTrajectoryPlannerParams(),
            speed_profiler=CONFIG.ROLLING_BASIS_DEFAULT_SPEED_PROFILER,
            avoidance_params=StopAndWaitAvoidanceParams(timeout=30),
            acs_detection_profile_params=RectangularProjectionAcsDetectionProfileParams(
                acs_distance=55,
                width_view=40,
            ),
            stabilization_delay=1,  # Delay to stabilize before construction
        )
