from config_loader import CONFIG

# External imports
import asyncio
import time

# Import from common
from brain import Brain

from WS_comms import WSmsg, WSclientRouteManager, WServerRouteManager
from geometry import OrientedPoint, Point, distance, Polygon

from logger import Logger, LogLevels
import math
from utils import Utils
import matplotlib.pyplot as plt
import time
import numpy as np
import random
# Import from local path
from controllers import RollingBasis, RollingBasisDummy

from path_finding import PathFinder
from arena import ShowArena
from rolling_basis_handler import RollingBasisHandler, RollingBasisCommand
from movement_manager import MovementManager, GoToParams
from rolling_basis_handler import SpeedProfile


class MainBrain(Brain):

    def __init__(
            self, logger: Logger,
            # Controllers
            rolling_basis: RollingBasis | RollingBasisDummy,
            # Environment
            arena: ShowArena,
            # Movement
            movement_manager: MovementManager,
    ) -> None:
        if isinstance(rolling_basis, RollingBasisDummy):
            logger.log("RollingBasisDummy is used", LogLevels.WARNING)

        # Controllers
        self.rolling_basis: RollingBasis = rolling_basis
        # Environment
        self.arena: ShowArena = arena
        # Movement
        self.movement_manager: MovementManager = movement_manager

        super().__init__(logger, self)

        # Attributes for the visualization
        self.fig, self.ax = plt.subplots()

        # For testing
        # self.enemy_point_generator = random_point_generator(
        #     start_point=OrientedPoint(280, 180, 0),
        #     step_size=30.0
        # )
        self.enemy_point_generator = straight_line_generator(
            start_point=OrientedPoint(280, 180, 0),
            end_point=OrientedPoint(150, 100, 0),
            step_size=5.0
        )

    @Brain.task(process=False, run_on_start=True, refresh_rate=0.1)
    async def handle_rolling_basis_for_go_to(self) -> None:
        cmd: RollingBasisCommand = self.movement_manager.handle_go_to()
        if cmd is not None:
            self.rolling_basis.set_speed_and_position(*cmd.get_command())
            self.logger.log(
                f"RollingBasisCommand: {cmd.get_command()}",
                LogLevels.DEBUG
            )

    @Brain.task(process=False, run_on_start=True, refresh_rate=0.2)
    async def update_arena(self) -> None:
        self.arena.update(
            ally_position=self.rolling_basis.odometrie,
            enemy_position=next(self.enemy_point_generator),  # TODO: use the lidar to get the enemy position
            enemy_velocity=0.0,  # TODO: use the lidar to get the enemy velocity
            optimized_update=True
        )
        self.ax.clear()
        self.arena.visualize(
            display_default_destination_zone=False,
            trajectory=self.movement_manager.path_finder.oriented_path_found,
            plot=(self.ax, self.fig),
            show=False
        )
        plt.pause(0.01)

    @Brain.task(process=False, run_on_start=False)
    async def initialize(self):
        self.arena.set_team_color("yellow")
        self.rolling_basis.odometrie = OrientedPoint(
            24, 10, 0)  # Assume the robot is at position (24, 10) if begin the match in yellow zone

    @Brain.task(process=False, run_on_start=True)
    async def main(self):
        await self.initialize()

        speed_profile: SpeedProfile = SpeedProfile(
            max_linear_speed=15.0,
            max_angular_speed=6.0,
            max_linear_acceleration=1.0,
            max_angular_acceleration=1.0,
            max_linear_deceleration=0.5,
            max_angular_deceleration=1.0
        )
        go_to_params = GoToParams(
            initial_linear_speed=self.rolling_basis.linear_speed,
            initial_angular_speed=self.rolling_basis.angular_speed,
            speed_profile=speed_profile,
            goal=OrientedPoint(250, 140),
            acs_distance=10,
            path_finder_recompute_distance=20,
            timeout=-1.0,
            is_mandatory=False,
            smooth_trajectory=True,
            goal_tolerance=0.1,
        )

        self.movement_manager.go_to(params=go_to_params)


# Only for testing
def random_point_generator(
        start_point: OrientedPoint,
        step_size: float = 10.0,
        x_limits=(0, 300),
        y_limits=(0, 200)
):
    current_point = start_point

    while True:
        dx = random.uniform(-step_size, step_size)
        dy = random.uniform(-step_size, step_size)

        new_x = min(max(current_point.x + dx, x_limits[0]), x_limits[1])
        new_y = min(max(current_point.y + dy, y_limits[0]), y_limits[1])

        current_point = OrientedPoint(new_x, new_y, current_point.theta)

        yield current_point


def straight_line_generator(start_point: OrientedPoint, end_point: OrientedPoint, step_size: float):
    # Calculer la direction du mouvement
    dx = end_point.x - start_point.x
    dy = end_point.y - start_point.y
    d = math.sqrt(dx ** 2 + dy ** 2)

    # Si la distance est nulle, retourner directement le point d'arrivée
    if d == 0:
        while True:
            yield start_point

    # Normaliser le vecteur de direction
    direction_x = dx / d
    direction_y = dy / d

    # Générer les points sur la ligne droite
    current_point = start_point
    while d > step_size:
        # Calculer le prochain point
        new_x = current_point.x + direction_x * step_size
        new_y = current_point.y + direction_y * step_size

        # Créer un nouveau point avec la même orientation
        current_point = OrientedPoint(new_x, new_y, current_point.theta)

        # Réduire la distance restante
        d -= step_size

        yield current_point

    # Une fois arrivé au point final, continuer à renvoyer ce point
    while True:
        yield end_point
