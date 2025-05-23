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
class ServoArm(Servo):
    docking: int


@dataclass
class ServoPlank(Servo):
    maintain_plank: int


@dataclass
class Stepper:
    top_steps: int
    folded_steps: int
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
        self.servos = {  # default servo with 2 position
            i: Servo(cfg["deploy_angle"], cfg["fold_angle"], cfg["max_angle"])
            for i, cfg in CONFIG.ACTUATOR_SERVOS_CONFIG.items()
            if i < 8
        }

        servo_arm = CONFIG.ACTUATOR_SERVOS_CONFIG[8]
        self.servos[8] = ServoArm(
            servo_arm["deploy_angle"],
            servo_arm["fold_angle"],
            servo_arm["max_angle"],
            servo_arm["docking"],
        )

        servo_plank = CONFIG.ACTUATOR_SERVOS_CONFIG[9]
        self.servos[9] = ServoPlank(
            servo_plank["deploy_angle"],
            servo_plank["fold_angle"],
            servo_plank["max_angle"],
            servo_plank["maintain_plank"],
        )

        stepper_config = CONFIG.ACTUATOR_ELEVATOR_CONFIG
        print(stepper_config)
        self.stepper = Stepper(
            stepper_config["top_steps"],
            stepper_config["folded_steps"],
            stepper_config["bottom_steps"],
            stepper_config["speed"],
        )

    def _check_pin(self, pin) -> bool:
        if pin not in self.servos or self.servos[pin] is None:
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
        for i in self.servos.keys():
            if i != 9:
                self.deploy(i)

    def fold_all(self):
        for i in self.servos.keys():
            self.fold(i)

    # def init_actuator(self):
    #     self.stepper_step(
    #         self.stepper.top_steps - self.elevator_ticks, self.stepper.speed
    #     )
    #     self.fold_all()
    #     self.stepper_step(
    #         self.stepper.folded_steps - self.elevator_ticks, self.stepper.speed
    #     )

    # def ready_to_pickup(self):
    #     self.stepper_step(
    #         self.stepper.top_steps - self.elevator_ticks, self.stepper.speed
    #     )
    #     self.deploy(self.center)
    #     self.stepper_step(
    #         self.stepper.bottom_steps - self.elevator_ticks, self.stepper.speed
    #     )
    #     self.deploy(self.upper_arm + self.side_arms)

    # def pick_up(self):
    #     self.set_servo_angle(
    #         self.upper_arm, 90, max_angle=self.servos[self.upper_arm].max_angle
    #     )
    #     self.deploy(self.end_servos)

    # def build(self):
    #     self.fold(self.side_arms)
    #     self.stepper_step(
    #         self.stepper.top_steps - self.elevator_ticks, self.stepper.speed
    #     )
    #     self.deploy(self.side_arms)
    #     self.fold(self.end_servos)

    # def end_build(self):
    #     self.fold(self.side_arms + self.center)
    #     self.stepper_step(
    #         self.stepper.top_steps - self.elevator_ticks, self.stepper.speed
    #     )
