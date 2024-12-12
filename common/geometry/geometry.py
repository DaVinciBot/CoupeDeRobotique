from typing import Any, ClassVar, Dict, Tuple

from shapely import (
    Point,
    Polygon,
)

import shapely.geometry as geometry


def create_straight_rectangle(p1: Point, p2: Point) -> Polygon:
    return geometry.box(
        min(p1.x, p2.x), min(p1.y, p2.y), max(p1.x, p2.x), max(p1.y, p2.y)
    )


### Point inheritance: cf https://github.com/shapely/shapely/issues/1233
# Very weird but works; if not possible for some reason, maybe just migrate to a composition of Point and float instead
# cf Jupyter notebook in common/arena for different versions tested, this is a version that supports both tuple, theta and x, y, theta initialization and has explicit str conversions for less ide warnings (combination of OrientedPoint2 and 3 as I am writing this). It's the slowest, but not by much, and allows the fullest compatibility with Point and shapely as a whole.


class OrientedPoint(Point):
    _id_to_attrs: ClassVar[Dict[str, Any]] = {}

    __slots__ = (
        Point.__slots__
    )  # slots must be the same for assigning __class__ - https://stackoverflow.com/a/52140968

    theta: float  # For documentation generation and static type checking

    def __init__(
        self,
        x_or_coords: float | Tuple[float, float],
        y_or_theta: float | None = None,
        theta: float = 0.0,
    ) -> (
        None
    ):  # if theta is not optional or if the structure of the arguments change (eg: self, x, y, theta) then MultiPoint becomes impossible with OrientedPoint
        self._id_to_attrs[str(id(self))] = dict(
            theta=(
                theta
                if not isinstance(x_or_coords, Tuple)
                else (0.0 if y_or_theta is None else y_or_theta)
            )
        )

    def __new__(
        cls,
        x_or_coords: float | Tuple[float, float],
        y: float | None = None,
        *args,
        **kwargs,
    ) -> "OrientedPoint":
        if isinstance(x_or_coords, Tuple):
            point = super().__new__(cls, x_or_coords)
        else:
            point = super().__new__(cls, x_or_coords, y)

        point.__class__ = cls
        return point

    def __del__(self) -> None:
        del self._id_to_attrs[str(id(self))]

    def __getattr__(self, name: str) -> Any:
        try:
            return OrientedPoint._id_to_attrs[str(id(self))][name]
        except KeyError as e:
            raise AttributeError(str(e)) from None

    def __str__(self) -> str:
        return f"{self.wkt}, theta: {self.theta}"

    def __repr__(self) -> str:
        return self.__str__()

    @classmethod
    def from_Point(cls, point: Point, theta: float = 0.0):
        return cls((point.x, point.y), theta)
