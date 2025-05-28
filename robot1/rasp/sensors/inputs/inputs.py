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

    async def wait_for_jack_trigger(self, wait_time: float = 0.1):
        false_jacks_in_a_row = 0
        while false_jacks_in_a_row < 5:
            if self.jack.safe_digital_read():
                false_jacks_in_a_row = 0
                self.logger.info(f"Jack state: {self.jack.digital_read()}")
            else:
                false_jacks_in_a_row += 1
                self.logger.info(f"Jack state: {self.jack.digital_read()}")
            await asyncio.sleep(wait_time)


