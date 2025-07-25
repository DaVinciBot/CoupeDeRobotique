# ====== Code Summary ======
# The BaseArena class models a physical arena with zones, border buffers, and obstacles.
# It initializes a list of zones with added buffers and includes a GridManager for managing grid-based zones.
# Methods include creating border zones, adding buffers to zones, handling zone accessibility, visualizing the arena,
# and computing enemy or robot positions based on various inputs.

from abc import ABC, abstractmethod
from typing import cast, override

import matplotlib.pyplot as plt
import numpy as np
from loggerplusplus import Logger, time_tracker

from arena.base_arena.arena_zones import (
    AllyZone,
    BaseArenaZone,
    BorderZone,
    EnemyZone,
)
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
        """Initializes the BaseArena instance with dimensions, zones, and configuration parameters.

        Args:
            logger (Logger): Logger instance for general arena logging.
            width (int): Width of the arena in centimeters.
            height (int): Height of the arena in centimeters.
            forbidden_cover_threshold (float): Threshold for forbidden cover in the grid.
            border_buffer (float): Buffer distance for the arena border.
            obstacle_buffer (float): Buffer distance for obstacles.
            zones (list[BaseArenaZone]): List of pre-defined zones in the arena.
            chunk_size (int, optional): Size of chunks in the grid manager. Defaults to 10.
            grid_manager_logger (Logger | None, optional): Logger instance for grid manager logging. Defaults to None.
        """
        # ====== Initialized constructor based attributes ======
        # 1. Logger
        self.logger: Logger = logger
        # 2. Dimensions
        self.width: int = width
        self.height: int = height

        if border_buffer % chunk_size != 0:
            self.logger.warning(
                "The border buffer is not a multiple of the chunk size -> "
                "the not walkable area will not be aligned with the grid",
            )

        if obstacle_buffer % chunk_size != 0:
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

        # Give to each zone the grid manager to do a callback when they update their state
        for i in range(len(self.zones)):
            self.zones[i].update_callback = self._get_grid_manager

        # Add forbidden and border zones to the grid manager
        for zone in self.zones:
            if not zone.is_accessible():
                self.grid_manager.add_forbidden_static_zone(zone.buffered_polygon)

        # ====== Initialized derivative attributes ======
        # 1. Team color
        self.team_color: TeamColor = TeamColor.UNDEFINED

        # 2. Additional zones: Border, Ally and Enemy
        # 2.1 Border zone
        # We don't need to add the border zone to self.zones, it's not a zone that need to be updated -> 100% static
        self.border_zone: BorderZone = self.__create_arena_border_zone()
        self.grid_manager.add_forbidden_static_zone(self.border_zone.buffered_polygon)

        # 2.2 Ally and Enemy zones
        # Don't need to add these zones to self.zones, they have their own update method
        # Don't need to add these zones to the grid manager, they are not static zones -> 100% dynamic
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

        # ====== Misc ======
        self.__prepare_zones()

    # ====== Private Methods ======
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

    # ====== Protected Methods ======
    def _get_grid_manager(self) -> GridManager:
        """Return the grid manager instance for zone callbacks.

        Returns:
            GridManager: The current grid manager.
        """
        return self.grid_manager

    def _pol_to_abs_cart(self, polars: np.ndarray) -> MultiPoint:
        """Converts polar coordinates to absolute Cartesian coordinates.

        Args:
            polars (np.ndarray): Array of polar coordinates in the form of (angle, distance).

        Returns:
            MultiPoint: Array of absolute Cartesian coordinates.
        """
        return MultiPoint(
            [
                (
                    self.ally_zone.point.x
                    + np.cos(self.ally_zone.point.theta - polars[i, 0]) * polars[i, 1],
                    self.ally_zone.point.y
                    + np.sin(self.ally_zone.point.theta - polars[i, 0]) * polars[i, 1],
                )
                for i in range(len(polars))
            ],
        )

    # ====== Public Methods ======
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
        optimized_update: bool = True,
        _enemy_position: Point | None = None,  # Only for testing and simulation purpose
    ) -> None:
        """Updates the state of the arena, zones, and grid based on ally and enemy positions.

        Args:
            ally_position (OrientedPoint): Current position of the ally robot.
            lidar_scan_polars (np.ndarray): Lidar scan data in polar coordinates.
            optimized_update (bool, optional): If ``True``, only updates intersecting zones. Defaults to ``True``.
            _enemy_position (Point | None, optional): Pre-defined enemy position. Defaults to None.
        """
        # 1.Compute enemy position if not directly provided in absolute cartesian coordinates
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
        all_points: list[OrientedPoint | Point] = [ally_position, enemy_position]
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
        _start_time: int = -1,
        _numb_enemy: bool = False,
    ) -> Point | OrientedPoint:
        """Computes the position of the enemy based on lidar scans and updates the arena.

        This function calculates the position of the enemy by processing the lidar scans.
        It removes any obstacles that are outside the arena, and then determines the closest obstacle as the enemy
        position.
        If the enemy position is within a stuff zone, it marks that zone as FORBIDDEN.

        Args:
            lidar_scan_polars (np.ndarray): Detection points from the LIDAR scan.
            ally_position (OrientedPoint): Current ally position.
            _start_time (int, optional): Starting timestamp for the computation. Defaults to -1 for no specific start time.
            _numb_enemy (bool, optional): Whether the enemy is inactive. Defaults to ``False``.

        Returns:
            Point | OrientedPoint: The computed enemy position.
        """
        obstacles: MultiPoint = self.remove_outside(
            self._pol_to_abs_cart(lidar_scan_polars),
        )

        if not is_empty(obstacles):
            return nearest_points(ally_position, obstacles)[1]

        return self.enemy_zone.point

    """
        Geometry helpers function part
    """

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
        goal: int | BaseArenaZone | OrientedPoint | Point,
    ) -> OrientedPoint | Point | None:
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

        # 3. If goal is an OrientedPoint or Point, return it as is
        if isinstance(goal, OrientedPoint) or isinstance(goal, Point):
            return goal

        # 4. If goal is not recognized, log an error
        self.logger.error(
            f"Invalid goal type: {type(goal)}. Expected int, BaseArenaZone, OrientedPoint, or Point.",
        )
        return None

    # TODO: Check if this function is still needed, test them (last year code)
    def valid_position(self, pos: Point) -> bool:
        """Check if a given position is within the valid playing area.

        Args:
            pos (Point): The position to check.

        Returns:
            bool: ``True`` if the position is within the playing area, ``False`` otherwise.
        """
        return self.playable_area.contains(pos) or self.playable_area.touches(pos)

    def get_zone_by_location(
        self,
        location: int | BaseArenaZone | Point | OrientedPoint,
    ) -> BaseArenaZone | None:
        """Find the zone that contains a given location.

        Args:
            location (int | BaseArenaZone | Point | OrientedPoint): The location to check.

        Returns:
            BaseArenaZone | None: The zone containing the location, or None if not found.
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
        """Check if a given geometric element intersects with any zone that has the specified accessibility.

        Args:
            accessibility (str): The accessibility type to check for zones.
            element (Geometry): The geometric element to check for intersection.

        Returns:
            bool: ``True`` if the element intersects with any zone that has the specified accessibility, ``False`` otherwise.

        Raises:
            ValueError: If no zones have the specified accessibility.
        """
        zones_to_check = self.find_zone_accessibility(accessibility)
        if not zones_to_check:
            raise ValueError(f"No zones has accessibility: '{accessibility}'.")

        for zone in zones_to_check:
            if zone and zone.polygon.intersects(element):
                return True
        return False

    def contains(self, element: Geometry) -> bool:
        """Check if a point is in the arena bounds

        Args:
            element (Geometry): The point to check. Points, Polygons etc. are all Geometries.

        Returns:
            bool: ``True`` if the element is entirely in the arena, ``False`` otherwise
        """
        return self.bounding_area.contains(element)

    """
        Visualisation part
    """

    # ====== Private Methods: draw helpers ======
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
            head_width (float | None): Width of the arrow head. Defaults to None -> norm * 0.2.
            head_length (float | None): Length of the arrow head. Defaults to None -> norm * 0.3.
        """
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
        """Plot a polygon or multipolygon on a matplotlib axis.

        - Fills polygons without holes, optionally with hatching.
        - Draws only outlines (dashed) for polygons with holes.
        - Ensures that the same legend label is not added more than once.

        Args:
            ax (plt.Axes): Axis on which to draw.
            polygon (Polygon): Polygon to plot.
            color (str): Fill color of the polygon.
            label (str | None, optional): Legend label. Defaults to None.
            alpha (float, optional): Transparency factor. Defaults to 1.0.
            hatch (str | None, optional): Matplotlib hatching pattern, e.g., '/' or '\\'. Defaults to None for no hatching.
            hatch_color (str | None, optional): Color of the hatching lines. Defaults to None.
        """
        # Avoid duplicate labels
        existing_labels = ax.get_legend_handles_labels()[1]
        if label is not None and label in existing_labels:
            label = None

        if len(polygon.interiors) == 0:
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
            transparency_factor (float, optional): Alpha value multiplier. Defaults to 1.0.
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
            # Don't plot uid for ally and enemy zones (they continuously increase at each update)
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
                    # Plot nearest go-to position as green arrow (if oriented point) or green dot (if point)
                    if go_to_position == nearest_point:
                        if isinstance(go_to_position, OrientedPoint):
                            self.__plot_oriented_arrow(
                                ax,
                                go_to_position,
                                color="green",
                                norm=5,
                                head_width=4,
                                head_length=3,
                            )
                        elif isinstance(go_to_position, Point):
                            ax.plot(go_to_position.x, go_to_position.y, "go")
                        else:
                            self.logger.error(
                                f"Invalid go-to position type: {type(go_to_position)}",
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

    # ====== Public Methods ======
    def visualize(
        self,
        # Visualization options
        show_buffer: bool = True,
        trajectory: list[OrientedPoint] | None = None,
        transparency_factor: float = 1.0,
        display_zones_go_to_positions: bool = True,
        show_ally_direction: bool = True,
        # Plot options
        show: bool = True,
        plot: tuple[plt.Axes, plt.Figure] | None = None,
        # Additional options
        additional_zones: list[BaseArenaZone] | None = None,
        additional_points: list[Point | OrientedPoint] | None = None,
    ) -> tuple[plt.Axes, plt.Figure]:
        # 1.Define the figure and axis
        if plot:
            ax, fig = plot
        else:
            fig, ax = plt.subplots(figsize=(20, 12))

        # 2. Draw the arena boundary
        self.__plot_polygon(ax, self.bounding_area, color="#f0f0f0", label="Arena")

        # 3. Plot zones and their buffers
        # 3.1 Border zone
        self.__plot_zone(
            ax,
            self.border_zone,
            show_buffer,
            show_ally_direction=False,
            display_zones_go_to_positions=False,
            transparency_factor=transparency_factor,
        )

        # 3.2 All zones (stored in self.zones)
        for zone in self.zones:
            self.__plot_zone(
                ax,
                zone,
                show_buffer,
                show_ally_direction=False,
                display_zones_go_to_positions=display_zones_go_to_positions,
                transparency_factor=transparency_factor,
            )

        # 3.3 Additional zones (if provided)
        if additional_zones:
            for zone in additional_zones:
                self.__plot_zone(
                    ax,
                    zone,
                    show_buffer,
                    show_ally_direction=False,
                    display_zones_go_to_positions=display_zones_go_to_positions,
                    transparency_factor=transparency_factor,
                )

        # 3.4 Ally and Enemy zones
        self.__plot_zone(
            ax,
            self.enemy_zone,
            show_buffer,
            show_ally_direction=False,
            display_zones_go_to_positions=False,
            transparency_factor=transparency_factor,
        )
        self.__plot_zone(
            ax,
            self.ally_zone,
            show_buffer,
            show_ally_direction,
            display_zones_go_to_positions=False,
            transparency_factor=transparency_factor,
        )

        # 4 Additional points (if provided)
        if additional_points:
            for p in additional_points:
                if isinstance(p, Point):
                    ax.plot(p.x, p.y, "ro")
                elif isinstance(p, OrientedPoint):
                    self.__plot_oriented_arrow(
                        ax,
                        p,
                        color="red",
                        norm=5,
                        head_width=4,
                        head_length=3,
                    )
                else:
                    self.logger.error(f"Invalid point type: {type(p)}")

        # 5. Plot trajectory
        if trajectory:
            for i in range(len(trajectory) - 1):
                # Draw a line connecting the current point to the next point
                ax.plot(
                    [trajectory[i].x, trajectory[i + 1].x],
                    [trajectory[i].y, trajectory[i + 1].y],
                    color="purple",
                    linewidth=1,
                    alpha=0.2,
                )

        # 6. Set plot properties
        ax.set_xlim(self.width, 0)  # Reverse x-axis
        ax.set_ylim(0, self.height)  # Keep y-axis normal
        ax.spines["top"].set_visible(False)  # Hide top frame line
        ax.spines["right"].set_visible(False)  # Hide right frame line
        ax.spines["left"].set_position(("axes", 1))  # Move y-axis to the right
        ax.yaxis.tick_right()  # Move y-axis labels to the right
        ax.yaxis.set_label_position("right")

        ax.set_aspect("equal", adjustable="box")
        ax.set_title("Arena Visualization")

        # Place legend on the right
        plt.legend(loc="center right", bbox_to_anchor=(-0.1, 0.5))

        # 6. Show or return the plot
        plt.tight_layout()
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
