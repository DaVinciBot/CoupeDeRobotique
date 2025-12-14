"""Integration tests for RollingBasisDummy motion simulation."""

from __future__ import annotations

import math
import time

from geometry import OrientedPoint
from navigation.trajectory_planner.structs import TrajectoryPlanCommand
from robot1.rasp.controllers.rolling_basis.rolling_basis_dummy import RollingBasisDummy


class _StubLogger:
    """Minimal logger stub to satisfy RollingBasisDummy dependencies."""

    def __getattr__(self, _name: str):  # type: ignore[override]
        def _noop(*_args, **_kwargs) -> None:
            return None

        return _noop


def _make_dummy(
    start: OrientedPoint | None = None,
    *,
    enable_realtime_simulation: bool = False,
    realtime_period: float = 0.02,
) -> RollingBasisDummy:
    dummy = RollingBasisDummy(
        logger=_StubLogger(),
        enable_realtime_simulation=enable_realtime_simulation,
        realtime_period=realtime_period,
    )
    if start is not None:
        dummy.set_odometrie(start)
    return dummy


def test_set_target_velocity_does_not_override_odometrie() -> None:
    start = OrientedPoint((0.0, 0.0), 0.0)
    dummy = _make_dummy(start)

    cmd = TrajectoryPlanCommand(
        position=OrientedPoint((50, 50), 1.0),
        linear_speed=0.0,
        angular_speed=0.0,
    )
    dummy.set_target_velocity(cmd)

    assert math.isclose(dummy.odometrie.x, 0.0, abs_tol=1e-9), (
        f"X coordinate mismatch {dummy.odometrie.x}"
    )
    assert math.isclose(dummy.odometrie.y, 0.0, abs_tol=1e-9), (
        f"Y coordinate mismatch {dummy.odometrie.y}"
    )
    assert math.isclose(dummy.odometrie.theta or 0.0, 0.0, abs_tol=1e-9), (
        f"Theta mismatch {dummy.odometrie.theta}"
    )
    assert dummy.target_position == cmd.position


def test_simulate_step_translation() -> None:
    dummy = _make_dummy(OrientedPoint((0.0, 0.0), 0.0))
    cmd = TrajectoryPlanCommand(
        position=OrientedPoint((10, 0.0), 0.0),
        linear_speed=5.0,
        angular_speed=0.0,
    )
    dummy.set_target_velocity(cmd)

    dummy.simulate_step(2.0)  # 5 cm/s for 2 s -> 10 cm forward

    assert math.isclose(dummy.odometrie.x, 10.0, abs_tol=1e-9), (
        f"X coordinate mismatch {dummy.odometrie.x}"
    )
    assert math.isclose(dummy.odometrie.y, 0.0, abs_tol=1e-9), (
        f"Y coordinate mismatch {dummy.odometrie.y}"
    )
    assert math.isclose(dummy.odometrie.theta or 0.0, 0.0, abs_tol=1e-9), (
        f"Theta mismatch {dummy.odometrie.theta or 0.0}"
    )


def test_simulate_step_rotation() -> None:
    dummy = _make_dummy(OrientedPoint((0.0, 0.0), 0.0))
    cmd = TrajectoryPlanCommand(
        position=OrientedPoint((0.0, 0.0), math.pi / 2),
        linear_speed=0.0,
        angular_speed=math.pi / 2,
    )
    dummy.set_target_velocity(cmd)

    dummy.simulate_step(1.0)

    assert math.isclose(dummy.odometrie.x, 0.0, abs_tol=1e-9), (
        f"X coordinate mismatch {dummy.odometrie.x}"
    )
    assert math.isclose(dummy.odometrie.y, 0.0, abs_tol=1e-9), (
        f"Y coordinate mismatch {dummy.odometrie.y}"
    )
    assert math.isclose(dummy.odometrie.theta or 0.0, math.pi / 2, abs_tol=1e-9), (
        f"Theta mismatch {dummy.odometrie.theta or 0.0}"
    )


def test_simulate_step_curve_motion() -> None:
    dummy = _make_dummy(OrientedPoint((0.0, 0.0), 0.0))
    cmd = TrajectoryPlanCommand(
        position=OrientedPoint((0.0, 0.0), 0.0),
        linear_speed=10,
        angular_speed=1,
    )
    dummy.set_target_velocity(cmd)

    dummy.simulate_step(1.0)

    expected_x = math.cos(0.5) * 10.0
    expected_y = math.sin(0.5) * 10.0

    assert math.isclose(dummy.odometrie.x, expected_x, rel_tol=1e-9, abs_tol=1e-9), (
        f"X coordinate mismatch {dummy.odometrie.x}, expected {expected_x}"
    )
    assert math.isclose(dummy.odometrie.y, expected_y, rel_tol=1e-9, abs_tol=1e-9), (
        f"Y coordinate mismatch {dummy.odometrie.y}, expected {expected_y}"
    )
    assert math.isclose(dummy.odometrie.theta or 0.0, 1.0, abs_tol=1e-9), (
        f"Theta mismatch {dummy.odometrie.theta or 0.0}"
    )


