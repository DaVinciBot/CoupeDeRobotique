"""Ensure trajectory planner preserves velocity signs."""

from __future__ import annotations

import math
import types

from geometry import OrientedPoint
from navigation.path_planner import Direction
from navigation.trajectory_planner.sequential_trajectory_planner import (
    SequentialTrajectoryPlanner,
)
from navigation.trajectory_planner.sequential_trajectory_planner.sequential_trajectory_planner_params import (  # noqa: E501
    SequentialTrajectoryPlannerParams,
)
from navigation.trajectory_planner.speed_profile.basic_speed_profile import (
    BasicSpeedProfile,
)
from navigation.trajectory_planner.speed_profile.speed_profiler import SpeedProfiler


def _bind_elapsed(planner: SequentialTrajectoryPlanner, elapsed: float) -> None:
    """Force elapsed time used by get_plan to a deterministic value.

    Args:
        planner (SequentialTrajectoryPlanner): Planner to patch.
        elapsed (float): Elapsed time to return.
    """
    planner._get_trajectory_time_elapsed = types.MethodType(  # type: ignore[method-assign]
        lambda _self: elapsed,
        planner,
    )


def test_linear_speed_is_negative_when_backward() -> None:
    """Backward trajectories must emit negative linear speed."""
    params = SequentialTrajectoryPlannerParams(direction=Direction.BACKWARD)
    profiler = SpeedProfiler(
        linear_speed_profile=BasicSpeedProfile(1.0),
        angular_speed_profile=BasicSpeedProfile(1.0),
    )
    planner = SequentialTrajectoryPlanner(params, profiler)
    planner.plan_trajectory(
        [
            OrientedPoint((0.0, 0.0), 0.0),
            OrientedPoint((1.0, 0.0), 0.0),
        ],
    )
    assert planner.segments_mapper is not None, "Segments mapper should be initialized"
    rotation_duration = planner.segments_mapper.segments[0].duration

    # Position ourselves mid-way through the straight segment
    _bind_elapsed(planner, rotation_duration + 0.5)
    cmd = planner.get_plan()

    assert math.isclose(cmd.linear_speed, -1.0, abs_tol=1e-9), (
        "Linear speed should be negative for backward direction"
    )
    assert math.isclose(cmd.angular_speed, 0.0, abs_tol=1e-9), (
        "Angular speed should be zero on straight segment"
    )


def test_rotation_keeps_direction_sign() -> None:
    """Angular speed should carry the sign of the planned rotation."""
    params = SequentialTrajectoryPlannerParams(direction=Direction.FORWARD)
    profiler = SpeedProfiler(
        linear_speed_profile=BasicSpeedProfile(1.0),
        angular_speed_profile=BasicSpeedProfile(1.0),
    )
    planner = SequentialTrajectoryPlanner(params, profiler)
    planner.plan_trajectory(
        [
            OrientedPoint((0.0, 0.0), math.pi / 2),
            OrientedPoint((1.0, 0.0), 0.0),
        ],
    )
    assert planner.segments_mapper is not None, "Segments mapper should be initialized"
    rotation_duration = planner.segments_mapper.segments[0].duration

    # Stay inside the rotation segment to read angular speed
    _bind_elapsed(planner, rotation_duration / 2.0)
    cmd = planner.get_plan()

    assert math.isclose(cmd.angular_speed, -1.0, abs_tol=1e-9), (
        "Angular speed should be negative for clockwise rotation"
    )
    assert math.isclose(cmd.linear_speed, 0.0, abs_tol=1e-9), (
        "Linear speed should be zero during rotation"
    )


def test_empty_path_returns_safe_stop_command() -> None:
    """Empty paths must not crash and should return a stop command."""
    params = SequentialTrajectoryPlannerParams(direction=Direction.FORWARD)
    profiler = SpeedProfiler(
        linear_speed_profile=BasicSpeedProfile(1.0),
        angular_speed_profile=BasicSpeedProfile(1.0),
    )
    planner = SequentialTrajectoryPlanner(params, profiler)

    planner.plan_trajectory([])
    cmd = planner.get_plan()

    assert math.isclose(cmd.linear_speed, 0.0, abs_tol=1e-9)
    assert math.isclose(cmd.angular_speed, 0.0, abs_tol=1e-9)
    assert math.isclose(cmd.position.x, 0.0, abs_tol=1e-9)
    assert math.isclose(cmd.position.y, 0.0, abs_tol=1e-9)
    assert math.isclose(cmd.position.theta or 0.0, 0.0, abs_tol=1e-9)


def test_single_waypoint_path_stops_on_that_position() -> None:
    """A single-waypoint path should hold that waypoint instead of crashing."""
    params = SequentialTrajectoryPlannerParams(direction=Direction.FORWARD)
    profiler = SpeedProfiler(
        linear_speed_profile=BasicSpeedProfile(1.0),
        angular_speed_profile=BasicSpeedProfile(1.0),
    )
    planner = SequentialTrajectoryPlanner(params, profiler)

    hold_position = OrientedPoint((42.0, 13.0), math.pi / 4)
    planner.plan_trajectory([hold_position])
    cmd = planner.get_plan()

    assert math.isclose(cmd.linear_speed, 0.0, abs_tol=1e-9)
    assert math.isclose(cmd.angular_speed, 0.0, abs_tol=1e-9)
    assert math.isclose(cmd.position.x, hold_position.x, abs_tol=1e-9)
    assert math.isclose(cmd.position.y, hold_position.y, abs_tol=1e-9)
    assert cmd.position.theta is not None
    assert hold_position.theta is not None
    assert math.isclose(cmd.position.theta, hold_position.theta, abs_tol=1e-9)
