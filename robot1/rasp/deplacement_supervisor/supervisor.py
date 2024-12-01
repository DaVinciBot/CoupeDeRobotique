from config_loader import CONFIG
from geometry import OrientedPoint
from curve import Curve
from bisect import bisect_left

class MovementSupervisor:
    def __init__(self, profile_name: str, linear_speed: float, angular_speed: float):
        """
        Initializes the supervisor by loading the specified profile from config.json.
    
        :param profile_name: Name of the profile to use (high_speed, cruise_speed, low_speed).
        """
        self.profile = CONFIG.SPEED_PROFILES[profile_name] # Load the speed profile from config.json. Ensure config.json is updated with the correct profiles.
        if not self.profile:
            raise ValueError(f"Profile '{profile_name}' not found in the configuration.")

        self.trajectory = [] # Trajectory to follow in the form [((x, y), θ), ...]
        self.cumulative_distances = [] # Cumulative distance between trajectory points

        self.linear_speed = linear_speed
        self.angular_speed = angular_speed
        self.linear_curve: Curve
        self.angular_curve: Curve
        self.total_duration: float = 0.0
        self.current_time: float = 0.0
        # self.set_trajectory(pathfinder.get_trajectory())

    def set_trajectory(self, trajectory):
        """
        Sets the trajectory to follow.

        :param trajectory: List of points in the form [((x, y), θ), ...].
        """
        self.trajectory = trajectory
        self.cumulative_distances = [0]
        total_distance = 0
        for i in range(1, len(self.trajectory)):
            x1, y1 = self.trajectory[i - 1][0]
            x2, y2 = self.trajectory[i][0]
            total_distance += ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
            self.cumulative_distances.append(total_distance)
        if self.trajectory:
            self._initialize_curves()
        else:
            raise ValueError("The trajectory cannot be empty.")

    def compute_future_state(self, t):
        """
        Computes the desired point and speeds in t seconds.

        :param t: Time in seconds for the future state calculation.
        :return: Tuple (((x, y), θ), linear_speed_desired, angular_speed_desired)
        """
        self.current_time += t
        if self.current_time > self.total_duration:
            self.current_time = self.total_duration
        future_position = self._calculate_future_position(self.current_time)
        future_linear_speed, future_angular_speed = self._calculate_future_velocity(self.current_time)
        return future_position, future_linear_speed, future_angular_speed

    def _initialize_curves(self):
        """
        Initializes the motion curves for linear and angular speeds.
        """
        total_linear_distance = self.cumulative_distances[-1]
        
        # Pour simplifier, on suppose que le robot suit une trajectoire plane sans rotation pour le mouvement linéaire
        # Pour le mouvement angulaire, on calcule la différence totale d'angle
        if len(self.trajectory) < 2:
            total_angular_distance = 0
        else:
            total_angular_distance = abs(self.trajectory[-1][1] - self.trajectory[0][1])

        # Profile parameters
        Vd_lin = self.linear_speed
        Vm_lin = self.profile["max_linear_speed"]
        Va_lin = 0.0 # Assume the robot stops at the end of the movement
        Dd_lin = total_linear_distance * 0.1 # Linear departure distance
        Da_lin = total_linear_distance * 0.1 # Linear arrival distance
        
        Vd_ang = self.angular_speed
        Vm_ang = self.profile["max_angular_speed"]
        Va_ang = 0.0 # Assume the robot stops at the end of the movement
        Dd_ang = total_angular_distance * 0.1 # Angular departure distance
        Da_ang = total_angular_distance * 0.1 # Angular arrival distance
        
        # Create Curve objects for linear and angular movements
        self.linear_curve = Curve(Vd_lin, Vm_lin, Va_lin, total_linear_distance, Dd_lin, Da_lin)
        self.angular_curve = Curve(Vd_ang, Vm_ang, Va_ang, total_angular_distance, Dd_ang, Da_ang)
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
        
        (x1, y1), theta1 = self.trajectory[i - 1]
        (x2, y2), theta2 = self.trajectory[i]
        
        x = x1 + ratio * (x2 - x1)
        y = y1 + ratio * (y2 - y1)
        theta = theta1 + ratio * (theta2 - theta1)
        
        return ((x, y), theta)

    def _calculate_future_velocity(self, t):
        """
        Calculates the future speed of the robot at time t.
        """
        if self.angular_curve is None:
            raise ValueError("Angular curve is not initialized.")
        v_linear = self.linear_curve.PlannedVelocity(t)
        v_angular = self.angular_curve.PlannedVelocity(t)
        return v_linear, v_angular
