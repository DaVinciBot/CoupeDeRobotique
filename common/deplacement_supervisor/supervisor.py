import time
import math
from geometry import OrientedPoint
from deplacement_supervisor.curve import Curve
from bisect import bisect_left


class MovementSupervisor:
    def __init__(self, profile: dict, linear_speed: float, angular_speed: float):
        """
        Initializes the supervisor by loading the specified profile.

        :param profile: Acceleration, deceleration, and speed profile as a dictionary.
        """
        self.profile = profile

        self.trajectory = []  # Trajectory of OrientedPoint to follow
        self.cumulative_distances = []  # Cumulative distance between trajectory points

        self.linear_speed = linear_speed
        self.angular_speed = angular_speed
        self.linear_curve: Curve

        self.total_duration: float = 0.0
        self.current_time: float = 0.0
        self.start_time: float = time.time()
        # self.set_trajectory(pathfinder.get_trajectory())

        self.last_theta = None
        self.last_time_theta = 0.0

    def set_trajectory(self, trajectory):
        """
        Sets the trajectory to follow.

        :param trajectory: List of OrientedPoint objects representing the trajectory
        """
        self.trajectory = trajectory
        self.cumulative_distances = [0]
        total_distance = 0
        for i in range(1, len(self.trajectory)):
            x1, y1 = self.trajectory[i - 1].x, self.trajectory[i - 1].y
            x2, y2 = self.trajectory[i].x, self.trajectory[i].y
            total_distance += ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
            self.cumulative_distances.append(total_distance)
        if self.trajectory:
            self._initialize_curves()
            self.start_time = time.time()
            self.last_theta = self.trajectory[0].theta
        else:
            raise ValueError("The trajectory cannot be empty.")

    def compute_future_state(self, t=time.time()):
        """
        Computes the desired point and speeds at t seconds.

        :param t: Time in seconds for the future state calculation.
        :return: Oriented Point position_desired, linear_speed_desired, angular_speed_desired
        """
        self.current_time = t - self.start_time
        if self.current_time > self.total_duration:
            self.current_time = self.total_duration
        future_position: OrientedPoint = self._calculate_future_position(
            self.current_time
        )
        future_linear_speed, future_angular_speed = self._calculate_future_velocity(
            self.current_time, future_position.theta
        )
        return future_position, future_linear_speed, future_angular_speed

    def _initialize_curves(self):
        """
        Initializes the motion curve for linear speed.
        """
        total_linear_distance = self.cumulative_distances[-1]

        Vd_lin = self.linear_speed
        Vm_lin = self.profile["max_linear_speed"]
        Va_lin = 0.0  # Assume the robot stops at the end
        amax_lin = self.profile["max_linear_acceleration"]
        dmax_lin = self.profile["max_linear_deceleration"]

        # Create Curve objects for linear and angular movements
        self.linear_curve = Curve(
            Vd_lin, Vm_lin, Va_lin, total_linear_distance, amax_lin, dmax_lin
        )
        self.total_duration = self.linear_curve.PlannedTotalTime()

    def _calculate_future_position(self, t):
        """
        Calculates the future position of the robot at time t.
        """
        # Distance traveled at time t
        if self.linear_curve is None:
            raise ValueError("Linear curve is not initialized.")
        s = self.linear_curve.PlannedPosition(t)

        # Find the trajectory points between which the robot is located
        if not self.cumulative_distances:
            raise ValueError("Cumulative distances list is empty.")
        i = bisect_left(self.cumulative_distances, s)
        if i == len(self.cumulative_distances):
            i -= 1
        # Linear interpolation between points i-1 and i
        s1 = self.cumulative_distances[i - 1]
        s2 = self.cumulative_distances[i]
        if s2 == s1:
            ratio = 0
        else:
            ratio = (s - s1) / (s2 - s1)

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

        x = x2 + ratio * (x1 - x2)
        y = y2 + ratio * (y1 - y2)
        theta = theta2 + ratio * (theta1 - theta2)

        future_position = OrientedPoint(x, y, theta)

        return future_position

    def _calculate_future_velocity(self, t: float, theta: float):
        """
        Calculates the future speed of the robot at time t.
        """
        v_linear = self.linear_curve.PlannedVelocity(t)

        if (
            self.last_theta is None
            or self.last_time_theta is None
            or t == self.last_time_theta
        ):
            v_angular = self.angular_speed
        else:
            dt = t - self.last_time_theta
            dtheta = theta - self.last_theta

            if dtheta > math.pi:
                dtheta -= 2 * math.pi
            elif dtheta < -math.pi:
                dtheta += 2 * math.pi

            v_angular = dtheta / dt

        if abs(v_angular) > self.profile["max_angular_speed"]:
            v_angular = self.profile["max_angular_speed"] * (v_angular / abs(v_angular))

        self.last_theta = theta
        self.last_time_theta = t

        return v_linear, v_angular
