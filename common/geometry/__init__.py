# No shapely native geometry
from geometry.oriented_point import OrientedPoint
# Geometry helpers
from geometry.helpers import create_straight_rectangle

# Native shapely geometry
from shapely import (
    Point,
    MultiPoint,
    Polygon,
    MultiPolygon,
    LineString,
    LinearRing,
    BufferCapStyle,
    BufferJoinStyle,
    Geometry,
    prepare,
    distance,
    is_empty
)
from shapely.geometry import box
from shapely.ops import nearest_points
from shapely import is_empty
