# ====== Code Summary ======
# This class, RollingBasisHandler, manages the motion control of a robot by defining its trajectory and speed profile.
# It calculates the robot's position and velocity at any given time based on predefined curves for linear and angular motion.
# The class supports trajectory initialization, position and speed computation, and emergency stopping.

# ====== Standard Library Imports ======
import time
import math
from bisect import bisect_left

# ====== Third-Party Library Imports ======

# ====== Internal Project Imports ======
from loggerplusplus import Logger
from geometry import OrientedPoint
from rolling_basis_handler.curve import Curve
from rolling_basis_handler.speed_profile import SpeedProfile
from rolling_basis_handler.rolling_basis_command import RollingBasisCommand


class RollingBasisHandler:
    """
    Handles the motion control of a robot, including trajectory tracking and speed computation.
    """

    def __init__(
            self,
            logger: Logger,
            profile: SpeedProfile,
            initial_linear_speed: float,
            initial_angular_speed: float,
            trajectory: list[OrientedPoint]
    ):
        """
        Initializes the RollingBasisHandler.

        Args:
            profile (SpeedProfile): The speed profile for the robot's motion.
            trajectory (list[OrientedPoint]): The trajectory points to follow.
        """
        self.logger: Logger = logger
        self.speed_profile: SpeedProfile = profile

        # Initial linear and angular speeds
        self.initial_linear_speed: float = initial_linear_speed
        self.initial_angular_speed: float = initial_angular_speed

        # Trajectory points and related metadata
        self.trajectory: list[OrientedPoint] = []
        self.cumulative_distances = [0]  # Cumulative distance between trajectory points

        # Timing variables
        self.start_time: float = 0.0  # Time when the trajectory started
        self.current_time: float = 0.0  # Current time since start
        self.total_duration: float = 0.0  # Total duration of the trajectory

        # Variables for speed curves
        self.linear_curve: Curve | None = None

        # Variables for angular speed
        self.last_theta = None  # Last recorded angular position
        self.last_time_theta = 0.0  # Time of last angular position update

        # Initialize trajectory and curves
        self.__set_trajectory(trajectory)
        self.__init_curves()

        # Set initial conditions
        self.start_time = time.time()
        self.last_theta = self.trajectory[0].theta

    def __set_trajectory(self, trajectory: list[OrientedPoint]) -> None:
        """
        Sets the trajectory to follow and computes cumulative distances.

        Args:
            trajectory (list[OrientedPoint]): The trajectory points to follow.
        """
        self.start_time = time.time()
        self.trajectory = trajectory

        # Compute cumulative distances between trajectory points
        total_distance = 0
        for i in range(1, len(self.trajectory)):
            x1, y1 = self.trajectory[i - 1].x, self.trajectory[i - 1].y
            x2, y2 = self.trajectory[i].x, self.trajectory[i].y
            total_distance += math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
            self.cumulative_distances.append(total_distance)

    def __init_curves(self) -> None:
        """
        Initializes the motion curves for linear speed based on the speed profile.
        """
        # Total distance covered by the trajectory
        total_linear_distance = self.cumulative_distances[-1]

        # Extract parameters from the speed profile
        Vd_lin = self.initial_linear_speed
        Vm_lin = self.speed_profile.max_linear_speed
        Va_lin = 0.0  # Assume the robot stops at the end of the trajectory
        amax_lin = self.speed_profile.max_linear_acceleration
        dmax_lin = self.speed_profile.max_linear_deceleration

        # Create a curve for linear motion
        self.linear_curve = Curve(
            Vd_lin, Vm_lin, Va_lin, total_linear_distance, amax_lin, dmax_lin
        )

        # Determine the total duration of the planned motion
        self.total_duration = self.linear_curve.PlannedTotalTime()

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
            self.trajectory[i - 1].x,
            self.trajectory[i - 1].y,
            self.trajectory[i - 1].theta,
        )
        x2, y2, theta2 = (
            self.trajectory[i].x,
            self.trajectory[i].y,
            self.trajectory[i].theta,
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
                self.last_theta is None
                or self.last_time_theta is None
                or t == self.last_time_theta
        ):
            v_angular = self.initial_angular_speed
        else:
            dt = t - self.last_time_theta
            dtheta = theta - self.last_theta

            # Normalize angular difference to the range [-π, π]
            if dtheta > math.pi:
                dtheta -= 2 * math.pi
            elif dtheta < -math.pi:
                dtheta += 2 * math.pi

            v_angular = dtheta / dt

        # Clamp angular velocity to the maximum allowed value
        if abs(v_angular) > self.speed_profile.max_angular_speed:
            v_angular = self.speed_profile.max_angular_speed * (
                    v_angular / abs(v_angular)
            )

        # Update state for future computations
        self.last_theta = theta
        self.last_time_theta = t

        return v_linear, v_angular

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
        self.current_time = t - self.start_time

        # Limit the computation to the total trajectory duration
        if self.current_time > self.total_duration:
            self.current_time = self.total_duration

        # Compute position and speeds
        position = self.__compute_position(self.current_time)
        linear_speed, angular_speed = self.__compute_velocity(
            self.current_time, position.theta
        )
        return RollingBasisCommand(
            position=position,
            linear_speed=linear_speed,
            angular_speed=angular_speed
        )


