"""Convenience imports for geometry primitives and helpers."""

# Native shapely geometry
from shapely import (
    BufferCapStyle,
    BufferJoinStyle,
    Geometry,
    LinearRing,
    LineString,
    MultiPoint,
    MultiPolygon,
    Point,
    Polygon,
    distance,
    is_empty,
    prepare,
)
from shapely.affinity import rotate, translate
from shapely.geometry import box
from shapely.ops import nearest_points

# Geometry helpers; No shapely native geometry
from geometry.helpers import create_straight_rectangle
from geometry.oriented_point import OrientedPoint

__all__ = [
    "BufferCapStyle",
    "BufferJoinStyle",
    "Geometry",
    "LineString",
    "LinearRing",
    "MultiPoint",
    "MultiPolygon",
    "OrientedPoint",
    "Point",
    "Polygon",
    "box",
    "create_straight_rectangle",
    "distance",
    "is_empty",
    "nearest_points",
    "prepare",
    "rotate",
    "translate",
]
