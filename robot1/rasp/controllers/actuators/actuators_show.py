from config_loader import CONFIG
from controllers.actuators import Actuators
from dataclasses import dataclass
import time


@dataclass
class Servo:
    deploy_angle: int
    fold_angle: int
    max_angle: int

@dataclass
class Stepper:
    top_steps: int
    bottom_steps: int
    speed: int

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
        self.servos = [Servo(servo["deploy_angle"], servo["fold_angle"], servo["max_angle"]) for servo in CONFIG.ACTUATOR_SERVOS_CONFIG ]
        self.center = CONFIG.ACTUATOR_CENTER_ARM
        self.side_arms = CONFIG.ACTUATOR_SIDE_ARMS
        self.upper_arm = CONFIG.ACTUACTOR_UPPER_ARM
        self.end_servos = CONFIG.ACTUATOR_END_SERVOS
        
        stepper_config = CONFIG.ACTUATOR_ELEVATOR_CONFIG
        self.stepper = Stepper(stepper_config["top_steps"], stepper_config["bottom_steps"], stepper_config["speed"])
        
        
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

    def fold(self, pins: int | list[int]):
        if isinstance(pins, int):
            pins = [pins]
        for pin in pins:
            if self._check_pin(pin):
                self.set_servo_angle(
                    pin,
                    self.servos[pin].fold_angle,
                    max_angle=self.servos[pin].max_angle,
                )

    def deploy_all(self):
        for i in range(len(self.servos)):
            self.deploy(i)

    def tide_all(self):
        for i in range(len(self.servos)):
            self.tide(i) 
    
    def pick_up(self):
        self.stepper_step()
        self.deploy(self.center + self.side_arms + self.upper_arm)
        self.deploy(self.end_servos)
        self.fold(self.center + self.side_arms)
        
    def build(self):
        pass