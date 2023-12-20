import time
from classes.tools import *
from environment.geometric_shapes.oriented_point import OrientedPoint
from log.log import *

state.start_time = get_current_date()["date_timespamp"]
time.sleep(2)
log_start()
@log_call("random")
def add(a,b,c=OrientedPoint(1,1,1)):
    return a+b+c

add(OrientedPoint(1,2,3),OrientedPoint(1,1,1))
add(OrientedPoint(1,2,3),OrientedPoint(1,1,1))

