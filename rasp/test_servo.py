#import Libraries.Teensy_Com as teensy
from classes.tools import*
from classes.constants import*
from Libraries.Teensy_Com import Actuators
import time
from log.log import log_start

state.start_time = get_current_date()["date_timespamp"]
log_start()

actuators = Actuators(crc=False)
actuators.servo_go_to(pin=SERVO1_PIN,angle=90)
delay = 1
time.sleep(delay)
actuators.servo_go_to(pin=SERVO1_PIN,angle=10)
time.sleep(delay)
actuators.servo_go_to(pin=SERVO1_PIN,angle=40)
time.sleep(delay)
actuators.servo_go_to(pin=SERVO1_PIN,angle=90)
time.sleep(delay)
actuators.servo_go_to(pin=SERVO2_PIN,angle=180)
time.sleep(delay)
actuators.servo_go_to(pin=SERVO2_PIN,angle=10)
time.sleep(delay)
actuators.servo_go_to(pin=SERVO2_PIN,angle=60)
time.sleep(delay)
actuators.servo_go_to(pin=SERVO3_PIN,angle=180)
time.sleep(delay)
actuators.servo_go_to(pin=SERVO3_PIN,angle=10)
time.sleep(delay)
actuators.servo_go_to(pin=SERVO3_PIN,angle=60)
print("finished demo")

