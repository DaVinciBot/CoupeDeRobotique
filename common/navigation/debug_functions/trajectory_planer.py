from matplotlib import pyplot as plt
from navigation.trajectory_planner import BaseTrajectoryPlanner
from geometry import OrientedPoint
import time
import numpy as np


def test_trajectory_planning(trajectory_planner: BaseTrajectoryPlanner, path: list[OrientedPoint],
                             time_step: float = 0.1):
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

    # Création d'une figure avec plusieurs sous-graphiques
    fig, axs = plt.subplots(2, 2, figsize=(12, 8))

    # Graphique des vitesses angulaires
    axs[0, 0].plot(angular_speeds, label="Vitesse angulaire")
    axs[0, 0].set_xlabel("Temps (itérations)")
    axs[0, 0].set_ylabel("Vitesse angulaire")
    axs[0, 0].set_title("Évolution de la vitesse angulaire")
    axs[0, 0].legend()
    axs[0, 0].grid(True)

    # Graphique des vitesses linéaires
    axs[0, 1].plot(linear_speeds, label="Vitesse linéaire", color='r')
    axs[0, 1].set_xlabel("Temps (itérations)")
    axs[0, 1].set_ylabel("Vitesse linéaire")
    axs[0, 1].set_title("Évolution de la vitesse linéaire")
    axs[0, 1].legend()
    axs[0, 1].grid(True)

    # Graphique des positions X-Y (Trajectoire) avec double axe Y
    ax1 = axs[1, 0]  # Axe principal
    ax2 = ax1.twinx()  # Deuxième axe Y

    ax1.plot(x_positions, color='b', label="X (Position)")
    ax1.plot(y_positions, color='r', label="Y (Position)")
    ax1.set_ylabel("Position (cm)", color='b')
    ax1.tick_params(axis='y', labelcolor='b')

    ax2.plot(theta_positions, label="Orientation (Theta)", color='m')
    ax2.set_ylabel("Orientation (theta)", color='m')
    ax2.tick_params(axis='y', labelcolor='m')

    ax1.set_xlabel("Temps (itérations)")
    ax1.set_title("Évolution de la position X et Y")
    ax1.grid(True)

    axs[1, 1].plot(theta_positions, label="Orientation (Theta)", color='m')
    axs[1, 1].set_xlabel("Temps (itérations)")
    axs[1, 1].set_ylabel("Theta (orientation)")
    axs[1, 1].set_title("Évolution de l'orientation Theta")
    axs[1, 1].legend()
    axs[1, 1].grid(True)

    plt.tight_layout()
    plt.show()

    plt.figure()

    # Affichage de la première couche : les points du path (en bleu)
    for idx, point in enumerate(path):
        # Affichage du point
        plt.plot(point.x, point.y, 'bo', label="Path" if idx == 0 else "")
        # Calcul de l'orientation
        dx = np.cos(point.theta)
        dy = np.sin(point.theta)
        # Affichage de la flèche indiquant l'orientation
        plt.arrow(point.x, point.y, dx, dy, head_width=0.1, head_length=0.1, fc='b', ec='b')

    # Affichage de la deuxième couche : les points de la simulation (en rouge)
    for idx, point in enumerate(positions[::2]):
        plt.plot(point.x, point.y, 'ro', label="Simulation" if idx == 0 else "")
        dx = np.cos(point.theta) * 0.5
        dy = np.sin(point.theta) * 0.5
        plt.arrow(point.x, point.y, dx, dy, head_width=0.1, head_length=0.1, fc='r', ec='r')

    plt.xlabel('x')
    plt.ylabel('y')
    plt.title('Path et Simulation de Trajectoire')
    plt.legend()
    plt.grid(True)
    plt.axis('equal')
    plt.show()
