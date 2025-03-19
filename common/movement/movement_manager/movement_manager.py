# ====== Code Summary ======
# The MovementManager class manages robot movement within an arena.
# It computes and executes movement paths while considering obstacles and enemy positions.
# The class utilizes a trajectory computer and logs movement actions.
import math
import time

# ====== Imports ======
# Internal project imports
from arena import BaseArena, BaseArenaZone
from loggerplusplus import Logger
from geometry import OrientedPoint

from movement.params import GoToParams, TrajectoryParams, SpeedProfile, RollingBasisCommand
from movement.movement_manager.movement_status import MovementStatus
from movement.trajectory_computer import TrajectoryComputer


# ====== Class Part ======
class MovementManager:
    """
    Manages robot movement within an arena, including trajectory computation,
    movement execution, and obstacle handling.
    """

    def __init__(
            self,
            # Loggers
            logger: Logger,
            path_finder_logger: Logger,
            trajectory_computer_logger: Logger,
            # Context object
            arena_ptr: BaseArena,
    ) -> None:
        """
        Initializes the MovementManager with logging and arena context.

        Args:
            logger (Logger): Logger for general movement logs.
            path_finder_logger (Logger): Logger for path finding.
            trajectory_computer_logger (Logger): Logger for trajectory computation.
            arena_ptr (BaseArena): Reference to the arena instance.
        """

        # Loggers
        self.logger: Logger = logger
        self.path_finder_logger: Logger = path_finder_logger
        self.trajectory_computer_logger: Logger = trajectory_computer_logger

        # Context variables
        self.arena_ptr: BaseArena = arena_ptr

        # Movement status
        self.status: MovementStatus = MovementStatus.NOT_STARTED

        # Attributes (use later)
        self.params: GoToParams | None = None
        self.trajectory_computer: TrajectoryComputer | None = None

        # Reverse
        self.reverse_threshold_angle: float = 5  # en degré
        self.reverse_threshold_distance: float = 10

        # Timeout
        self.movement_start_time: float = -1
        self.timeout_limit: float = 15

    # ====== Private Methods ======
    def __get_ally_enemy_distance(self) -> float:
        """
        Calculates the distance between the ally and enemy zones.

        Returns:
            float: Distance between the ally and enemy zones.
        """
        return self.arena_ptr.ally_zone.point.distance(self.arena_ptr.enemy_zone.point)

    @staticmethod
    def __are_path_different(
            path_a: list[OrientedPoint], path_b: list[OrientedPoint]
    ) -> bool:
        """
        Compares two paths to determine if they are different.

        Args:
            path_a (list[OrientedPoint]): First path to compare.
            path_b (list[OrientedPoint]): Second path to compare.

        Returns:
            bool: True if paths differ, otherwise False.
        """
        min_length = min(len(path_a), len(path_b))

        for i in range(1, min_length + 1):
            if path_a[-i] != path_b[-i]:
                return True
        return True

    # ====== Protected Methods ======
    def _acs(self) -> RollingBasisCommand | None:
        """
       Anti-Collision System (ACS) that stops movement if an enemy is too close.

       Returns:
           RollingBasisCommand | None: Stop command if enemy is too close, else None.
       """
        if self.params is None:
            self.logger.warning(
                "ACS was called but no movement parameters found!"
            )
            return

        # Anti Collision System
        too_close = self.__get_ally_enemy_distance() < self.params.acs_distance

        if too_close:
            # Stop the robot (set speed to 0 !)
            self.status = MovementStatus.ACS
            self.logger.warning(
                "ACS: Enemy is too close, stopping the robot"
            )
            return RollingBasisCommand(
                position=self.arena_ptr.ally_zone.point, linear_speed=0.0, angular_speed=0.0
            )
        return

    def _go_to_is_arrived(self) -> bool:
        """
        Checks if the movement goal has been reached.

        Returns:
            bool: True if the goal is reached, else False.
        """
        if (
                self.arena_ptr.ally_zone.point.distance(self.trajectory_computer.computed_goal)
                < self.params.goal_tolerance
        ):
            self.status = MovementStatus.SUCCESS
            self.logger.info("Go To is arrived")
            return True
        return False

    # ====== Public Methods ======
    def compute_go_to(
            self,
            # Currents rolling basis state (the position/odometrie is already stored in the arena)
            current_linear_speed: float,
            current_angular_speed: float,
            # Parameters of the go to
            params: GoToParams,
    ):
        """
        Computes a trajectory and initiates movement towards the goal.

        Args:
            current_linear_speed (float): Current linear speed.
            current_angular_speed (float): Current angular speed.
            params (GoToParams): Movement parameters.

        Returns:
            MovementStatus: Current movement status.
        """

        # Warn if a movement is already in progress
        if not self.status.is_finished():
            self.logger.warning(
                "A movement is already in progress and a new one is requested.",
            )

        self.params: GoToParams = params
        self.status: MovementStatus = MovementStatus.PENDING

        # 1. Compute the trajectory
        # 1.1 Create the trajectory computer
        self.trajectory_computer: TrajectoryComputer = TrajectoryComputer(
            logger=self.trajectory_computer_logger,
            path_finder_logger=self.path_finder_logger,
            arena_ptr=self.arena_ptr,
            trajectory_params=params.trajectory_params
        )
        # 1.2 Compute the trajectory (without dynamic obstacles: ignore enemy position for first computation)
        self.trajectory_computer.compute(
            use_static_and_dynamic_grid=False,
            current_linear_speed=current_linear_speed,
            current_angular_speed=current_angular_speed,
        )

        # 2. Check if the path is found
        if not self.trajectory_computer.path_finder.oriented_path_found:
            self.status = MovementStatus.NO_ACCESSIBLE
            self.params = None
            return self.status

    def handle_go_to(self) -> RollingBasisCommand | None:
        """
        Handles movement execution and dynamically adjusts the trajectory.

        Returns:
            RollingBasisCommand | None: Next movement command or None.
        """

        # 0. Start timing movement
        if self.movement_start_time == -1:
            self.movement_start_time = time.time()

        # 1. Check if a movement is in progress and if the parameters are set
        # 1.1 Check if a movement is in progress
        if self.status.is_finished():
            self.logger.warning(
                "Handle Go To was called but no movement is in progress!"
            )
            return

        # 1.2 Check if the movement parameters are set
        if self.params is None:
            self.logger.warning(
                "Handle Go To was called but no movement parameters found!"
            )
            return

        # 2. Check if the enemy is too close
        acs = self._acs()
        if acs is not None:
            return acs

        # 3. Check if the path has to be recomputed
        # -> if the enemy distance is under the recompute distance threshold
        # AND the path is not near the end
        enemy_distance = self.__get_ally_enemy_distance()
        if (
                self.params.distance_to_goal_to_dont_recompute_path
                < enemy_distance <
                self.params.path_finder_recompute_distance
        ):
            # 3.1 Save old path for comparison
            current_used_path = self.trajectory_computer.path_finder.oriented_path_found

            # 3.2 Recompute the path (use dynamic obstacles: consider enemy position)
            self.trajectory_computer.compute_path(
                use_static_and_dynamic_grid=True,
                current_position=self.arena_ptr.ally_zone.point  # use real current aly robot position
            )

            # 3.3 Check if the path has changed
            if self.__are_path_different(
                    current_used_path,
                    self.trajectory_computer.path_finder.oriented_path_found,
            ):
                self.logger.info(
                    "The path has changed, updating the rolling basis handler"
                )
                # 3.3.1 When the path has changed, update the trajectory according to the new path
                # The path is already computed and updated in the trajectory computer.
                # We only have to recompute the trajectory with the new path.
                # To compute the new trajectory, we need to get the current speed of the rolling basis handler

                # 3.3.1.1 Get the current speed of the rolling basis handler
                # To get the current speed of the rolling basis and update the new path with a smooth transition
                # We use the current TrajectoryComputer to get it
                # (it is not the best way to do this, it could be better to get the last sent command instead)
                position_speed: RollingBasisCommand = (
                    self.trajectory_computer.get_position_speed()
                )

                # 3.3.1.2 Update the trajectory with the new path
                self.trajectory_computer.compute_trajectory(
                    initial_linear_speed=position_speed.linear_speed,
                    initial_angular_speed=position_speed.angular_speed,
                )

        # 4. Check if the goal is reached
        if self._go_to_is_arrived():
            return

        # 5. Check timeout
        if time.time() - self.movement_start_time > self.timeout_limit:
            self.logger.warning("Movement exceeded time limit, stopping the robot")
            self.status = MovementStatus.TIMEOUT
            self.movement_start_time = -1
            return RollingBasisCommand(position=self.arena_ptr.ally_zone.point, linear_speed=0.0, angular_speed=0.0)

        # 6. Get the next RollingBasisCommand
        command = self.trajectory_computer

        # 6.1 Apply backward movement if necessary
        if self.go_backwards(command):
            command.get_position_speed().linear_speed = -abs(command.get_position_speed().linear_speed)
            self.logger.info("Marche arrière activée!")  # temp to test IRL

        # 6.2 Return the command
        return command.get_position_speed()

    # A certaines occasions il est nécessaire d'avoir un certain angle à implémenter après
    # Version à retravailler
    def go_backwards(self, command: TrajectoryComputer | None) -> bool:
        """
        si on est à 175 et 185 degré de notre objectif et à une distance de 5cm
        marche arrière
        """

        trajectory_computed = command.computed_goal # je suis pas sûre que c'est lui que je dois prendre
        ally_location = self.arena_ptr.ally_zone.point

        if isinstance(trajectory_computed, OrientedPoint):
            difference_angle = abs(
                trajectory_computed.theta - ally_location.theta
            )  # en radians

        elif trajectory_computed is not None:
            angle_to_goal = math.atan2(trajectory_computed.y - ally_location.y, trajectory_computed.x - ally_location.x)
            difference_angle = abs(
                angle_to_goal-ally_location.theta
            )

        else:
            return False

        # Normalisation de la différence d'angle jsp si c nécessaire
        # difference_angle = (difference_angle + math.pi) % (2 * math.pi) - math.pi

        distance = math.sqrt(
            (trajectory_computed.x - ally_location.x)**2 +
            (trajectory_computed.y - ally_location.y)**2
        )  # en cm

        # On regarde si le but est derrière le robot
        objective_behind_robot = (
                math.radians(180 - self.reverse_threshold_angle) < abs(difference_angle) < math.radians(
            180 + self.reverse_threshold_angle)
        )

        return difference_angle < self.reverse_threshold_angle \
            and distance < self.reverse_threshold_distance \
            and objective_behind_robot


