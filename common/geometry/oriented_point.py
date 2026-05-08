"""Shapely ``Point`` subclass that includes an orientation angle ``theta``.

This implementation addresses challenges related to inheriting from the ``Point`` class
(see [Shapely Issue #1233](https://github.com/shapely/shapely/issues/1233)). While the
approach might seem unconventional, it works effectively. If for any reason this method
becomes unfeasible, a potential alternative would be to use a composition of a ``Point``
object and a ``float`` for additional properties.

Key Features:
- Supports multiple initialization methods:
  - Using a tuple ``(x, y, theta)``.
  - Using explicit values for ``x``, ``y``, and ``theta``.
- Includes explicit ``str`` conversions to reduce IDE warnings and improve code clarity.
"""

from __future__ import annotations

import math
from typing import Any, ClassVar, Self, cast, override

from shapely import Point


class OrientedPoint(Point):
    """Point with an additional ``theta`` orientation attribute.

    Attributes:
        theta (float | None): Orientation angle in radians.
    """

    _id_to_attrs: ClassVar[dict[str, Any]] = {}
    __slots__ = Point.__slots__
    theta: float | None

    def __init__(
        self,
        x_or_coords: float | tuple[float, float],
        y_or_theta: float | None = None,
        theta: float | None = None,
    ) -> None:
        """Initialize the oriented point.

        Args:
            x_or_coords (float | tuple[float, float]): X coordinate or coordinate tuple.
            y_or_theta (float | None, optional):
                Y coordinate or ``theta`` when using a tuple. Defaults to ``None``.
            theta (float | None, optional): Orientation angle. Defaults to ``None``.
        """
        self._id_to_attrs[str(id(self))] = {
            "theta": (
                theta
                if not isinstance(x_or_coords, tuple)
                else (None if y_or_theta is None else self._normalize_angle(y_or_theta))
            ),
        }
        super().__init__()

    def __new__(
        cls,
        x_or_coords: float | tuple[float, float],
        y_or_theta: float | None = None,
        *_args: float | None,
    ) -> Self:
        """Create a new oriented point instance.

        Args:
            x_or_coords (float | tuple[float, float]): X coordinate or coordinate tuple.
            y_or_theta (float | None, optional):
                Y coordinate when providing separate values. Defaults to ``None``.
            *_args (float | None): Additional arguments for future use.

        Returns:
            Self: Newly created oriented point.

        Raises:
            ValueError: If coordinates are not provided correctly.
        """
        if isinstance(x_or_coords, tuple):
            point = super().__new__(cls, x_or_coords)
        elif y_or_theta is not None:
            point = super().__new__(cls, x_or_coords, y_or_theta)
        else:
            msg = (
                "OrientedPoint must be initialized with either a tuple (x, y) "
                "or separate x and y values."
            )
            raise ValueError(msg)

        point.__class__ = cls  # Force the new instance to be an OrientedPoint
        return point

    def angle(self, other: OrientedPoint) -> float:
        """Compute angle to another oriented point.

        Args:
            other (OrientedPoint): Target oriented point.

        Returns:
            float: Angle in radians from this point to the other.
        """
        return math.atan2(other.y - self.y, other.x - self.x)

    def __del__(self) -> None:
        """Remove stored attributes when the point is deleted."""
        del self._id_to_attrs[str(id(self))]

    def __getattr__(self, name: str) -> float | None:
        """Retrieve extra attributes like ``theta`` dynamically.

        Args:
            name (str): Attribute name to fetch.

        Returns:
            float | None: Value of the requested attribute.

        Raises:
            AttributeError: If the attribute is not found.
        """
        try:
            return OrientedPoint._id_to_attrs[str(id(self))][name]
        except KeyError as e:
            msg = f"Attribute '{name}' not found, error: {e}"
            raise AttributeError(msg) from None

    @override
    def __setattr__(self, name: str, value: float | None) -> None:
        """Set extra attributes like ``theta`` with automatic normalization.

        Args:
            name (str): Attribute name to set.
            value (float | None): Value to set for the attribute.
        """
        if name == "theta":
            normalized_value = (
                self._normalize_angle(value) if value is not None else None
            )
            OrientedPoint._id_to_attrs[str(id(self))][name] = normalized_value
        else:
            object.__setattr__(self, name, value)

    @override
    def __str__(self) -> str:
        """Return WKT representation including ``theta``.

        Returns:
            str: Readable representation of the point.
        """
        return f"{self.wkt}, theta: {self.theta}"

    @override
    def __repr__(self) -> str:
        """Return debug representation including ``theta``.

        Returns:
            str: Debug representation of the point.
        """
        return f"{self.wkt}, theta: {self.theta}"

    @override
    def __format__(self, format_spec: str) -> str:
        """Format the point as a string.

        Args:
            format_spec (str): Formatting specification.

        Returns:
            str: Formatted string representation.
        """
        return str(self)

    @override
    def __eq__(self, other: object) -> bool:
        """Return ``True`` if coordinates and ``theta`` match.

        Args:
            other (object): Object to compare.

        Returns:
            bool: ``True`` if both points are equal.
        """
        if not isinstance(other, OrientedPoint):
            return False
        return self.x == other.x and self.y == other.y and self.theta == other.theta

    def __add__(self, other: object) -> OrientedPoint:
        """Add two points or a point and a vector.

        Args:
            other (object): Point or oriented point to add.

        Returns:
            OrientedPoint: Resulting oriented point.
        """
        if isinstance(other, OrientedPoint):
            if self.theta is None and other.theta is None:
                theta = None
            elif self.theta is not None and other.theta is not None:
                theta = self._normalize_angle(self.theta + other.theta)
            else:
                theta = self.theta or other.theta
            return OrientedPoint(
                (self.x + other.x, self.y + other.y),
                theta,
            )
        if isinstance(other, Point):
            return OrientedPoint((self.x + other.x, self.y + other.y), self.theta)
        return NotImplemented

    @override
    def __sub__(self, other: object) -> OrientedPoint:
        """Subtract coordinates or another oriented point.

        Args:
            other (object): Point or oriented point to subtract.

        Returns:
            OrientedPoint: Resulting oriented point.
        """
        if isinstance(other, OrientedPoint):
            if self.theta is None and other.theta is None:
                theta = None
            elif self.theta is not None and other.theta is not None:
                theta = self._normalize_angle(self.theta - other.theta)
            else:
                theta = self.theta or other.theta
            return OrientedPoint(
                (self.x - other.x, self.y - other.y),
                theta,
            )
        if isinstance(other, Point):
            return OrientedPoint((self.x - other.x, self.y - other.y), self.theta)

        return NotImplemented

    @override
    def __hash__(self) -> int:
        """Return a hash based on coordinates and orientation.

        Returns:
            int: Hash of the oriented point.
        """
        return hash((self.x, self.y, self.theta))

    @classmethod
    def from_point(cls, point: Point, theta: float | None = None) -> OrientedPoint:
        """Create an :class:`OrientedPoint` from a :class:`Point`.

        Args:
            point (Point): Source point.
            theta (float | None, optional): Orientation angle. Defaults to ``None``.

        Returns:
            OrientedPoint: Oriented point with the same coordinates.
        """
        return cls((point.x, point.y), theta)

    @staticmethod
    def _normalize_angle(angle: float) -> float:
        """Normalize angle to [-pi, pi).

        Args:
            angle (float): Angle in radians.

        Returns:
            float: Normalized angle in radians.
        """
        angle = (angle + math.pi) % (2 * math.pi)
        if angle < 0:
            angle += 2 * math.pi
        return angle - math.pi

    # ----------------------------------------------------------------------
    # Custom Serialization Methods
    #
    # The purpose of implementing __reduce__ and __setstate__ is to customize the
    # pickling behavior of the OrientedPoint class. By default, when you pickle an
    # object,
    # only the base class (in this case, Point) might be used during deserialization,
    # causing your additional attributes (like 'theta') to be lost. These methods
    # ensure that:
    #
    # 1. The correct constructor (OrientedPoint) is used during unpickling.
    # 2. The extra state (here, the 'theta' attribute) is preserved and restored.
    # 3. The custom extra attributes stored in _id_to_attrs are reinitialized.
    #
    # This is particularly important when subclassing types from libraries that have
    # their own
    # serialization logic (such as Shapely's geometry objects).
    # ----------------------------------------------------------------------

    @override
    def __reduce__(
        self,
    ) -> tuple[
        type[OrientedPoint],
        tuple[tuple[float, float], float | None],
        dict[str, float | None],
    ]:
        """Customize pickling for :class:`OrientedPoint`.

        Returns:
            tuple[type["OrientedPoint"], tuple[tuple[float, float], float | None], dict[str, float | None]]:
                A tuple describing how to reconstruct the object.
        """
        coords = cast("tuple[float, float]", next(iter(self.coords)))
        theta = self.theta
        return (
            self.__class__,
            ((coords, theta)),
            {"theta": theta},
        )

    def __setstate__(self, state: dict[str, float | None]) -> None:
        """Restore the extra state for the :class:`OrientedPoint` during unpickling.

        Args:
            state (dict[str, float | None]):
                State dictionary created by :py:meth:`__reduce__`.
        """
        OrientedPoint._id_to_attrs[str(id(self))] = {"theta": state.get("theta", 0.0)}
