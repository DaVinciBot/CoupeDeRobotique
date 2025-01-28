# ====== Internal Project Imports ======
from shapely import (
    Point,
    Polygon,
)
from shapely.geometry import box


def create_straight_rectangle(p1: Point, p2: Point) -> Polygon:
    return box(
        min(p1.x, p2.x), min(p1.y, p2.y), max(p1.x, p2.x), max(p1.y, p2.y)
    )
