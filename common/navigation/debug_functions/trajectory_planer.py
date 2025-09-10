"""Helper utilities to simulate and plot a trajectory planner's behavior."""

# ruff: noqa: T201, PT028
from __future__ import annotations

import time
from typing import TYPE_CHECKING

import numpy as np
from matplotlib import pyplot as plt

if TYPE_CHECKING:
    from geometry import OrientedPoint
    from navigation.trajectory_planner.base_trajectory_planner.base_trajectory_planner import (  # noqa: E501
        BaseTrajectoryPlanner,
    )


def test_trajectory_planning(
    trajectory_planner: BaseTrajectoryPlanner,
    path: list[OrientedPoint],
    time_step: float = 0.1,
) -> None:
    """Simulates and visualizes the performance of a trajectory planner.

    Args:
        trajectory_planner (BaseTrajectoryPlanner):
            The trajectory planner instance to test.
        path (list[OrientedPoint]): List of waypoints to follow.
        time_step (float, optional): Sampling interval for simulation. Defaults to 0.1.

    """
    print("Testing trajectory planner:", trajectory_planner)
    trajectory_planner.plan_trajectory(path)
    total_duration = trajectory_planner.get_total_duration()

    linear_speeds = []
    angular_speeds = []
    positions = []
    times = []

    trajectory_planner.start_planning()
    start_time = time.time()
    while time.time() - start_time < total_duration:
        cmd = trajectory_planner.get_plan()

        positions.append(cmd.position)
        linear_speeds.append(cmd.linear_speed)
        angular_speeds.append(cmd.angular_speed)
        times.append(time.time() - start_time)

        time.sleep(time_step)

    x_positions = [pos.x for pos in positions]
    y_positions = [pos.y for pos in positions]
    theta_positions = [pos.theta for pos in positions]

    # Plotting evolution of angular and linear speeds
    _, axs = plt.subplots(2, 2, figsize=(12, 8))

    axs[0, 0].plot(angular_speeds, label="Vitesse angulaire")
    axs[0, 0].set_xlabel("Temps (itérations)")
    axs[0, 0].set_ylabel("Vitesse angulaire")
    axs[0, 0].set_title("Évolution de la vitesse angulaire")
    axs[0, 0].legend()
    axs[0, 0].grid(visible=True)

    axs[0, 1].plot(linear_speeds, label="Vitesse linéaire", color="r")
    axs[0, 1].set_xlabel("Temps (itérations)")
    axs[0, 1].set_ylabel("Vitesse linéaire")
    axs[0, 1].set_title("Évolution de la vitesse linéaire")
    axs[0, 1].legend()
    axs[0, 1].grid(visible=True)

    # Dual-axis plot for position and orientation
    ax1 = axs[1, 0]
    ax2 = ax1.twinx()

    ax1.plot(x_positions, color="b", label="X (Position)")
    ax1.plot(y_positions, color="r", label="Y (Position)")
    ax1.set_ylabel("Position", color="b")
    ax1.tick_params(axis="y", labelcolor="b")

    ax2.plot(theta_positions, label="Orientation (Theta)", color="m")
    ax2.set_ylabel("Orientation (theta)", color="m")
    ax2.tick_params(axis="y", labelcolor="m")

    ax1.set_xlabel("Temps (itérations)")
    ax1.set_title("Évolution de la position X et Y")
    ax1.grid(visible=True)

    axs[1, 1].plot(theta_positions, label="Orientation (Theta)", color="m")
    axs[1, 1].set_xlabel("Temps (itérations)")
    axs[1, 1].set_ylabel("Theta (orientation)")
    axs[1, 1].set_title("Évolution de l'orientation Theta")
    axs[1, 1].legend()
    axs[1, 1].grid(visible=True)

    plt.tight_layout()
    plt.show()

    # Visualizing the planned path and simulated trajectory
    plt.figure()

    # Plot original path with orientation arrows
    for idx, point in enumerate(path):
        plt.plot(point.x, point.y, "bo", label="Path" if not idx else "")
        dx = np.cos(point.theta)
        dy = np.sin(point.theta)
        plt.arrow(
            point.x,
            point.y,
            dx,
            dy,
            head_width=0.1,
            head_length=0.1,
            fc="b",
            ec="b",
        )

    # Plot simulated trajectory with orientation arrows
    for idx, point in enumerate(positions[::2]):
        plt.plot(point.x, point.y, "ro", label="Simulation" if not idx else "")
        dx = np.cos(point.theta) * 0.5
        dy = np.sin(point.theta) * 0.5
        plt.arrow(
            point.x,
            point.y,
            dx,
            dy,
            head_width=0.1,
            head_length=0.1,
            fc="r",
            ec="r",
        )

    plt.xlabel("x")
    plt.ylabel("y")
    plt.title("Path et Simulation de Trajectoire")
    plt.legend()
    plt.grid(visible=True)
    plt.axis("equal")
    plt.show()
