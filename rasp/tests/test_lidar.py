import pytest
from bot.Lidar import *


class TestLidar:
    def test_relative_to_abs_cartesian_1(self):
        test_cord = [Point(1, 1), Point(2, 2), Point(0, 0)]
        robot_pos = OrientedPoint(1, 4, 0)
        result_cord = relative_to_absolute_cartesian_coordinates(test_cord, robot_pos)
        assert result_cord == [Point(2, 5), Point(3, 6), Point(1, 4)]
        
    def test_relative_to_abs_cartesian_2(self):
        test_cord = []
        robot_pos = OrientedPoint(1, 4, 0.7)
        result_cord = relative_to_absolute_cartesian_coordinates(test_cord, robot_pos)
        assert result_cord == []
    
    def test_relative_to_abs_cartesian_3(self):
        test_cord = [Point(1, 1), Point(2, 2), Point(0, 0)]
        robot_pos = OrientedPoint(0, 0, 0)
        result_cord = relative_to_absolute_cartesian_coordinates(test_cord, robot_pos)
        assert result_cord == [Point(1, 1), Point(2, 2), Point(0, 0)]
        
    def test_is_under_threshold_1(self):
        test_cord = [OrientedPoint(1, 1), OrientedPoint(2, 2), OrientedPoint(0, 0)]
        result = is_under_threshold(test_cord, 3)
        assert result == True
        
    def test_is_under_threshold_2(self):
        # polar coordinates are in the form (angle, distance)
        test_cord = [OrientedPoint(1, 1), OrientedPoint(2, 2)]
        result = is_under_threshold(test_cord, 0.5)
        assert result == False
        
    def test_is_under_threshold_3(self):
        test_cord = [OrientedPoint(1, 1), OrientedPoint(2, 2), OrientedPoint(0, 0)]
        result = is_under_threshold(test_cord, 0)
        assert result == False

    def test_polar_to_cartesian_1(self):
        test_cord = [Point(math.pi*2, 5.5), Point(math.pi/2, 0)]
        result_cord = polar_to_cartesian(test_cord)
        assert result_cord == [Point(5.5, 0.0), Point(0.0, 0.0)]

    def test_polar_to_cartesian_2(self):
        test_cord = [Point(0, 0), Point(0, 0), Point(0, 0)]
        result_cord = polar_to_cartesian(test_cord)
        assert result_cord == [Point(0.0, 0.0), Point(0.0, 0.0), Point(0.0, 0.0)]
        
    def test_polar_to_cartesian_3(self):
        test_cord = [Point(0, 5.5), Point(math.pi/2, 3), Point(math.pi, 7)]
        result_cord = polar_to_cartesian(test_cord)
        assert result_cord == [Point(5.5, 0.0), Point(0.0, 3.0), Point(-7.0, 0.0)]
