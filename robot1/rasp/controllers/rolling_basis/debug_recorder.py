"""Debug recorder for rolling basis telemetry.

This module captures command/state samples over time and exports static artifacts
at the end of execution.
"""

from __future__ import annotations

import csv
import json
import math
import time
from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from pathlib import Path

    from loggerplusplus import Logger

    from geometry import OrientedPoint

_CSV_FIELDS = [
    "time_s",
    "event",
    "target_linear_cm_s",
    "target_angular_rad_s",
    "actual_linear_cm_s",
    "actual_angular_rad_s",
    "linear_error_cm_s",
    "angular_error_rad_s",
    "linear_cmd",
    "angular_cmd",
    "left_pwm",
    "right_pwm",
    "left_ticks",
    "right_ticks",
    "odom_x_cm",
    "odom_y_cm",
    "odom_theta_rad",
]


@dataclass(slots=True)
class _LatestTelemetry:
    target_linear_cm_s: float | None = None
    target_angular_rad_s: float | None = None
    actual_linear_cm_s: float | None = None
    actual_angular_rad_s: float | None = None
    linear_error_cm_s: float | None = None
    angular_error_rad_s: float | None = None
    linear_cmd: float | None = None
    angular_cmd: float | None = None
    left_pwm: int | None = None
    right_pwm: int | None = None
    left_ticks: int | None = None
    right_ticks: int | None = None
    odom_x_cm: float | None = None
    odom_y_cm: float | None = None
    odom_theta_rad: float | None = None


def _normalize_angle(angle: float) -> float:
    """Normalize angle to [-pi, pi).

    Args:
        angle (float): Angle in radians.

    Returns:
        float: Normalized angle in radians.
    """
    normalized = math.fmod(angle + math.pi, 2.0 * math.pi)
    if normalized < 0.0:
        normalized += 2.0 * math.pi
    return normalized - math.pi


