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
)


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

    def __add__(self, p: object) -> object:
        return OrientedPoint(
            self.__point.x + p.x, self.__point.y + p.y, self.theta + p.theta
        )

    def __sub__(self, p: object) -> object:
        return OrientedPoint(
            self.__point.x + p.x, self.__point.y - p.y, self.theta - p.theta
        )

    def __str__(self) -> str:
        return f"Point(x={self.__point.x}, y={self.__point.y}, theta={self.theta})"

    def __repr__(self) -> str:
        return self.__str__()
