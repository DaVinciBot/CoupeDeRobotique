from typing import Union
from geometry import (
    Point,
    Polygon,
    MultiPolygon,
    LineString,
    BufferCapStyle,
    BufferJoinStyle,
    Geometry,
    create_straight_rectangle,
    prepare,
    distance,
    scale,
)


class Arena:
    """Represent an arena"""

    def __init__(
        self,
        game_borders: Polygon = create_straight_rectangle(Point(0, 0), Point(200, 300)),
        zones: Union[dict[str, MultiPolygon], None] = None,
    ):

        self.game_borders = game_borders
        if zones is not None:
            self.zones = zones

        else:
            self.zones = {}

        self.prepare_zones()  # Not necessary but should optimize future intersection calulations etc.

    def prepare_zones(self):
        """Prepare all values of self.zones, to optimize later calculations"""
        for zone in self.zones.values():
            prepare(zone)

    def contains(self, element: Geometry) -> bool:
        """Check if a point is in the arena bounds

        Args:
            element (Geometry): The point to check. Points, Polygons etc. are all Geometries.

        Returns:
            bool: True if the element is entirely in the arena, False otherwise
        """
        return self.game_borders.contains(element)

    def zone_intersects(self, zone_name: str, element: Geometry) -> bool:

        if zone_name not in self.zones:
            raise ValueError("Tried to check intersection with unknown zone in arena")

        return self.zones[zone_name].intersects(element)

    def enable_go_to(
        self,
        path: LineString,
        buffer_distance: float = 0,
        forbidden_zone_name: str = "forbidden",
    ) -> bool:
        """this function checks if a given line (or series of connected lines) move can be made into the arena. It
        avoids collisions with the boarders and the forbidden area. takes into account the width and the length of
        the robot

        Args:
            path (LineString): Path to check
            buffer_distance (float, optional): Max distance around the path to be checked (in all directions). Defaults to 0.
            forbidden_zone_name (str): Name of the zone to check against (in addition to game borders). Defaults to "forbidden".

        Raises:
            Exception: _description_

        Returns:
            bool: Whether this path is theoretically allowed
        """

        # define the area touched by the buffer, for example the sides of a robot moving

        geometry_to_check = (
            path.buffer(
                buffer_distance,
                cap_style=BufferCapStyle.round,
                join_style=BufferJoinStyle.round,
            )
            if buffer_distance > 0
            else path
        )
        # Important to check buffer_distance > 0, otherwise the geometry can become a polygon without surface that never
        # intersects with anything

        # verify that the area touched is in the arena and do not collide with boarders
        if not self.game_borders.contains(geometry_to_check):
            return False

        # verify that the area touched isn't in the forbidden area

        return not self.zone_intersects(forbidden_zone_name, geometry_to_check)

    def compute_go_to_destination(
        self, start_point: Point, zone_name: str, delta: float = 0, closer: bool = True
    ):
        center = self.zones[zone_name].centroid

        # Get the boundary (circle) of the disc of radius delta around the center
        circle_delta = center.buffer(delta).boundary

        # Compute the line from start_point to the center of the zone, then scale it by 2 to make sure it interesects
        # the circle twice (unless start_point is inside the circle_delta, which will be checked)
        line = scale(LineString([start_point, center]), xfact=2, yfact=2)

        intersections = circle_delta.intersection(line)

        # Check that we found at least 2 intersections, should always be ok unless start_point is inside circle_delta
        # (therefore the scale function wasn't enough to reach the far away intersection)
        # or the circle is a point (delta = 0)
        if (delta > 0 and len(intersections.geoms) < 2) or (
            delta == 0 and len(intersections.geoms) < 1
        ):
            return None

        # return closest or furthest intersection

        else:
            if distance(start_point, intersections.geoms[0]) <= distance(
                start_point, intersections.geoms[1]
            ):
                return intersections.geoms[0] if closer else intersections.geoms[1]
            else:
                return intersections.geoms[1] if closer else intersections.geoms[0]
