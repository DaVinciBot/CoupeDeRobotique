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
        a = Point(2,2)
        b = OrientedPoint(2,2)
        p1 = Point(0,0)
        p2 = Point(0,4)
        p3 = Point(4,0)
        p4 = Point(4,4)
        q1 = Point(1,1)
        q2 = Point(1,3)
        q3 = Point(3,1)
        q4 = Point(3,3)
        q5 = OrientedPoint(3,3)
        assert isinstance(compute_go_to_destination(a,a),OrientedPoint)
        assert isinstance(compute_go_to_destination(a,b),OrientedPoint)
        assert compute_go_to_destination(p1,a,distance=2**(1/2),nb_digits=1) == q1
        assert compute_go_to_destination(p1,a,distance=2**(1/2),nb_digits=1, closer=False) == q4
        assert compute_go_to_destination(p2,a,distance=2**(1/2),nb_digits=1) == q2
        assert compute_go_to_destination(p2,a,distance=2**(1/2),nb_digits=1, closer=False) == q3
        assert compute_go_to_destination(p3,a,distance=2**(1/2),nb_digits=1) == q3
        assert compute_go_to_destination(p3,a,distance=2**(1/2),nb_digits=1, closer=False) == q2
        assert compute_go_to_destination(p4,a,distance=2**(1/2),nb_digits=1) == q4
        assert compute_go_to_destination(p4,a,distance=2**(1/2),nb_digits=1, closer=False) == q1
        assert compute_go_to_destination(q5,a,distance=2**(1/2),nb_digits=1, closer=False) == q1
        assert compute_go_to_destination(q5,b,distance=2**(1/2),nb_digits=1, closer=False) == q1
        
        
        
