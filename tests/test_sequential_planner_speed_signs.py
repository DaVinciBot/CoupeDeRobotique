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
    """Force elapsed time used by get_plan to a deterministic value."""
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
