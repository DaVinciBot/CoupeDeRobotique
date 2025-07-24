# ====== Code Summary ======
# This script defines a function to test and visualize the execution of a navigation system.
# It simulates a navigator executing its task in an arena, logging the robot's trajectory,
# speed, task states, avoidance states, and the distance to the enemy over time.
# After the task is completed, the script generates multiple plots showing the robot’s
# spatial path, temporal evolution of motion parameters, and categorical state changes.

import time

import matplotlib.pyplot as plt
import numpy as np

from arena import BaseArena
from geometry import Point
from navigation.navigator import Navigator


def test_navigator_execution(
    navigator: Navigator,
    arena: BaseArena,
    time_step: float = 0.1,
) -> None:
    """Simulate the navigator until its current task is finished, logging the navigation data and plotting the key metrics over time.

    This function records at each timestep:
        - Time elapsed
        - X and Y positions
        - Linear and angular speeds
        - Trajectory planner's elapsed time (if task is active)
        - Task state enumeration
        - Avoidance state enumeration
        - Distance to the enemy

    It then visualizes this data using line plots, a 2D trajectory plot, and categorical state plots.

    Args:
        navigator (Navigator): The navigator object controlling the robot's movement.
        arena (BaseArena): The arena where navigation is simulated.
        time_step (float, optional): The delay between iterations in seconds. Defaults to 0.1.
    """
    # 1) Prepare storage for logging metrics
    times: list[float] = []
    x_positions: list[float] = []
    y_positions: list[float] = []
    linear_speeds: list[float] = []
    angular_speeds: list[float] = []
    traj_times: list[float] = []
    task_states: list[str] = []
    avoidance_states: list[str] = []
    distances_to_enemy: list[float] = []

    start_t = time.time()

    # 2) Loop until current task finishes
    while navigator.current_task is not None:
        cmd = navigator.handle(
            ally_zone=arena.ally_zone,
            enemy_zone=arena.enemy_zone,
        )
        arena.update(
            ally_position=cmd.position,
            lidar_scan_polars=np.array([]),  # Empty lidar scan for this test
            optimized_update=False,
            _enemy_position=Point(
                arena.enemy_zone.point.x - 10,
                arena.enemy_zone.point.y,
            ),  # Enemy is positioned 10 units left
        )

        # Update distance to enemy
        distance = arena.ally_zone.point.distance(arena.enemy_zone.point)

        t = time.time() - start_t
        times.append(t)
        x_positions.append(cmd.position.x)
        y_positions.append(cmd.position.y)
        linear_speeds.append(cmd.linear_speed)
        angular_speeds.append(cmd.angular_speed)
        distances_to_enemy.append(distance)

        if navigator.current_task is not None:
            traj_times.append(
                navigator.current_task.trajectory_planner._get_trajectory_time_elapsed(),
            )
            task_states.append(navigator.current_task.state.name)
            avoidance_states.append(navigator.current_task.avoidance.state.name)
        else:
            traj_times.append(-1.0)
            task_states.append("None")
            avoidance_states.append("None")

        # Debug print for each step
        print(
            f"[{t:.2f}s] x={cmd.position.x:.2f}, y={cmd.position.y:.2f}, "
            f"v_lin={cmd.linear_speed:.2f}, v_ang={cmd.angular_speed:.2f}, "
            f"traj_t={traj_times[-1]:.2f}, state={task_states[-1]}, "
            f"avoid={avoidance_states[-1]}, dist_enemy={distance:.2f}",
        )

        time.sleep(time_step)

    # 3) Plot numeric time-series metrics
    _, axs = plt.subplots(5, 1, figsize=(10, 20), sharex=True)

    # 3.1 Plot X and Y positions over time
    axs[0].plot(times, x_positions, label="X pos")
    axs[0].plot(times, y_positions, label="Y pos")
    axs[0].set_ylabel("Position")
    axs[0].set_title("X & Y over Time")
    axs[0].legend()
    axs[0].grid(visible=True)

    # 3.2 Plot linear speed over time
    axs[1].plot(times, linear_speeds, label="Linear speed")
    axs[1].set_ylabel("v_lin")
    axs[1].set_title("Linear Speed")
    axs[1].grid(visible=True)

    # 3.3 Plot angular speed over time
    axs[2].plot(times, angular_speeds, label="Angular speed")
    axs[2].set_ylabel("v_ang")
    axs[2].set_title("Angular Speed")
    axs[2].grid(visible=True)

    # 3.4 Plot trajectory planner time elapsed
    axs[3].plot(times, traj_times, label="Planned traj time")
    axs[3].set_ylabel("t_traj")
    axs[3].set_title("Trajectory Planner Time Elapsed")
    axs[3].grid(visible=True)

    # 3.5 Plot distance to enemy over time
    axs[4].plot(times, distances_to_enemy, label="Distance to Enemy")
    axs[4].set_xlabel("Time (s)")
    axs[4].set_ylabel("Distance")
    axs[4].set_title("Distance to Enemy over Time")
    axs[4].grid(visible=True)

    plt.tight_layout()
    plt.show()

    # 4) Plot 2D spatial path (trajectory in space)
    _, ax = plt.subplots(figsize=(8, 8))
    ax.plot(x_positions, y_positions, marker="o", markersize=3, label="Path")
    ax.set_xlabel("X Position")
    ax.set_ylabel("Y Position")
    ax.set_title("2D Trajectory of Robot")
    ax.grid(visible=True)
    ax.legend()
    plt.axis("equal")
    plt.show()

    # 5) Plot enums (task/avoidance states) as categorical step plots
    def plot_enum(
        times: list[float],
        values: list[str],
        title: str,
    ) -> None:
        """Plot categorical enum values as a step function over time.

        Args:
            times (list[float]): Time points.
            values (list[str]): Enum value names at each time.
            title (str): Plot title.
        """
        unique = list(dict.fromkeys(values))  # Preserve order
        code = {v: i for i, v in enumerate(unique)}  # Map to integers
        codes = [code[v] for v in values]

        _, ax = plt.subplots(figsize=(10, 3))
        ax.step(times, codes, where="post")
        ax.set_yticks(range(len(unique)))
        ax.set_yticklabels(unique)
        ax.set_xlabel("Time (s)")
        ax.set_title(title)
        ax.grid(visible=True)
        plt.show()

    plot_enum(times, task_states, "Task State over Time")
    plot_enum(times, avoidance_states, "Avoidance State over Time")
