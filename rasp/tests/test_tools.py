import pytest
from bot.Shapes import Rectangle,Point,OrientedPoint
from bot.tools import *

class TestTools:
    def test_compute_go_to_destination(self):
        
        # y=cst
        a = Rectangle(Point(4,0),Point(0,4))
        point = OrientedPoint(2,-5)
        assert compute_go_to_destination(point,a)==OrientedPoint(2,2)
        print(compute_go_to_destination(point,a,distance_center=2))
        assert OrientedPoint(2,0) == compute_go_to_destination(point,a,distance_center=2)
        # x = cst
        b = Rectangle(Point(3,1),Point(1,3))
        point = OrientedPoint(9,2)