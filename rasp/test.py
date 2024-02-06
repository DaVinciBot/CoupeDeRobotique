from bot.Shapes import Rectangle, OrientedPoint, Point
from bot.tools import *
r = Rectangle(Point(3,1),Point(1,3))
c = Circle(Point(2,2),3)
p1 = OrientedPoint(9,2)
p2 = OrientedPoint(2,2)
p3 = OrientedPoint(5,2)
print(compute_go_to_destination(p1,r,distance=3)) # point to rectangle)