"""Utilities for checking motion within the 2024 Mars arena."""

from __future__ import annotations

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

ADJUST_EPSILON = 0.1
EXPECTED_INTERSECTIONS = 2
MIN_LIDAR_DISTANCE = 5


class Arena:
    """Represent an arena."""

    def __init__(
        self,
        logger: Logger,
        safe_collision_distance: float = 30,
        game_borders: Polygon | None = None,
        zones: dict[str, MultiPolygon] | None = None,
        *,
        border_buffer: float,
        robot_buffer: float,
    ) -> None:
        """Initialize an arena.

        Args:
            logger (Logger): Logger to use.
            safe_collision_distance (float, optional):
                Safety distance for collision detection. Defaults to 30.
            game_borders (Polygon | None, optional):
                Game field borders. Defaults to a 200x300 rectangle.
            zones (dict[str, MultiPolygon] | None, optional):
                Dictionary of arena zones. Defaults to None.
            border_buffer (float): Buffer around the borders.
            robot_buffer (float): Buffer around the robot.
        """
        self.logger: Logger = logger
        if game_borders is None:
            game_borders = create_straight_rectangle(Point(0, 0), Point(200, 300))
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

        # Precompute prepared geometries for faster future intersections
        self.prepare_zones()

    def prepare_zones(self) -> None:
        """Prepare all values of self.zones, to optimize later calculations."""
        prepare(self.game_borders)
        prepare(self.game_borders_buffered)
        for zone in self.zones.values():
            prepare(zone)

    def validate_position(self, pos: Point) -> bool:
        """Validate the position of a robot within the arena.

        Args:
            pos (Point): The position to validate.

        Returns:
            bool: ``True`` if ``pos`` lies within the game borders, ``False`` otherwise.
        """
        rob_polygon = pos.buffer(self.robot_buffer)
        return self.game_borders.buffer(-ADJUST_EPSILON).contains(rob_polygon)

    def contains(self, element: Geometry, *, buffered_zone: bool = False) -> bool:
        """Check if an element is within the arena bounds.

        Args:
            element (Geometry): The element to check (Point, Polygon, etc.).
            buffered_zone (bool, optional):
                If ``True``, use the buffered border. Defaults to ``False``.

        Returns:
            bool: ``True`` if the element is entirely within the arena,
                ``False`` otherwise.
        """
        if buffered_zone:
            return self.game_borders_buffered.contains(element)
        return self.game_borders.contains(element)

    def zone_intersects(self, zone_name: str, element: Geometry) -> bool:
        """Check if an element intersects a specific zone.

        Args:
            zone_name (str): Name of the zone to check.
            element (Geometry): The element to check for intersection.

        Returns:
            bool: ``True`` if the element intersects the zone, ``False`` otherwise.

        Raises:
            ValueError: If ``zone_name`` is unknown.
        """
        if zone_name not in self.zones:
            msg = "Unknown zone requested"
            raise ValueError(msg)
        zone = self.zones.get(zone_name)
        if zone is None:
            return False
        return zone.intersects(element)

    def enable_go_to_point(
        self,
        start: Point,
        target: Point,
        forbidden_zone_name: str = "forbidden",
    ) -> bool:
        """Check if a direct move from ``start`` to ``target`` is allowed.

        Args:
            start (Point): Starting point of the move.
            target (Point): Target point of the move.
            forbidden_zone_name (str, optional):
                Name of the forbidden zone to check against. Defaults to "forbidden".

        Returns:
            bool: ``True`` if the move is allowed, ``False`` otherwise.
        """
        return self.enable_go_on_path(
            LineString([start, target]),
            forbidden_zone_name=forbidden_zone_name,
        )

    def enable_go_on_path(
        self,
        path: LineString,
        forbidden_zone_name: str = "forbidden",
    ) -> bool:
        """Check if a given path can be taken in the arena without collision.

        Args:
            path (LineString): Path to check.
            forbidden_zone_name (str, optional):
                Name of the forbidden zone to check against (in addition to
                game borders). Defaults to "forbidden".

        Returns:
            bool: ``True`` if the path is allowed, ``False`` otherwise.
        """
        # define the area touched by the buffer, for example the sides of a robot moving

        geometry_to_check = (
            path.buffer(self.robot_buffer) if self.robot_buffer > 0 else path
        )

        if not self.contains(geometry_to_check):
            return False

        return not self.zone_intersects(forbidden_zone_name, geometry_to_check)

    def _shift_inside(self, point: Point, borders: Polygon) -> Point:
        """Shift ``point`` inside ``borders`` to avoid collisions.

        Args:
            point (Point): The point to shift.
            borders (Polygon): The borders to stay within.

        Returns:
            Point: Adjusted point within the borders.
        """
        projected_point = borders.exterior.interpolate(
            borders.exterior.project(point),
        )
        adjust = self.robot_buffer - point.distance(projected_point) + ADJUST_EPSILON
        x, y = point.x, point.y
        if abs(y - projected_point.y) < ADJUST_EPSILON:
            x += adjust if projected_point.x - x < 0 else -adjust
        elif projected_point.y - y > 0:
            y -= adjust
        else:
            y += adjust
        return Point(x, y)

    def compute_go_to_destination(
        self,
        start_point: Point,
        zone: Polygon,
        delta: float = 0,
    ) -> Point | None:
        """Compute a destination point within a zone, considering an optional delta.

        Args:
            start_point (Point): Starting point.
            zone (Polygon): Target zone.
            delta (float, optional):
                Distance around the center of the zone. Defaults to 0.

        Returns:
            Point | None: The computed point, or ``None`` if not reachable.

        Raises:
            ValueError: If the intersection computation fails.
        """
        borders = self.game_borders
        center: Point = zone.centroid
        if not delta:
            msg = (
                "delta == 0, returning as close as the centroid of zone as possible "
                "to avoid collision with the border"
            )
            self.logger.log(msg, LogLevels.DEBUG)
            if self.validate_position(center):
                return center
            center = self._shift_inside(center, borders)
            if not self.validate_position(center):
                center = self._shift_inside(center, borders)
            return center

        abs_delta = abs(delta)
        disc_delta = center.buffer(abs_delta)

        if disc_delta.intersects(start_point):
            self.logger.log("start_point is inside circle_delta", LogLevels.DEBUG)
            return None

        circle_delta = disc_delta.boundary
        line = scale(LineString([start_point, center]), xfact=3, yfact=3)
        intersections = circle_delta.intersection(line)

        if (
            not isinstance(intersections, MultiPoint)
            or len(intersections.geoms) != EXPECTED_INTERSECTIONS
        ):
            msg = "Expected exactly two intersections"
            raise ValueError(msg)

        if delta > 0:
            return nearest_points(start_point, intersections)[1]

        first, second = intersections.geoms
        if distance(start_point, first) <= distance(start_point, second):
            return second
        return first

    def check_collision_by_distances(
        self,
        distances_to_check: list[float],
        pos_robot: OrientedPoint,
    ) -> bool:
        """Check for collision from a list of distances (e.g., LIDAR).

        Args:
            distances_to_check (list[float]): List of distances to check.
            pos_robot (OrientedPoint): Robot position and orientation.

        Returns:
            bool: ``True`` if a collision is detected, ``False`` otherwise.
        """
        for i, distance_to_check in enumerate(distances_to_check):
            if (
                MIN_LIDAR_DISTANCE < distance_to_check < self.safe_collision_distance
                and self.game_borders_buffered.intersects(
                    self.translate_relative_polar(distance_to_check, i / 3, pos_robot),
                )
            ):
                return True

        return False

    @staticmethod
    def translate_relative_polar(
        dist: float,
        relative_angle: float,
        pos_robot: OrientedPoint,
    ) -> Point:
        """Convert relative polar coordinates to an absolute point.

        Args:
            dist (float): The distance from the robot.
            relative_angle (float): The angle relative to the robot's orientation.
            pos_robot (OrientedPoint): The robot's position and orientation.

        Returns:
            Point: The absolute point in the game world.
        """
        return Point(
            pos_robot.x + dist * cos(radians(pos_robot.theta - 45 + relative_angle)),
            pos_robot.y + dist * sin(radians(pos_robot.theta - 45 + relative_angle)),
        )

    def remove_outside(self, points: MultiPoint) -> Geometry:
        """Remove points outside the game borders.

        Args:
            points (MultiPoint): The points to check.

        Returns:
            Geometry: The geometry of the points inside the game borders.
        """
        return self.game_borders_buffered.intersection(points)
