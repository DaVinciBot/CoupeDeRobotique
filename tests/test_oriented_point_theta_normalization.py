"""Test automatic theta normalization in OrientedPoint."""

import math

import pytest

from common.geometry.oriented_point import OrientedPoint


def test_theta_normalization_on_creation() -> None:
    """Test that theta is normalized when creating an OrientedPoint."""
    # Test with angle > π
    p1 = OrientedPoint((0, 0), 5 * math.pi)
    assert abs(p1.theta) <= math.pi, f"Theta should be normalized, got {p1.theta}"


def test_theta_normalization_on_modification() -> None:
    """Test that theta is automatically normalized when modified."""
    # Test with positive angle
    p2 = OrientedPoint((1, 1), 0)
    p2.theta = 3 * math.pi
    assert abs(p2.theta) <= math.pi, f"Theta should be normalized, got {p2.theta}"
    assert math.isclose(p2.theta, -math.pi, abs_tol=1e-9), (
        f"3π should normalize to -π, got {p2.theta}"
    )


def test_theta_normalization_negative_angle() -> None:
    """Test that negative angles are normalized correctly."""
    p3 = OrientedPoint((2, 2), 0)
    p3.theta = -5 * math.pi
    assert abs(p3.theta) <= math.pi, f"Theta should be normalized, got {p3.theta}"
    assert math.isclose(p3.theta, -math.pi, abs_tol=1e-9), (
        f"-5π should normalize to -π, got {p3.theta}"
    )


def test_theta_none_remains_none() -> None:
    """Test that None values remain None after modification."""
    p4 = OrientedPoint((3, 3), None)
    assert p4.theta is None, "Theta should be None"

    p4.theta = None
    assert p4.theta is None, "Theta should remain None after setting to None"


@pytest.mark.parametrize(
    "angle,expected_in_range",
    [
        (math.pi, True),  # π should remain ±π
        (-math.pi, True),  # -π should normalize to ±π
        (2 * math.pi, True),  # 2π should normalize to valid range
        (0, True),  # 0 is already normalized
        (math.pi / 2, True),  # π/2 is already normalized
        (-math.pi / 2, True),  # -π/2 is already normalized
    ],
)
def test_theta_normalization_edge_cases(angle: float, expected_in_range: bool) -> None:
    """Test edge cases for theta normalization.

    Args:
        angle (float): The angle to test.
        expected_in_range (bool):
            Whether the angle should be in [-π, π] after normalization.
    """
    p = OrientedPoint((0, 0), 0)
    p.theta = angle
    if expected_in_range:
        assert abs(p.theta) <= math.pi, (
            f"Angle {angle} should be normalized, got {p.theta}"
        )
    else:
        assert abs(p.theta) > math.pi, (
            f"Angle {angle} should not be normalized, got {p.theta}"
        )


def test_theta_normalization_preserves_equivalent_angles() -> None:
    """Test that equivalent angles normalize to the same value."""
    p1 = OrientedPoint((0, 0), 0)
    p2 = OrientedPoint((0, 0), 2 * math.pi)
    p3 = OrientedPoint((0, 0), 4 * math.pi)

    # All should normalize to approximately the same angle
    assert math.isclose(p1.theta, p2.theta, abs_tol=1e-9), (
        f"0 and 2π should normalize to same angle: {p1.theta} vs {p2.theta}"
    )
    assert math.isclose(p2.theta, p3.theta, abs_tol=1e-9), (
        f"2π and 4π should normalize to same angle: {p2.theta} vs {p3.theta}"
    )
