import matplotlib.pyplot as plt
import numpy as np
import time

from config_loader import CONFIG

from geometry import OrientedPoint
from arena import ShowArena
from movement import MovementManager, GoToParams, TrajectoryParams, SpeedProfile
from controllers.rolling_basis import RollingBasisDummy

from loggerplusplus import Logger


# Instantiate object
arena = ShowArena(
    logger=Logger(identifier="ShowArena", follow_logger_manager_rules=True),
    border_buffer=2,
    obstacle_buffer=1,
    chunk_size=5,
    forbidden_cover_threshold=0.1,
)
movement_manager = MovementManager(
    logger=Logger(identifier="MovementManager", follow_logger_manager_rules=True),
    path_finder_logger=Logger(identifier="PathFinder", follow_logger_manager_rules=True),
    trajectory_computer_logger=Logger(identifier="TrajectoryComputer", follow_logger_manager_rules=True),
    arena_ptr=arena,
)
rolling_basis = RollingBasisDummy(logger=Logger(identifier="RollingBasis", follow_logger_manager_rules=True))

# Setup initial position
start = OrientedPoint(30, 30, 0.0)
goal = OrientedPoint(150, 140, 0.0)

rolling_basis.set_odometrie(start)
arena.set_team_color("yellow")
arena.update(ally_position=start, lidar_scan_polars=np.array([]), optimized_update=False)

# Set trajectory
movement_manager.compute_go_to(
    current_linear_speed=0.0,
    current_angular_speed=0.0,
    params=GoToParams(
        trajectory_params=TrajectoryParams(
            speed_profile=SpeedProfile.from_dict(CONFIG.ROLLING_BASIS_HIGH_SPEED_PROFILE),
            goal=goal,
            resolution=1,
            smooth_trajectory=True,
        ),
        acs_distance=30,
        path_finder_recompute_distance=60,
        timeout=-1.0,
        is_mandatory=False,
        goal_tolerance=0.1,
        distance_to_goal_to_dont_recompute_path=5,
    ),
)

# Run trajectory
fig, ax = plt.subplots()

start_time = time.time()
while start_time + movement_manager.trajectory_computer.total_duration > time.time():
    # Handle Trajectory
    cmd = movement_manager.handle_go_to()
    if cmd is None:
        movement_manager.logger.warning("No command received")
        break

    # Update Rolling Basis
    rolling_basis.set_speed_and_position(*cmd.get_command())

    # Update Arena
    arena.update(
        ally_position=rolling_basis.odometrie,
        lidar_scan_polars=np.array([]),
        optimized_update=True
    )

    # Visualize -> update plot
    ax.clear()
    arena.visualize(
        display_default_destination_zone=False,
        trajectory=movement_manager.trajectory_computer.path_finder.oriented_path_found,
        plot=(ax, fig),
        show=False,
    )
    plt.pause(0.01)