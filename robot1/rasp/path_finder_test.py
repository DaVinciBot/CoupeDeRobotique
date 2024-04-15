import matplotlib.pyplot as plt
import numpy as np
import math
import random
import time

from matplotlib.animation import FuncAnimation
from config_loader import CONFIG

# Import from common
from WS_comms import WSclient, WSclientRouteManager, WSender, WSreceiver, WSmsg
from logger import Logger, LogLevels
from geometry import OrientedPoint
from arena import MarsArena
from path_finding.grid import Grid
from path_finding.node import Node
from path_finding.path_finder import PathFinder

logger_arena = Logger(
    identifier="arena",
    decorator_level=LogLevels.INFO,
    print_log_level=LogLevels.INFO,
    file_log_level=LogLevels.DEBUG,
)
arena = MarsArena(0, logger_arena)

grid = arena.get_grid(5)

path_finder = PathFinder(
    motions= [
        Node(1, 0, 1),
        Node(0, 1, 1),
        Node(-1, 0, 1),
        Node(0, -1, 1),
        Node(1, 1, math.sqrt(2)),
        Node(1, -1, math.sqrt(2)),
        Node(-1, 1, math.sqrt(2)),
        Node(-1, -1, math.sqrt(2))
    ],
    initial_grid=grid,
    start=(0, 0),
    goal=(35, 35)
)

last_enemy_pos = []

def generate_enemy():
    pos_tl = (random.randint(6, 54), random.randint(6, 34))
    pos_br = (pos_tl[0] + 5, pos_tl[1] + 5)

    obstacle_position = []
    for x in range(pos_tl[0], pos_br[0]):
        for y in range(pos_tl[1], pos_br[1]):
            obstacle_position.append((x, y))

    return obstacle_position

def update(frame):
    global last_enemy_pos
    plt.clf()  # Clear the current figure
    path_finder.find_shortest_path()
    path = path_finder.compute_current_path()

    X = [n.coords[1] for n in path]
    Y = [n.coords[0] for n in path]

    plt.scatter(X, Y)
    plt.imshow(path_finder.grid.g, cmap='Reds', interpolation='nearest')
    plt.colorbar()


    # Update obstacles
    tmp = generate_enemy()
    path_finder.update_obstacle(
        obstacles_to_add=tmp,
        obstacles_to_remove=last_enemy_pos
    )
    last_enemy_pos = tmp

fig, ax = plt.subplots()  # Set up the plot
ani = FuncAnimation(fig, update, interval=1000)  # Update every 2000 milliseconds (2 seconds)
plt.show()


