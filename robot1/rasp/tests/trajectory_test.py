import matplotlib.pyplot as plt
import numpy as np
import math
import random
import time

from matplotlib.animation import FuncAnimation
from config_loader import CONFIG

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

# Import from common
from geometry import OrientedPoint

from arena import (
    ShowArena,
    BaseArenaZone,
    ZoneType,
    EnemyZone,
    StuffZone,
    ForbiddenZone,
    BlueReservedZone,
    YellowReservedZone,
    BorderZone,
)
from movement_manager import MovementManager, GoToParams, MovementStatus
from rolling_basis_handler import SpeedProfile
from pathfinding.core.grid import Grid, GridNode
from loggerplusplus import Logger

from path_finding import PathFinder

start = OrientedPoint(30, 30, 0.0)
goal = OrientedPoint(150, 140, 0.0)

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
arena_logger = Logger(identifier="PathFinder", follow_logger_manager_rules=True)

from movement.trajectory_computer.trajectory_computer import TrajectoryComputer, TrajectoryParams

trajectory_computer = TrajectoryComputer(
    logger=Logger(identifier="TrajectoryComputer", follow_logger_manager_rules=True),
    path_finder_logger=arena_logger,
    arena_ptr=arena,
    trajectory_params=TrajectoryParams(
        speed_profile=SpeedProfile.from_dict(CONFIG.ROLLING_BASIS_HIGH_SPEED_PROFILE),
        goal=arena.zones[6],
        resolution=5,
        smooth_trajectory=True,
    )
)

arena.update(
    ally_position=start,
    lidar_scan_polars=np.array([]),
)

trajectory_computer.compute(use_static_and_dynamic_grid=False)

arena.visualize(trajectory=trajectory_computer.path_finder.oriented_path_found)

angular_speeds = []
linear_speeds = []
positions = []

start_time = time.time()
while start_time + trajectory_computer.total_duration > time.time():
    time.sleep(0.1)
    cmd = trajectory_computer.get_position_speed()

    positions.append(cmd.position)
    linear_speeds.append(cmd.linear_speed)
    angular_speeds.append(cmd.angular_speed)
    print(f"{int(time.time() - start_time)}/{int(trajectory_computer.total_duration)}")


x_positions = [pos.x for pos in positions]
y_positions = [pos.y for pos in positions]
theta_positions = [pos.theta for pos in positions]

# Création d'une figure avec plusieurs sous-graphiques
fig, axs = plt.subplots(2, 2, figsize=(12, 8))

# Graphique des vitesses angulaires
axs[0, 0].plot(angular_speeds, label="Vitesse angulaire")
axs[0, 0].set_xlabel("Temps (itérations)")
axs[0, 0].set_ylabel("Vitesse angulaire")
axs[0, 0].set_title("Évolution de la vitesse angulaire")
axs[0, 0].legend()
axs[0, 0].grid(True)

# Graphique des vitesses linéaires
axs[0, 1].plot(linear_speeds, label="Vitesse linéaire", color='r')
axs[0, 1].set_xlabel("Temps (itérations)")
axs[0, 1].set_ylabel("Vitesse linéaire")
axs[0, 1].set_title("Évolution de la vitesse linéaire")
axs[0, 1].legend()
axs[0, 1].grid(True)

# Graphique des positions X-Y (Trajectoire) avec double axe Y
ax1 = axs[1, 0]  # Axe principal
ax2 = ax1.twinx()  # Deuxième axe Y

ax1.plot(x_positions, color='b', label="X (Position)")
ax1.plot(y_positions, color='r', label="Y (Position)")
ax1.set_ylabel("Position (cm)", color='b')
ax1.tick_params(axis='y', labelcolor='b')

ax2.plot(theta_positions, label="Orientation (Theta)", color='m')
ax2.set_ylabel("Orientation (theta)", color='m')
ax2.tick_params(axis='y', labelcolor='m')

ax1.set_xlabel("Temps (itérations)")
ax1.set_title("Évolution de la position X et Y")
ax1.grid(True)

# Graphique des angles Theta en fonction du temps
axs[1, 1].plot(theta_positions, label="Orientation (Theta)", color='m')
axs[1, 1].set_xlabel("Temps (itérations)")
axs[1, 1].set_ylabel("Theta (orientation)")
axs[1, 1].set_title("Évolution de l'orientation Theta")
axs[1, 1].legend()
axs[1, 1].grid(True)

# Ajustement des espacements entre les sous-graphiques
plt.tight_layout()
plt.show()
