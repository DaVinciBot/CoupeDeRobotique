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
from movement import (
    MovementManager,
    GoToParams,
    TrajectoryParams,
    SpeedProfile,
    RollingBasisCommand,
    TrajectoryComputer,
)
from arena import AllyZone, TeamColor

# ====== Internal Project Imports ======
from controllers.rolling_basis import RollingBasis, RollingBasisDummy
from sensors import Lidar
from tasks import TaskPlanner, Task


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
        game_tasks=list[Task],
        game_duration_sec: int = 90,
        solve_planner_limit_sec=1,
        final_goal=OrientedPoint(170, 270),  # TODO: define real destination
    ) -> None:
        # Sensor
        self.lidar: Lidar = lidar
        # Environment
        self.arena: ShowArena = arena
        # WS routes
        self.ws_cmd: WServerRouteManager = ws_cmd

        # Shared processes attributes
        self.rolling_basis_odometrie = OrientedPoint(0, 0, 0)

        self.go_to_params: GoToParams | None = None

        # For test purpose
        self.th_ally_zone: AllyZone = AllyZone(
            logger=Logger(identifier="th_ally", follow_logger_manager_rules=True),
            point=self.rolling_basis_odometrie,
            robot_size=5,
        )
        self.th_ally_zone.zone_color = "#82795f"

        self.path: list[OrientedPoint] = []

        super().__init__(logger, self)

        # Attributes for the visualization
        self.fig, self.ax = plt.subplots()

        self.game_tasks = game_tasks
        if self.game_duration_sec <= 0:
            raise ValueError("game_duration_sec must be greater than 0")
        self.game_duration_sec = game_duration_sec
        if solve_planner_limit_sec <= 0:
            raise ValueError("solve_planner_limit_sec must be greater than 0")
        self.solve_planner_limit_sec = solve_planner_limit_sec
        self.final_goal = final_goal

        self.path_finder_logger_simulation = Logger(
            identifier="PathFinder",
            follow_logger_manager_rules=True,
        )

        self.movemement_manager_logger_simulation = Logger(
            identifier="MovementManager",
            follow_logger_manager_rules=True,
        )

    """
    ### Secondary Processes ###
    """

    """ ### Routines ### """

    @Brain.task(
        process=True,
        run_on_start=True,
        refresh_rate=0.1,
        define_loop_later=True,
        start_loop_marker="# --- MetaProg is insane (loop) --- #",
    )
    def handle_movement_manager(self) -> None:
        # --- Initialization --- #
        movement_manager = MovementManager(
            logger=Logger(
                identifier="MovementManager", follow_logger_manager_rules=True
            ),
            path_finder_logger=Logger(
                identifier="PathFinder", follow_logger_manager_rules=True
            ),
            trajectory_computer_logger=Logger(
                identifier="TrajectoryComputer", follow_logger_manager_rules=True
            ),
            arena_ptr=self.arena,
        )
        rolling_basis = RollingBasisDummy(
            logger=Logger(identifier="RollingBasis", follow_logger_manager_rules=True)
        )

        if isinstance(rolling_basis, RollingBasisDummy):
            rolling_basis.logger.warning("RollingBasisDummy is used")

        # --- MetaProg is insane (loop) --- #

        # Update rolling basis odometrie if main process has updated it
        if self.rolling_basis_odometrie != rolling_basis.odometrie:
            rolling_basis.set_odometrie(self.rolling_basis_odometrie)

        # Force the sync of arena inside the movement_manager
        movement_manager.arena_ptr = self.arena

        # Trigger movement manager to go to the new destination when the params change
        if self.go_to_params != movement_manager.params:
            print(self.go_to_params)
            print(movement_manager.params)
            movement_manager.compute_go_to(
                current_linear_speed=rolling_basis.linear_speed,
                current_angular_speed=rolling_basis.angular_speed,
                params=self.go_to_params,
            )
            movement_manager.logger.info("New GoToParams received")

        # Handle the 'go to' command
        if movement_manager.params is not None:
            cmd: RollingBasisCommand = movement_manager.handle_go_to()
            if cmd is not None:
                self.th_ally_zone = AllyZone(
                    logger=Logger(
                        identifier="th_ally", follow_logger_manager_rules=True
                    ),
                    point=cmd.position,
                    robot_size=5,
                )
                rolling_basis.set_speed_and_position(*cmd.get_command())
                self.rolling_basis_odometrie = rolling_basis.odometrie
                self.path = movement_manager.trajectory_computer.path_to_follow

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
        )

        # obstacles = self.arena.remove_outside(
        #     self.arena._pol_to_abs_cart(self.lidar.scan_to_polars())
        # )

        # Visualize the arena
        self.ax.clear()
        self.arena.visualize(
            # Visualization options
            show_buffer=True,
            trajectory=self.path,
            display_zones_go_to_positions=True,
            show_ally_direction=True,
            # Plot options
            show=False,
            plot=(self.ax, self.fig),
            # Additional options
            additional_zones=[self.th_ally_zone],
            # additional_points=list(obstacles.geoms) if not is_empty(obstacles) else None,
        )
        plt.pause(0.01)

    @Brain.task(process=False, run_on_start=True, refresh_rate=0.5)
    async def zombie_mode(self):
        """
        executes requests received by the server. Use Postman to send request to the server
        Use eval and await eval to run the code you want. Code must be sent as a string
        """
        # Check cmd
        cmd = await self.ws_cmd.receiver.get(wait_msg=True)

        if cmd != WSmsg():
            self.logger.info(f"Zombie instruction {cmd.msg} received: {cmd.data}")

            instructions = []
            if isinstance(cmd.data, str):
                instructions.append(cmd.data)
            elif isinstance(cmd.data, list):
                instructions = cmd.data

            # Exec: for attribution cases (x = 1)
            if cmd.msg == "exec":
                for instruction in instructions:
                    exec(instruction)

            # Eval: for return cases (print(x))
            elif cmd.msg == "eval":
                instructions = []
                execution = "No instructions"
                if isinstance(cmd.data, str):
                    instructions.append(cmd.data)
                elif isinstance(cmd.data, list):
                    instructions = cmd.data
                for instruction in instructions:
                    if instruction.startswith("await "):
                        execution = await eval(instruction.removeprefix("await "))
                    else:
                        execution = eval(instruction)
                message = WSmsg.from_json(
                    {
                        "sender": CONFIG.WS_SENDER_NAME,
                        "msg": "Execution of sender instruction",
                        "data": str(execution),
                    }
                )
                await self.ws_cmd.sender.send(message)

            else:
                self.logger.warning(
                    f"Command not implemented: {cmd.msg} / {cmd.data}",
                )

    """ ### One-Shot Tasks ### """

    @Brain.task(process=False, run_on_start=True)
    async def start(self):
        self.arena.set_team_color(TeamColor.YELLOW)
        # Start robot position
        self.rolling_basis_odometrie = OrientedPoint(20, 25, 0)
        self.arena.enemy_zone.update(
            self.arena.team_color, self.rolling_basis_odometrie, Point(290, 190)
        )

    def load_preplanned_tasks(self, file_path: str = "solution.json"):
        with open(file_path, "r") as f:
            solution = json.load(f)
        self.game_tasks_planification = solution

    # read demo.ipynb for further details
    def get_game_tasks_planification(  # TODO: move to an acs logic outside of the brain and  refactor
        self, solve_planner_limit_sec: int = -1, save_planification: bool = False
    ):
        scores = [task.score for task in self.game_tasks]
        tasks_duration_sec = [task.execution_time for task in self.game_tasks]

        travels_duration_matrix_sec = [
            [0 for _ in range(len(scores) + 2)] for _ in range(len(scores) + 2)
        ]

        # Going from start to destination shouldn't be the chosen path as it doesn't bring any points, so we set the duration to infinity for quicker computations
        travels_duration_matrix_sec[0][-1] = float("inf")
        travels_duration_matrix_sec[-1][0] = travels_duration_matrix_sec[0][-1]

        # handle separatly travel to origin and to destination as they are not tasks
        for i in range(1, len(scores)):
            _ = TrajectoryComputer(
                logger=self.movemement_manager_logger_simulation,
                path_finder_logger=self.path_finder_logger_simulation,
                arena_ptr=self.arena,
                trajectory_params=self.game_tasks[i].go_to_params.trajectory_params,
            )
            _.compute(
                use_dynamic_grid=False,
            )
            travels_duration_matrix_sec[0][i] = _.total_duration
            travels_duration_matrix_sec[i][0] = travels_duration_matrix_sec[0][i]
            _ = TrajectoryComputer(
                logger=self.movemement_manager_logger_simulation,
                path_finder_logger=self.path_finder_logger_simulation,
                arena_ptr=self.arena,
                trajectory_params=self.game_tasks[i].go_to_params.trajectory_params,
            )
            _.compute(
                use_dynamic_grid=False,
            )
            travels_duration_matrix_sec[-1][i] = _.total_duration
            travels_duration_matrix_sec[i][-1] = travels_duration_matrix_sec[-1][i]

        for i in range(1, len(scores)):
            for j in range(1, i, len(scores) + 1):
                _ = TrajectoryComputer(  # duration from Task[i] to Task[j]
                    logger=self.movemement_manager_logger_simulation,
                    path_finder_logger=self.path_finder_logger_simulation,
                    arena_ptr=self.arena,
                    trajectory_params=self.game_tasks[j].go_to_params.trajectory_params,
                )
                _.compute(
                    current_position=self.game_tasks[i],
                    use_dynamic_grid=False,
                )
                travels_duration_matrix_sec[i][j] = _.total_duration
                travels_duration_matrix_sec[j][i] = travels_duration_matrix_sec[i][j]

        self.task_planner = TaskPlanner(
            tasks_scores=scores,
            tasks_duration_sec=tasks_duration_sec,
            travels_duration_matrix_sec=travels_duration_matrix_sec,
            max_time_sec=self.game_duration_sec,
            solve_limit_sec=(
                self.solve_planner_limit_sec
                if solve_planner_limit_sec <= 0
                else solve_planner_limit_sec
            ),
        )
        self.game_tasks_planification = self.task_planner.solve(
            save_mode=save_planification
        )
        self.logger.fatal(f"Game tasks planification: {self.game_tasks_planification}")

    def load_preplanned_tasks(self, file_path: str = "solution.json"):
        with open(file_path, "r") as f:
            solution = json.load(f)
        self.game_tasks_planification = solution

    def visualize_tasks_in_arena(self, draw_remaining_edges=False):
        def _annotate_task_point(ax, task, pos: Point):
            ax.annotate(
                f"{task.name}\nS: {task.score}\nT: {task.execution_time}s",
                (pos.x, pos.y),
                xytext=(10, 10),
                textcoords="offset points",
            )

        def _display_task_point(ax, task, pos: Point, annotate=False):
            ax.plot(pos.x, pos.y, marker="o", markersize=5, color="red")
            if annotate:
                _annotate_task_point(ax, task, pos)

        ax, self.fig = self.arena.visualize(show=False)

        # Draw tasks as before
        for task in self.game_tasks:
            if isinstance(task.go_to_params.trajectory_params.goal, Point):
                _display_task_point(
                    ax, task, task.go_to_params.trajectory_params.goal, annotate=True
                )
            elif isinstance(task.go_to_params.trajectory_params.goal, BaseArenaZone):
                if task.go_to_params.trajectory_params.goal.go_to_positions:
                    i = 0
                    _annotate_task_point(
                        ax,
                        task,
                        task.go_to_params.trajectory_params.goal.go_to_positions[i],
                    )
                    while i < len(
                        task.go_to_params.trajectory_params.goal.go_to_positions
                    ):
                        _display_task_point(
                            ax,
                            task,
                            task.go_to_params.trajectory_params.goal.go_to_positions[i],
                        )
                        i += 1
                else:
                    try:
                        _display_task_point(
                            ax,
                            task,
                            task.go_to_params.trajectory_params.goal.polygon.centroid,
                            annotate=True,
                        )
                    except:
                        self.logger.warning(
                            f"Task {task.id} has no go_to_positions or centroid"
                        )

        # Draw solution edges if game_tasks_planification exists
        if hasattr(self, "game_tasks_planification"):
            ordered_tasks = self.game_tasks_planification.ordered_tasks
            solution_edges = set()

            def get_node_position(index):
                if index == 0:
                    return Point(20, 25)  # Start position
                elif index == len(self.game_tasks) + 1:
                    return self.final_goal  # Destination
                else:
                    task = self.game_tasks[index - 1]
                    goal = task.go_to_params.trajectory_params.goal
                    if isinstance(goal, (Point, OrientedPoint)):
                        return Point(goal.x, goal.y)
                    elif isinstance(goal, BaseArenaZone):
                        if goal.go_to_positions:
                            return goal.go_to_positions[0]
                        else:
                            return goal.polygon.centroid
                    else:
                        return Point(0, 0)

            # Draw solution edges
            for i in range(len(ordered_tasks) - 1):
                u = ordered_tasks[i]
                v = ordered_tasks[i + 1]
                solution_edges.add((u, v))

                pos_u = get_node_position(u)
                pos_v = get_node_position(v)

                # Draw green arrow for solution edge
                ax.annotate(
                    "",
                    xy=(pos_v.x, pos_v.y),
                    xytext=(pos_u.x, pos_u.y),
                    arrowprops=dict(arrowstyle="->", color="green", lw=2),
                )

                # Add duration text if available
                if (
                    hasattr(self, "task_planner")
                    and u < len(self.task_planner.travels_duration_matrix_sec)
                    and v < len(self.task_planner.travels_duration_matrix_sec[u])
                ):
                    duration = self.task_planner.travels_duration_matrix_sec[u][v]
                    mid_x = (pos_u.x + pos_v.x) / 2
                    mid_y = (pos_u.y + pos_v.y) / 2
                    ax.text(
                        mid_x,
                        mid_y,
                        f"{duration:.1f}s",
                        color="green",
                        fontsize=8,
                        ha="center",
                        va="center",
                    )

            # Draw remaining edges if enabled and task_planner exists
            if draw_remaining_edges and hasattr(self, "task_planner"):
                matrix = self.task_planner.travels_duration_matrix_sec
                n = len(matrix)
                for i in range(n):
                    for j in range(n):
                        if i == j:
                            continue
                        if (i, j) in solution_edges:
                            continue
                        duration = matrix[i][j]
                        if duration == float("inf"):
                            continue
                        pos_i = get_node_position(i)
                        pos_j = get_node_position(j)
                        # Draw grey dashed arrow with curvature to avoid overlap
                        ax.annotate(
                            "",
                            xy=(pos_j.x, pos_j.y),
                            xytext=(pos_i.x, pos_i.y),
                            arrowprops=dict(
                                arrowstyle="->",
                                color="grey",
                                lw=1,
                                linestyle="dashed",
                                alpha=0.5,
                                connectionstyle="arc3,rad=0.1",
                            ),
                        )

        plt.show()


