from shapely import (
    Point,
    Polygon,
    MultiPolygon,
    LineString,
    BufferCapStyle,
    BufferJoinStyle,
    Geometry,
    geometry,
    prepare,
    distance,
)

from shapely.affinity import scale


def create_straight_rectangle(p1: Point, p2: Point) -> Polygon:
    return geometry.box(
        min(p1.x, p2.x), min(p1.y, p2.y), max(p1.x, p2.x), max(p1.y, p2.y)
    )


class OrientedPoint:
    def __init__(self, x: float, y: float, theta: float = 0.0):
        self.__point = Point(x, y)
        self.theta = theta

    def __getattr__(self, attr):
        """Redirect all other attribute calls to the point object"""
        return getattr(self.__point, attr)
