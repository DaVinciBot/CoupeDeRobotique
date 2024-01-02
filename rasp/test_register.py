import time
from classes.tools import *
from environment.geometric_shapes.oriented_point import OrientedPoint
from environment.arenas.arena import Arena
from log.log import *

o = op(1,2)
ar = Arena()
state.start_time = get_current_date()["date_timespamp"]
time.sleep(2)
log_start()
@log_call("random")
def add(a,b,c=OrientedPoint(1,1,1)):
    return a+b+c
ar.is_in(op(5,9))
ar.is_in(op(-1,2))

add(OrientedPoint(1,2,3),OrientedPoint(1,1,1),OrientedPoint(1,2,3))
add(OrientedPoint(1,2,3),OrientedPoint(1,1,1))

