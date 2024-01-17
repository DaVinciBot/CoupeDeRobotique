from bot.Com import Actuators
import time

servo = False
ultrasonic = True
actuators = Actuators(crc=False)
if servo:
    time.sleep(1.3)
    actuators.servo_go_to(5,0)
    time.sleep(1.3)
    actuators.servo_go_to(5,100)
    time.sleep(1.3)
    actuators.servo_go_to(5,0)
    time.sleep(1.3)
    actuators.servo_go_to(5,180)

if ultrasonic:
    actuators.read_ultrasonic(12,14)
    time.sleep(3)
    print(actuators.distances_ultrasonic)