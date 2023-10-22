#from classes.intercom_tools import intercom, send_coords, update_target_point
from classes.tools import get_current_date
from classes.lidar import Lidar
from classes.pinInteract import PIN
from classes.arena import RectangleArena
from classes.point import point
import Libraries.Teensy_Com as teensy
import math

# Get Lidar
lidar = Lidar(-math.pi, math.pi)

# Get On Off Pin
on_off_pin = PIN(19)
on_off_pin.setup("OUTPUT")

# Get Tirette Pin
tirette_pin = PIN(26)
tirette_pin.setup("input_pulldown", reverse_state=True)

# Led States
led_lidar = PIN(13)
led_lidar.setup("OUTPUT")
led_start = PIN(6)
led_start.setup("OUTPUT")
led_time = PIN(5)
led_time.setup("OUTPUT")

# Print variables
last_print = get_current_date()["date_timespamp"]

# Init All pins states
on_off_pin.digitalWrite(False)
led_start.digitalWrite(False)
led_lidar.digitalWrite(False)
led_time.digitalWrite(False)

# Return to start timing
start_time = 0
time_to_return_to_home = 80

# Get arena
arena : RectangleArena = RectangleArena()

# Get Rolling_basis
rolling_basis = teensy.Rolling_basis()

def select_action_at_position(zone : int):
    if zone == 0:
        print("taking plant")
    elif zone == 1:
        print("deposing plant into depot zone")
    elif zone == 2:
        print("deposing plant into gardener")
    else:
        print(f"zone {zone} isn't take in cahrge")

# 0 = pots_area
# 1 = depot_zone
# 2 = gardener 

actions_list = [(point,0), (point,1)] 

while True:
    
    # is_there an obstacle in front of the robot ? 
    is_obstacle : bool = True # for safety in case of lidar dysfunction
    try:
        is_obstacle = lidar.is_obstacle_infront()
        led_lidar.digitalWrite(True)
    except:
        led_lidar.digitalWrite(False)

    # Run authorize ?
    run_auth : bool = not is_obstacle and tirette_pin.digitalRead()

    if not run_auth:
        rolling_basis.Keep_Current_Position()

    # Check if there is enought time
    if tirette_pin.digitalRead() and start_time == 0:
        start_time = get_current_date()["date_timespamp"]

    # if time exceeds time_to_return_home then go to the starting posistion
    if start_time !=0 and get_current_date()["date_timespamp"] - start_time > time_to_return_to_home:
        rolling_basis.Go_To(arena.starting_position)

    # A print every 500 ms
    if (get_current_date()["date_timespamp"] - last_print) > 0.5:
        last_print = get_current_date()["date_timespamp"]

        print(f"#-- Lidar --#\n"
              f"is_obstacle: {is_obstacle}\n\n"
              f"#-- Pins --#\n"
              f"State ON / OFF: {on_off_pin.digitalRead()}\n"
              f"State Tirette: {tirette_pin.digitalRead()}\n"
              f"#-- Timer (return to home) --#\n"
              f"Timer to return: {time_to_return_to_home}\n"
              f"Current time: {round(get_current_date()['date_timespamp'] - start_time)}\n"
              f"#-- Run --#\n"
              f"Auth state: {run_auth}\n")

