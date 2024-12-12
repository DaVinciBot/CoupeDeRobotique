from geometry.geometry import (
    create_straight_rectangle,
    OrientedPoint,
)

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
    geometry,
    prepare,
    distance,
)

from shapely.ops import nearest_points
from shapely import is_empty

from shapely.geometry import box
