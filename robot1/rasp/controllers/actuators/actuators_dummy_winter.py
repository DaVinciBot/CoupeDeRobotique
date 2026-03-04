from __future__ import annotations

from typing import TYPE_CHECKING, override

from loggerplusplus import log

from a_config_loader import CONFIG
from controllers.actuators.actuators_winter import (
    ActuatorsWinter,
    ArmServo,
    CursorServo,
    RotateServo,
)

if TYPE_CHECKING:
    from loggerplusplus import Logger


class ActuatorsWinterDummy(ActuatorsWinter):
    """Dummy version of ActuatorsWinter that only logs actions."""

    def __init__(
        self,
        logger: Logger,
        serial_number: int = CONFIG.ACTUATOR_TEENSY_SER,
        vid: int = CONFIG.TEENSY_VID,
        pid: int = CONFIG.TEENSY_PID,
        baudrate: int = CONFIG.TEENSY_BAUDRATE,
        *,
        enable_crc: bool = CONFIG.TEENSY_CRC,
    ) -> None:
        super().__init__(
            logger=logger,
            serial_number=serial_number,
            vid=vid,
            pid=pid,
            baudrate=baudrate,
            enable_crc=enable_crc,
            enable_dummy=True,
        )

    def __str__(self) -> str:
        return self.__class__.__name__

    @override
    @log("Actuators")
    def set_servo_angle(
        self,
        pin: int,
        angle: int,
        min_angle: int = 0,
        max_angle: int = 180,
        *,
        detach: bool = False,
        detach_delay: int = 1000,
        use_i2c: bool = False,
    ) -> None:
        """Dummy simulation of servo movement with full validation logic."""
        if not self._check_pin(pin):
            return

        servo = self.servos.get(pin)
        if servo is None:
            self._logger.error(f"[CTRL:ACT:Dummy] No servo configured for pin {pin}")
            return

        if isinstance(servo, ArmServo):
            computed_min = min(servo.retract_angle, servo.extend_angle)
        elif isinstance(servo, RotateServo):
            computed_min = min(servo.retract_angle, servo.rotation_angle)
        elif isinstance(servo, CursorServo):
            computed_min = min(servo.retract_angle, servo.deploy_angle)
        else:
            computed_min = servo.retract_angle

        pin_exceptions: dict[int, int] = {
            6: 90,
        }

        computed_min = pin_exceptions.get(pin, computed_min)

        computed_max = servo.max_angle

        if computed_min <= angle <= computed_max:
            if detach:
                self._logger.info(
                    f"[CTRL:ACT:Dummy] Servo pin {pin} → {angle}degrees "
                    f"(range {computed_min}-{computed_max}) "
                    f"[detach after {detach_delay}ms]",
                )
            else:
                self._logger.info(
                    f"[CTRL:ACT:Dummy] Servo pin {pin} → {angle}degrees "
                    f"(range {computed_min}-{computed_max})",
                )
        else:
            self._logger.error(
                f"[CTRL:ACT:Dummy] Angle {angle}degrees out of range "
                f"[{computed_min},{computed_max}] for pin {pin}",
            )

    @override
    @log("Actuators")
    def stepper_step(
        self,
        steps: int,
        speed: int,
        *,
        disable_driver: bool = False,
    ) -> None:
        self.elevator_ticks += steps
        self._logger.info(
            f"[CTRL:ACT:Dummy] Stepper {steps} steps @ {speed} "
            f"(disable_driver={disable_driver})",
        )