def test_real_time_simulation_updates_odometrie() -> None:
    """Background loop should integrate speeds over wall-clock time."""
    dummy = _make_dummy(
        OrientedPoint((0.0, 0.0), 0.0),
        enable_realtime_simulation=True,
        realtime_period=0.01,
    )
    cmd = TrajectoryPlanCommand(
        position=OrientedPoint((0.0, 0.0), 0.0),
        linear_speed=1.0,
        angular_speed=0.0,
    )
    dummy.set_target_velocity(cmd)

    # Wait long enough for a few realtime ticks
    time.sleep(0.05)
    dummy.stop_realtime_simulation()

    assert dummy.odometrie.x > 0.03
    assert math.isclose(dummy.odometrie.y, 0.0, abs_tol=1e-6)


def test_simulate_real_time_step_translation() -> None:
    dummy = _make_dummy(
        OrientedPoint((0.0, 0.0), 0.0),
        enable_realtime_simulation=True,
        realtime_period=0.01,
    )
    cmd = TrajectoryPlanCommand(
        position=OrientedPoint((10, 0.0), 0.0),
        linear_speed=5.0,
        angular_speed=0.0,
    )
    dummy.set_target_velocity(cmd)

    time.sleep(2.0)  # 5 cm/s for 2 s -> 10 cm forward
    dummy.stop_realtime_simulation()

    assert math.isclose(dummy.odometrie.x, 10.0, abs_tol=1e-2), (
        f"X coordinate mismatch {dummy.odometrie.x}"
    )
    assert math.isclose(dummy.odometrie.y, 0.0, abs_tol=1e-2), (
        f"Y coordinate mismatch {dummy.odometrie.y}"
    )
    assert math.isclose(dummy.odometrie.theta or 0.0, 0.0, abs_tol=1e-2), (
        f"Theta mismatch {dummy.odometrie.theta or 0.0}"
    )


def test_simulate_real_time_step_rotation() -> None:
    dummy = _make_dummy(
        OrientedPoint((0.0, 0.0), 0.0),
        enable_realtime_simulation=True,
        realtime_period=0.01,
    )
    cmd = TrajectoryPlanCommand(
        position=OrientedPoint((0.0, 0.0), math.pi / 2),
        linear_speed=0.0,
        angular_speed=math.pi / 2,
    )
    dummy.set_target_velocity(cmd)

    time.sleep(1.0)
    dummy.stop_realtime_simulation()

    assert math.isclose(dummy.odometrie.x, 0.0, abs_tol=1e-2), (
        f"X coordinate mismatch {dummy.odometrie.x}"
    )
    assert math.isclose(dummy.odometrie.y, 0.0, abs_tol=1e-2), (
        f"Y coordinate mismatch {dummy.odometrie.y}"
    )
    assert math.isclose(dummy.odometrie.theta or 0.0, math.pi / 2, abs_tol=1e-2), (
        f"Theta mismatch {dummy.odometrie.theta or 0.0}"
    )


def test_simulate_real_time_step_curve_motion() -> None:
    dummy = _make_dummy(
        OrientedPoint((0.0, 0.0), 0.0),
        enable_realtime_simulation=True,
        realtime_period=0.01,
    )
    cmd = TrajectoryPlanCommand(
        position=OrientedPoint((0.0, 0.0), 0.0),
        linear_speed=10,
        angular_speed=math.pi / 4,
    )
    dummy.set_target_velocity(cmd)

    time.sleep(0.3)
    dummy.stop_realtime_simulation()

    expected_x = math.cos(math.pi / 8 * 0.3) * 3.0
    expected_y = math.sin(math.pi / 8 * 0.3) * 3.0

    assert math.isclose(dummy.odometrie.x, expected_x, rel_tol=1e-9, abs_tol=1e-1), (
        f"X coordinate mismatch {dummy.odometrie.x}, expected {expected_x}"
    )
    assert math.isclose(dummy.odometrie.y, expected_y, rel_tol=1e-9, abs_tol=1e-1), (
        f"Y coordinate mismatch {dummy.odometrie.y}, expected {expected_y}"
    )
    assert math.isclose(
        dummy.odometrie.theta or 0.0,
        math.pi / 4 * 0.3,
        abs_tol=1e-2,
    ), f"Theta mismatch {dummy.odometrie.theta or 0.0}"
