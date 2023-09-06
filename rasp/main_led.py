#from classes.intercom_tools import intercom, send_coords, update_target_point
from classes.tools import get_current_date
from classes.lidar import Lidar
from classes.pinInteract import PIN
import math

# Get Lidar
lidar = Lidar(-math.pi, math.pi)

# Get On Off Pin
on_off_pin = PIN(19)
on_off_pin.setup("OUTPUT")

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

# Return to start timing
start_time = 0
time_to_return_to_home = 80
end_game = 100

while True:
    # Get Nearest point
    nearest_point = 0
    try:
        nearest_point = lidar.safe_get_nearest_point()
    except:pass

    # Run authorize ?
    run_auth = nearest_point >= 0.4 and tirette_pin.digitalRead()

    # Supervize Teensy
    on_off_pin.digitalWrite(run_auth)

    # Check if there is enought time
    if tirette_pin.digitalRead() and start_time == 0:
        start_time = get_current_date()["date_timespamp"]

    # End of the game
    if get_current_date()["date_timespamp"] - start_time > end_game and start_time != 0:
        deguisement_pin.digitalWrite(1)

    # A print every 500 ms
    if (get_current_date()["date_timespamp"] - last_print) > 0.5:
        last_print = get_current_date()["date_timespamp"]

        print(f"#-- Lidar --#\n"
              f"Distance: {nearest_point}\n\n"
              f"#-- Pins --#\n"
              f"State ON / OFF: {on_off_pin.digitalRead()}\n"
              f"State Tirette: {tirette_pin.digitalRead()}\n"
              f"#-- Timer (return to home) --#\n"
              f"Timer to return: {time_to_return_to_home}\n"
              f"Current time: {round(get_current_date()['date_timespamp'] - start_time)}\n"
              f"#-- Run --#\n"
              f"Auth state: {run_auth}\n")

