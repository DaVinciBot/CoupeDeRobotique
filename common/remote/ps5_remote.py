from pydualsense import *
import math
import time
from logger import Logger, LogLevels


class PS5Remote:
    def __init__(self, logger: Logger):
        """Initialize the connection with the PS5 controller"""
        self.dualsense = pydualsense()
        self.connected = False

        # Configuration parameters
        self.max_speed = 1.0  # maximum speed in m/s
        self.max_angle = math.pi / 2  # maximum angle in radians (90 degrees)

        # Sensitivity parameters
        self.throttle_sensitivity = 2.0  # Higher = more responsive acceleration
        self.brake_sensitivity = 2.0  # Higher = more responsive braking
        self.angle_sensitivity = 2.5  # Higher = more responsive steering

        # Smoothing parameters
        self.speed_smoothing = 0.15  # Lower = smoother speed changes (0-1)
        self.angle_smoothing = 0.2  # Lower = smoother steering (0-1)

        # Dead zones
        self.trigger_deadzone = 0.1  # For L2/R2
        self.stick_deadzone = 0.1  # For analog stick

        # Command states with acceleration and momentum
        self.current_speed = 0.0
        self.target_speed = 0.0
        self.current_angle = 0.0
        self.target_angle = 0.0

        # Logger setup
        self.logger = logger

    def connect(self):
        """Establishes Bluetooth connection with the controller"""
        try:
            self.dualsense.init()
            self.connected = True
            self.logger.log("PS5 controller successfully connected", LogLevels.INFO)
        except Exception as e:
            self.logger.log(f"Connection error: {str(e)}", LogLevels.ERROR)
            self.connected = False

    def disconnect(self):
        """Disconnects the controller"""
        if self.connected:
            self.dualsense.close()
            self.connected = False
            self.logger.log("PS5 controller disconnected", LogLevels.INFO)

    def _apply_deadzone(self, value, deadzone):
        """Applies a dead zone to input values with smooth transition"""
        if abs(value) < deadzone:
            return 0.0
        # Smooth transition after deadzone
        normalized = (abs(value) - deadzone) / (1 - deadzone)
        return math.copysign(normalized, value)

    def _smooth_value(self, current, target, smoothing):
        """Smoothly interpolates between current and target values"""
        return current + (target - current) * smoothing

    def _apply_sensitivity(self, value, sensitivity):
        """Applies a non-linear sensitivity curve to the input"""
        return math.copysign(abs(value) ** sensitivity, value)

    def get_control_values(self):
        """
        Retrieves speed and angle values from the controller
        Returns: tuple (speed, angle)
            - speed: float between -max_speed and max_speed (m/s)
            - angle: float between -max_angle and max_angle (radians)
        """
        if not self.connected:
            self.logger.log("Controller not connected", LogLevels.WARNING)
            return 0.0, 0.0

        # Get trigger values (L2 and R2)
        # pydualsense gives values between 0 and 255
        throttle = self._apply_deadzone(
            self.dualsense.state.R2 / 255.0, self.trigger_deadzone
        )
        brake = self._apply_deadzone(
            self.dualsense.state.L2 / 255.0, self.trigger_deadzone
        )

        # Right stick for steering (X-axis)
        steering = self._apply_deadzone(
            self.dualsense.state.RX / 128.0, self.stick_deadzone
        )

        # Apply sensitivity curves
        throttle = self._apply_sensitivity(throttle, self.throttle_sensitivity)
        brake = self._apply_sensitivity(brake, self.brake_sensitivity)
        steering_normalized = self._apply_sensitivity(steering, self.angle_sensitivity)

        # Calculate target speed based on throttle and brake
        # Throttle increases speed positively, brake increases speed negatively
        if throttle > 0:
            self.target_speed = throttle * self.max_speed
        elif brake > 0:
            self.target_speed = -brake * self.max_speed
        else:
            # If no input, gradually return to zero (simulate friction)
            self.target_speed = 0

        # Update target angle
        self.target_angle = steering_normalized * self.max_angle

        # Smooth transitions
        self.current_speed = self._smooth_value(
            self.current_speed, self.target_speed, self.speed_smoothing
        )
        self.current_angle = self._smooth_value(
            self.current_angle, self.target_angle, self.angle_smoothing
        )

        self.logger.log(
            f"Speed: {self.current_speed:.2f} m/s, Angle: {math.degrees(self.current_angle):.1f}°, "
            f"Throttle: {throttle:.2f}, Brake: {brake:.2f}",
            LogLevels.DEBUG,
        )

        return self.current_speed, self.current_angle

    def update_sensitivity(self, throttle_sens=None, brake_sens=None, angle_sens=None):
        """Updates controller sensitivity parameters"""
        if throttle_sens is not None:
            self.throttle_sensitivity = max(0.1, throttle_sens)
        if brake_sens is not None:
            self.brake_sensitivity = max(0.1, brake_sens)
        if angle_sens is not None:
            self.angle_sensitivity = max(0.1, angle_sens)

    def update_smoothing(self, speed_smooth=None, angle_smooth=None):
        """Updates controller smoothing parameters"""
        if speed_smooth is not None:
            self.speed_smoothing = max(0.01, min(1.0, speed_smooth))
        if angle_smooth is not None:
            self.angle_smoothing = max(0.01, min(1.0, angle_smooth))

    def run(self):
        """Main loop for continuous control"""
        try:
            while self.connected:
                speed, angle = self.get_control_values()
                self.logger.log(
                    f"Speed: {speed:.2f} m/s, Angle: {math.degrees(angle):.1f}°",
                    LogLevels.INFO,
                )
                return speed, angle

        except KeyboardInterrupt:
            self.logger.log("Controller stopped", LogLevels.INFO)
            self.disconnect()


# Example usage
if __name__ == "__main__":
    controller = PS5Remote()

    # Example: Customize sensitivity and smoothing
    controller.update_sensitivity(throttle_sens=2.0, brake_sens=2.0, angle_sens=2.5)
    controller.update_smoothing(speed_smooth=0.15, angle_smooth=0.2)

    controller.connect()
    controller.run()
