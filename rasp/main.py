import time
from bot import MarsArena, RollingBasis, State, Lidar, Actuators
from bot.Shapes import OrientedPoint
from bot.tools import compute_go_to_destination
from bot.utils import Utils
from bot.logger import Logger

def go_to(__object : object,  distance = 0, nb_digits : int = 2, closer = True)->bool:
    destination_point = compute_go_to_destination(rolling_basis.odometrie,__object,distance,nb_digits=nb_digits,closer=True)
    if isinstance(destination_point,OrientedPoint):
        if State.go_to_verif:
            if arena.enable_go_to():
                rolling_basis.Go_To(destination_point)
                return True
            return False
        rolling_basis.Go_To(destination_point)
        return True
    return False
    
# PLANT_AREA = 0
# DROP_ZONE = 1
# GARDENER = 2

# call the function corresponding to the given zone
# def select_action_at_position(zone : int):
#     if zone == PLANT_AREA:
#         print("taking plant")
#     elif zone == DROP_ZONE:
#         print("deposing plant into the drop zone")
#     elif zone == GARDENER:
#         print("deposing plant into gardener")
#     else:
#         print(f"zone {zone} isn't taken in charge")
   
lidar = Lidar()
arena = MarsArena(1)
l = Logger()
rolling_basis = RollingBasis()
actuators = Actuators()
last_print = Utils.get_current_date()["date_timespamp"]

if State.test:
    rolling_basis.Set_Home()
    print(rolling_basis.odometrie)
    time.sleep(0.01)
    
    
State.start_time = Utils.get_current_date()["date_timespamp"]
    
while True:
    while(State.index_destination_point<State.index_last_point+1 and not State.game_finished):
        if State.activate_lidar:
            try:
                State.is_obstacle = lidar.is_obstacle_infront()
            except Exception as e:
                print(e)
        else: State.is_obstacle = False 
        State.run_auth : bool = not State.is_obstacle # usefull to add conditions if necessary 

        if not State.run_auth:
            if State.is_moving :
                rolling_basis.Keep_Current_Position()
                State.is_moving = False
        if State.run_auth and not State.is_moving:
            rolling_basis.Go_To(State.points_list[State.index_destination_point][0])
            State.is_moving = True
        if rolling_basis.action_finished:
            print(f"arrived at {State.points_list[State.index_destination_point][0]}")
            State.index_destination_point += 1
            State.is_moving = False

        # if time exceeds time_to_return_home then go to the starting posistion
        if State.start_time !=0 and Utils.get_current_date()["date_timespamp"] - State.start_time > State.time_to_return_to_home:
            if not State.test:
                if not go_to(arena.home):
                    State.points_list.append(arena.home.center) # we must use points_list to keep lidar anticollison system
                    rolling_basis.Go_To(State.points_list[-1])

        # A print every 500 ms if activated
        if State.activate_print and (Utils.get_current_date()["date_timespamp"] - last_print) > 0.5:
            last_print = Utils.get_current_date()["date_timespamp"]

            print
            (
                f"#-- Lidar --#\n"
                f"is_obstacle: {State.is_obstacle}\n\n"
                f"#-- Pins --#\n"
                #f"State Tirette: {tirette_pin.digitalRead()}\n"
                f"#-- Timer (return to home) --#\n"
                f"Timer to return: {State.time_to_return_to_home}\n"
                f"Current time: {round(Utils.get_current_date()['date_timespamp'] - State.start_time)}\n"
                f"#-- Run --#\n"
                f"Auth State: {State.run_auth}\n"
            )

