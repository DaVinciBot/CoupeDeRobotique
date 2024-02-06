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
        
class TestClosest_zone:
    def test_distance(self):
        zones ={
            0:(Rectangle(Point(45, 0), Point(0, 45)),False),  # 0 - Blue (Possible forbidden area)
            1:(Rectangle(Point(122.5, 0), Point(77.5, 45)),False),  # 1 - Yellow
            2:(Rectangle(Point(200, 0), Point(155, 45)),False),  # 2 - Blue
            3:(Rectangle(Point(45, 255), Point(0, 300)),False),  # 3 - Yellow (Possible forbidden area)
            4:(Rectangle(Point(122, 255), Point(77.5, 300)),False),  # 4 - Blue
            5:(Rectangle(Point(200, 255), Point(155, 300)),False)  # 5 - Yellow
        }
        drop_zones = [
            (Rectangle(Point(45, 0), Point(0, 45)),False),  # 0 - Blue (Possible forbidden area)
            (Rectangle(Point(122.5, 0), Point(77.5, 45)),False),  # 1 - Yellow
            (Rectangle(Point(200, 0), Point(155, 45)),False),  # 2 - Blue
            (Rectangle(Point(45, 255), Point(0, 300)),False),  # 3 - Yellow (Possible forbidden area)
            (Rectangle(Point(122, 255), Point(77.5, 300)),False),  # 4 - Blue
            (Rectangle(Point(200, 255), Point(155, 300)),False)  # 5 - Yellow
        ]
        
        p1 = Point(0,0)
        p2 = Point(99,120)
        p3 = Point(160,5)
        
        x1 = closest_zone(drop_zones,p1,False,False)
        r1 = [zones[0],zones[1],zones[2],zones[3],zones[4],zones[5]]
        x2 = closest_zone(drop_zones,p2,False,False)
        r2 = [zones[1],zones[0],zones[2],zones[4],zones[3],zones[5]]
        x3 = closest_zone(drop_zones,p3,False,False)
        r3 = [zones[2],zones[1],zones[0],zones[5],zones[4],zones[3]]
        
        results = [x1,x2,x3]
        responses = [r1,r2,r3]
        for j in range(len(results)):
            for i in range(len(zones)):
                assert results[j][i][0]==responses[j][i][0]
                
    def test_exlude(self):
        zones ={
            0:(Rectangle(Point(45, 0), Point(0, 45)),False),  # 0 - Blue (Possible forbidden area)
            1:(Rectangle(Point(122.5, 0), Point(77.5, 45)),False),  # 1 - Yellow
            2:(Rectangle(Point(200, 0), Point(155, 45)),False),  # 2 - Blue
            3:(Rectangle(Point(45, 255), Point(0, 300)),False),  # 3 - Yellow (Possible forbidden area)
            4:(Rectangle(Point(122, 255), Point(77.5, 300)),False),  # 4 - Blue
            5:(Rectangle(Point(200, 255), Point(155, 300)),False)  # 5 - Yellow
        }
        drop_zones = [
            (Rectangle(Point(45, 0), Point(0, 45)),True),  # 0 - Blue (Possible forbidden area)
            (Rectangle(Point(122.5, 0), Point(77.5, 45)),False),  # 1 - Yellow
            (Rectangle(Point(200, 0), Point(155, 45)),False),  # 2 - Blue
            (Rectangle(Point(45, 255), Point(0, 300)),False),  # 3 - Yellow (Possible forbidden area)
            (Rectangle(Point(122, 255), Point(77.5, 300)),True),  # 4 - Blue
            (Rectangle(Point(200, 255), Point(155, 300)),False)  # 5 - Yellow
        ]
        
        p1 = Point(0,0)
        p2 = Point(99,120)
        p3 = Point(160,5)
        p4 = Point(199,299)
        
        x1 = closest_zone(drop_zones,p1,False,True,basic = False)
        r1 = [zones[1],zones[2],zones[3],zones[5], zones[0],zones[4]]
        x2 = closest_zone(drop_zones,p2,False,True,basic = False)
        r2 = [zones[1],zones[2],zones[3],zones[5],zones[0],zones[4]]
        x3 = closest_zone(drop_zones,p3,False,True,basic = False)
        r3 = [zones[2],zones[1],zones[5],zones[3],zones[0],zones[4]]
        x4 = closest_zone(drop_zones,p4,False,True,basic = False)
        r4 = [zones[5],zones[3],zones[2],zones[1],zones[4],zones[0]]
        x5 = closest_zone(drop_zones,p1,False,True,basic = True)
        r5 = [zones[0],zones[4],zones[1],zones[2],zones[3],zones[5]]
        x6 = closest_zone(drop_zones,p1,True,False,basic = False,color = "blue")
        r6 = [zones[0],zones[2],zones[4]]
        x7 = closest_zone(drop_zones,p1,True,False,basic = False,color = "yellow")
        r7 = [zones[1],zones[3],zones[5]]
        x8 = closest_zone(drop_zones,p1,True,True,basic = False,color = "blue")
        r8 = [zones[2],zones[0],zones[4]]
        
        results = [x1,x2,x3,x4,x5,x6,x7,x8]
        responses = [r1,r2,r3,r4,r5,r6,r7,r8]
        for j in range(len(results)):
            for i in range(len(results[j])):
                assert results[j][i][0]==responses[j][i][0]
        
        
