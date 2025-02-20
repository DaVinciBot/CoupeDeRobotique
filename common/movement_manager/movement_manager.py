# ====== Imports ======
# Internal project imports
from arena import BaseArena, BaseArenaZone
from loggerplusplus import Logger, LogLevels
from geometry import OrientedPoint, Polygon, Point


from path_finding import PathFinder
from rolling_basis_handler import RollingBasisHandler

from movement_manager.movement_params import GoToParams
from movement_manager.movement_status import MovementStatus

from rolling_basis_handler import RollingBasisCommand


# ====== Class Part ======
class MovementManager:
    """
    Manages the movement of a robot, including pathfinding, collision avoidance, and trajectory handling.

    Attributes:
        logger (Logger): Logger for movement manager events.
        rolling_basis_handler_logger (Logger): Logger for rolling basis handler events.
        path_finder_logger (Logger): Logger for pathfinding events.
        movement_resolution (float): Resolution for pathfinding and movement.
        arena (BaseArena): The arena where the robot operates.
    """

    def __init__(
        self,
        # Loggers
        logger: Logger,
        rolling_basis_handler_logger: Logger,
        path_finder_logger: Logger,
        # Constants
        movement_resolution: float,
        # Context variables
        arena: BaseArena,
    ) -> None:
        """
        Initializes the MovementManager with loggers, parameters, and context variables.

        Args:
            logger (Logger): Main logger.
            rolling_basis_handler_logger (Logger): Logger for rolling basis handler.
            path_finder_logger (Logger): Logger for pathfinding.
            movement_resolution (float): Movement resolution for pathfinding.
            arena (BaseArena): Arena in which the robot operates.
        """
        # Loggers
        self.logger: Logger = logger
        self.rolling_basis_handler_logger: Logger = rolling_basis_handler_logger
        self.path_finder_logger: Logger = path_finder_logger

        # Constants
        self.movement_resolution: float = movement_resolution

        # Context variables
        self.arena: BaseArena = arena

        # Movement variables
        self.status: MovementStatus = MovementStatus.NOT_STARTED
        self.params: GoToParams | None = None
        self.path_finder: PathFinder | None = None
        self.rolling_basis_handler: RollingBasisHandler | None = None

    def __get_ally_enemy_distance(self) -> float:
        return self.arena.ally_zone.point.distance(self.arena.enemy_zone.point)

    @staticmethod
    def __are_path_different(
        path_a: list[OrientedPoint], path_b: list[OrientedPoint]
    ) -> bool:
        min_length = min(len(path_a), len(path_b))

        for i in range(1, min_length + 1):
            if path_a[-i] != path_b[-i]:
                return True
        return True

    @staticmethod
    def find_path_static(
        movement_manager: "MovementManager",
        arena: BaseArena,
        path_finder_logger: Logger,
        start,
        goal,
        path_resolution,
        smooth_trajectory: bool,
        consider_dynamic_obstacles: bool | None = None,
        update_position: bool = True,
    ) -> PathFinder:
        # Compute path with dynamic grid (included enemy position) only if the enemy is close to aly position
        # Compute distance between ally and enemy

        goal = MovementManager.get_go_to_destination_point(arena, goal)

        if not goal:
            movement_manager.logger.error("Goal is None, returned None")
            return None

        distance = movement_manager.__get_ally_enemy_distance()

        if movement_manager.params is None:
            movement_manager.logger.warning(
                "Find Path was called but no movement parameters found!"
            )
            return

        path_finder = PathFinder(
            logger=path_finder_logger,
            start=arena.ally_zone.point,
            goal=goal,
            grid_manager=arena.grid_manager,
            path_resolution=movement_manager.movement_resolution,
        )

        # Take in consideration the dynamic grid only if the enemy is close to the ally
        if consider_dynamic_obstacles is None:
            use_static_and_dynamic_grid = (
                distance < movement_manager.params.path_finder_recompute_distance
            )
        else:
            use_static_and_dynamic_grid = consider_dynamic_obstacles

        if use_static_and_dynamic_grid:
            movement_manager.logger.info(
                "Using static and dynamic grid for path finding"
            )
        else:
            movement_manager.logger.info("Using only static grid for path finding")

        if update_position:
            movement_manager.path_finder.update_current_position(
                movement_manager.arena.ally_zone.point
            )

        path_finder.find_oriented_path(
            smooth_path=smooth_trajectory,
            use_static_and_dynamic_grid=use_static_and_dynamic_grid,
        )

        return path_finder

    def _acs(self) -> RollingBasisCommand | None:
        if self.params is None:
            self.logger.warning("ACS was called but no movement parameters found!")
            return

        # Anti Collision System
        to_close = self.__get_ally_enemy_distance() < self.params.acs_distance

        if to_close:
            # Stop the robot
            self.status = MovementStatus.ACS
            self.logger.warning("ACS: Enemy is too close, stopping the robot")
            return RollingBasisCommand(
                position=self.arena.ally_zone.point, linear_speed=0.0, angular_speed=0.0
            )
        return

    def go_to_is_arrived(self) -> bool:
        if (
            self.arena.ally_zone.point.distance(self.params.goal)
            < self.params.goal_tolerance
        ):
            self.status = MovementStatus.SUCCESS
            self.logger.info("Go To is arrived")
            return True
        return False

    @staticmethod
    def get_go_to_destination_point(
        arena: BaseArena, goal: Point | OrientedPoint | BaseArenaZone | Polygon
    ) -> OrientedPoint:
        def compute_go_to_destination_from_polygon(pol: Polygon) -> OrientedPoint:
            if not pol.centroid:
                arena.logger.log(
                    f"The destination polygon {pol} has no centroid, couldn't establish a destination point.",
                    LogLevels.WARNING,
                )
                return None
            destination_point = pol.centroid
            new_x = destination_point.x
            new_y = destination_point.y

            if destination_point.x < arena.border_buffer + arena.obstacle_buffer:
                new_x = arena.border_buffer + arena.obstacle_buffer
            if (arena.width - destination_point.x) < (
                arena.border_buffer + arena.obstacle_buffer
            ):
                new_x = arena.width - (arena.border_buffer + arena.obstacle_buffer)
            if destination_point.y < arena.border_buffer + arena.obstacle_buffer:
                new_y = arena.border_buffer + arena.obstacle_buffer
            if (arena.height - destination_point.y) < (
                arena.border_buffer + arena.obstacle_buffer
            ):
                new_y = arena.height - (arena.border_buffer + arena.obstacle_buffer)

            return OrientedPoint(new_x, new_y)

        destination = None

        if isinstance(goal, OrientedPoint):
            destination = goal
        elif isinstance(goal, Point):
            destination = OrientedPoint.from_Point(goal)
        elif isinstance(goal, BaseArenaZone):
            if goal.go_to_positions is not None:
                destination = goal.get_go_to_position(
                    arena.ally_zone.point, arena.team_color
                )
            else:
                destination = compute_go_to_destination_from_polygon(goal.polygon)
        elif isinstance(goal, Polygon):
            destination = compute_go_to_destination_from_polygon(goal)
        return destination

    def get_path_from_start_to_goal(
        self, start: OrientedPoint, goal: OrientedPoint
    ) -> list[OrientedPoint]:
        """
        Get the path from the start to the goal using the path finder.
        """

    def go_to(self, params: GoToParams) -> MovementStatus:
        # Warn if a movement is already in progress
        if not self.status.is_finished():
            self.logger.warning(
                "A movement is already in progress and a new one is requested.",
            )

        self.params: GoToParams = params
        self.status: MovementStatus = MovementStatus.PENDING

        goal = self.get_go_to_destination_point(self.arena, params.goal)

        if goal is None:
            self.logger.error("Goal is None")
            self.status = MovementStatus.NO_ACCESSIBLE
            self.params = None
            return self.status

        self.path_finder = PathFinder(
            logger=self.path_finder_logger,
            start=self.arena.ally_zone.point,
            goal=goal,
            grid_manager=self.arena.grid_manager,
            path_resolution=self.movement_resolution,
        )
        # Run pathfinder
        self.path_finder = self.find_path_static(
            logger=self.path_finder_logger,
            start=self.arena.ally_zone.point,
            goal=goal,
            grid_manager=self.arena.grid_manager,
            path_resolution=self.movement_resolution,
            smooth_trajectory=params.smooth_trajectory,
            update_position=False,
        )

        # 2. If the path is found, initialize the rolling basis handler
        if not self.path_finder or self.path_finder.oriented_path_found:
            self.status = MovementStatus.NO_ACCESSIBLE
            self.params = None
            return self.status

        self.rolling_basis_handler = RollingBasisHandler(
            logger=self.rolling_basis_handler_logger,
            initial_linear_speed=params.initial_linear_speed,
            initial_angular_speed=params.initial_angular_speed,
            profile=params.speed_profile,
            trajectory=self.path_finder.oriented_path_found,
        )

    def handle_go_to(self) -> RollingBasisCommand | None:
        """
        Return order to send to rolling basis handler
        """
        if self.params is None:
            self.logger.warning(
                "Handle Go To was called but no movement parameters found!"
            )
            return

        # Check enemy distance
        acs = self._acs()
        if acs:
            return acs

        # Re-Compute path if enemy is close
        if (
            self.__get_ally_enemy_distance()
            < self.params.path_finder_recompute_distance
        ):
            self.find_path_static(
                smooth_trajectory=self.params.smooth_trajectory,
                consider_dynamic_obstacles=True,
                update_position=True,
            )

            # Check if the path has changed if so update the rolling basis handler
            if self.__are_path_different(
                self.rolling_basis_handler.trajectory,
                self.path_finder.oriented_path_found,
            ):
                self.logger.info(
                    "The path has changed, updating the rolling basis handler"
                )
                # To get the current speed of the rolling basis and update the new path with a smooth transition
                # We use rolling basis handler to get it
                # (it is not the best way to do this, it could be better to get the last sent command instead)
                position_speed: RollingBasisCommand = (
                    self.rolling_basis_handler.get_position_speed()
                )

                self.rolling_basis_handler = RollingBasisHandler(
                    logger=self.rolling_basis_handler_logger,
                    initial_linear_speed=position_speed.linear_speed,
                    # TODO: je pense pas que le handler prenne en compte la initiale angular speed correctement
                    initial_angular_speed=position_speed.angular_speed,
                    profile=self.params.speed_profile,
                    # We remove the first point because it is the current position
                    trajectory=self.path_finder.oriented_path_found[1:],
                )

                self.logger.warning(
                    f"first point: {self.rolling_basis_handler.trajectory[0]} | {self.path_finder.oriented_path_found[0]}"
                )

        # Update status
        self.go_to_is_arrived()

        # Get command to send to the rolling basis from the rolling basis handler
        return self.rolling_basis_handler.get_position_speed()
