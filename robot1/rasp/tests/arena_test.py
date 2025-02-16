# ====== Imports ======
# Config
from config_loader import CONFIG

# Logger: LoggerManager + global configuration
from loggerplusplus import LoggerManager, LogLevels, LoggerConfig, Logger, logger_colors

LoggerManager.enable_files_logs_monitoring_only_for_one_logger = True
LoggerManager.global_config = LoggerConfig.from_kwargs(
    colors=logger_colors.ClassicColors,
    path="logs",
    # LogLevels
    decorator_log_level=LogLevels.DEBUG,
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

from path_finding import PathFinder
import numpy as np
from arena import (
    ShowArena,
    BaseArenaZone,
    BaseArena,
    ForbiddenZone,
    ZoneType,
    EnemyZone,
    StuffZone,
    BlueReservedZone,
    YellowReservedZone,
    BorderZone,
    ZoneAccessibility,
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

import asyncio

ally_finder_logger = Logger(
    identifier="AllyPathFinder",
    follow_logger_manager_rules=True,
)
enemy_finder_logger = Logger(
    identifier="EnemyPathFinder",
    follow_logger_manager_rules=True,
)

arena_logger = Logger(
    identifier="ShowArena",
    follow_logger_manager_rules=True,
)

arena = ShowArena(
    logger=arena_logger,
    border_buffer=2,
    obstacle_buffer=1,
    chunk_size=5,
    forbidden_cover_threshold=0.1,
)

start = OrientedPoint((10, 10))
goal = OrientedPoint((280, 120))

enemy_start = OrientedPoint((230, 60))
enemy_goal = OrientedPoint((70, 140))

arena.visualize()
arena.grid_manager.visualize(only_static_grid=True)
arena.set_team_color("yellow")
arena.visualize()
arena.grid_manager.visualize(only_static_grid=True)

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

arena.update(
    ally_position=OrientedPoint((10, 10)),
    lidar_scan_polars=np.array([]),
)
arena.grid_manager.visualize(only_static_grid=True, path=[ally_path, enemy_path])
