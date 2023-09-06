import RPi.GPIO as GPIO

class PIN:
    def __init__(self, pin):
        self.pin = pin

    def setup(self, mode, reverse_state=False):
        mode = mode.lower()
        self.mode = mode

        self.reverse_state = reverse_state

        GPIO.setmode(GPIO.BCM)

        if mode == "output":
            GPIO.setup(self.pin, GPIO.OUT)
        elif mode == "input":
            GPIO.setup(self.pin, GPIO.IN)
        elif mode == "input_pullup":
            GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        elif mode == "input_pulldown":
            GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    def digitalWrite(self, state: bool):
        GPIO.output(self.pin, self.__correct_state(state))

    def digitalRead(self) -> bool:
        return self.__correct_state(GPIO.input(self.pin))

    def __correct_state(self, state: bool) -> bool:
        return not state if self.reverse_state else state
