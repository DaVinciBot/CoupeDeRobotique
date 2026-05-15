"""Generic maneuver tasks such as relative moves and zone centroids."""

from __future__ import annotations

from typing import TYPE_CHECKING, override

from a_config_loader import CONFIG
from boombot_strategy.tasks.navigation_tasks.navigation_task import NavigationTask
from geometry import OrientedPoint, distance
from navigation.avoidance.acs_detection_profiles.rectangular_projection_acs_detection_profile import (  # noqa: E501
    RectangularProjectionAcsDetectionProfileParams,
)
from navigation.avoidance.no_avoidance import NoAvoidanceParams
from navigation.avoidance.stop_and_wait_avoidance import StopAndWaitAvoidanceParams
from navigation.navigator.task import NavigatorTask, NavigatorTaskParams
from navigation.path_planner import Direction
from navigation.path_planner.basic_path_planner import (
    BasicPathPlannerParams,
)
from navigation.path_planner.delta_path_planner import DeltaPathPlannerParams
from navigation.trajectory_planner.sequential_trajectory_planner import (
    SequentialTrajectoryPlannerParams,
)

if TYPE_CHECKING:
    from boombot_strategy.winter_game_context import WinterGameContext
    from strategy.core import BaseGameContext


class RelativeBackward(NavigationTask):
    """Navigation task to move the robot a specified distance backward."""

    def __init__(
        self,
        distance: float,
        position_reached_tolerance_cm: float = 1.0,
        angle_reached_tolerance_rad: float = 0.05,
        finish_after_expected_end_delay_s: float | None = None,
    ) -> None:
        """Initialize the RelativeBackward task.

        Args:
            distance (float): The distance to move backward in centimeters.
        """
        super().__init__(
            goal=None,
            path_planner_params=DeltaPathPlannerParams(distance=-distance),
            trajectory_planner_params=SequentialTrajectoryPlannerParams(
                direction=Direction.BACKWARD,
                respect_goal_orientation=False,
            ),
            speed_profiler=CONFIG.ROLLING_BASIS_DEFAULT_SPEED_PROFILER,
            avoidance_params=NoAvoidanceParams(),
            acs_detection_profile_params=RectangularProjectionAcsDetectionProfileParams(
                10,
                35,
            ),
            stabilization_delay=1,  # Delay to stabilize after moving backward
            timeout=20,
            points=0,
            position_reached_tolerance_cm=position_reached_tolerance_cm,
            angle_reached_tolerance_rad=angle_reached_tolerance_rad,
            finish_after_expected_end_delay_s=finish_after_expected_end_delay_s,
        )
        self.estimated_duration = (
            self.speed_profiler.linear_speed_profile.get_total_duration(
                distance=abs(distance),
            )
        )


class RelativeForward(NavigationTask):
    """Navigation task to move the robot a specified distance forward."""

    def __init__(
        self,
        distance: float,
        position_reached_tolerance_cm: float = 1.0,
        angle_reached_tolerance_rad: float = 0.05,
        finish_after_expected_end_delay_s: float | None = None,
    ) -> None:
        """Initialize the RelativeForward task.

        Args:
            distance (float): The distance to move forward in centimeters.
        """
        super().__init__(
            goal=None,
            path_planner_params=DeltaPathPlannerParams(distance=distance),
            trajectory_planner_params=SequentialTrajectoryPlannerParams(),
            speed_profiler=CONFIG.ROLLING_BASIS_DEFAULT_SPEED_PROFILER,
            avoidance_params=StopAndWaitAvoidanceParams(timeout=20),
            acs_detection_profile_params=RectangularProjectionAcsDetectionProfileParams(
                55,
                90,
            ),
            stabilization_delay=0.5,  # Delay to stabilize after moving forward
            position_reached_tolerance_cm=position_reached_tolerance_cm,
            angle_reached_tolerance_rad=angle_reached_tolerance_rad,
            finish_after_expected_end_delay_s=finish_after_expected_end_delay_s,
        )


