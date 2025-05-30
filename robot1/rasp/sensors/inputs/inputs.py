from GPIO import PIN

from loggerplusplus import Logger
import asyncio


class Inputs:
    def __init__(self, pin_jack: int, pin_bau: int, logger: Logger | None = None):
        self.logger = logger or Logger(
            identifier="Inputs", follow_logger_manager_rules=True
        )

        self.jack: PIN = PIN(pin_jack)
        self.jack.setup("input_pullup", reverse_state=True)

        self.bau: PIN = PIN(pin_bau)
        self.bau.setup("input_pullup", reverse_state=False)

    async def wait_for_jack_trigger(self, wait_time: float = 0.001):
        false_jacks_in_a_row = 0
        self.logger.info(f"Wait jack trigger...")
        while false_jacks_in_a_row < 5:
            if self.jack.safe_digital_read():
                false_jacks_in_a_row = 0
            else:
                false_jacks_in_a_row += 1
            self.logger.debug(
                f"Jack trigger signal seems to be detected: {false_jacks_in_a_row}."
            )
            await asyncio.sleep(wait_time)
        self.logger.info(f"Jack trigger detected !")

    async def wait_for_jack_plugged(self, wait_time: float = 0.001):
        true_jacks_in_a_row = 0
        self.logger.info("Waiting for jack to be plugged in…")
        while true_jacks_in_a_row < 5:
            if self.jack.safe_digital_read():
                true_jacks_in_a_row += 1
            else:
                true_jacks_in_a_row = 0
            self.logger.debug(f"Jack plug presence count: {true_jacks_in_a_row}")
            await asyncio.sleep(wait_time)
        self.logger.info("Jack plugged in!")
