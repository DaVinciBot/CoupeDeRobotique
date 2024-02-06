from bot.Com import Actuators
import time

servo = True
ultrasonic = False
actuators = Actuators()
if servo:
    time.sleep(1.3)
    actuators.servo_go_to(5,50)
    time.sleep(1.3)
    actuators.servo_go_to(5,100)
    time.sleep(1.3)
    actuators.servo_go_to(5,0)
    time.sleep(1.3)
    actuators.servo_go_to(5,180)
    time.sleep(1.3)
    actuators.servo_go_to(5,0)

if ultrasonic:
    actuators.read_ultrasonic(11,17)
    time.sleep(3)
    print(actuators.distances_ultrasonic)