class RelativeRotation(NavigationTask):
    """Navigation task to rotate the robot by a specified angle."""

    def __init__(
        self,
        angle: float,
        position_reached_tolerance_cm: float = 1.0,
        angle_reached_tolerance_rad: float = 0.05,
        finish_after_expected_end_delay_s: float | None = None,
    ) -> None:
        """Initialize the RelativeRotation task.

        Args:
            angle (float): The angle to rotate in radians.
        """
        super().__init__(
            goal=None,
            path_planner_params=DeltaPathPlannerParams(rotation=angle),
            trajectory_planner_params=SequentialTrajectoryPlannerParams(),
            speed_profiler=CONFIG.ROLLING_BASIS_SLOW_SPEED_PROFILER,
            avoidance_params=NoAvoidanceParams(),
            acs_detection_profile_params=RectangularProjectionAcsDetectionProfileParams(
                10,
                35,
            ),
            stabilization_delay=0.5,  # Delay to stabilize after moving forward
            points=0,
            position_reached_tolerance_cm=position_reached_tolerance_cm,
            angle_reached_tolerance_rad=angle_reached_tolerance_rad,
            finish_after_expected_end_delay_s=finish_after_expected_end_delay_s,
        )
        self.estimated_duration = (
            self.speed_profiler.angular_speed_profile.get_total_duration(
                distance=abs(angle),
            )
        )


class GoCentroidOfZone(NavigationTask):
    """Navigation task to go to the centroid of a given zone."""

    def __init__(self, zone_id: int) -> None:
        """Initialize the GoCentroidOfZone task.

        Args:
            zone_id (int): The ID of the target zone.
        """
        super().__init__(
            goal=zone_id,
            path_planner_params=BasicPathPlannerParams(),
            trajectory_planner_params=SequentialTrajectoryPlannerParams(
                step_sleep_delay=2,
            ),
            speed_profiler=CONFIG.ROLLING_BASIS_SLOW_SPEED_PROFILER,
            avoidance_params=StopAndWaitAvoidanceParams(timeout=20),
            acs_detection_profile_params=RectangularProjectionAcsDetectionProfileParams(
                acs_distance=55,
                width_view=40,
            ),
            stabilization_delay=0.5,
            points=0,
        )
        self.zone_id: int = zone_id
        self._is_initialized: bool = False
        self.navigator_task: NavigatorTask
        self.estimated_duration = self.compute_estimated_duration

    def compute_estimated_duration(self, ctx: WinterGameContext) -> float:
        """Estimate the duration to reach the centroid of the zone.

        Args:
            ctx (WinterGameContext): The game context providing arena information.

        Returns:
            float: Estimated duration in seconds.
        """
        centroid: OrientedPoint = OrientedPoint.from_point(
            ctx.arena.zones[self.zone_id].polygon.centroid,
        )
        dist: float = float(distance(centroid, ctx.arena.ally_zone.point))
        return (
            self.speed_profiler.linear_speed_profile.get_total_duration(
                distance=dist,
            )
            + self.stabilization_delay
        )

    @override
    def _initialize(self, ctx: BaseGameContext) -> None:
        """Initialize by computing the target position from the zone centroid.

        Args:
            ctx (BaseGameContext): The game context providing arena information.
        """
        self._is_initialized = True

        # Compute the goal position with orientation
        centroid: OrientedPoint = OrientedPoint.from_point(
            ctx.arena.zones[self.zone_id].polygon.centroid,
        )

        # Create a NavigatorTask using the calculated goal
        self.navigator_task = NavigatorTask(
            params=NavigatorTaskParams(
                goal=centroid,
                timeout=self.timeout,
                position_reached_tolerance_cm=self.position_reached_tolerance_cm,
                angle_reached_tolerance_rad=self.angle_reached_tolerance_rad,
                finish_after_expected_end_delay_s=(
                    self.finish_after_expected_end_delay_s
                ),
                path_planner_params=self.path_planner_params,
                trajectory_planner_params=self.trajectory_planner_params,
                speed_profiler=self.speed_profiler,
                avoidance_params=self.avoidance_params,
                acs_detection_profile_params=self.acs_detection_profile_params,
                stabilization_delay=self.stabilization_delay,
            ),
        )


class GoToOrientedPoint(NavigationTask):
    """Navigation task to go to a specific oriented point."""

    def __init__(self, target: OrientedPoint) -> None:
        """Initialize the GoToOrientedPoint task.

        Args:
            target (OrientedPoint): The target position and orientation.
        """
        super().__init__(
            goal=target,
            path_planner_params=BasicPathPlannerParams(),
            trajectory_planner_params=SequentialTrajectoryPlannerParams(
                step_sleep_delay=2,
            ),
            speed_profiler=CONFIG.ROLLING_BASIS_DEFAULT_SPEED_PROFILER,
            avoidance_params=StopAndWaitAvoidanceParams(timeout=20),
            acs_detection_profile_params=RectangularProjectionAcsDetectionProfileParams(
                acs_distance=55,
                width_view=40,
            ),
            stabilization_delay=2,
        )
