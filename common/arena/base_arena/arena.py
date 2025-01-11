# ====== Code Summary ======
# The BaseArena class models a physical arena with zones, border buffers, and obstacles.
# It initializes a list of zones with added buffers and includes a GridManager for managing grid-based zones.
# Methods include creating border zones, adding buffers to zones, and visualizing the arena with optional buffer zones.

# ====== Imports ======
# Standard library imports
from concurrent.futures import ThreadPoolExecutor
from functools import partial

# Third-party library imports
from matplotlib import scale
import matplotlib.pyplot as plt
import shapely

# Internal project imports
from geometry import (
    BufferCapStyle,
    BufferJoinStyle,
    LineString,
    Polygon,
    box,
    Point,
    OrientedPoint,
    MultiPoint,
    prepare,
    Geometry,
    create_straight_rectangle,
    distance,
)
from logger import Logger, LogLevels, time_tracker
from arena.base_arena.grid_manager import GridManager
from arena.base_arena.arena_zone import (
    # Enums
    ZoneType,
    ZoneAccessibility,
    # Zones
    BaseArenaZone,
    BorderZone,
    YellowReservedZone,
    BlueReservedZone,
    EnemyZone,
)


# ====== BaseArena Class ======
class BaseArena:
    """
    Represents the arena and its zones, including buffer zones and borders.

    Attributes:
        logger (Logger): Logger instance for logging information.
        width (int): Width of the arena in centimeters.
        height (int): Height of the arena in centimeters.
        border_buffer (float): Buffer distance for the arena border.
        obstacle_buffer (float): Buffer distance for obstacles.
        zones (list[BaseArenaZone]): List of all zones in the arena.
        grid_manager (GridManager): Grid manager instance for managing zones.
    """

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
        grid_manager_logger: Logger = Logger(
            identifier="GridManager",
            decorator_level=LogLevels.INFO,
            print_log_level=LogLevels.DEBUG,
            file_log_level=LogLevels.DEBUG,
        ),
    ) -> None:
        self.logger: Logger = logger

        self.width: int = width
        self.height: int = height

        if border_buffer % chunk_size != 0:
            self.logger.log(
                "The border buffer is not a multiple of the chunk size -> "
                "the not walkable area will not be aligned with the grid",
                LogLevels.WARNING,
            )

        if obstacle_buffer % chunk_size != 0:
            self.logger.log(
                "The obstacle buffer is not a multiple of the chunk size -> "
                "the not walkable area will not be aligned with the grid",
                LogLevels.WARNING,
            )

        self.border_buffer: float = border_buffer
        self.obstacle_buffer: float = obstacle_buffer

        # Initialize zones with added buffer
        self.zones: list[BaseArenaZone] = zones

        # Add border zone
        self.border_zone = self.__create_arena_border_zone()
        self.zones.append(self.border_zone)

        # Initialize grid manager
        self.grid_manager: GridManager = GridManager(
            grid_manager_logger, chunk_size, width, height, forbidden_cover_threshold
        )

        # Give to each zone the grid manager to do a callback when they update their state
        for i in range(len(self.zones)):
            self.zones[i].update_callback = lambda: self.grid_manager

        # Add forbidden and border zones to the grid manager
        for zone in self.zones:
            if not zone.is_accessible():
                self.grid_manager.add_forbidden_static_zone(zone.buffered_polygon)

        self.team_color = None

        # Add area for calculation
        self.game_area: Polygon = create_straight_rectangle(
            Point(0, 0), Point(width, height)
        )

        # Add playing area for calculation
        self.playing_area: Polygon = self.game_area.difference(
            self.border_zone.buffered_polygon
        ).buffer(-self.obstacle_buffer)

        self.prepare_zones()

    # ====== Private Methods ======

    def __create_arena_border_zone(self) -> BorderZone:
        """
        Create a border zone around the arena with a specified buffer width.
        Prevents the robot from approaching too close to the arena edges.
        """
        arena_polygon = box(0, 0, self.width, self.height)
        inner_polygon = BaseArenaZone.add_buffer_to_zone(
            arena_polygon, -self.border_buffer
        )
        border_zone_polygon = arena_polygon.difference(inner_polygon)

        return BorderZone(
            logger=Logger(
                identifier="BorderZone",
                decorator_level=LogLevels.INFO,
                print_log_level=LogLevels.DEBUG,
                file_log_level=LogLevels.DEBUG,
            ),
            buffer_size=self.border_buffer,
            buffered_polygon=border_zone_polygon,
        )

    @staticmethod
    def __plot_polygon(
        ax,
        polygon: Polygon,
        color: str,
        label: str = None,
        alpha: float = 1.0,
        hatch: str = None,
        hatch_color: str = None,
    ) -> None:
        """
        Helper method to plot a polygon or multipolygon on a matplotlib axis.

        - Fills polygons without holes, optionally with hatching.
        - Draws only outlines (dashed) for polygons with holes.
        - Ensures that the same legend label is not added more than once.

        Parameters:
        - ax: matplotlib axis
        - polygon: Polygon to plot (from shapely.geometry)
        - color: Color of the polygon (fill or outline)
        - label: Legend label (optional)
        - alpha: Transparency of the fill or line (default=1.0)
        - hatch: Hatching pattern (optional), e.g., '/' or '\\'. Set None for no hatching.
        - hatch_color: Color of the hatching lines (optional, default same as outline color)
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
        ax,
        zone: BaseArenaZone,
        show_buffer: bool,
        transparency_factor: float = 1.0,
    ) -> None:
        """Plots zones and their buffers on the arena."""
        if show_buffer:
            # Plot buffer zone in transparent color
            self.__plot_polygon(
                ax,
                zone.buffered_polygon,
                color=zone.zone_color,
                alpha=0.5 * transparency_factor,
            )

        # Plot the original zone in full color and hatch if necessary
        if not zone.is_instance(BorderZone):
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

            self.__plot_polygon(
                ax,
                zone.polygon,
                color=zone.zone_color,
                label=zone.zone_type.name,
                alpha=0.8 * transparency_factor,
                **hatch_params,
            )

    # ====== Public Methods ======
    @time_tracker(lambda self: self.logger)
    def set_team_color(self, team_color: str) -> None:
        """Set the team color for determining zone accessibility."""
        self.team_color = team_color
        self.update([], [], optimized_update=False)  # Force to update all zones
        print()

    @time_tracker(lambda self: self.logger)
    def update(
        self,
        ally_positions: list[OrientedPoint],
        enemy_positions: list[OrientedPoint],
        enemy_velocity: list[float] = 0.0,
        optimized_update: bool = True,
    ) -> None:
        """Update the zones based on the positions of allies and enemies."""
        for i in range(len(ally_positions)):
            ally_positions[i] = Point(ally_positions[i].x, ally_positions[i].y)
        for i in range(len(enemy_positions)):
            enemy_positions[i] = Point(enemy_positions[i].x, enemy_positions[i].y)

        # Create Enemy zone based on position and velocity
        enemy_zones = [
            EnemyZone(
                logger=self.logger,
                polygon=create_straight_rectangle(
                    Point(enemy_position.x - 5, enemy_position.y - 5),
                    Point(enemy_position.x + 5, enemy_position.y + 5),
                ),
            )
            for enemy_position in enemy_positions
        ]
        # Remove previous enemy zones
        self.zones = [zone for zone in self.zones if zone != EnemyZone]

        self.zones.extend(enemy_zones)
        self.grid_manager.update_dynamic_forbidden_zones(
            [enemy_zone.polygon for enemy_zone in enemy_zones]
        )

        # Update zone
        # optimized: Update only the zones that intersect with the points
        all_points = ally_positions + enemy_positions
        for zone in self.zones:
            if not optimized_update or any(
                zone.polygon.contains(pt) for pt in all_points
            ):
                zone.update(
                    self.team_color,
                    ally_positions=ally_positions,
                    enemy_positions=enemy_positions,
                )

        # def _update_zone(_zone, _optimized_update, _all_points, _team_color, _ally_positions, _enemy_positions):
        #     try:
        #         if not _optimized_update or any(_zone.polygon.contains(pt) for pt in _all_points):
        #             _zone.update(
        #                 team_color=_team_color,
        #                 ally_positions=_ally_positions,
        #                 enemy_positions=_enemy_positions
        #             )
        #     except Exception as e:
        #         print(e)
        #
        # prewrapped_update = partial(
        #     _update_zone,
        #     _optimized_update=optimized_update,
        #     _all_points=ally_positions + enemy_positions,
        #     _team_color=self.team_color,
        #     _ally_positions=ally_positions,
        #     _enemy_positions=enemy_positions
        # )
        #
        # # Utilisation de ThreadPoolExecutor
        # with ThreadPoolExecutor() as executor:
        #     list(executor.map(prewrapped_update, self.zones))

    def visualize(
        self,
        show_buffer: bool = True,
        show: bool = True,
        plot: tuple[plt.axes, plt.figure] = None,
        transparency_factor: float = 1.0,
        display_points: list[Point] = None,
        display_default_destination_zone=True,
        starting_point_to_display_default_destination_zone: Point = None,
    ) -> tuple[plt.axes, plt.figure]:
        """
        Visualize the arena, including its zones, buffers, and accessibility grid.

        Args:
            show_buffer (bool): If True, buffer zones are displayed.
            show (bool): If True, the plot is displayed.
            plot (tuple[plt.axes, plt.figure]): Tuple containing axes and figure for plotting.
            transparency_factor (float): Transparency factor zones (default=0.5).
            display_points (list[Point]): List of points to display on the plot.
            display_default_destination_zone (bool): If True, the default destination point of each zone is displayed.
            starting_point_to_display_default_destination_zone: The starting point to display the default destination zone.
        """
        if plot:
            ax, fig = plot
        else:
            fig, ax = plt.subplots(figsize=(12, 6))

        # Draw the arena boundary
        arena_polygon = box(0, 0, self.width, self.height)
        self.__plot_polygon(ax, arena_polygon, color="#f0f0f0", label="Arena")

        # Plot zones and their buffers
        for zone in self.zones:
            self.__plot_zone(ax, zone, show_buffer, transparency_factor)

        if display_points:
            if not isinstance(display_points, list):
                display_points = [display_points]
            for point in display_points:
                ax.plot(point.x, point.y, "ro")

        if not starting_point_to_display_default_destination_zone:
            starting_point_to_display_default_destination_zone = Point(
                self.width / 2, self.height / 2
            )

        if display_default_destination_zone:
            for zone in self.zones:
                if isinstance(zone, BorderZone):
                    continue
                destination_point = self.compute_go_to_destination(
                    starting_point_to_display_default_destination_zone, zone.polygon
                )
                if destination_point:
                    ax.plot(
                        destination_point.x,
                        destination_point.y,
                        "bo",
                    )

        ax.set_xlim(self.width, 0)  # Reverse x-axis
        ax.set_ylim(0, self.height)  # Keep y-axis normal
        ax.spines["top"].set_visible(False)  # Hide top frame line
        ax.spines["right"].set_visible(False)  # Hide right frame line
        ax.spines["left"].set_position(("axes", 1))  # Move y-axis to the right
        ax.yaxis.tick_right()  # Move y-axis labels to the right
        ax.yaxis.set_label_position("right")

        ax.set_aspect("equal", adjustable="box")
        ax.set_title("Arena Visualization")

        # Place legend on the left
        plt.legend(loc="center right", bbox_to_anchor=(-0.1, 0.5))

        plt.tight_layout()
        if show:
            plt.show()
        return ax, fig

    def prepare_zones(self):
        """Prepare all values of self.zones, to optimize later calculations"""
        prepare(self.game_area)
        prepare(self.playing_area)
        for zone in self.zones:
            prepare(zone.polygon)

    def valid_position(self, pos: Point) -> bool:
        """
        Check if a given position is within the valid playing area.

        Args:
            pos (Point): The position to check.

        Returns:
            bool: True if the position is within the playing area, False otherwise.
        """
        return self.playing_area.contains(pos)

    def find_zone_accessibility(self, accessibility: str) -> list[BaseArenaZone]:
        """
        Find and return a list of zones with the specified accessibility.

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
        """
        Check if a given geometric element intersects with any zone that has the specified accessibility.
        Args:
            accessibility (str): The accessibility type to check for zones.
            element (Geometry): The geometric element to check for intersection.
        Returns:
            bool: True if the element intersects with any zone that has the specified accessibility, False otherwise.
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
            bool: True if the element is entirely in the arena, False otherwise
        """
        return self.game_area.contains(element)

    def nearest_points_between_geoms(g1, g2):
        """Returns the calculated nearest points in the input geometries

        The points are returned in the same order as the input geometries.
        """
        seq = shapely.shortest_line(g1, g2)
        if seq is None:
            if g1.is_empty:
                raise ValueError("The first input geometry is empty")
            else:
                raise ValueError("The second input geometry is empty")

        p1 = shapely.get_point(seq, 0)
        p2 = shapely.get_point(seq, 1)
        return (p1, p2)

    def compute_go_to_destination(
        self,
        start_point: Point,
        destination: Polygon | Point,
    ) -> Point | None:
        """Compute the destination point to go to inside the specified zone. Only works is the arena is rectangular.

        Args:
            start_point (Point): The starting point for the robot.
            zone (Polygon): The zone where the robot should go.
            delta (float): The distance from the border of the zone.

        Returns:
            Point: The destination point to go to inside the zone.
        """

        # TODO: Implement delta as in 2024 if necessary

        if not self.valid_position(start_point):
            self.logger.log(
                f"The starting point {start_point} is outside the arena bounds.",
                LogLevels.WARNING,
            )
            return None

        if isinstance(destination, Point):
            if not self.valid_position(destination):
                self.logger.log(
                    f"The destination point {destination} is outside the arena's bounds.",
                    LogLevels.WARNING,
                )
                return None
            return destination

        if isinstance(destination, Polygon):
            if not destination.centroid:
                self.logger.log(
                    f"The destination polygon {destination} has no centroid, couldn't establish a destination point.",
                    LogLevels.WARNING,
                )
                return None
            destination_point = destination.centroid
            new_x = destination_point.x
            new_y = destination_point.y

            if destination_point.x < self.border_buffer + self.obstacle_buffer:
                new_x = self.border_buffer + self.obstacle_buffer
            if (self.width - destination_point.x) < (
                self.border_buffer + self.obstacle_buffer
            ):
                new_x = self.width - (self.border_buffer + self.obstacle_buffer)
            if destination_point.y < self.border_buffer + self.obstacle_buffer:
                new_y = self.border_buffer + self.obstacle_buffer
            if (self.height - destination_point.y) < (
                self.border_buffer + self.obstacle_buffer
            ):
                new_y = self.height - (self.border_buffer + self.obstacle_buffer)

            destination_point = Point(new_x, new_y)

            return destination_point

        self.logger.log(
            f"The destination {destination} is not a valid geometry.",
            LogLevels.WARNING,
        )
        return None
