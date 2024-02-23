import pytest
from bot import MarsArena, Arenas
from bot.Shapes import Point, Rectangle


class TestArena:
    def test_enable_go_to(self):
        arena = Arenas.Arena(forbidden_area=Rectangle(Point(2, 2), Point(5, 5)))
        a = Point(1, 1)
        b = Point(1, 6)
        c = Point(3, 1)
        d = Point(6, 1)
        e = Point(2, 6)
        f = Point(3, 6)
        # check without width
        assert arena.enable_go_to(a, b, robot_width=0, robot_length=0.01)
        assert not arena.enable_go_to(a, b, robot_width=0, robot_length=12.01)
        assert arena.enable_go_to(a, e, robot_width=0, robot_length=0.01)
        assert arena.enable_go_to(a, d, robot_width=0, robot_length=0.01)
        assert not arena.enable_go_to(c, f, robot_width=0, robot_length=0.01)
        assert not arena.enable_go_to(c, b, robot_width=0, robot_length=0.01)

        arena = Arenas.Arena(forbidden_area=Rectangle(Point(5, 4), Point(9, 7)))
        # check with width
        a = Point(1, 1)
        b = Point(4, 7)
        c = Point(8, 10)
        d = Point(10, 7)
        e = Point(10, 1)
        f = Point(2, 3)
        g = Point(9, 3)
        assert arena.enable_go_to(a, b, robot_width=0, robot_length=0.01)
        assert arena.enable_go_to(f, g, robot_width=0, robot_length=0.01)
        assert arena.enable_go_to(c, d, robot_width=0, robot_length=0.01)
        assert arena.enable_go_to(d, e, robot_width=0, robot_length=0.01)
        assert not arena.enable_go_to(d, e, robot_width=1, robot_length=0.01)


class TestMarsArena:
    def test_enable_go_to(self):
        arena = MarsArena(1)
        assert arena.enable_go_to(Point(10, 10), Point(100, 100))
        assert arena.enable_go_to(Point(10, 10), Point(100, 100))
        assert not arena.enable_go_to(Point(10, 10), Point(100, 400))
        assert not arena.enable_go_to(Point(10, 10), Point(10, 275))
