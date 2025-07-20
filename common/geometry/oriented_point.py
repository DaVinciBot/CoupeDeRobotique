"""Handles inheritance for the Point class.

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

from typing import Any, ClassVar

from shapely import Point


class OrientedPoint(Point):
    _id_to_attrs: ClassVar[dict[str, Any]] = {}

    __slots__ = (
        Point.__slots__
    )  # slots must be the same for assigning __class__ - https://stackoverflow.com/a/52140968

    theta: float  # For documentation generation and static type checking

    def __init__(
        self,
        x_or_coords: float | tuple[float, float],
        y_or_theta: float | None = None,
        theta: float = 0.0,
    ) -> (
        None
    ):  # if theta is not optional or if the structure of the arguments change (eg: self, x, y, theta) then MultiPoint becomes impossible with OrientedPoint
        self._id_to_attrs[str(id(self))] = dict(
            theta=(
                theta
                if not isinstance(x_or_coords, tuple)
                else (0.0 if y_or_theta is None else y_or_theta)
            ),
        )

    def __new__(
        cls,
        x_or_coords: float | tuple[float, float],
        y: float | None = None,
        *args,
        **kwargs,
    ) -> "OrientedPoint":
        if isinstance(x_or_coords, tuple):
            point = super().__new__(cls, x_or_coords)
        else:
            point = super().__new__(cls, x_or_coords, y)

        point.__class__ = cls  # Force the new instance to be an OrientedPoint
        return point

    def __del__(self) -> None:
        # Clean up the extra attribute when the instance is deleted.
        del self._id_to_attrs[str(id(self))]

    def __getattr__(self, name: str) -> Any:
        try:
            return OrientedPoint._id_to_attrs[str(id(self))][name]
        except KeyError as e:
            raise AttributeError(f"Attribute '{name}' not found, error: {e}") from None

    def __str__(self) -> str:
        return f"{self.wkt}, theta: {self.theta}"

    def __repr__(self) -> str:
        return f"{self.wkt}, theta: {self.theta}"

    def __format__(self, format_spec: str) -> str:
        return str(self)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, OrientedPoint):
            return False
        return self.x == other.x and self.y == other.y and self.theta == other.theta

    def __add__(self, other):
        if isinstance(other, OrientedPoint):
            return OrientedPoint(
                (self.x + other.x, self.y + other.y),
                self.theta + other.theta,
            )
        if isinstance(other, Point):
            return OrientedPoint((self.x + other.x, self.y + other.y), self.theta)
        return NotImplemented

    def __sub__(self, other):
        if isinstance(other, OrientedPoint):
            return OrientedPoint(
                (self.x - other.x, self.y - other.y),
                self.theta - other.theta,
            )
        if isinstance(other, Point):
            return OrientedPoint((self.x - other.x, self.y - other.y), self.theta)

        return NotImplemented

    @classmethod
    def from_Point(cls, point: Point, theta: float = 0.0) -> "OrientedPoint":
        return cls((point.x, point.y), theta)

    # ----------------------------------------------------------------------
    # Custom Serialization Methods
    #
    # The purpose of implementing __reduce__ and __setstate__ is to customize the
    # pickling behavior of the OrientedPoint class. By default, when you pickle an object,
    # only the base class (in this case, Point) might be used during deserialization,
    # causing your additional attributes (like 'theta') to be lost. These methods ensure that:
    #
    # 1. The correct constructor (OrientedPoint) is used during unpickling.
    # 2. The extra state (here, the 'theta' attribute) is preserved and restored.
    # 3. The custom extra attributes stored in _id_to_attrs are reinitialized.
    #
    # This is particularly important when subclassing types from libraries that have their own
    # serialization logic (such as Shapely's geometry objects).
    # ----------------------------------------------------------------------

    def __reduce__(
        self,
    ) -> tuple[
        type["OrientedPoint"],
        tuple[tuple[float, float], float],
        dict[str, float],
    ]:
        """Customize pickling for :class:`OrientedPoint`.

        Returns:
            tuple[type["OrientedPoint"], tuple[tuple[float, float], float], dict[str, float]]:
                A tuple describing how to reconstruct the object.
        """
        # Retrieve the point's coordinates (assuming a single point, so take the first coordinate tuple)
        coords = tuple(self.coords)[0]
        # Retrieve theta from the extra attributes storage
        theta = self.theta
        # Return a tuple (constructor, arguments, state)
        # When unpickled, the constructor is called with (coords, theta)
        return (self.__class__, ((coords, theta)), {"theta": theta})

    def __setstate__(self, state: dict) -> None:
        """Restore the extra state for the :class:`OrientedPoint` during unpickling.

        Args:
            state (dict): State dictionary created by :py:meth:`__reduce__`.
        """
        # Reinitialize the extra attribute in the class-level mapping
        OrientedPoint._id_to_attrs[str(id(self))] = {"theta": state.get("theta", 0.0)}
