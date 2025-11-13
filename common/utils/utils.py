"""Miscellaneous time and geometry utilities."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from geometry.oriented_point import OrientedPoint

if TYPE_CHECKING:
    from shapely import MultiPoint


class Utils:
    """Collection of static helper methods."""

    @staticmethod
    def get_date() -> datetime:
        """Get the current date and time.

        Returns:
            datetime: The current date and time.
        """
        return datetime.now(tz=UTC)

    @staticmethod
    def get_str_date(str_format: str = "%H:%M:%S.%f") -> str:
        """Get the current date as a formatted string.

        Args:
            str_format (str, optional):
                The format string to use. Defaults to "%H:%M:%S.%f".

        Returns:
            str: The formatted date string.
        """
        return datetime.now(tz=UTC).strftime(str_format)

    @staticmethod
    def get_ts() -> float:
        """Get the current timestamp as a float.

        Returns:
            float: The current timestamp.
        """
        return datetime.now(tz=UTC).timestamp()

    @staticmethod
    def time_since(ts: float) -> float:
        """Calculate the time elapsed since a given timestamp.

        Args:
            ts (float): The timestamp to compare against.

        Returns:
            float: The time elapsed since the given timestamp.
        """
        return Utils.get_ts() - ts

    @staticmethod
    def geom_to_str(geom: MultiPoint | OrientedPoint) -> str:
        """Convert a Geometry object to a string representation.

        Args:
            geom (MultiPoint | OrientedPoint): The geometry object to convert.

        Returns:
            str: The string representation of the geometry.
        """
        r = ""
        if isinstance(geom, OrientedPoint):
            return str((
                round(geom.x, 2),
                round(geom.y, 2),
                round(geom.theta, 2) if geom.theta is not None else None,
            ))

        try:
            r = (
                "["
                + ", ".join(
                    [
                        Utils.geom_to_str(OrientedPoint.from_point(smaller_geom))
                        for smaller_geom in geom.geoms
                    ],
                )
                + "]"
            )
        except Exception:  # noqa: BLE001
            r = str(geom)

        return r
