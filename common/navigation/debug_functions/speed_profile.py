# ====== Code Summary ======
# This module provides a test utility to visualize a given `BaseSpeedProfile` over time.
# It plots both speed and distance with respect to time using matplotlib, allowing developers
# to inspect the profile shape and dynamics (e.g., acceleration, cruising, deceleration).

# ====== Third-Party Library Imports ======
from matplotlib import pyplot as plt

# ====== Internal Project Imports ======
from navigation.trajectory_planner.speed_profile.base_speed_profile import BaseSpeedProfile


def test_speed_profile(profile: BaseSpeedProfile, distance: float, step_time: float = 0.1):
    """
    Plot the speed and distance over time for a given speed profile.

    Args:
        profile (BaseSpeedProfile): The speed profile to test.
        distance (float): Target distance to simulate.
        step_time (float): Time interval for sampling the profile.
    """
    print("Testing profile:", profile)
    total_duration = profile.get_total_duration(distance)

    speeds = []
    distances = []
    times = []

    current_time = 0.0
    while current_time < total_duration:
        distances.append(profile.get_distance(time_elapsed=current_time, distance=distance))
        speeds.append(profile.get_speed(time_elapsed=current_time, distance=distance))
        times.append(current_time)
        current_time += step_time

    fig, ax1 = plt.subplots()

    color = 'tab:blue'
    ax1.set_xlabel('Temps (s)')
    ax1.set_ylabel('Vitesse (m/s)', color=color)
    ax1.plot(times, speeds, color=color, label='Vitesse')
    ax1.tick_params(axis='y', labelcolor=color)

    ax2 = ax1.twinx()
    color = 'tab:orange'
    ax2.set_ylabel('Distance (m)', color=color)
    ax2.plot(times, distances, color=color, linestyle='--', label='Distance')
    ax2.tick_params(axis='y', labelcolor=color)

    plt.title("Vitesse et distance en fonction du temps")
    fig.tight_layout()
    plt.grid(True)
    plt.show()
