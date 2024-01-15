import pytest

# works with the py -m unittest discover commands launched from Perso_cdr
from bot.Shapes import Point, Rectangle


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


class TestRectangle:
    def test_constructor(self):
        p2 = Point(12, 3)
        p1 = Point(-2, 2.5)
        r1 = Rectangle(p1, p2)
        assert not (
            r1.corner.x != -2
            or r1.corner.y != 2.5
            or r1.opposite_corner.x != 12
            or r1.opposite_corner.y != 3
        )

    def test_is_in_inside(self):
        corner = Point(0.0, 0.0)
        opposite_corner = Point(4.0, 4.0)
        r = Rectangle(corner, opposite_corner)
        point_inside = Point(2.0, 2.0)
        assert r.is_in(point_inside)

    def test_is_in_outside(self):
        corner = Point(0.0, 0.0)
        opposite_corner = Point(4.0, 4.0)
        r = Rectangle(corner, opposite_corner)
        point_outside = Point(5.0, 5.0)
        assert not r.is_in(point_outside)

    def test_is_in_on_boundary(self):
        corner = Point(0.0, 0.0)
        opposite_corner = Point(4.0, 4.0)
        r = Rectangle(corner, opposite_corner)
        point_on_boundary = Point(4.0, 4.0)
        assert r.is_in(point_on_boundary)
