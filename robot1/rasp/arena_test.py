import numpy as np

from config_loader import CONFIG

from pathfinding.core.grid import Grid, GridNode

from path_finding import PathFinder
import matplotlib.pyplot as plt

from arena import (
    ShowArena, AllyZone
)

from geometry import (
    Point,
    MultiPoint,
    Polygon,
    MultiPolygon,
    LineString,
    BufferCapStyle,
    BufferJoinStyle,
    Geometry,
    create_straight_rectangle,
    prepare,
    distance,
    OrientedPoint,
    nearest_points,
    box,
)
from loggerplusplus import LoggerManager, LogLevels, LoggerConfig, Logger, logger_colors
from sensors import Lidar, LidarDummy

import asyncio

LoggerManager.enable_files_logs_monitoring_only_for_one_logger = True
LoggerManager.global_config = LoggerConfig.from_kwargs(
    colors=logger_colors.ClassicColors,
    path="logs",
    # LogLevels
    decorator_log_level=LogLevels.INFO,
    print_log_level=LogLevels.DEBUG,
    file_log_level=LogLevels.DEBUG,
    # Loggers Output
    print_log=True,
    write_to_file=True,
    # Monitoring
    display_monitoring=False,
    files_monitoring=False,
    file_size_unit="Go",
    disk_alert_threshold_percent=0.8,
    log_files_size_alert_threshold_percent=0.2,
    max_log_file_size=1.0,
    # Placement
    identifier_max_width=15,
    filename_lineno_max_width=15,
)

ally_finder_logger = Logger(
    identifier="AllyPathFinder",
    follow_logger_manager=True
)
enemy_finder_logger = Logger(
    identifier="EnemyPathFinder",
    dfollow_logger_manager=True
)

arena_logger = Logger(
    identifier="ShowArena",
    follow_logger_manager=True
)

logger_lidar = Logger(
    identifier="LiDAR",
    follow_logger_manager_rules=True,
)

logger_movement_manager = Logger(
    identifier="MovementManager",
    follow_logger_manager_rules=True,
)

arena = ShowArena(
    logger=arena_logger,
    border_buffer=2,
    obstacle_buffer=1,
    chunk_size=5,
    forbidden_cover_threshold=0.1,
)

lidar = LidarDummy(
    logger=logger_lidar,
    min_angle=CONFIG.LIDAR_MIN_ANGLE,
    max_angle=CONFIG.LIDAR_MAX_ANGLE,
    unit_angle=CONFIG.LIDAR_ANGLES_UNIT,
    unit_distance=CONFIG.LIDAR_DISTANCES_UNIT,
    min_distance=CONFIG.LIDAR_MIN_DISTANCE_DETECTION,
)

start = OrientedPoint((200, 100))
goal = OrientedPoint((20, 20))

enemy_start = OrientedPoint((230, 60))
enemy_goal = OrientedPoint((70, 140))

arena.set_team_color("yellow")


async def run_arena_test():
    # arena.visualize(display_points=[Point(15, 15), Point(30, 30)])
    #arena.visualize(display_default_destination_zone=False)
    # scans: np.ndarray = lidar.scan_to_polars()

    arena.update(start, np.ndarray([]), enemy_start)

    #arena.visualize(display_default_destination_zone=False)

    # Ally path
    ally_path_finder = PathFinder(
        logger=ally_finder_logger,
        start=start,
        goal=goal,
        grid_manager=arena.grid_manager,
        path_resolution=5,
    )
    ally_path = ally_path_finder.find_oriented_path(smooth_path=True)

    # Enemy path
    enemy_path_finder = PathFinder(
        logger=enemy_finder_logger,
        start=enemy_start,
        goal=enemy_goal,
        grid_manager=arena.grid_manager,
        path_resolution=5,
    )
    enemy_path = enemy_path_finder.find_oriented_path(smooth_path=True)

    arena.update(start, lidar.scan_to_polars())
    arena.grid_manager.visualize(only_static_grid=True, path=[ally_path])

    # Visualize the path forwarding

    # Initialize figure and axis
    fig, ax = plt.subplots()
    plt.ion()  # Turn on interactive mode

    while len(ally_path) > 3:
        # Update arena visualization
        arena.update(
            ally_position=ally_path[1],
            lidar_scan_polars=np.ndarray([]),
            enemy_position=enemy_path[1],
            optimized_update=True,
        )

        ax.clear()  # Clear the plot instead of closing it

        arena.visualize(display_default_destination_zone=False, plot=(ax, fig))

        # Ensure real-time update
        plt.draw()
        plt.pause(0.01)

        # Update positions
        ally_path_finder.update_current_position(ally_path[1])
        enemy_path_finder.update_current_position(enemy_path[1])

        ally_path = ally_path_finder.find_oriented_path(
            smooth_path=True, use_static_and_dynamic_grid=True
        )
        enemy_path = enemy_path_finder.find_oriented_path(
            smooth_path=True, use_static_and_dynamic_grid=False
        )


asyncio.run(run_arena_test())
