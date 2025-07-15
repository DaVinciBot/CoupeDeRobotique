from pydualsense import *
import math
import time
from loggerplusplus import Logger, LogLevels


class PS5Remote:
    def __init__(self, logger: Logger |None = None) -> None:
        """Initialize the connection with the PS5 controller"""
        self.dualsense = pydualsense()

        self.connected = False

        # Configuration parameters
        self.max_linear_speed = 1.0  # maximum linear speed in m/s
        self.max_rotation_speed = 10.0  # maximum rotation speed in rad/s

        # Sensitivity parameters
        self.linear_speed_sensitivity = 2.0  # Higher = more responsive speed
        self.rotation_speed_sensitivity = 1  # Higher = more responsive steering

        # Smoothing parameters
        self.speed_smoothing_factor = 0.15  # Lower = smoother speed changes (0-1)
        self.rotation_smoothing_factor = 0.2  # Lower = smoother angle changes (0-1)

        # Dead zones
        self.trigger_deadzone = 0.1  # For L2/R2
        self.stick_deadzone = 15  # For left/right stick

        # Command states with acceleration and momentum
        self.current_linear_speed = 0
        self.target_linear_speed = 0
        self.current_rotation_speed = 0

        self.angle = 0

        # Logger setup
        self.logger = logger or Logger(
            identifier=self.__class__.__name__, follow_logger_manager_rules=True
        )

        self.connect()

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

    def _apply_deadzone(self, value, deadzone, is_normalized=False):
        """Applies a dead zone to input values with smooth transition"""
        if abs(value) < deadzone:
            return 0.0
        normalized = (abs(value) - deadzone) / (1 - deadzone)
        return math.copysign(normalized, value)

    def _smooth_value(self, current, target, smoothing):
        """Smoothly interpolates between current and target values"""
        return current + (target - current) * smoothing

    def _apply_linear_speed_sensitivity(self, value, sensitivity):
        """Applies a non-linear sensitivity curve to the input"""
        return math.copysign(abs(value) ** sensitivity, value)

    def get_joystick_input(self):
        """Retrieves joystick values and normalizes them in [-1,1]."""
        x = self.dualsense.state.RX  # Raw value (-128 to 128)
        y = self.dualsense.state.RY

        if abs(x) < self.stick_deadzone:
            x = 0
        if abs(y) < self.stick_deadzone:
            y = 0

        return x / 128.0, y / 128.0

    def update_rotation_speed(self):
        x, _ = self.get_joystick_input()
        target_rotation_speed = (
            x * self.max_rotation_speed * self.rotation_speed_sensitivity
        )
        self.current_rotation_speed += (
            target_rotation_speed - self.current_rotation_speed
        ) * self.rotation_smoothing_factor
        self.angle = (self.angle + math.radians(self.current_rotation_speed)) % (
            2 * math.pi
        )

    def update_linear_speed(self):
        if not self.connected:
            self.logger.log("Controller not connected", LogLevels.WARNING)
            return 0.0, 0.0

        # Get trigger values (L2 and R2)
        # pydualsense gives values between 0 and 255
        throttle = self._apply_deadzone(
            self.dualsense.state.R2 / 255.0, self.trigger_deadzone, is_normalized=True
        )
        brake = self._apply_deadzone(
            self.dualsense.state.L2 / 255.0, self.trigger_deadzone, is_normalized=True
        )

        # Apply sensitivity curves
        throttle = self._apply_linear_speed_sensitivity(
            throttle, self.linear_speed_sensitivity
        )
        brake = self._apply_linear_speed_sensitivity(
            brake, self.linear_speed_sensitivity
        )

        if throttle > 0:
            self.target_linear_speed = throttle * self.max_linear_speed
        elif brake > 0:
            if self.current_linear_speed > 0:
                self.target_linear_speed = -brake * self.max_linear_speed
            else:
                self.target_linear_speed = -brake * self.max_linear_speed
        else:
            self.target_linear_speed = 0

        # Smooth transitions
        self.current_linear_speed = self._smooth_value(
            self.current_linear_speed,
            self.target_linear_speed,
            self.speed_smoothing_factor,
        )

    def update_sensitivity(self, throttle_sens=None, brake_sens=None, angle_sens=None):
        """Updates controller sensitivity parameters"""
        if throttle_sens is not None:
            self.throttle_sensitivity = max(0.1, throttle_sens)
        if brake_sens is not None:
            self.brake_sensitivity = max(0.1, brake_sens)
        if angle_sens is not None:
            self.rotation_speed_sensitivity = max(0.1, angle_sens)

    def update_smoothing(self, speed_smooth=None, angle_smooth=None):
        """Updates controller smoothing parameters"""
        if speed_smooth is not None:
            self.speed_smoothing_factor = max(0.01, min(1.0, speed_smooth))
        if angle_smooth is not None:
            self.rotation_smoothing_factor = max(0.01, min(1.0, angle_smooth))

    def update(self):
        self.update_linear_speed()
        self.update_rotation_speed()

    # def run(self):
    #     """Main loop for continuous control"""
    #     while True:
    #         try:
    #             while self.connected:
    #                 speed, angle = self.get_control_values()
    #                 self.logger.log(
    #                     f"Speed: {speed:.2f} m/s, Angle: {math.degrees(angle) % 360:.1f}°",
    #                     LogLevels.INFO,
    #                 )
    #                 time.sleep(0.1)

    #         except KeyboardInterrupt:
    #             self.logger.log("Controller stopped", LogLevels.INFO)
    #             self.disconnect()


# Example usage
if __name__ == "__main__":
    logger = Logger()
    controller = PS5Remote(logger)

    # Example: Customize sensitivity and smoothing
    controller.update_sensitivity(throttle_sens=2.0, brake_sens=2.0, angle_sens=2.5)
    controller.update_smoothing(speed_smooth=0.15, angle_smooth=0.2)

    controller.connect()
    controller.run()
