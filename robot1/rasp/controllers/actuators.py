from config_loader import CONFIG
from loggerplusplus import Logger, log

# Import from common
from teensy_comms import Teensy
import asyncio
import struct


class Actuators(Teensy):
    def __init__(
        self,
        logger: Logger,
        ser=CONFIG.ACTUATOR_TEENSY_SER,
        vid=CONFIG.TEENSY_VID,
        pid=CONFIG.TEENSY_PID,
        crc=CONFIG.TEENSY_CRC,
        baudrate=CONFIG.TEENSY_BAUDRATE,
        dummy: bool = CONFIG.TEENSY_DUMMY,
    ):
        super().__init__(
            logger, ser=ser, vid=vid, pid=pid, baudrate=baudrate, crc=crc, dummy=dummy
        )
        # Admit that default elevator position is at the bottom
        self.elevator_ticks = 0

        self.is_lcd_declared = False

    class Command:  # values must correspond to the one defined on the teensy
        Update_servo = b"\x01"
        StepperStep = b"\x02"
        Update_servo_detach = b"\x03"
        Lcd_init = b"\x04"
        Lcd_print = b"\x05"

    def __str__(self) -> str:
        return self.__class__.__name__

    #########################
    # User facing functions #
    #########################

    @log("Actuators")
    async def stepper_step(self, steps: int, speed: int) -> None:
        """
        Moves the stepper motor a specified number of steps. Note that the number of motor pin can change depending on the motor.
        2 or 5 pins are common.

        Args:
            steps (int): The number of steps to move the motor.
            pin_dir (int): The pin number of the direction pin.
            pin_step (int): The pin number of the step pin.

        Returns:
            None
        """
        # Update elevator theorical steps
        self.elevator_ticks += steps

        # WARNING: pin_driver is also defined in the C++ code, because it needs to receive a HIGH from the beginning or it will start heating up
        pin_dir = 13
        pin_step = 14
        pin_driver = 15

        msg = (
            self.Command.StepperStep
            + struct.pack("<i", abs(steps))
            + struct.pack("<?", (steps >= 0))
            + struct.pack("<i", speed)
            + struct.pack("<B", pin_dir)
            + struct.pack("<B", pin_step)
            + struct.pack("<B", pin_driver)
            # https://docs.python.org/3/library/struct.html#format-characters
        )
        self.send_bytes(msg)

    @log("Actuators")
    async def update_servo(
        self,
        pin: int,
        angle: int,
        min_angle: int = 0,
        max_angle: int = 180,
        detach=False,
        # If True, the servo will detach after setting the angle, DO NOT USE DETACH = TRUE AND DETACH = FALSE ON THE SAME SERVO
        detach_delay=1000,
    ) -> None:
        """Set the angle of the servo at the given pin.

        Args:
            pin (int): The pin number of the servo.
            angle (int): The angle to set for the servo.
            min_angle (int, optional): The minimum angle allowed for the servo. Defaults to 0.
            max_angle (int, optional): The maximum angle allowed for the servo. Defaults to 180.
            detach (bool, optional): Whether to detach the servo after setting the angle. Defaults to False.
            detach_delay (int, optional): The time in milliseconds to keep the servo detached. Defaults to 1000.
        """
        if angle >= min_angle and angle <= max_angle:
            if detach:
                msg = (
                    self.Command.Update_servo_detach
                    + struct.pack("<B", pin)
                    + struct.pack("<B", angle)
                    + struct.pack("<i", detach_delay)
                )
                self.send_bytes(msg)
            else:
                if self.gpio_manager.is_available_gpio(pin):
                    self.gpio_manager.add_gpio(
                        pin, self.gpio_manager.TypeActuator.SERVO
                    )
                    self.logger.log(f"Pin {pin} added as a servo pin", LogLevels.INFO)
                elif not self.gpio_manager.is_valid_gpio(
                    pin, self.gpio_manager.TypeActuator.SERVO
                ):
                    self.logger.log(
                        f"Pin {pin} is not a valid servo pin because it is registered as a {str(self.gpio_manager.get_type_gpio())}",
                        LogLevels.ERROR,
                    )
                else:
                    msg = (
                        self.Command.Update_servo
                        + struct.pack("<B", pin)
                        + struct.pack("<B", angle)
                    )
                    self.send_bytes(msg)
            # https://docs.python.org/3/library/struct.html#format-characters

        else:
            self.logger.error(
                f"You tried to write {angle}° on pin {pin}, whereas the angle must be between {min_angle} and {max_angle}°"
            )

    @log("Actuators")
    async def lcd_init(self, adress=0x27, nb_col: int = 16, nb_line: int = 2) -> None:
        """
        Initializes the LCD display.

        Args:
            adress (int, optional): The I2C address of the LCD display. Defaults to 0x27.
            nb_col (int, optional): The number of columns in the LCD display. Defaults to 16.
            nb_line (int, optional): The number of lines in the LCD display. Defaults to 2.

        Returns:
            None
        """
        msg_ = (
            self.Command.Lcd_init
            + struct.pack("<B", adress)
            + struct.pack("<B", nb_col)
            + struct.pack("<B", nb_line)
        )
        self.send_bytes(msg_)

    @log("Actuators")
    async def lcd_print(
        self, msg: str, nb_col: int = 16, nb_line: int = 2, adress=0x27
    ) -> None:
        """Display a message on the LCD screen.

        Args:
            msg (str): The message to display.
        """
        msg = msg.encode("ascii", errors="ignore")  # Ignorer les caractères non-ASCII
        if len(msg) > nb_col * nb_line:
            self.logger.warning(
                f"Message too long for the LCD screen, {len(msg)} characters, max is {nb_col * nb_line}. Truncated.",
            )
            msg = msg[: nb_col * nb_line]
        if not self.is_lcd_declared:
            await self.lcd_init(nb_col=nb_col, nb_line=nb_line, adress=adress)
            await asyncio.sleep(CONFIG.MINIMUM_DELAY)
        msg_ = self.Command.Lcd_print + struct.pack(f"<{len(msg) + 1}s", msg + b"\0")
        self.send_bytes(msg_)
