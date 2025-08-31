"""Helper functions for creating simple geometric shapes."""

from __future__ import annotations

from typing import TYPE_CHECKING

from shapely.geometry import box

if TYPE_CHECKING:
    from shapely import Point, Polygon


def create_straight_rectangle(p1: Point, p2: Point) -> Polygon:
    """Create an axis-aligned rectangle defined by two points.

    Args:
        p1 (Point): First corner of the rectangle.
        p2 (Point): Opposite corner of the rectangle.

    Returns:
        Polygon: Axis-aligned rectangle spanning the two points.

    """
    return box(min(p1.x, p2.x), min(p1.y, p2.y), max(p1.x, p2.x), max(p1.y, p2.y))
