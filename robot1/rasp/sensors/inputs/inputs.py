"""Input handling for physical sensors such as jack and plug."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from log_manager import LogLogger

if TYPE_CHECKING:
    from loggerplusplus import Logger


CONSECUTIVE_TRIGGER_THRESHOLD = 5
CONSECUTIVE_PLUG_THRESHOLD = 5


class Inputs:
    """Handles input from various sensors."""

    def __init__(
        self,
        pin_jack: int,
        pin_bau: int,
        logger: Logger | None = None,
        *,
        use_dummy_gpio: bool = False,
    ) -> None:
        """Initialize the Inputs class.

        Args:
            pin_jack (int): GPIO pin number for the jack input.
            pin_bau (int): GPIO pin number for the BAU input.
            logger (Logger | None, optional):
                Logger instance for logging. Defaults to None.
            use_dummy_gpio (bool, optional):
                Use simulated pins instead of Raspberry Pi GPIO. Defaults to False.
        """
        self._logger = logger or LogLogger(
            identifier="Inputs",
            follow_logger_manager_rules=True,
        )

        if use_dummy_gpio:
            from gpio.dummy_gpio import PIN  # noqa: PLC0415

            self._logger.info("[SENSOR:Inputs] Dummy GPIO mode initialized")
        else:
            from gpio import PIN  # noqa: PLC0415

        self.jack: PIN = PIN(pin_jack)
        self.jack.setup("input_pullup", reverse_state=True)

        self.bau: PIN = PIN(pin_bau)
        self.bau.setup("input_pullup", reverse_state=False)

    async def wait_for_jack_trigger(self, wait_time: float = 0.001) -> None:
        """Wait for the jack trigger to be activated.

        Args:
            wait_time (float, optional): Time to wait between checks. Defaults to 0.001.
        """
        false_jacks_in_a_row = 0
        self._logger.info("[SENSOR:Jack] Waiting for jack trigger...")
        while false_jacks_in_a_row < CONSECUTIVE_TRIGGER_THRESHOLD:
            if self.jack.safe_digital_read():
                false_jacks_in_a_row = 0
            else:
                false_jacks_in_a_row += 1
            await asyncio.sleep(wait_time)
        self._logger.info("[SENSOR:Jack] Trigger detected - starting match!")

    async def wait_for_jack_plugged(self, wait_time: float = 0.001) -> None:
        """Wait for the jack to be plugged in.

        Args:
            wait_time (float, optional): Time to wait between checks. Defaults to 0.001.
        """
        true_jacks_in_a_row = 0
        self._logger.info("[SENSOR:Jack] Waiting for jack plug...")
        while true_jacks_in_a_row < CONSECUTIVE_PLUG_THRESHOLD:
            if self.jack.safe_digital_read():
                true_jacks_in_a_row += 1
            else:
                true_jacks_in_a_row = 0
            await asyncio.sleep(wait_time)
        self._logger.info("[SENSOR:Jack] Jack plugged in - ready to start!")
