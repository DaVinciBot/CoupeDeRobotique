from config_loader import CONFIG

# External imports
import asyncio
import time

# Import from common
from taskbrain import Brain
from ws_comms import WSmsg, WSreceiver, WServerRouteManager, WSender
from geometry import OrientedPoint, Point, distance, Polygon, MultiPoint

from loggerplusplus import Logger
import math
from utils import Utils
import matplotlib.pyplot as plt
import time
import numpy as np
import random
import gc

# Import from local path
from controllers import RollingBasis, RollingBasisDummy

from path_finding import PathFinder
from arena import ShowArena
from rolling_basis_handler import RollingBasisHandler, RollingBasisCommand
from movement_manager import MovementManager, GoToParams
from rolling_basis_handler import SpeedProfile
from sensors import Lidar, LidarDummy
from arena import AllyZone
from tasks import Task, TaskPlanner
import json


class MainBrain(Brain):
    def __init__(
        self,
        logger: Logger,
        # Controllers
        rolling_basis: RollingBasis | RollingBasisDummy,
        # Sensors
        lidar: Lidar | LidarDummy,
        # Environment
        arena: ShowArena,
        # Movement
        movement_manager: MovementManager,
        # WS routes
        ws_cmd: WServerRouteManager,
        game_duration_sec: int = 90,
        solve_planner_limit_sec: int = 1,
        tasks: list[Task] = [],
    ) -> None:
        if isinstance(rolling_basis, RollingBasisDummy):
            logger.warning("RollingBasisDummy is used")

        # Controllers
        self.rolling_basis: RollingBasis = rolling_basis
        # Sensors
        self.lidar: Lidar = lidar
        # Environment
        self.arena: ShowArena = arena
        # Movement
        self.movement_manager: MovementManager = movement_manager
        # WS routes
        self.ws_cmd: WServerRouteManager = ws_cmd

        self.game_duration_sec = game_duration_sec
        self.solve_planner_limit_sec = solve_planner_limit_sec
        self.game_tasks = tasks
        self.game_tasks_planification = None

        super().__init__(logger, self)

        # Attributes for the visualization
        self.fig, self.ax = plt.subplots()

        # For testing
        # self.enemy_point_generator = random_point_generator(
        #     start_point=OrientedPoint(280, 180, 0),
        #     step_size=30.0
        # )
        self.enemy_point_generator = straight_line_generator(
            start_point=OrientedPoint(280, 93, 0),
            end_point=OrientedPoint(23, 135, 0),
            step_size=3.0,
        )

        self.theorical_ally_position = AllyZone(
            logger=Logger(identifier="th_ally"),
            point=self.rolling_basis.odometrie,
            robot_size=5,
        )
        self.theorical_ally_position.zone_color = "#fcba03"

        # TMP for test purpose
        self.lidar_scan_polars = self.lidar.scan_to_polars()

    """ ### Routines ### """

    @Brain.task(process=False, run_on_start=True, refresh_rate=0.1)
    async def handle_rolling_basis_for_go_to(self) -> None:
        cmd: RollingBasisCommand = self.movement_manager.handle_go_to()
        if cmd is not None:
            self.theorical_ally_position.point = cmd.position
            self.rolling_basis.set_speed_and_position(*cmd.get_command())
            self.logger.debug(f"RollingBasisCommand: {cmd.get_command()}")

    @Brain.task(process=False, run_on_start=True, refresh_rate=0.2)
    async def update_arena(self) -> None:
        self.lidar_scan_polars = self.lidar.scan_to_polars()
        self.arena.update(
            ally_position=self.rolling_basis.odometrie,
            lidar_scan_polars=self.lidar_scan_polars,
            enemy_position=next(self.enemy_point_generator),
            optimized_update=True,
        )

        self.ax.clear()
        self.arena.visualize(
            display_default_destination_zone=False,
            theorical_ally_position=self.theorical_ally_position,
            trajectory=(
                self.movement_manager.path_finder.oriented_path_found
                if self.movement_manager.path_finder is not None
                else []
            ),
            # Display lidar scan point
            # display_points=[
            #     point for point in self.arena._pol_to_abs_cart(self.lidar_scan_polars).geoms
            # ],
            plot=(self.ax, self.fig),
            show=False,
        )
        plt.pause(0.01)

    @Brain.task(process=False, run_on_start=CONFIG.ZOMBIE_MODE, refresh_rate=0.5)
    async def zombie_mode(self):
        """
        executes requests received by the server. Use Postman to send request to the server
        Use eval and await eval to run the code you want. Code must be sent as a string
        """
        # Check cmd
        cmd = await self.ws_cmd.receiver.get()

        if cmd != WSmsg():
            self.logger.info(f"Zombie instruction {cmd.msg} received: {cmd.data}")

            if cmd.msg == "eval":
                instructions = []
                if isinstance(cmd.data, str):
                    instructions.append(cmd.data)
                elif isinstance(cmd.data, list):
                    instructions = cmd.data

                for instruction in instructions:
                    if instruction.startswith("await "):
                        await eval(instruction.removeprefix("await "))
                    else:
                        eval(instruction)

            else:
                self.logger.warning(
                    f"Command not implemented: {cmd.msg} / {cmd.data}",
                )

    """ ### One-Shot Tasks ### """

    @Brain.task(process=False, run_on_start=False)
    async def initialize(self):
        self.arena.set_team_color("yellow")
        self.rolling_basis.odometrie = OrientedPoint(
            24, 10, 0
        )  # Assume the robot is at position (24, 10) if begin the match in yellow zone

    @Brain.task(process=False, run_on_start=True)
    async def main(self):
        await self.initialize()

        speed_profile: SpeedProfile = SpeedProfile(
            max_linear_speed=20.0,  # cm/s
            max_angular_speed=6.0,  # rad/s
            max_linear_acceleration=3.0,  # cm/s^2
            max_angular_acceleration=1.0,  # rad/s^2
            max_linear_deceleration=0.5,  # cm/s^2
            max_angular_deceleration=1.0,  # rad/s^2
        )
        go_to_params = GoToParams(
            initial_linear_speed=self.rolling_basis.linear_speed,
            initial_angular_speed=self.rolling_basis.angular_speed,
            speed_profile=speed_profile,
            goal=OrientedPoint(250, 140),
            acs_distance=10,
            path_finder_recompute_distance=80,
            timeout=-1.0,
            is_mandatory=False,
            smooth_trajectory=True,
            goal_tolerance=0.1,
        )

        self.movement_manager.go_to(params=go_to_params)

    def get_game_tasks_planification(
        self, solve_planner_limit_sec: int = -1, save_planification: bool = False
    ):
        scores = [task.score for task in self.game_tasks]
        tasks_duration_sec = [task.execution_time for task in self.game_tasks]
        # TODO: get the travel time matrix with time computed according to arena and robot speed (avg speed or profile)
        travels_duration_matrix_sec = [
            [0 if i == j else random.randint(1, 10) for j in range(len(scores) + 2)]
            for i in range(len(scores) + 2)
        ]
        self.task_planner = TaskPlanner(
            tasks_scores=scores,
            tasks_duration_sec=tasks_duration_sec,
            travels_duration_matrix_sec=travels_duration_matrix_sec,
            max_time_sec=self.game_duration_sec,
            solve_limit_sec=(
                self.solve_planner_limit_sec
                if solve_planner_limit_sec < 0
                else solve_planner_limit_sec
            ),
        )
        self.game_tasks_planification = self.task_planner.solve(
            save_mode=save_planification
        )

    def load_preplanned_tasks(self, file_path: str = "solution.json"):
        with open(file_path, "r") as f:
            solution = json.load(f)
        self.game_tasks_planification = solution

    @staticmethod
    def get_dummy_brain(
        game_duration_sec: int = 90,
        solve_planner_limit_sec: int = 1,
        tasks: list[Task] = [],
    ) -> "MainBrain":

        arena = ShowArena(
            logger=Logger(identifier="Dummy Arena"),
            border_buffer=2,
            obstacle_buffer=1,
            chunk_size=5,
            forbidden_cover_threshold=0.1,
            grid_manager_logger=Logger(identifier="Dummy Grid Manager"),
        )
        return MainBrain(
            logger=Logger(identifier="Dummy Brain"),
            rolling_basis=RollingBasisDummy(Logger(identifier="Dummy Rolling Basis")),
            lidar=LidarDummy(
                logger=Logger(identifier="Dummy Lidar"),
                min_angle=CONFIG.LIDAR_MIN_ANGLE,
                max_angle=CONFIG.LIDAR_MAX_ANGLE,
                unit_angle=CONFIG.LIDAR_ANGLES_UNIT,
                unit_distance=CONFIG.LIDAR_DISTANCES_UNIT,
                min_distance=CONFIG.LIDAR_MIN_DISTANCE_DETECTION,
            ),
            arena=arena,
            movement_manager=MovementManager(
                logger=Logger(identifier="Dummy Movement Manager"),
                rolling_basis_handler_logger=Logger(
                    identifier="Dummy Rolling Basis Handler"
                ),
                path_finder_logger=Logger(identifier="Dummy Path Finder"),
                movement_resolution=1,
                arena=arena,
            ),
            ws_cmd=WServerRouteManager(
                WSreceiver(use_queue=True), WSender(CONFIG.WS_SENDER_NAME)
            ),
            game_duration_sec=game_duration_sec,
            solve_planner_limit_sec=solve_planner_limit_sec,
            tasks=tasks,
        )


# Only for testing
def random_point_generator(
    start_point: OrientedPoint,
    step_size: float = 10.0,
    x_limits=(0, 300),
    y_limits=(0, 200),
):
    current_point = start_point

    while True:
        dx = random.uniform(-step_size, step_size)
        dy = random.uniform(-step_size, step_size)

        new_x = min(max(current_point.x + dx, x_limits[0]), x_limits[1])
        new_y = min(max(current_point.y + dy, y_limits[0]), y_limits[1])

        current_point = OrientedPoint(new_x, new_y, current_point.theta)

        yield current_point


def straight_line_generator(
    start_point: OrientedPoint, end_point: OrientedPoint, step_size: float
):
    # Calculer la direction du mouvement
    dx = end_point.x - start_point.x
    dy = end_point.y - start_point.y
    d = math.sqrt(dx**2 + dy**2)

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