class RollingBasisDebugRecorder:
    """Capture telemetry and export static debug artifacts."""

    def __init__(
        self,
        logger: Logger,
        *,
        output_dir: Path,
        file_prefix: str,
        enabled: bool,
        sample_period_s: float = 0.02,
        max_samples: int = 120000,
    ) -> None:
        self._logger = logger
        self._enabled = enabled
        self._output_dir = output_dir
        self._file_prefix = file_prefix
        self._sample_period_s = sample_period_s
        self._max_samples = max_samples

        self._start_time = time.time()
        self._samples: list[dict[str, Any]] = []
        self._latest = _LatestTelemetry()
        self._last_sample_time = 0.0
        self._last_event = "init"

        self._last_pose: OrientedPoint | None = None
        self._last_pose_ts: float | None = None

    @property
    def enabled(self) -> bool:
        """Whether the recorder is enabled."""
        return self._enabled

    def set_target(
        self,
        *,
        linear_speed: float,
        angular_speed: float,
        target_pose: OrientedPoint,
    ) -> None:
        """Update latest target command values."""
        if not self._enabled:
            return

        self._latest.target_linear_cm_s = float(linear_speed)
        self._latest.target_angular_rad_s = float(angular_speed)

        # Keep target_pose in signature for future extensions and call-site symmetry.
        _ = target_pose

    def set_odometry(
        self,
        position: OrientedPoint,
        *,
        measured_linear_speed: float | None = None,
        measured_angular_speed: float | None = None,
    ) -> None:
        """Update latest odometry and optionally compute estimated speeds."""
        if not self._enabled:
            return

        now = time.time()

        linear_speed = measured_linear_speed
        angular_speed = measured_angular_speed
        if self._last_position is not None and self._last_position_ts is not None:
            dt = now - self._last_position_ts
            if dt > 0.0:
                dx = position.x - self._last_position.x
                dy = position.y - self._last_position.y

                if linear_speed is None:
                    if self._last_position.theta is None:
                        linear_speed = math.hypot(dx, dy) / dt
                    else:
                        linear_speed = (
                            math.cos(self._last_position.theta) * dx
                            + math.sin(self._last_position.theta) * dy
                        ) / dt

                if (
                    angular_speed is None
                    and position.theta is not None
                    and self._last_position.theta is not None
                ):
                    dtheta = _normalize_angle(
                        position.theta - self._last_position.theta
                    )
                    angular_speed = dtheta / dt

        self._latest.odom_x_cm = position.x
        self._latest.odom_y_cm = position.y
        self._latest.odom_theta_rad = position.theta

        if linear_speed is not None:
            self._latest.actual_linear_cm_s = float(linear_speed)
        if angular_speed is not None:
            self._latest.actual_angular_rad_s = float(angular_speed)

        if (
            self._latest.target_linear_cm_s is not None
            and self._latest.actual_linear_cm_s is not None
        ):
            self._latest.linear_error_cm_s = (
                self._latest.target_linear_cm_s - self._latest.actual_linear_cm_s
            )

        if (
            self._latest.target_angular_rad_s is not None
            and self._latest.actual_angular_rad_s is not None
        ):
            self._latest.angular_error_rad_s = (
                self._latest.target_angular_rad_s - self._latest.actual_angular_rad_s
            )

        self._last_pose = pose
        self._last_pose_ts = now

    def add_sample(self, *, event: str, force: bool = False) -> None:
        """Append a sample using the latest known values."""
        if not self._enabled:
            return

        now = time.time()
        if not force and self._last_sample_time > 0.0:
            if now - self._last_sample_time < self._sample_period_s:
                return
        self._last_sample_time = now
        self._last_event = event

        sample: dict[str, Any] = {
            "time_s": now - self._start_time,
            "event": event,
            "target_linear_cm_s": self._latest.target_linear_cm_s,
            "target_angular_rad_s": self._latest.target_angular_rad_s,
            "actual_linear_cm_s": self._latest.actual_linear_cm_s,
            "actual_angular_rad_s": self._latest.actual_angular_rad_s,
            "linear_error_cm_s": self._latest.linear_error_cm_s,
            "angular_error_rad_s": self._latest.angular_error_rad_s,
            "linear_cmd": self._latest.linear_cmd,
            "angular_cmd": self._latest.angular_cmd,
            "left_pwm": self._latest.left_pwm,
            "right_pwm": self._latest.right_pwm,
            "left_ticks": self._latest.left_ticks,
            "right_ticks": self._latest.right_ticks,
            "odom_x_cm": self._latest.odom_x_cm,
            "odom_y_cm": self._latest.odom_y_cm,
            "odom_theta_rad": self._latest.odom_theta_rad,
        }
        self._samples.append(sample)
        if len(self._samples) > self._max_samples:
            self._samples.pop(0)

    def get_live_snapshot(self) -> dict[str, float | int | str | None]:
        """Return latest telemetry values for live UI updates."""
        if not self._enabled:
            return {
                "enabled": 0,
                "time_s": 0.0,
                "last_event": "disabled",
                "sample_count": 0,
                "target_linear_cm_s": None,
                "target_angular_rad_s": None,
                "actual_linear_cm_s": None,
                "actual_angular_rad_s": None,
                "linear_error_cm_s": None,
                "angular_error_rad_s": None,
                "odom_x_cm": None,
                "odom_y_cm": None,
                "odom_theta_rad": None,
            }

        return {
            "enabled": 1,
            "time_s": time.time() - self._start_time,
            "last_event": self._last_event,
            "sample_count": len(self._samples),
            "target_linear_cm_s": self._latest.target_linear_cm_s,
            "target_angular_rad_s": self._latest.target_angular_rad_s,
            "actual_linear_cm_s": self._latest.actual_linear_cm_s,
            "actual_angular_rad_s": self._latest.actual_angular_rad_s,
            "linear_error_cm_s": self._latest.linear_error_cm_s,
            "angular_error_rad_s": self._latest.angular_error_rad_s,
            "odom_x_cm": self._latest.odom_x_cm,
            "odom_y_cm": self._latest.odom_y_cm,
            "odom_theta_rad": self._latest.odom_theta_rad,
        }

    def export_report(self, *, reason: str) -> dict[str, Path] | None:
        """Export CSV and metadata JSON files.

        Returns:
            dict[str, Path] | None: Paths of generated artifacts, if any.
        """
        if not self._enabled:
            return None

        self._output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        stem = f"{self._file_prefix}_{timestamp}"

        csv_path = self._output_dir / f"{stem}.csv"
        meta_path = self._output_dir / f"{stem}.json"

        with csv_path.open("w", newline="", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=_CSV_FIELDS)
            writer.writeheader()
            writer.writerows(self._samples)

        metadata = {
            "reason": reason,
            "sample_count": len(self._samples),
            "duration_s": self._samples[-1]["time_s"] if self._samples else 0.0,
            "csv": str(csv_path),
        }
        with meta_path.open("w", encoding="utf-8") as meta_file:
            json.dump(metadata, meta_file, indent=2)

        return {
            "csv": csv_path,
            "metadata": meta_path,
        }
