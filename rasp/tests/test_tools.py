import pytest
from bot.Shapes import Rectangle,Point,OrientedPoint
from bot.tools import *

class TestCompute_go_to:
    def test_x_cst(self):
        r = Rectangle(Point(4,0),Point(0,4))
        c = Circle(Point(2,2),3)
        p1 = OrientedPoint(2,-5)
        p2 = OrientedPoint(2,2)
        p3 = OrientedPoint(2,0)
        p4 = OrientedPoint(2,12)
        assert p2 == compute_go_to_destination(p1,r) # point to rectangle
        assert p3 == compute_go_to_destination(p1,r,distance=2) # point to rectangle
        assert p2 == compute_go_to_destination(p1,p2) # point to point
        assert p3 == compute_go_to_destination(p1,p2,distance=2) # point to point
        assert p2 == compute_go_to_destination(p1,c) # point to circle
        assert p3 == compute_go_to_destination(p1,c,distance=2) # point to circle
        print(compute_go_to_destination(p4,r,distance=3))
        assert Point(2,5) == compute_go_to_destination(p4,c,distance=3) # from the 
        
    def test_y_cst(self):
        r = Rectangle(Point(3,1),Point(1,3))
        c = Circle(Point(2,2),3)
        p1 = OrientedPoint(9,2)
        p2 = OrientedPoint(2,2)
        p3 = OrientedPoint(5,2)
        p4 = OrientedPoint(0,2)
        p5 = Point(2,2)
        assert p2 == compute_go_to_destination(p1,r) # point to rectangle
        assert p3 == compute_go_to_destination(p1,r,distance=3) # point to rectangle
        assert p2 == compute_go_to_destination(p1,p2) # point to point
        assert p3 == compute_go_to_destination(p1,p2,distance=3) # point to point
        assert p3 == compute_go_to_destination(p1,p5,distance=3) # point to point
        assert p2 == compute_go_to_destination(p1,c) # point to circle
        assert p3 == compute_go_to_destination(p1,c,distance=3) # point to circle
        assert Point(1,2) == compute_go_to_destination(p4,r,distance=1) # from the top 
        
    def test_default(self):
        r = Rectangle(Point(7,1),Point(5,3))
        c = Circle(Point(6,2),3)
        p1 = OrientedPoint(1,7)
        p2 = OrientedPoint(6,2)
        p3 = OrientedPoint(5,3)
        assert p2 == compute_go_to_destination(p1,p2)
        print(compute_go_to_destination(p1,p2,distance=3*2**(1/2),nb_digits=2))
        assert p3 == compute_go_to_destination(p1,p2,distance=3*2**(1/2),nb_digits=2)
        
        
        