"""
This main brain is dedicated to test the robot movement WITHOUT Lidar.

Use ZOMBIE_MODE to send instructions to the robot.
Instruction example:
---
self.go_to_params = GoToParams(
    trajectory_params=TrajectoryParams(
        speed_profile=SpeedProfile.from_dict(
            CONFIG.ROLLING_BASIS_HIGH_SPEED_PROFILE
        ),
        goal=OrientedPoint(250, 140),
        resolution=1,
        smooth_trajectory=True,
    ),
    acs_distance=30,
    path_finder_recompute_distance=80,
    timeout=-1.0,
    is_mandatory=False,
    goal_tolerance=0.1,
    distance_to_goal_to_dont_recompute_path=10,
)
---

Exemple in postman with zombie mode:
url: ws://rob.local:8080/cmd?sender=postman_zombie
message:
{
    "sender": "zombie_master",
    "msg": "exec",
    "data": "self.go_to_params = GoToParams(trajectory_params=TrajectoryParams(speed_profile=SpeedProfile.from_dict(CONFIG.ROLLING_BASIS_HIGH_SPEED_PROFILE), goal=OrientedPoint(250, 140), resolution=1, smooth_trajectory=True), acs_distance=30, path_finder_recompute_distance=80, timeout=-1.0, is_mandatory=False, goal_tolerance=0.1, distance_to_goal_to_dont_recompute_path=10)"
}
"""
