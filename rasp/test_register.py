from classes.tools import *
from environment.geometric_shapes.oriented_point import OrientedPoint

data.start_time = get_current_date()["date_timespamp"]
time.sleep(2)

@register_call("random")
def add(a,b):
    return a+b

@register_call("radom")
def TaperEliza(nb = 3):
    for i in range(nb):
        print("cheh")



add(OrientedPoint(1,2,3),OrientedPoint(1,1,1))
time.sleep(2)
TaperEliza()
save_registered_ations()
print(data.registered_actions)


