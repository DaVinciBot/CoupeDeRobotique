from dataclasses import dataclass
from geometry import OrientedPoint


@dataclass
class LineSegment:
    start: OrientedPoint
    end: OrientedPoint
    duration: float
    direction: float  # orientation constante sur le segment (en radians)
