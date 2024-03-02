from shapely import (
    Point,
    Polygon,
    LineString,
    geometry,
    BufferCapStyle,
    BufferJoinStyle,
)


class Arena:
    """Represent an arena"""

    def __init__(
        self,
        area: Polygon = geometry.box(0, 0, 200, 300),
        forbidden_area: Polygon or None = None,
        home: Polygon or None = None,
    ):
        self.area = area
        self.forbidden_area = forbidden_area
        self.home = home

    def contains(self, point: Point) -> bool:
        """Check if a point is in the arena

        Args:
            point (Point): The point to check

        Returns:
            bool: True if the point is in the arena, False otherwise
        """
        return self.area.contains(point)

    def contains_in_forbidden_area(self, point: Point) -> bool:
        return self.forbidden_area.contains(point)

    def enable_go_to(self, path: LineString, buffer_distance: float = 0) -> bool:
        """this function checks if a given line (or series of connected lines) move can be made into the arena. It avoid collisions with the boarders and the forbidden area.
            takes into account the width and the length of the robot

        Args:
            path (LineString): _description_
            buffer_distance (float, optional): _description_. Defaults to 0.

        Raises:
            Exception: _description_

        Returns:
            bool: _description_
        """

        # define the area touched by the buffer, for example the sides of a robot moving

        area_touched_by_buffer_along_path = path.buffer(
            buffer_distance,
            cap_style=BufferCapStyle.square,
            join_style=BufferJoinStyle.round,
        )

        # verify that the area touched is in the arena and do not collide with boarders

        if not self.area.contains_properly(area_touched_by_buffer_along_path):
            return False

        # verify that the area touched isn't in the forbidden area
        if area_touched_by_buffer_along_path.intersects(self.forbidden_area):
            return False

        return True
