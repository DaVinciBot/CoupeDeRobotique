"""Trajectory segment representing a pause in motion."""

from __future__ import annotations

from navigation.trajectory_planner.segments.base_segment import BaseSegment


class StopSegment(BaseSegment):
    """Segment representing a stop or pause in the trajectory."""
