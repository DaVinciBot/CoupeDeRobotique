import pytest

from bot import RollingBasis, Shapes
from bot.Com import calc_center


class TestRollingBasis:
    def test_calc_center_1(self):
        a = Shapes.OrientedPoint(0, 0, 0)
        b = Shapes.OrientedPoint(10, 0, 0)
        c = Shapes.OrientedPoint(0, 10, 0)
        assert calc_center(b, c, a) == Shapes.OrientedPoint(5.0, 5.0)

    def test_calc_center_2(self):
        a = Shapes.OrientedPoint(2.59, 1.04, 0)
        b = Shapes.OrientedPoint(3.12, 3.32, 0)
        c = Shapes.OrientedPoint(6.18, 1, 0)
        print(calc_center(a, b, c))
        assert calc_center(a, b, c) == Shapes.OrientedPoint(
            4.39393887697407, 1.822264208422694
        )

    def test_curve_go_to_1(self):
        bot = RollingBasis(dummy=True)
        bot.odometrie = Shapes.OrientedPoint(5, 5, 0)
        assert bot.curve_go_to(
            Shapes.OrientedPoint(5, 10, 0), 10, 20, test=True
        ) == Shapes.OrientedPoint(9.6875, 7.5, 0)

    def test_curve_go_to_2(self):
        """
        Test the 0 division case
        """
        bot = RollingBasis(dummy=True)
        bot.odometrie = Shapes.OrientedPoint(0, 0, 0)
        assert bot.curve_go_to(
            Shapes.OrientedPoint(10, 0, 0), 5, 20, test=True
        ) == Shapes.OrientedPoint(5, 0, 0)

    def test_curve_go_to_3(self):
        """
        test if the robot is already at the destination
        """
        bot = RollingBasis(dummy=True)
        bot.odometrie = Shapes.OrientedPoint(0, 0, 0)
        assert bot.curve_go_to(
            Shapes.OrientedPoint(0, 0, 0), 5, 20, test=True
        ) == Shapes.OrientedPoint(0, 0, 0)

    def test_queue_1(self):
        bot = RollingBasis(dummy=True)
        bot.Go_To(Shapes.OrientedPoint(5, 5, 0))
        assert bot.queue == [{b"\00": b"00"}]
