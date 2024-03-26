import time
from controllers import Actuators
servo = True
ultrasonic = False
actuators = Actuators()
if servo:
    time.sleep(1.3)
    actuators.update_servo(5,50)
    time.sleep(1.3)
    actuators.update_servo(5,100)
    time.sleep(1.3)
    actuators.update_servo(5,0)
    time.sleep(1.3)
    actuators.update_servo(5,180)
    time.sleep(1.3)
    actuators.update_servo(5,0)

if ultrasonic:
    actuators.read_ultrasonic(12,14)
    time.sleep(3)
    print(actuators.distances_ultrasonic)