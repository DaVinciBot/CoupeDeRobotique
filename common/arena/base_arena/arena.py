"""Base arena representation and visualization utilities.

The :class:`BaseArena` class models a physical arena with zones, border buffers, and
obstacles. It provides helpers for creating border zones, managing a grid-based
view of the arena, handling zone accessibility, and rendering the arena for
debug or user interfaces.

"""

from __future__ import annotations

from abc import ABC, abstractmethod
from math import pi
from typing import TYPE_CHECKING, cast, override

import matplotlib.pyplot as plt
import numpy as np
from loggerplusplus import Logger, time_tracker

from arena.base_arena.arena_zones import AllyZone, BaseArenaZone, BorderZone, EnemyZone
from arena.base_arena.grid_manager import GridManager
from arena.base_arena.team_color import TeamColor
from geometry import (
    Geometry,
    MultiPoint,
    OrientedPoint,
    Point,
    Polygon,
    box,
    create_straight_rectangle,
    is_empty,
    nearest_points,
    prepare,
)

if TYPE_CHECKING:
    from matplotlib.figure import Figure as pltFigure


class BaseArena(ABC):
    """Represents the arena and its zones, including buffer areas."""

    def __init__(
        self,
        logger: Logger,
        width: int,
        height: int,
        forbidden_cover_threshold: float,
        border_buffer: float,
        obstacle_buffer: float,
        zones: list[BaseArenaZone],
        chunk_size: int = 10,
        grid_manager_logger: Logger | None = None,
    ) -> None:
        """Initializes an instance with dimensions, zones, and configuration parameters.

        Args:
            logger (Logger): Logger instance for general arena logging.
            width (int): Width of the arena in centimeters.
            height (int): Height of the arena in centimeters.
            forbidden_cover_threshold (float):
                Threshold for forbidden cover in the grid.
            border_buffer (float): Buffer distance for the arena border.
            obstacle_buffer (float): Buffer distance for obstacles.
            zones (list[BaseArenaZone]): List of pre-defined zones in the arena.
            chunk_size (int, optional):
                Size of chunks in the grid manager. Defaults to 10.
            grid_manager_logger (Logger | None, optional):
                Logger instance for grid manager logging. Defaults to None.
        """
        # region ====== Initialized constructor based attributes ======
        # 1. Logger
        self.logger: Logger = logger
        # 2. Dimensions
        self.width: int = width
        self.height: int = height

        if border_buffer % chunk_size:
            self.logger.warning(
                "The border buffer is not a multiple of the chunk size -> "
                "the not walkable area will not be aligned with the grid",
            )

        if obstacle_buffer % chunk_size:
            self.logger.warning(
                "The obstacle buffer is not a multiple of the chunk size -> "
                "the not walkable area will not be aligned with the grid",
            )
        # 3. Buffers
        self.border_buffer: float = border_buffer
        self.obstacle_buffer: float = obstacle_buffer

        # 4. Grid Manager
        self.grid_manager: GridManager = GridManager(
            logger=grid_manager_logger
            or Logger(
                identifier="GridManager",
                follow_logger_manager_rules=True,
            ),
            chunk_size=chunk_size,
            width=width,
            height=height,
            forbidden_cover_threshold=forbidden_cover_threshold,
        )

        # 5. Zones
        self.zones: list[BaseArenaZone] = zones

        # Give to each zone the grid manager to do a callback when they update state
        for zone in self.zones:
            zone.update_callback = self._get_grid_manager

        # Add forbidden and border zones to the grid manager
        for zone in self.zones:
            if not zone.is_accessible():
                self.grid_manager.add_forbidden_static_zone(zone.buffered_polygon)

        # endregion

        # region ====== Initialized derivative attributes ======
        # 1. Team color
        self.team_color: TeamColor = TeamColor.UNDEFINED

        # 2. Additional zones: Border, Ally and Enemy
        # 2.1 Border zone
        # We don't need to add the border zone to self.zones, it's a 100% static zone
        self.border_zone: BorderZone = self.__create_arena_border_zone()
        self.grid_manager.add_forbidden_static_zone(self.border_zone.buffered_polygon)

        # 2.2 Ally and Enemy zones
        # Don't need to add these zones to self.zones, they have their own update method
        # Don't need to add these zones to the grid manager, they are 100% dynamic zones
        # Don't add them now as dynamic forbidden zones because they are not updated yet
        #   -> default position for now (wait BaseArena.update method for update)
        self.ally_zone: AllyZone = AllyZone(
            logger=Logger(identifier="AllyZone", follow_logger_manager_rules=True),
            point=OrientedPoint(self.width / 2, self.height / 2, 0),
            robot_size=1,
            # The robot is in reality assimilated to a point of null size,
            # but for the visualisation we need to give it a size
        )

        self.enemy_zone: EnemyZone = EnemyZone(
            logger=Logger(identifier="EnemyZone", follow_logger_manager_rules=True),
            point=OrientedPoint(self.width / 2, self.height / 2, 0),
            robot_size=15,
        )

        # 3. Bounding Area and Playable Area
        # 3.1 Bounding Area: The entire arena (including border buffer)
        self.bounding_area: Polygon = create_straight_rectangle(
            Point(0, 0),
            Point(width, height),
        )

        # 3.2 Playable Area: The real playable area (excluding border buffer)
        self.playable_area: Polygon = self.bounding_area.difference(
            self.border_zone.buffered_polygon,
        ).buffer(-self.obstacle_buffer)

        # endregion

        # ====== Misc ======
        self.__prepare_zones()

    # region ====== Private Methods ======
    def __create_arena_border_zone(self) -> BorderZone:
        """Create a border zone around the arena with a specified buffer width.

        Prevents the robot from approaching too close to the arena edges.

        Returns:
            BorderZone: A zone representing the arena's border.
        """
        arena_polygon = box(0, 0, self.width, self.height)
        inner_polygon = BaseArenaZone.add_buffer_to_zone(
            arena_polygon,
            -self.border_buffer,
        )
        border_zone_polygon = cast("Polygon", arena_polygon.difference(inner_polygon))

        return BorderZone(
            logger=Logger(
                identifier="BorderZone",
                follow_logger_manager_rules=True,
            ),
            buffer_size=self.border_buffer,
            buffered_polygon=border_zone_polygon,
        )

    def __prepare_zones(self) -> None:
        """Prepare all zones that could be used for calculations.

        It will improve the computing performance.
        """
        prepare(self.bounding_area)
        prepare(self.playable_area)
        for zone in self.zones:
            prepare(zone.polygon)

    # endregion

    # region ====== Protected Methods ======
    def _get_grid_manager(self) -> GridManager:
        """Return the grid manager instance for zone callbacks.

        Returns:
            GridManager: The current grid manager.
        """
        return self.grid_manager

    def _pol_to_abs_cart(self, polars: np.ndarray) -> MultiPoint:
        """Converts polar coordinates to absolute Cartesian coordinates.

        Args:
            polars (np.ndarray):
                Array of polar coordinates in the form of (angle, distance).

        Returns:
            MultiPoint: Array of absolute Cartesian coordinates.
        """
        return MultiPoint(
            [
                (
                    self.ally_zone.point.x
                    + np.cos(self.ally_zone.point.theta + polars[i, 0]) * polars[i, 1],
                    self.ally_zone.point.y
                    + np.sin(self.ally_zone.point.theta + polars[i, 0]) * polars[i, 1],
                )
                for i in range(len(polars))
            ],
        )

    # endregion

    # region ====== Public Methods ======
    @time_tracker(lambda self: self.logger)
    def set_team_color(self, team_color: TeamColor) -> None:
        """Set the team color and trigger updates to zones.

        Args:
            team_color (TeamColor): The team's color.
        """
        if team_color not in {TeamColor.YELLOW, TeamColor.BLUE}:
            self.logger.error(
                f"Invalid team color: {team_color}. Must be 'yellow' or 'blue'.",
            )

        self.team_color: TeamColor = team_color
        self.update(
            ally_position=self.ally_zone.point,
            lidar_scan_polars=np.array([]),
            optimized_update=False,
        )  # Force to update all zones

    @time_tracker(lambda self: self.logger)
    def update(
        self,
        ally_position: OrientedPoint,
        lidar_scan_polars: np.ndarray,  # Polars coordinates issued from the lidar scan
        *,
        optimized_update: bool = True,
        _enemy_position: OrientedPoint
        | None = None,  # Only for testing and simulation purpose
    ) -> None:
        """Updates the state of the arena, zones, and grid.

        Args:
            ally_position (OrientedPoint): Current position of the ally robot.
            lidar_scan_polars (np.ndarray): Lidar scan data in polar coordinates.
            optimized_update (bool, optional):
                If ``True``, only updates intersecting zones. Defaults to ``True``.
            _enemy_position (OrientedPoint | None, optional):
                Pre-defined enemy position. Defaults to None.
        """
        # 1.Compute enemy position if not directly provided in absolute coordinates
        if not _enemy_position:
            # Compute enemy position based on lidar scans -> match situation
            enemy_position = self.compute_enemy_position(
                lidar_scan_polars,
                ally_position,
            )
        else:
            # Use the provided enemy position -> testing or simulation
            enemy_position = _enemy_position

        # 2.Update ally and enemy zones (specific zone, there are not in self.zones)
        self.ally_zone.update(self.team_color, ally_position, enemy_position)
        self.enemy_zone.update(self.team_color, ally_position, enemy_position)

        # 3.Update all other zones
        # optimized: Update only the zones that intersect with the points
        all_points: list[OrientedPoint] = [
            ally_position,
            enemy_position,
        ]
        for zone in self.zones:
            if not optimized_update or any(
                zone.polygon.contains(pt) for pt in all_points
            ):
                zone.update(
                    self.team_color,
                    ally_position=ally_position,
                    enemy_position=enemy_position,
                )

        # 4.Update Grid Manager dynamic forbidden zones (only enemy zone)
        # self.grid_manager.update_dynamic_forbidden_zones([self.enemy_zone.polygon])

    def compute_enemy_position(
        self,
        lidar_scan_polars: np.ndarray,
        ally_position: OrientedPoint,
        *,
        _start_time: int = -1,
        _numb_enemy: bool = False,
    ) -> OrientedPoint:
        """Computes the position of the enemy and updates the arena.

        This function calculates the position of the enemy by processing the
        lidar scans.
        It removes any obstacles that are outside the arena, and then determines
        the closest obstacle as the enemy position.
        If the enemy position is within a stuff zone, it marks that zone as FORBIDDEN.

        Args:
            lidar_scan_polars (np.ndarray): Detection points from the LIDAR scan.
            ally_position (OrientedPoint): Current ally position.
            _start_time (int, optional):
                Starting timestamp for the computation. Defaults to -1.
            _numb_enemy (bool, optional):
                Whether the enemy is inactive. Defaults to ``False``.

        Returns:
            OrientedPoint: The computed enemy position.
        """
        obstacles: MultiPoint = self.remove_outside(
            self._pol_to_abs_cart(lidar_scan_polars),
        )

        if not is_empty(obstacles):
            return OrientedPoint.from_point(nearest_points(ally_position, obstacles)[1])

        return self.enemy_zone.point

    # region ====== Geometry helpers function part ======

    def remove_outside(self, points: MultiPoint) -> MultiPoint:
        """Remove points that are outside the playable area of the arena.

        Args:
            points (MultiPoint): Points to check against the playable area.

        Returns:
            MultiPoint: The points that are within the playable area.
        """
        return cast("MultiPoint", self.playable_area.intersection(points))

    def compute_goal_position(
        self,
        goal: int | BaseArenaZone | OrientedPoint,
    ) -> OrientedPoint | None:
        """Compute a goal position based on zone or point information.

        Args:
            goal (int | BaseArenaZone | OrientedPoint): Zone identifier
                or direct destination.

        Returns:
            OrientedPoint | None: Computed destination or ``None`` if the
            goal type is invalid.
        """
        # 1. If goal is defined as int, it's a zone ID
        if isinstance(goal, int):
            if goal > len(self.zones):
                self.logger.error("Invalid zone ID given in trajectory parameters.")
                return None

            return self.zones[goal].get_go_to_position(
                ally_position=self.ally_zone.point,
                team_color=self.team_color,
            )

        # 2. If goal is a BaseArenaZone -> compute the best goal point
        if isinstance(goal, BaseArenaZone):
            return goal.get_go_to_position(
                ally_position=self.ally_zone.point,
                team_color=self.team_color,
            )

        # 3. If goal is an OrientedPoint, return it as is
        return goal

    # TODO: Check if this function is still needed, test them (last year code)
    def valid_position(self, pos: OrientedPoint) -> bool:
        """Check if a given position is within the valid playing area.

        Args:
            pos (OrientedPoint): The position to check.

        Returns:
            bool: ``True`` if the position is within the playing area,
                ``False`` otherwise.
        """
        return self.playable_area.contains(pos) or self.playable_area.touches(pos)

    def get_closest_wall_goal(self) -> OrientedPoint | None:
        """
        Determine the closest accessible wall point in the arena.

        Returns:
            OrientedPoint: The closest accessible wall point.
        """
        robot_pos = self.ally_zone.point

        arena_width = 300
        arena_height = 200
        arena_border = 5

        closest_point: OrientedPoint | None = None
        min_distance: float = float("inf")

        walls = [
            ("x", arena_border, range(0, arena_height + 1), 0),
            ("x", arena_width - arena_border, range(0, arena_height + 1), pi),
            ("y", arena_border, range(0, arena_width + 1), -pi / 2),
            ("y", arena_height - arena_border, range(0, arena_width + 1), pi / 2),
        ]

        for axis, fixed, var_range, orientation in walls:
            for var in var_range:
                if axis == "x":
                    candidate = OrientedPoint(fixed, var, orientation)
                else:
                    candidate = OrientedPoint(var, fixed, orientation)

                zone = self.get_zone_by_location(candidate)
                if zone is None:
                    continue
                if zone not in self.find_zone_accessibility("FREE"):
                    continue

                dx = candidate.x - robot_pos.x
                dy = candidate.y - robot_pos.y
                distance = (dx ** 2 + dy ** 2) ** 0.5

                if distance < min_distance:
                    min_distance = distance
                    closest_point = candidate

        return closest_point

    def get_zone_by_location(
        self,
        location: int | BaseArenaZone | OrientedPoint,
    ) -> BaseArenaZone | None:
        """Find the zone that contains a given location.

        Args:
            location (int | BaseArenaZone | OrientedPoint):
                The location to check.

        Returns:
            BaseArenaZone | None:
                The zone containing the location, or None if not found.
        """
        if isinstance(location, int):
            if location >= len(self.zones):
                self.logger.error("Invalid zone ID given in trajectory parameters.")
                return None
            return self.zones[location]
        if isinstance(location, BaseArenaZone):
            return location
        for zone in self.zones:
            if zone.polygon.contains(location):
                return zone
        return None

    def find_zone_accessibility(self, accessibility: str) -> list[BaseArenaZone]:
        """Find and return a list of zones with the specified accessibility.

        Args:
            accessibility (str): The accessibility level to filter zones by.
                                 This should be a string representing the name
                                 of the accessibility level (case insensitive).

        Returns:
            list[BaseArenaZone]: A list of BaseArenaZone objects that match the
                                 specified accessibility level.
        """
        return [
            zone
            for zone in self.zones
            if zone.accessibility.name == accessibility.upper()
        ]

    # We check if an element intersects with at least one zone of the specified type
    def zone_intersects(self, accessibility: str, element: Geometry) -> bool:
        """Check if a geometric element intersects zones of a given accessibility.

        Args:
            accessibility (str): Accessibility level to filter zones by.
            element (Geometry): Geometric element to test for intersection.

        Returns:
            bool:
                ``True`` if a matching zone intersects ``element``, ``False`` otherwise.

        Raises:
            ValueError: If no zones have the specified accessibility.
        """
        zones_to_check = self.find_zone_accessibility(accessibility)
        if not zones_to_check:
            msg = f"No zones has accessibility: '{accessibility}'."
            raise ValueError(msg)

        return any(zone.polygon.intersects(element) for zone in zones_to_check)

    def contains(self, element: Geometry) -> bool:
        """Check if a point is in the arena bounds.

        Args:
            element (Geometry): The point to check. Points, polygons, etc. are all
                ``Geometry`` instances.

        Returns:
            bool: ``True`` if the element is entirely in the arena, ``False`` otherwise.
        """
        return self.bounding_area.contains(element)

    # endregion

    # endregion

    # region ====== Visualisation part ======

    # region ====== Private Methods: draw helpers ======
    @staticmethod
    def __plot_oriented_arrow(
        ax: plt.Axes,
        point: OrientedPoint,
        norm: float = 5.0,
        color: str = "#000000",
        head_width: float | None = None,
        head_length: float | None = None,
    ) -> None:
        """Draws an arrow from an oriented point with a given direction.

        Args:
            ax (plt.Axes): Matplotlib axis to draw the arrow on.
            point (OrientedPoint): Oriented point (x, y, theta) with position and angle.
            norm (float): Length of the arrow. Defaults to 5.0.
            color (str): Color of the arrow. Defaults to '#000000'.
            head_width (float | None): Width of the arrow head.
                Defaults to None -> norm * 0.2.
            head_length (float | None): Length of the arrow head.
                Defaults to None -> norm * 0.3.

        Raises:
            ValueError: If `point.theta` is None.
        """
        if point.theta is None:
            msg = "point.theta must be defined to draw an oriented arrow."
            raise ValueError(msg)
        if head_width is None:
            head_width = norm * 0.2
        if head_length is None:
            head_length = norm * 0.3

        # Compute the destination point based on the angle and norm
        dx = norm * np.cos(point.theta)
        dy = norm * np.sin(point.theta)

        # Draw the arrow
        ax.arrow(
            point.x,
            point.y,
            dx,
            dy,
            head_width=head_width,
            head_length=head_length,
            fc=color,
            ec=color,
            linewidth=2,
        )

    @staticmethod
    def __plot_zone_uid(
        ax: plt.Axes,
        zone: BaseArenaZone,
        color: str = "#000000",
        fontsize: int = 12,
    ) -> None:
        """Draws the zone UID at the center of the zone.

        Args:
            ax (plt.Axes): Matplotlib axis to draw the UID on.
            zone (BaseArenaZone): Zone to draw the UID for.
            color (str, optional): Color of the UID. Defaults to '#000000'.
            fontsize (int, optional): Font size of the UID. Defaults to 12.
        """
        ax.text(
            zone.polygon.centroid.x,
            zone.polygon.centroid.y,
            str(zone.uid),
            ha="center",
            va="center",
            fontsize=fontsize,
            color=color,
        )

    def __get_hatch_parameters(self, zone: BaseArenaZone) -> dict[str, str]:
        hatch_params = {}
        if zone.is_accessible(team_color=self.team_color):
            pass  # No hatch
        elif zone.is_accessible_for_emergency(team_color=self.team_color):
            hatch_params = {
                "hatch": "\\",
                "hatch_color": "red",
            }  # Hatch with red lines for restricted zones
        elif not zone.is_accessible(team_color=self.team_color):
            hatch_params = {
                "hatch": "/",
                "hatch_color": "black",
            }  # Hatch with black lines for forbidden zones

        return hatch_params

    @staticmethod
    def __plot_polygon(
        ax: plt.Axes,
        polygon: Polygon,
        color: str,
        label: str | None = None,
        alpha: float = 1.0,
        hatch: str | None = None,
        hatch_color: str | None = None,
    ) -> None:
        r"""Plot a polygon or multipolygon on a matplotlib axis.

        - Fills polygons without holes, optionally with hatching.
        - Draws only outlines (dashed) for polygons with holes.
        - Ensures that the same legend label is not added more than once.

        Args:
            ax (plt.Axes): Axis on which to draw.
            polygon (Polygon): Polygon to plot.
            color (str): Fill color of the polygon.
            label (str | None, optional): Legend label. Defaults to None.
            alpha (float, optional): Transparency factor. Defaults to 1.0.
            hatch (str | None, optional): Matplotlib hatching pattern,
                e.g., ``/`` or ``\\``. Defaults to None for no hatching.
            hatch_color (str | None, optional): Color of the hatching lines.
                Defaults to None.
        """
        # Avoid duplicate labels
        existing_labels = ax.get_legend_handles_labels()[1]
        if label is not None and label in existing_labels:
            label = None

        if not polygon.interiors:
            # Polygon without holes
            x, y = polygon.exterior.xy
            ax.fill(
                x,
                y,
                alpha=alpha,
                fc=color,
                label=label,
                hatch=hatch,
                ec=hatch_color or color,
            )
        else:
            # Polygon with holes: outline and interior lines
            x, y = polygon.exterior.xy
            ax.plot(x, y, color=color, linestyle="--", label=label, alpha=alpha)
            for interior in polygon.interiors:
                x, y = interior.xy
                ax.plot(x, y, color=color, linestyle="--", alpha=alpha)

    def __plot_zone(
        self,
        ax: plt.Axes,
        zone: BaseArenaZone,
        *,
        show_buffer: bool,
        show_ally_direction: bool,
        display_zones_go_to_positions: bool,
        transparency_factor: float = 1.0,
    ) -> None:
        """Plot a zone and its buffer on the arena.

        Args:
            ax (plt.Axes): Axis on which to draw.
            zone (BaseArenaZone): Zone to display.
            show_buffer (bool): Whether to plot the buffered polygon.
            show_ally_direction (bool): Draw an arrow for the ally direction.
            display_zones_go_to_positions (bool): Draw go-to positions if any.
            transparency_factor (float, optional):
                Alpha value multiplier. Defaults to 1.0.
        """
        if show_buffer:
            # Plot buffer zone in transparent color
            self.__plot_polygon(
                ax,
                zone.buffered_polygon,
                color=zone.zone_color,
                alpha=0.5 * transparency_factor,
            )

        if isinstance(zone, BorderZone):
            self.__plot_polygon(
                ax,
                zone.polygon,
                color=zone.zone_color,
                alpha=0.5 * transparency_factor,
            )
        else:
            # 1. Define hatch parameters (depends on zone accessibility)
            hatch_params = self.__get_hatch_parameters(zone)

            # 2. Plot zone uid
            # Don't plot uid for ally and enemy zones (they increase at each update)
            if not isinstance(zone, AllyZone) and not isinstance(zone, EnemyZone):
                self.__plot_zone_uid(ax, zone)

            # 3. Plot the zone polygon
            self.__plot_polygon(
                ax,
                zone.polygon,
                color=zone.zone_color,
                label=zone.zone_type.name,
                alpha=0.8 * transparency_factor,
                **hatch_params,
            )

            # 4. Plot go-to positions
            if display_zones_go_to_positions and zone.go_to_positions:
                # Get the go-to position nearest to the ally robot
                nearest_point = zone.get_go_to_position(
                    ally_position=self.ally_zone.point,
                    team_color=self.team_color,
                )
                for go_to_position in zone.go_to_positions:
                    # Plot nearest go-to position as green arrow or green dot
                    if go_to_position == nearest_point:
                        if go_to_position.theta is not None:
                            ax.plot(
                                go_to_position.x,
                                go_to_position.y,
                                "gx",
                                markersize=5,
                            )
                            self.__plot_oriented_arrow(
                                ax,
                                go_to_position,
                                color="green",
                                norm=5,
                                head_width=3,
                                head_length=1.5,
                            )
                        else:
                            ax.plot(
                                go_to_position.x,
                                go_to_position.y,
                                "go",
                                markersize=4,
                            )
                    else:
                        ax.plot(go_to_position.x, go_to_position.y, "rx", markersize=5)

            # 5. Plot ally direction
            if show_ally_direction and isinstance(zone, AllyZone):
                self.__plot_oriented_arrow(
                    ax,
                    zone.point,
                    color=zone.zone_color,
                    norm=zone.robot_size + 10,
                )

    @staticmethod
    def _init_plot(
        plot: tuple[plt.Axes, pltFigure] | None,
    ) -> tuple[plt.Axes, pltFigure]:
        """Return the axis and figure used for visualization.

        Args:
            plot (tuple[plt.Axes, pltFigure] | None): Existing axis and figure to
                reuse.

        Returns:
            tuple[plt.Axes, pltFigure]: Axis and figure for plotting.
        """
        if plot:
            return plot
        fig, ax = plt.subplots(figsize=(20, 12))
        return ax, fig

    def _plot_zones(
        self,
        ax: plt.Axes,
        *,
        show_buffer: bool,
        display_zones_go_to_positions: bool,
        show_ally_direction: bool,
        transparency_factor: float,
        additional_zones: list[BaseArenaZone] | None,
    ) -> None:
        """Plot all arena zones and optional extra zones.

        Args:
            ax (plt.Axes): Axis on which to draw.
            show_buffer (bool): Whether to display buffer polygons.
            display_zones_go_to_positions (bool): Draw go-to positions if any.
            show_ally_direction (bool): Draw an arrow for the ally direction.
            transparency_factor (float): Alpha multiplier for polygons.
            additional_zones (list[BaseArenaZone] | None): Extra zones to draw.
        """
        self.__plot_zone(
            ax,
            self.border_zone,
            show_buffer=show_buffer,
            show_ally_direction=False,
            display_zones_go_to_positions=False,
            transparency_factor=transparency_factor,
        )
        for zone in self.zones:
            self.__plot_zone(
                ax,
                zone,
                show_buffer=show_buffer,
                show_ally_direction=False,
                display_zones_go_to_positions=display_zones_go_to_positions,
                transparency_factor=transparency_factor,
            )
        if additional_zones:
            for zone in additional_zones:
                self.__plot_zone(
                    ax,
                    zone,
                    show_buffer=show_buffer,
                    show_ally_direction=False,
                    display_zones_go_to_positions=display_zones_go_to_positions,
                    transparency_factor=transparency_factor,
                )
        self.__plot_zone(
            ax,
            self.enemy_zone,
            show_buffer=show_buffer,
            show_ally_direction=False,
            display_zones_go_to_positions=False,
            transparency_factor=transparency_factor,
        )
        self.__plot_zone(
            ax,
            self.ally_zone,
            show_buffer=show_buffer,
            show_ally_direction=show_ally_direction,
            display_zones_go_to_positions=False,
            transparency_factor=transparency_factor,
        )

    def _plot_additional_points(
        self,
        ax: plt.Axes,
        points: list[OrientedPoint] | None,
    ) -> None:
        """Plot additional points or oriented points on the arena.

        Args:
            ax (plt.Axes): Axis on which to draw.
            points (list[OrientedPoint] | None): Points to display.
        """
        if not points:
            return
        for p in points:
            if p.theta is not None:
                self.__plot_oriented_arrow(
                    ax,
                    p,
                    color="red",
                    norm=5,
                    head_width=4,
                    head_length=3,
                )
            else:
                ax.plot(p.x, p.y, "ro")

    @staticmethod
    def _plot_trajectory(
        ax: plt.Axes,
        trajectory: list[OrientedPoint],
    ) -> None:
        """Plot a trajectory connecting oriented points.

        Args:
            ax (plt.Axes): Axis on which to draw.
            trajectory (list[OrientedPoint]): Path to draw.
        """
        for i in range(len(trajectory) - 1):
            ax.plot(
                [trajectory[i].x, trajectory[i + 1].x],
                [trajectory[i].y, trajectory[i + 1].y],
                color="purple",
                linewidth=1,
                alpha=0.2,
            )

    def _finalize_plot(self, ax: plt.Axes) -> None:
        """Finalize axis properties and legend positioning.

        Args:
            ax (plt.Axes): Axis to configure.
        """
        ax.set_xlim(0, self.width)
        ax.set_ylim(0, self.height)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.set_aspect("equal", adjustable="box")
        ax.set_title("Arena Visualization")
        plt.legend(loc="center right", bbox_to_anchor=(-0.1, 0.5))
        plt.tight_layout()

    # endregion

    # region ====== Public Methods ======
    def visualize(
        self,
        *,
        show_buffer: bool = True,
        trajectory: list[OrientedPoint] | None = None,
        transparency_factor: float = 1.0,
        display_zones_go_to_positions: bool = True,
        show_ally_direction: bool = True,
        show: bool = True,
        plot: tuple[plt.Axes, pltFigure] | None = None,
        additional_zones: list[BaseArenaZone] | None = None,
        additional_points: list[OrientedPoint] | None = None,
    ) -> tuple[plt.Axes, pltFigure]:
        """Visualize the arena and optionally display the plot.

        Args:
            show_buffer (bool, optional): Whether to display buffered polygons.
                Defaults to ``True``.
            trajectory (list[OrientedPoint] | None, optional): Trajectory to draw.
                Defaults to ``None``.
            transparency_factor (float, optional): Alpha multiplier. Defaults to 1.0.
            display_zones_go_to_positions (bool, optional): Plot go-to positions.
                Defaults to ``True``.
            show_ally_direction (bool, optional): Draw ally orientation arrow.
                Defaults to ``True``.
            show (bool, optional): If ``True``, display the plot immediately.
                Defaults to ``True``.
            plot (tuple[plt.Axes, pltFigure] | None, optional):
                Existing axis and figure. Defaults to ``None``.
            additional_zones (list[BaseArenaZone] | None, optional):
                Extra zones to draw. Defaults to ``None``.
            additional_points (list[OrientedPoint] | None, optional):
                Extra points to draw. Defaults to ``None``.

        Returns:
            tuple[plt.Axes, pltFigure]: Axis and figure containing the visualization.
        """
        ax, fig = self._init_plot(plot)
        self.__plot_polygon(ax, self.bounding_area, color="#f0f0f0", label="Arena")
        self._plot_zones(
            ax,
            show_buffer=show_buffer,
            display_zones_go_to_positions=display_zones_go_to_positions,
            show_ally_direction=show_ally_direction,
            transparency_factor=transparency_factor,
            additional_zones=additional_zones,
        )
        self._plot_additional_points(ax, additional_points)
        if trajectory:
            self._plot_trajectory(ax, trajectory)
        self._finalize_plot(ax)
        if show:
            plt.show()
        return ax, fig

    # ====== Built-in Method ======
    @override
    @abstractmethod
    def __eq__(self, other: object) -> bool:
        pass

    @override
    @abstractmethod
    def __ne__(self, other: object) -> bool:
        pass

    @override
    def __hash__(self) -> int:
        """Return a unique hash based on the instance identity.

        Returns:
            int: Hash of the arena instance.
        """
        return id(self)

    # endregion

    # endregion
