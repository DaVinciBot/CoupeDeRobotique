# ====== Standard Library Imports ======
from typing import Any, ClassVar, Dict, Tuple

# ====== Third-Party Imports ======
from shapely import Point

"""
Handles inheritance for the Point class.

This implementation addresses challenges related to inheriting from the `Point` class 
(see [Shapely Issue #1233](https://github.com/shapely/shapely/issues/1233)). While the approach 
might seem unconventional, it works effectively. If for any reason this method becomes unfeasible, 
a potential alternative would be to use a composition of a `Point` object and a `float` for additional properties.

Key Features:
- Supports multiple initialization methods:
  - Using a tuple `(x, y, theta)`.
  - Using explicit values for `x`, `y`, and `theta`.
- Includes explicit `str` conversions to reduce IDE warnings and improve code clarity.

Testing and Implementation Notes:
- Different versions of this implementation have been tested, with details available 
  in the Jupyter notebook located in the `common/arena` directory.
- The current implementation combines the functionality of `OrientedPoint2` and `OrientedPoint3`.

Final Version:
- While this is the slowest of the tested implementations, the performance difference is minimal.
- It offers the broadest compatibility with the `Point` class and the broader Shapely ecosystem.
"""


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
