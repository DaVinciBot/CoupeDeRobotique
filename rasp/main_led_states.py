#from classes.intercom_tools import intercom, send_coords, update_target_point
from classes.tools import get_current_date
from classes.lidar import Lidar
from classes.pinInteract import PIN
import math
from time import sleep

# Get Lidar
lidar = Lidar(-math.pi, math.pi)

# Get On Off Pin
on_off_pin = PIN(19)
on_off_pin.setup("OUTPUT")

# Get State Pins
ready_pin = PIN(21)
lidar_pin = PIN(20)
tirette_led_pin = PIN(16)
detection_pin = PIN(12)
#auth_to_move_pin = PIN(13)
time_to_return_to_home = PIN(6)

ready_pin.setup("OUTPUT")
lidar_pin.setup("OUTPUT")
tirette_led_pin.setup("OUTPUT")
detection_pin.setup("OUTPUT")
#auth_to_move_pin.setup("OUTPUT")
time_to_return_to_home.setup("OUTPUT")

# Get Tirette Pin
tirette_pin = PIN(26)
tirette_pin.setup("input_pulldown", reverse_state=True)

# Deguisement
deguisement_pin = PIN(13)
deguisement_pin.setup("OUTPUT")

# Print variables
last_print = get_current_date()["date_timespamp"]

# Init All pins states
on_off_pin.digitalWrite(False)
deguisement_pin.digitalWrite(False)
ready_pin.digitalWrite(False)

for _ in range(10):  
    ready_pin.digitalWrite(True)
    sleep(0.2)
    ready_pin.digitalWrite(False)
    sleep(0.2)

lidar_pin.digitalWrite(False)
tirette_led_pin.digitalWrite(False)
detection_pin.digitalWrite(False)
#auth_to_move_pin.digitalWrite(False)
time_to_return_to_home.digitalWrite(False)

# Return to start timing
start_time = 0
delay_to_return_to_home = 70
end_game = 95

while True:
    # Raspi is running 
    ready_pin.digitalWrite(True)

    # Get Nearest point
    nearest_point = 0
    try:
        nearest_point = lidar.safe_get_nearest_point()
        lidar_pin.digitalWrite(True)
    except: 
        lidar_pin.digitalWrite(False)

    # Tirette
    tirette_state = tirette_pin.digitalRead()
    tirette_led_pin.digitalWrite(not tirette_state)
    if not tirette_state:
        start_time = 0

    # Run authorize ?
    run_auth = nearest_point >= 0.4 and tirette_state
    #auth_to_move_pin.digitalWrite(run_auth)
    detection_pin.digitalWrite(not run_auth and tirette_state)

    # Supervize Teensy
    on_off_pin.digitalWrite(run_auth)

    # Check if there is enought time
    if tirette_pin.digitalRead() and start_time == 0:
        start_time = get_current_date()["date_timespamp"]

    # Time to return to home
    time_to_return_to_home.digitalWrite(
        get_current_date()["date_timespamp"] -
        start_time > delay_to_return_to_home and start_time != 0
    )

    # End of the game
    deguisement_pin.digitalWrite(
        get_current_date()["date_timespamp"] - 
        start_time > end_game and start_time != 0
    )

    # A print every 500 ms
    if (get_current_date()["date_timespamp"] - last_print) > 0.5:
        last_print = get_current_date()["date_timespamp"]

        print(f"#-- Lidar --#\n"
              f"Distance: {nearest_point}\n\n"
              f"#-- Pins --#\n"
              f"State ON / OFF: {on_off_pin.digitalRead()}\n"
              f"State Tirette: {tirette_pin.digitalRead()}\n"
              f"#-- Timer (return to home) --#\n"
              f"Current time: {round(get_current_date()['date_timespamp'] - start_time)}\n"
              f"#-- Run --#\n"
              f"Auth state: {run_auth}\n")

