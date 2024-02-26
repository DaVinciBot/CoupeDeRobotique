
# works with the py -m pytest discover commands launched from rasp
from bot.Shapes import Point, Rectangle, OrientedPoint


class TestPoint:
    def test_add(self):
        p2 = Point(12, 3)
        p1 = Point(-2, 2.5)
        p3 = Point(10, 5.5)
        assert p1 + p2 == p3

    def test_sub(self):
        p1 = Point(12, 3)
        p2 = Point(-2, 2.5)
        p3 = Point(14, 0.5)
        assert p1 - p2 == p3

    def test_str(self):
        p1 = Point(12, 3)
        assert p1.__str__() == "Point(x=12, y=3)"
        
    def test_eq(self):
        p1 = Point(1,1)
        p2 = Point(1,1)
        p3 = OrientedPoint(1,1)
        p4 = OrientedPoint(2,2)
        n = 5
        assert p1 == p2
        assert p1 == p3
        assert not p1==p4
        assert not p3==p4
        assert not n==p1
    
    def test_round(test):
        p1 = Point(1.144444,1.6)
        p2 = Point(1.144444,1.668)
        p1.__round__(2)
        p2.__round__(2)
        assert p1 == Point(1.14,1.6)
        assert p2 == OrientedPoint(1.14,1.67)
        
    def test_to_OrientedPoint(self):
        p1 = Point(1,1)
        p2 = p1.to_OrientedPOint()
        assert isinstance(p2,OrientedPoint) and p1 == p2

class TestOrientedPoint:
    
    def test_eq(self):
        p1 = OrientedPoint(1,1,1)
        p2 = OrientedPoint(1,1,1)
        p3 = OrientedPoint(1,1,0)
        p4 = Point(1,1)
        assert p1==p2
        assert not p1==p3
        assert p1 == p4
        assert p4 == p1
    
    def test_round(self):
        p1 = OrientedPoint(1.144444,1.6)
        p2 = OrientedPoint(1.144444,1.668, 0.119)
        p1.__round__(2)
        p2.__round__(2)
        assert  p1 == OrientedPoint(1.14,1.6)
        assert p2 == OrientedPoint(1.14,1.67,0.12)

class TestRectangle:
    def test_constructor(self):
        p1 = Point(7, 4)
        p2 = Point(4, 7)
        r1 = Rectangle(p1, p2)
        assert not (
            r1.corner.x != 7
            or r1.corner.y != 4
            or r1.opposite_corner.x != 4
            or r1.opposite_corner.y != 7
        )

    def test_is_in_inside(self):
        corner = Point(7, 4)
        opposite_corner = Point(4, 7)
        r = Rectangle(corner, opposite_corner)
        point_inside = Point(5, 5)
        assert r.is_in(point_inside)
        point_inside = Point(4, 4)
        assert r.is_in(point_inside)

    def test_is_in_outside(self):
        corner = Point(7, 4)
        opposite_corner = Point(4, 7)
        r = Rectangle(corner, opposite_corner)
        point_outside = Point(3, 3)
        assert not r.is_in(point_outside)
        point_outside = Point(3, 5)
        assert not r.is_in(point_outside)

    def test_is_in_on_boundary(self):
        corner = Point(4.0, 0.0)
        opposite_corner = Point(0, 4.0)
        r = Rectangle(corner, opposite_corner)
        point_on_boundary = Point(4.0, 4.0)
        assert r.is_in(point_on_boundary)
