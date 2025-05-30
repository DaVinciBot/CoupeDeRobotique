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
class ServoDocking(Servo):
    special_angle: int = 0  # Angle for special movement such as docking


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
        self.folded: bool = True  # Indicates if the actuators are folded
        self.servos: dict[
            int | CONFIG.ACTUATORS_CONFIG, Servo | ServoArm | ServoPlank | ServoDocking
        ] = {  # default servo with 2 position
            i: Servo(cfg["deploy_angle"], cfg["fold_angle"], cfg["max_angle"])
            for i, cfg in CONFIG.ACTUATOR_SERVOS_CONFIG.items()
            if i < 8
        }

        # Modify servos 0 and 2:
        self.servos[0] = ServoDocking(
            self.servos[0].deploy_angle,
            self.servos[0].fold_angle,
            self.servos[0].max_angle,
            CONFIG.ACTUATOR_SERVOS_CONFIG[0]["docking"],
        )

        self.servos[2] = ServoDocking(
            self.servos[2].deploy_angle,
            self.servos[2].fold_angle,
            self.servos[2].max_angle,
            CONFIG.ACTUATOR_SERVOS_CONFIG[2]["docking"],
        )

        # 0: Interior Right Arm
        # 1 : Interior Right Magnet
        # 2 : Interior Left Arm
        # 3 : Interior Left Magnet
        # 4 : Exterior Right Arm
        # 5 : Exterior Right Magnet
        # 6 : Exterior Left Arm
        # 7 : Exterior Left Magnet

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

        # 9 : Folded = Catch plank

        stepper_config = CONFIG.ACTUATOR_ELEVATOR_CONFIG
        print(stepper_config)
        self.stepper = Stepper(
            stepper_config["top_steps"],
            stepper_config["folded_steps"],
            stepper_config["bottom_steps"],
            stepper_config["speed"],
        )

    # Protected methods
    def _check_pin(self, pin) -> bool:
        """
        Checks if the specified pin is a valid servo pin.
        Args:
            pin (int): The pin number to check.
        Returns:
            bool: True if the pin is a valid servo pin, False otherwise.
        """
        if pin not in self.servos or self.servos[pin] is None:
            self.logger.warning(f"Pin {pin} is not a servo")
            return False
        return True

    # Private methods
    def __move_to_save_folded_position(self):
        """
        Moves the elevator to a safe folded position before deploying the servo arm.
        This method ensures that the elevator is in a safe position before deploying the servo arm.
        """
        steps_to_move = self.stepper.folded_steps - self.elevator_ticks + 20
        self.stepper_step(steps_to_move, self.stepper.speed, disable_driver=False)

    def __align_dropping_cans(self):
        """
        Aligns the dropping cans by setting the servos to specific angles.
        This method sets the angles of the servos to predefined values for the dropping cans.
        """
        self.set_servo_angle(pin=4, angle=160, max_angle=270)
        self.set_servo_angle(pin=6, angle=90, max_angle=270)

    # Public methods

    def deploy(self, pins: int | list[int]):
        """
        Deploys the specified servos to their deploy angle.
        This method sets the specified servos to their deploy angle, effectively deploying the servo arm.
        Args:
            pins (int | list[int]): The pin number or a list of pin numbers to deploy.
        """
        if isinstance(pins, int):
            pins = [pins]
        for pin in pins:
            if pin == 8:
                self.folded = False
            if self._check_pin(pin):
                self.set_servo_angle(
                    pin,
                    self.servos[pin].deploy_angle,
                    max_angle=self.servos[pin].max_angle,
                )

    def fold(self, pins: int | list[int]):
        """
        Folds the specified servos to their fold angle.
        This method sets the specified servos to their fold angle, effectively folding the servo arm.
        Args:
            pins (int | list[int]): The pin number or a list of pin numbers to fold.
        """
        if isinstance(pins, int):
            pins = [pins]
        for pin in pins:
            if self._check_pin(pin):
                if pin == 8:
                    self.__move_to_save_folded_position()
                    self.folded = True
                self.set_servo_angle(
                    pin,
                    self.servos[pin].fold_angle,
                    max_angle=self.servos[pin].max_angle,
                )

    def deploy_all(self):
        """
        Deploys all servos to their deploy angle.
        This method sets all servos to their deploy angle, effectively deploying the servo arm.
        """
        if 8 in self.servos:
            self.deploy(8)

        for i in self.servos.keys():
            if i != 8:
                self.deploy(i)

    def deploy_all_pickup(self):
        """
        Deploys all servos and moves the elevator to a safe position for pickup.
        This method ensures that the elevator is in a safe position before deploying the servo arm.
        """
        self.folded = False
        self.docking()

        for i in self.servos.keys():
            if i != 8:
                self.deploy(i)

    def fold_all(self):
        """
        Folds all servos to their fold angle.
        This method sets all servos to their fold angle, effectively folding the servo arm.
        """
        for i in self.servos.keys():
            if i != 8:
                self.fold(i)

        if 8 in self.servos:
            self.fold(8)

    def demagnetize_all(self):
        """
        Demagnetizes the servos by setting them to their fold angle.
        This is useful for ensuring that the servos are not holding any position
        when they are not in use.
        """
        pins = [1, 3, 5, 7]
        for pin in pins:
            if self._check_pin(pin):
                self.set_servo_angle(
                    pin,
                    self.servos[pin].fold_angle,
                    max_angle=self.servos[pin].max_angle,
                )

    def magnetize_all(self):
        """
        Magnetizes the servos by setting them to their deploy angle.
        This is useful for ensuring that the servos are holding their position
        when they are in use.
        """
        pins = [1, 3, 5, 7]
        for pin in pins:
            if self._check_pin(pin):
                self.set_servo_angle(
                    pin,
                    self.servos[pin].deploy_angle,
                    max_angle=self.servos[pin].max_angle,
                )

    def docking(self):
        """
        Moves the interior servos arms to the docking position.
        This method sets the interior servo arms to its docking position, which is used for docking purposes.
        """
        if self._check_pin(0) and self._check_pin(2):
            self.set_servo_angle(
                0,
                self.servos[0].special_angle,
                max_angle=self.servos[0].max_angle,
            )
            self.set_servo_angle(
                2,
                self.servos[2].special_angle,
                max_angle=self.servos[2].max_angle,
            )

    def deploy_banner(self):
        self.deploy([0, 2])

    def place_upper_cans(self):
        """
        Places the upper cans by setting the servos to specific angles.
        This method sets the angles of the servos to predefined values for the upper cans.
        """
        self.set_servo_angle(pin=4, angle=160, max_angle=270)
        self.set_servo_angle(pin=6, angle=90, max_angle=270)

    def raise_plank(self):
        """
        Raises the plank by moving the elevator to the top position.
        This method is used to raise the plank to its top position.
        """
        steps_to_move = self.stepper.top_steps
        self.stepper_step(steps_to_move, self.stepper.speed)

    def go_to_top(self):
        """
        Moves the elevator to the top position.
        If the elevator is folded, it will move to the folded position first.
        """
        if self.folded and self.elevator_ticks == 0:
            self.elevator_ticks = self.stepper.folded_steps
        steps_to_move = self.stepper.top_steps - self.elevator_ticks
        self.logger.info(f"Moving to top: {steps_to_move} steps")
        self.stepper_step(steps_to_move, self.stepper.speed, disable_driver=False)
        self.logger.info(f"Steps current: {self.elevator_ticks}")

    def elevator_drop_top(self):
        """
        Moves the elevator to the top position.
        If the elevator is folded, it will move to the folded position first.
        """
        if self.folded and self.elevator_ticks == 0:
            self.elevator_ticks = self.stepper.folded_steps
        steps_to_move = 600 - self.elevator_ticks
        self.logger.info(f"Moving to top: {steps_to_move} steps")
        self.stepper_step(steps_to_move, self.stepper.speed, disable_driver=False)
        self.logger.info(f"Steps current: {self.elevator_ticks}")

    def go_to_bottom(self):
        """
        Moves the elevator to the bottom position.
        If the elevator is folded, it will move to the folded position first.
        """
        if self.folded:
            steps_to_move = (
                self.stepper.bottom_steps
                + self.stepper.folded_steps
                - self.elevator_ticks
            )
        else:
            steps_to_move = self.stepper.bottom_steps - self.elevator_ticks
        self.logger.info(f"Moving to bottom: {steps_to_move} steps")
        self.stepper_step(steps_to_move, self.stepper.speed, disable_driver=True)
        self.logger.info(f"Steps current: {self.elevator_ticks}")

    def build_floors(self):
        # Ask if I should use time.sleep or asyncio.sleep and thus making this method async
        """
        Builds the floors by deploying the servos and moving the elevator to the top position.
        This method is used to build the floors by deploying the servos and moving the elevator to the top position.
        """

        self.go_to_top()
        time.sleep(2)
        # Set cans to correct position
        self.__align_dropping_cans()
        time.sleep(2)

        # Demagnetize and release plank
        self.demagnetize_all()
        self.deploy(9)

        time.sleep(2)

        # Retrieve actuators
        self.fold(4)
        self.fold(6)

    # def init_actuator(self):
    #     self.stepper_step(
    #         self.stepper.top_steps - self.elevator_ticks, self.stepper.speed
    #     )
    #     self.fold_all()
    #     self.stepper_step(
    #         self.stepper.folded_steps - self.elevator_ticks, self.stepper.speed
    #     )

    def ready_to_pickup(self):
        """
        Preparation and magnetization of all servos.
        """
        # Prep and go magnetized
        self.deploy_all_pickup()  # Magnetize
        time.sleep(1)
        self.deploy(8)
        self.go_to_bottom()
        time.sleep(0.001)

    def pick_up(self):
        """
        Catch cans and plank
        """
        # Catch and raise cans and plank
        self.fold(4)
        self.fold(6)
        self.fold(9)
        time.sleep(2)
        self.set_servo_angle(pin=9, angle=200, max_angle=270)  # On serre pour tester
        time.sleep(0.5)

    def ready_to_approach_to_pickup(self):
        self.magnetize_all()
        self.set_stepper_driver_activation_state(13, enable_driver=False)
        self.elevator_ticks = 0
        time.sleep(0.5)
        self.deploy_all_pickup()
        self.set_servo_angle(8, angle=35, max_angle=270)
        self.fold(9)

    def prepare_to_pickup(self):
        self.magnetize_all()
        self.set_servo_angle(8, angle=135, max_angle=270)
        self.deploy(9)

    def pickup(self):
        def _pickup():
            self.deploy(9)
            self.deploy(8)
            time.sleep(0.3)
            self.fold(9)

        self.set_servo_angle(8, angle=135, max_angle=270)
        time.sleep(0.2)
        _pickup()
        time.sleep(0.2)
        _pickup()

    def build(self):
        self.fold(4)
        self.fold(6)
        time.sleep(1.5)
        self.go_to_top()
        time.sleep(1.5)
        self.set_servo_angle(pin=4, angle=160, max_angle=270)
        self.set_servo_angle(pin=6, angle=90, max_angle=270)
        time.sleep(2)
        self.elevator_drop_top()
        time.sleep(1)
        self.deploy(9)
        time.sleep(1)
        self.demagnetize_all()
        time.sleep(1)
        self.fold(4)
        self.fold(6)
        self.set_servo_angle(8, angle=130, max_angle=270)
        time.sleep(0.1)

    def start_position(self):
        self.set_stepper_driver_activation_state(13, enable_driver=False)
        self.elevator_ticks = 0
        self.set_servo_angle(8, angle=35, max_angle=270)
        time.sleep(0.5)
        self.deploy(0)
        self.deploy(2)
        self.fold(4)
        self.fold(6)

    def block_banner(self):
        self.set_stepper_driver_activation_state(13, enable_driver=False)
        self.elevator_ticks = 0
        self.set_servo_angle(8, angle=35, max_angle=270)
        # self.set_servo_angle(0, angle=105, max_angle=270)
        # self.set_servo_angle(2, angle=167, max_angle=270)
        self.set_servo_angle(0, angle=100, max_angle=270)
        self.set_servo_angle(2, angle=171, max_angle=270)

    def deplacement_position(self):
        self.set_stepper_driver_activation_state(13, enable_driver=False)
        self.elevator_ticks = 0
        time.sleep(0.5)
        self.demagnetize_all()
        self.fold(4)
        self.fold(6)
        self.deploy(2)
        self.deploy(0)
        self.set_servo_angle(8, angle=35, max_angle=270)
        self.fold(9)

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
