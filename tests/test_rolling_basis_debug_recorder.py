"""Tests for rolling basis offline debug recorder."""

from __future__ import annotations

import csv

from geometry import OrientedPoint
from robot1.rasp.controllers.rolling_basis.debug_recorder import (
    RollingBasisDebugRecorder,
)


class _StubLogger:
    """Minimal logger stub for recorder tests."""

    def __getattr__(self, _name: str):  # type: ignore[override]
        def _noop(*_args, **_kwargs) -> None:
            return None

        return _noop


def test_recorder_exports_static_artifacts(tmp_path) -> None:
    recorder = RollingBasisDebugRecorder(
        logger=_StubLogger(),
        output_dir=tmp_path,
        file_prefix="rolling_basis",
        enabled=True,
    )

    recorder.set_target(
        linear_speed=10.0,
        angular_speed=1.2,
        target_pose=OrientedPoint((100.0, 200.0), 0.3),
    )
    recorder.add_sample(event="target_velocity")

    recorder.set_odometry(
        OrientedPoint((101.0, 200.0), 0.35),
        measured_linear_speed=9.0,
        measured_angular_speed=1.0,
    )
    recorder.add_sample(event="odometry_update")

    artifacts = recorder.export_report(reason="pytest")

    assert artifacts is not None
    assert artifacts["csv"].exists()
    assert artifacts["metadata"].exists()

    with artifacts["csv"].open(newline="", encoding="utf-8") as csv_file:
        rows = list(csv.DictReader(csv_file))

    assert len(rows) == 2
    assert rows[1]["event"] == "odometry_update"
    assert rows[1]["target_linear_cm_s"] == "10.0"
    assert rows[1]["actual_linear_cm_s"] == "9.0"
    assert rows[1]["left_pwm"] == ""

    live_snapshot = recorder.get_live_snapshot()
    assert live_snapshot["sample_count"] == 2
    assert live_snapshot["last_event"] == "odometry_update"


def test_recorder_disabled_does_not_export(tmp_path) -> None:
    recorder = RollingBasisDebugRecorder(
        logger=_StubLogger(),
        output_dir=tmp_path,
        file_prefix="rolling_basis",
        enabled=False,
    )

    recorder.add_sample(event="ignored")

    assert recorder.export_report(reason="pytest") is None
