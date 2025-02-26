from geometry import OrientedPoint
from movement.params.trajectory_params import TrajectoryParams
from arena import BaseArena, GridManager, BaseArenaZone
from path_finding import PathFinder

from geometry import Point, Polygon
import time
from loggerplusplus import Logger
from movement.trajectory_computer.curve import Curve
import math
from bisect import bisect_left
from movement.params import RollingBasisCommand


class TrajectoryComputer:
    def __init__(
            self,
            # Loggers:
            logger: Logger,
            path_finder_logger: Logger,
            # Arena (should be a pointer of the arena)
            arena_ptr: BaseArena,
            # Trajectory params
            trajectory_params: TrajectoryParams,
    ):
        self.logger: Logger = logger
        self.path_finder_logger: Logger = path_finder_logger

        self.arena_ptr: BaseArena = arena_ptr
        self.trajectory_params = trajectory_params

        self.path_finder: PathFinder | None = None
        self.computed_goal: OrientedPoint | Point | None = None

        # Trajectory points and related metadata
        self.cumulative_distances = [0]  # Cumulative distance between trajectory points

        # Timing variables
        self.start_time: float = 0.0  # Time when the trajectory started
        self.total_duration: float = 0.0  # Total duration of the trajectory

        # Variables for speed curves
        self.linear_curve: Curve | None = None

        # Variables for angular speed
        self.__last_theta = None  # Last recorded angular position
        self.__last_time_theta = 0.0  # Time of last angular position update

        self.__initial_angular_speed: float = 0.0

    """
        Path part of the trajectory computer
    """

    # ====== Private/Protected methods ====== #

    def _compute_go_to_destination_from_zone(self) -> Point:
        # Get goal zone centroid
        centroid = self.trajectory_params.goal.centroid
        new_x = centroid.x
        new_y = centroid.y

        # Check if the goal is too close to the border
        if centroid.x < self.arena_ptr.border_buffer + self.trajectory_params.goal.obstacle_buffer:
            new_x = self.arena_ptr.border_buffer + self.trajectory_params.goal.obstacle_buffer
        if (self.arena_ptr.width - centroid.x) < (
                self.arena_ptr.border_buffer + self.trajectory_params.goal.obstacle_buffer
        ):
            new_x = self.arena_ptr.width - (self.arena_ptr.border_buffer + self.trajectory_params.goal.obstacle_buffer)
        if centroid.y < self.arena_ptr.border_buffer + self.trajectory_params.goal.obstacle_buffer:
            new_y = self.arena_ptr.border_buffer + self.trajectory_params.goal.obstacle_buffer
        if (self.arena_ptr.height - centroid.y) < (
                self.arena_ptr.border_buffer + self.trajectory_params.goal.obstacle_buffer
        ):
            new_y = self.arena_ptr.height - (self.arena_ptr.border_buffer + self.trajectory_params.goal.obstacle_buffer)

        return Point(new_x, new_y)

    def _get_goal(self) -> OrientedPoint | Point:
        # Get goal with OrientedPoint format

        # If goal is a BaseArenaZone
        if isinstance(self.trajectory_params.goal, BaseArenaZone):
            # Use zone method to get best goal point from zone
            self.computed_goal = self.trajectory_params.goal.get_go_to_position(
                ally_position=self.arena_ptr.ally_zone.point, team_color=self.arena_ptr.team_color
            )

            # If goal is None => zone is not accessible
            if self.computed_goal is None:
                self.logger.error("Goal is not accessible.")
                return

            # If goal is not an OrientedPoint ça veut dire que acune go to position n'est définie
            # On calcule alors automatiquemnt ce point
            if not isinstance(self.computed_goal, OrientedPoint):
                self.computed_goal = self._compute_go_to_destination_from_zone()

            # TODO: prendre en compte que quand on a que un point en goal, on ne peut pas avoir de theta,
            #  il faut le cacluler automatiqument (le même que celui d'avant dans la trjectoire par exmepl) voir pour mettre ay niveay du pathfinder

            return self.computed_goal

        self.computed_goal = self.trajectory_params.goal
        return self.computed_goal

    def _init_path_finder(self):
        self.path_finder = PathFinder(
            logger=self.path_finder_logger,
            start=self.arena_ptr.ally_zone.point,
            goal=self._get_goal(),
            grid_manager=self.arena_ptr.grid_manager,
            path_resolution=self.trajectory_params.resolution,
        )

    # ====== Public methods ====== #
    def compute_path(
            self,
            use_static_and_dynamic_grid: bool,
            current_position: OrientedPoint = None,
    ) -> list[OrientedPoint]:
        # Initie pathfinder if not aready done
        if self.path_finder is None:
            self._init_path_finder()
        else:
            # Update pathfinder with current position
            self.path_finder.update_current_position(
                self.arena_ptr.ally_zone.point if current_position is None else current_position
            )

        # Run pathfinder
        self.path_finder.find_oriented_path(
            use_static_and_dynamic_grid=use_static_and_dynamic_grid,
            smooth_path=self.trajectory_params.smooth_trajectory
        )

        return self.path_finder.oriented_path_found

    """
        Trajectory speeds part of the trajectory computer
    """

    # ====== Private/Protected methods ====== #
    def __compute_position(self, t: float) -> OrientedPoint:
        """
        Calculates the robot's position at time t.

        Args:
            t (float): Time in seconds.

        Returns:
            OrientedPoint: The calculated position.
        """
        # Compute the distance traveled along the trajectory at time t
        s = self.linear_curve.PlannedPosition(t)

        # Find the trajectory segment corresponding to the traveled distance
        i = bisect_left(self.cumulative_distances, s)
        i = min(i, len(self.cumulative_distances) - 1)

        # Interpolate between the points surrounding the current position
        s1 = self.cumulative_distances[i - 1]
        s2 = self.cumulative_distances[i]
        ratio = (s - s1) / (s2 - s1) if s2 > s1 else 0

        # Extract positions and orientations of the surrounding points
        x1, y1, theta1 = (
            self.path_finder.oriented_path_found[i - 1].x,
            self.path_finder.oriented_path_found[i - 1].y,
            self.path_finder.oriented_path_found[i - 1].theta,
        )
        x2, y2, theta2 = (
            self.path_finder.oriented_path_found[i].x,
            self.path_finder.oriented_path_found[i].y,
            self.path_finder.oriented_path_found[i].theta,
        )

        # Compute interpolated position and orientation
        x = x2 + ratio * (x1 - x2)
        y = y2 + ratio * (y1 - y2)
        theta = theta2 + ratio * (theta1 - theta2)

        return OrientedPoint(x, y, theta)

    def __compute_velocity(self, t: float, theta: float) -> tuple[float, float]:
        """
        Calculates the robot's linear and angular velocities at time t.

        Args:
            t (float): Time in seconds.
            theta (float): Current orientation of the robot.

        Returns:
            tuple[float, float]: Linear and angular velocities.
        """
        # Compute linear velocity
        v_linear = self.linear_curve.PlannedVelocity(t)

        # Compute angular velocity based on changes in orientation
        if (
                self.__last_theta is None
                or self.__last_time_theta is None
                or t == self.__last_time_theta
        ):
            v_angular = self.__initial_angular_speed
        else:
            dt = t - self.__last_time_theta
            dtheta = theta - self.__last_theta

            # Normalize angular difference to the range [-π, π]
            if dtheta > math.pi:
                dtheta -= 2 * math.pi
            elif dtheta < -math.pi:
                dtheta += 2 * math.pi

            v_angular = dtheta / dt

        # Clamp angular velocity to the maximum allowed value
        if abs(v_angular) > self.trajectory_params.speed_profile.max_angular_speed:
            v_angular = self.trajectory_params.speed_profile.max_angular_speed * (
                    v_angular / abs(v_angular)
            )

        # Update state for future computations
        self.__last_theta = theta
        self.__last_time_theta = t

        return v_linear, v_angular

    def __compute_cumulative_distance(self):
        self.start_time = time.time()

        # Compute cumulative distances between trajectory points
        total_distance = 0
        for i in range(1, len(self.path_finder.oriented_path_found)):
            x1, y1 = self.path_finder.oriented_path_found[i - 1].x, self.path_finder.oriented_path_found[i - 1].y
            x2, y2 = self.path_finder.oriented_path_found[i].x, self.path_finder.oriented_path_found[i].y
            total_distance += math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
            self.cumulative_distances.append(total_distance)

    def __init_curves(
            self,
            initial_linear_speed: float = None,
            initial_angular_speed: float = None,
    ) -> None:

        self.__initial_angular_speed = initial_angular_speed

        # Total distance covered by the trajectory
        total_linear_distance = self.cumulative_distances[-1]

        # Extract parameters from the speed profile
        Vd_lin = initial_linear_speed if initial_linear_speed is not None else 0.0
        Vm_lin = self.trajectory_params.speed_profile.max_linear_speed
        Va_lin = 0.0  # Assume the robot stops at the end of the trajectory
        amax_lin = self.trajectory_params.speed_profile.max_linear_acceleration
        dmax_lin = self.trajectory_params.speed_profile.max_linear_deceleration

        # Create a curve for linear motion
        self.linear_curve = Curve(
            Vd_lin, Vm_lin, Va_lin, total_linear_distance, amax_lin, dmax_lin
        )

        # Determine the total duration of the planned motion
        self.total_duration = self.linear_curve.PlannedTotalTime()

    # ====== Public methods ====== #
    def compute_trajectory(
            self,
            initial_linear_speed: float = None,
            initial_angular_speed: float = None,
    ):
        if self.path_finder is None:
            self.logger.error("PathFinder is not initialized.")
            return

        self.__compute_cumulative_distance()
        self.__init_curves(initial_linear_speed, initial_angular_speed)

        # Set initial conditions
        self.start_time = time.time()
        self.__last_theta = self.path_finder.oriented_path_found[0].theta

    """
       Global Usage of the TrajectoryComputer
    """

    def compute(
            self,
            use_static_and_dynamic_grid: bool,
            current_position: OrientedPoint = None,
            current_linear_speed: float = None,
            current_angular_speed: float = None,
    ):
        self.compute_path(use_static_and_dynamic_grid, current_position)
        self.compute_trajectory(current_linear_speed, current_angular_speed)

    def get_position_speed(self, t: float = None) -> RollingBasisCommand:
        """
        Computes the robot's position and speeds at the specified time.

        Args:
            t (float): Time in seconds for the future state calculation. Defaults to current time.

        Returns:
            tuple[OrientedPoint, float, float]: Position, linear speed, and angular speed.
        """
        if t is None:
            t = time.time()
        current_time = t - self.start_time

        # Limit the computation to the total trajectory duration
        if current_time > self.total_duration:
            current_time = self.total_duration

        # Compute position and speeds
        position = self.__compute_position(current_time)
        linear_speed, angular_speed = self.__compute_velocity(
            current_time, position.theta
        )
        return RollingBasisCommand(
            position=position,
            linear_speed=linear_speed,
            angular_speed=angular_speed
        )
