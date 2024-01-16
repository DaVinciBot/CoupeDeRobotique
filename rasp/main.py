import time
from bot import MarsArena, RollingBasis, State, Lidar, Shapes, Actuators
from bot.utils import Utils
from bot.logger import Logger

def add_op(oriented_point : Shapes.OrientedPoint)->bool:  # op stands for oriented point
    if State.check_collisions:
        if MarsArena.enable_go_to(State.points_list[-1],oriented_point):
            State.points_list.append(oriented_point)
            State.index_last_point += 1
            return True
        return False
    else:
        State.points_list.append(oriented_point)
        State.index_last_point += 1
        return True

PLANT_AREA = 0
DROP_ZONE = 1
GARDENER = 2

# call the function corresponding to the given zone
def select_action_at_position(zone : int):
    if zone == PLANT_AREA:
        print("taking plant")
    elif zone == DROP_ZONE:
        print("deposing plant into the drop zone")
    elif zone == GARDENER:
        print("deposing plant into gardener")
    else:
        print(f"zone {zone} isn't taken in charge")

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
    while(State.index_destination_point<State.index_last_point+1 and not State.game_finished): # while there are points left to go through and time is under treshold 
        # is_there an obstacle in front of the robot ? 
        # Run authorize ?
        try:
            State.is_obstacle = lidar.is_obstacle_infront()
        except Exception as e:
            print(e)
        State.run_auth : bool = not State.is_obstacle
        
        if State.test:
            print(f"action_finished : {rolling_basis.action_finished}")

        # Go to the next point. If an obstacle is detected stop the robot
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
                rolling_basis.Go_To(arena.home.center)

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

