from config_loader import CONFIG

# ====== Standard Library Imports ======
import matplotlib.pyplot as plt
import numpy as np
import random
import math
import json

# ====== Third-party library imports ======
from ws_comms import WSmsg, WSreceiver, WServerRouteManager, WSender
from loggerplusplus import Logger
from taskbrain import Brain

# ====== Local Library Imports ======
from geometry import OrientedPoint, Point, is_empty
from arena import ShowArena, BaseArenaZone
from navigation import (
    Navigator,
    NavigatorTaskParams,
    TrajectoryPlanCommand,
    PathPlannerPathPlanParamsFactory,
)
from arena import AllyZone, TeamColor

# ====== Internal Project Imports ======
from controllers.rolling_basis import RollingBasis, RollingBasisDummy
from controllers.actuators import Actuators, ActuatorsDummy
from sensors import Lidar
from navigation_tasks.tasks import yellow_start_tasks

from boombot_strategy import ShowGameContext
from boombot_strategy.strategies import yellow_strategy


class MainBrain(Brain):
    def __init__(
        self,
        logger: Logger,
        # Sensor
        lidar: Lidar,
        # Environment
        arena: ShowArena,
        # WS routes
        ws_cmd: WServerRouteManager,
    ) -> None:
        self.lidar: Lidar = lidar
        self.arena: ShowArena = arena
        self.ws_cmd: WServerRouteManager = ws_cmd

        # Shared attributes
        self.rolling_basis_odometrie: OrientedPoint = OrientedPoint(0, 0, 0)

        super().__init__(logger, self)

    """
    ### Secondary Processes ###
    """

    """ ### Routines ### """

    @Brain.task(
        process=True,
        run_on_start=False,
        refresh_rate=0.1,
        define_loop_later=True,
        start_loop_marker="# --- MetaProg is insane (loop) --- #",
    )
    def run_strategy(self) -> None:
        # --- Initialization --- #
        rolling_basis = RollingBasisDummy(
            logger=Logger(identifier="RollingBasis", follow_logger_manager_rules=True)
        )
        rolling_basis.set_odometrie(self.rolling_basis_odometrie)

        actuators = ActuatorsDummy(
            logger=Logger(identifier="Actuators", follow_logger_manager_rules=True)
        )

        # --- MetaProg is insane (loop) --- #
        yellow_strategy.tick(
            ShowGameContext(
                arena=self.arena, rolling_basis=rolling_basis, actuators=actuators
            )
        )

        self.rolling_basis_odometrie = rolling_basis.odometrie

    @Brain.task(
        process=True,
        run_on_start=True,
        refresh_rate=0.1,
        define_loop_later=True,
        start_loop_marker="# --- MetaProg is insane (loop) --- #",
    )
    def visualisation(self) -> None:
        fig, (ax1, ax2) = plt.subplots(1, 2)

        # --- MetaProg is insane (loop) --- #

        # Visualize the arena
        ax1.clear()
        self.arena.visualize(
            # Visualization options
            show_buffer=True,
            trajectory=None,
            display_zones_go_to_positions=True,
            show_ally_direction=True,
            # Plot options
            show=False,
            plot=(ax1, fig),
            # Additional options
            additional_zones=None,
        )
        ax1.set_title("Arena")

        # Visualize the grid manager
        ax2.clear()
        self.arena.grid_manager.visualize(
            only_static_grid=True,
            # Plot options
            show=False,
            plot=(ax2, fig),
        )
        ax2.set_title("Grid Manager")

        plt.tight_layout()
        plt.pause(0.01)

    """
    ### Main Process ###
    """

    """ ### Routines ### """

    @Brain.task(process=False, run_on_start=True, refresh_rate=0.2)
    async def update_arena(self) -> None:
        # Update the arena with the new position of the robot
        self.arena.update(
            ally_position=self.rolling_basis_odometrie,
            lidar_scan_polars=np.array([]),  # self.lidar.scan_to_polars(),
            optimized_update=True,
            # _enemy_position=self.position_generator(),
        )

    """ ### One-Shot Tasks ### """

    @Brain.task(process=False, run_on_start=True)
    async def start(self):
        self.arena.set_team_color(TeamColor.YELLOW)
        # Start robot position
        start_position = OrientedPoint(20, 25, 0)
        self.arena.enemy_zone.update(
            self.arena.team_color, start_position, Point(290, 190)
        )
        self.rolling_basis_odometrie = start_position

        await self.run_strategy()
