from controllers.actuators import Actuators
import time


class Servo:
    def __init__(self, tide_angle, deploy_angle, max_angle):
        self.deploy_angle = deploy_angle
        self.tide_angle = tide_angle
        self.max_angle = max_angle


class ActuatorsShow(Actuators):
    """
    ActuatorsShow is a subclass of Actuators that provides a specific implementation for the show mode.
    It inherits from the Actuators class and overrides its methods to provide functionality for the show mode.
    """

    def __init__(self, *args, **kwargs):
        """
        Initializes the ActuatorsShow class.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        super().__init__(*args, **kwargs)  # Call the parent constructor
        self.servos = [
            Servo(50, 150, 270),
            Servo(0, 180, 180),
            Servo(230, 120, 270),
            Servo(180, 0, 180),
            Servo(20, 110, 270),
            Servo(0, 180, 180),
            Servo(270, 200, 270),
            Servo(180, 0, 180),
            Servo(270, 180, 270),
            Servo(270, 0, 270),
        ]
        
    def _check_pin(self, pin) -> bool:
        if pin >= len(self.servos) or pin < 0 or self.servos[pin] is None:
            self.logger.warning(f"Pin {pin} is not a servo")
            return False
        return True    

    def deploy(self, pins: int | list[int]):
        if isinstance(pins, int):
            pins = [pins]
        for pin in pins:
            if self._check_pin(pin):
                self.set_servo_angle(
                    pin,
                    self.servos[pin].deploy_angle,
                    max_angle=self.servos[pin].max_angle,
                )
                time.sleep(0.02)

    def tide(self, pins: int | list[int]):
        if isinstance(pins, int):
            pins = [pins]
        for pin in pins:
            if self._check_pin(pin):
                self.set_servo_angle(
                    pin,
                    self.servos[pin].tide_angle,
                    max_angle=self.servos[pin].max_angle,
                )
                time.sleep(0.02)

    def deploy_all(self):
        for i in range(len(self.servos)):
            self.deploy(i)

    def tide_all(self):
        for i in range(len(self.servos)):
            self.tide(i) 
    
    def pick_up(self):
        pass