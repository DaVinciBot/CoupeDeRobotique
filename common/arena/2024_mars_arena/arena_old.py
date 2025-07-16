from math import cos, radians, sin

from old_logger import Logger, LogLevels
from shapely.affinity import scale

from geometry import (
    Geometry,
    LineString,
    MultiPoint,
    MultiPolygon,
    OrientedPoint,
    Point,
    Polygon,
    create_straight_rectangle,
    distance,
    nearest_points,
    prepare,
)


class Arena:
    """Represent an arena"""

    def __init__(
        self,
        logger: Logger,
        safe_collision_distance: float = 30,
        game_borders: Polygon = create_straight_rectangle(Point(0, 0), Point(200, 300)),
        zones: dict[str, MultiPolygon] | None = None,
        *,
        border_buffer,
        robot_buffer,
    ) -> None:
        self.logger: Logger = logger
        self.game_borders: Polygon = game_borders
        self.game_borders_buffered: Polygon = self.game_borders.buffer(border_buffer)
        self.safe_collision_distance: float = safe_collision_distance
        self.ennemy_position: Point | None = None
        self.border_buffer = border_buffer
        self.robot_buffer = robot_buffer

        if zones is not None:
            self.zones = zones

        else:
            self.zones = {}

        self.prepare_zones()  # Not necessary but should optimize future intersection calulations etc.

    def prepare_zones(self) -> None:
        """Prepare all values of self.zones, to optimize later calculations"""
        prepare(self.game_borders)
        prepare(self.game_borders_buffered)
        for zone in self.zones.values():
            prepare(zone)

    def valide_position(self, pos: Point) -> bool:
        pos = pos.buffer(self.robot_buffer)
        return self.game_borders.buffer(-0.01).contains(pos)

    def contains(self, element: Geometry, buffered_zone=False) -> bool:
        """Check if a point is in the arena bounds

        Args:
            element (Geometry): The point to check. Points, Polygons etc. are all Geometries.

        Returns:
            bool: True if the element is entirely in the arena, False otherwise
        """
        if buffered_zone:
            return self.game_borders_buffered.contains(element)
        return self.game_borders.contains(element)

    def zone_intersects(self, zone_name: str, element: Geometry) -> bool:
        if zone_name not in self.zones:
            raise ValueError("Tried to check intersection with unknown zone in arena")
        if self.zones[zone_name] is None:
            return False
        return self.zones[zone_name].intersects(element)

    def enable_go_to_point(
        self,
        start: Point,
        target: Point,
        forbidden_zone_name: str = "forbidden",
    ) -> bool:
        return self.enable_go_on_path(
            LineString([start, target]),
            forbidden_zone_name=forbidden_zone_name,
        )

    def enable_go_on_path(
        self,
        path: LineString,
        forbidden_zone_name: str = "forbidden",
    ) -> bool:
        """This function checks if a given line (or series of connected lines) move can be made into the arena. It
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
            path.buffer(self.robot_buffer) if self.robot_buffer > 0 else path
        )

        if not self.contains(geometry_to_check):
            return False

        return not (
            self.zone_intersects(forbidden_zone_name, geometry_to_check)
            # Below is code that checked for intersection with a buffer around the ennemy position as well
            # or (
            #     self.ennemy_position.buffer(self.robot_buffer).intersects(
            #         geometry_to_check
            #     )
            #     if self.ennemy_position is not None
            #     else False
            # )
        )

    def compute_go_to_destination(
        self,
        start_point: Point,
        zone: Polygon,
        delta: float = 0,
    ) -> Point | None:
        """_summary_

        Args:
            start_point (Point): _description_
            zone (Polygon): _description_
            delta (float, optional): _description_. Defaults to 0.
            closer (bool, optional): _description_. Defaults to True.

        Returns:
            _type_: _description_
        """
        borders = self.game_borders
        center: Point = zone.centroid
        if delta == 0:
            self.logger.log(
                "delta == 0, returning as close as the centroid of zone as possible to avoid collision with the border",
                LogLevels.DEBUG,
            )
            if self.valide_position(center):
                return center
            projected_point = borders.exterior.interpolate(
                borders.exterior.project(center),
            )
            x = center.x
            y = center.y
            if abs(y - projected_point.y) < 0.1:
                if projected_point.x - x < 0:
                    x = x + (self.robot_buffer - center.distance(projected_point) + 0.1)
                else:
                    x = x - (self.robot_buffer - center.distance(projected_point) + 0.1)
            elif projected_point.y - y > 0:
                y = y - (self.robot_buffer - center.distance(projected_point) + 0.1)
            else:
                y = y + (self.robot_buffer - center.distance(projected_point) + 0.1)
            center = Point(x, y)
            if not self.valide_position(center):
                projected_point = borders.exterior.interpolate(
                    borders.exterior.project(center),
                )
                if abs(y - projected_point.y) < 0.1:
                    if projected_point.x - x < 0:
                        x = x + (
                            self.robot_buffer - center.distance(projected_point) + 0.1
                        )
                    else:
                        x = x - (
                            self.robot_buffer - center.distance(projected_point) + 0.1
                        )
                elif projected_point.y - y > 0:
                    y = y - (self.robot_buffer - center.distance(projected_point) + 0.1)
                else:
                    y = y + (self.robot_buffer - center.distance(projected_point) + 0.1)
            return Point(x, y)

        if delta != 0:
            abs_delta = abs(delta)
            disc_delta = center.buffer(abs_delta)

            if disc_delta.intersects(start_point):
                self.logger.log("start_point is inside circle_delta", LogLevels.DEBUG)
                return None
            # Get the boundary (circle) of the disc of radius delta around the center
            circle_delta = disc_delta.boundary

            # Compute the line from start_point to the center of the zone, then scale it by more than 2 to make sure it intersect
            # the circle twice (unless start_point is inside the circle_delta, or delta == 0, which have been checked)
            line = scale(LineString([start_point, center]), xfact=3, yfact=3)

            intersections = circle_delta.intersection(line)

            # self.logger.log(
            #     f"Computed intersections: {intersections}", LogLevels.DEBUG
            # )

            assert (
                isinstance(intersections, MultiPoint) and len(intersections.geoms) == 2
            ), "Should get exactly 2 intersections"

            # Return closest or furthest intersection
            if delta > 0:
                return nearest_points(start_point, intersections)[1]

            # No clean way in case 'further' point
            if distance(start_point, intersections.geoms[0]) <= distance(
                start_point,
                intersections.geoms[1],
            ):
                return intersections.geoms[1]
            return intersections.geoms[0]

    def check_collision_by_distances(
        self,
        distances_to_check: list[float],
        pos_robot: OrientedPoint,
    ) -> bool:
        """Currently hard-coded for 90-180° with 3 distances/°

        Args:
            distances_to_check (list[float]): _description_
            pos_robot (OrientedPoint): _description_
        """
        for i in range(len(distances_to_check)):
            # Check if the point is close enough to be a risk, and far enough to remove lidar aberrations (might be done in lidar code as well)
            if 5 < distances_to_check[i] < self.safe_collision_distance:
                # Then check that it isn't outside the game zone (with a buffer)
                if self.game_borders_buffered.intersects(
                    self.translate_relative_polar(
                        distances_to_check[i],
                        i / 3,
                        pos_robot,
                    ),
                ):
                    return True

        return False

    @staticmethod
    def translate_relative_polar(
        distance: float,
        relative_angle: float,
        pos_robot: OrientedPoint,
    ):
        return Point(
            pos_robot.x
            + distance * cos(radians(pos_robot.theta - 45 + relative_angle)),
            pos_robot.y
            + distance * sin(radians(pos_robot.theta - 45 + relative_angle)),
        )

    def remove_outside(self, points: MultiPoint):
        return self.game_borders_buffered.intersection(points)
