from bot.Shapes import Rectangle, OrientedPoint, Point
from bot.tools import *
import time
from bot import MarsArena, RollingBasis, State, Lidar, Actuators
from bot.tools import compute_go_to_destination, drop_plant, drop_plant_gardener, take_plant, no_action
from bot.Utils import Utils
from bot.Logger import Logger

def go_to(__object : object,  distance = 0, nb_digits : int = 2, closer = True, action_at = no_action)->bool:
    destination_point = compute_go_to_destination(rolling_basis.odometrie,__object,distance,nb_digits=nb_digits,closer=closer)
     # forbidden area souldn't be crossed because of its position
    if isinstance(destination_point,OrientedPoint):
        if State.go_to_verif:
            # forbidden area souldn't be crossed because of its position
            if arena.enable_go_to(rolling_basis.odometrie,destination_point):
                rolling_basis.Go_ToPoint(destination_point, action_at = action_at)
                return True
            return False
        rolling_basis.Go_ToPoint(destination_point, action_at = action_at)
        return True
    return False

def plant_stage():
    # utile ou non de déclancher un crono pour skipp en cas de problème 
    while True:
        if State.action_selector == 0 and go_to(arena.closest_plant_zones()[0],take_plant):
            State.action_selector == 1 # wait
        elif State.action_selector == 2 and go_to(arena.closest_drop_zone()[0],drop_plant):
            State.action_selector == 1 # wait
    

lidar = Lidar()
arena = MarsArena(0)
l = Logger()
rolling_basis = RollingBasis()

rolling_basis.Reset_Odo()
go_to(arena.drop_zones[0])