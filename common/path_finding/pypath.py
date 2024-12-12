import random
import matplotlib.pyplot as plt
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder
from pathfinding.core.diagonal_movement import DiagonalMovement


def generate_grid(width_cm, height_cm, chunk_size_cm, obstacle_ratio):
    """Génère une grille avec obstacles aléatoires."""
    width = width_cm // chunk_size_cm
    height = height_cm // chunk_size_cm
    grid = [[1 if random.random() > obstacle_ratio else 0 for _ in range(width)] for _ in range(height)]
    return grid


import numpy as np
import matplotlib.pyplot as plt
import time

def visualize_path(grid, path=None, start=None, goal=None, dynamic_obstacles=None):
    """
    Visualise la grille avec la trajectoire calculée, le point de départ, l'arrivée, et des obstacles dynamiques.

    :param grid: Grille contenant les obstacles.
    :param path: Liste des cases du chemin [(x1, y1), ...]. Peut être None si aucun chemin n'est fourni.
    :param start: Position de départ (x, y).
    :param goal: Position d'arrivée (x, y).
    :param dynamic_obstacles: Liste de coordonnées [(x1, y1), ...] pour les obstacles ajoutés dynamiquement.
    """
    # Créer une copie de la grille pour la visualisation
    grid_visual = np.array(grid)
    grid_visual = 1 - grid_visual

    # Marquer la trajectoire si un chemin est fourni
    if path:
        for x, y in path:
            grid_visual[y][x] = 2  # Chemin marqué avec une valeur spéciale

    # Préparer les couleurs pour l'affichage
    cmap = plt.cm.binary  # Colormap noir et blanc
    cmap.set_over('blue')  # Chemin en bleu
    cmap.set_under('orange')  # Obstacles dynamiques en orange

    # Configurer les valeurs pour afficher les points spécifiques
    plt.figure(figsize=(8, 8))
    plt.imshow(grid_visual, cmap=cmap, origin="upper", vmin=0, vmax=2)

    # Marquer les obstacles dynamiques
    if dynamic_obstacles:
        for x, y in dynamic_obstacles:
            plt.scatter(x, y, color="orange", s=50, label="Obstacle Dynamique")

    # Marquer le point de départ et d'arrivée
    if start:
        start = (start.x, start.y) if hasattr(start, 'x') else start
        plt.scatter(start[0], start[1], color="green", label="Départ", s=100, edgecolor="black")

    if goal:
        goal = (goal.x, goal.y) if hasattr(goal, 'x') else goal
        plt.scatter(goal[0], goal[1], color="red", label="Arrivée", s=100, edgecolor="black")

    # Ajouter les titres et légendes
    plt.title("Visualisation de la Grille et du Chemin")
    plt.xticks([])
    plt.yticks([])
    plt.show()



def update_dynamic_obstacles(grid, num_obstacles):
    """Génère de nouveaux obstacles dynamiques."""
    return [(random.randint(0, len(grid[0]) - 1), random.randint(0, len(grid) - 1)) for _ in range(num_obstacles)]


def py_path_run():
    # Initialiser la grille, le départ et la destination
    grid = generate_grid(width_cm=300, height_cm=200, chunk_size_cm=20, obstacle_ratio=0.0)
    start = (1, 1)
    goal = (13, 8)
    grid[start[1]][start[0]] = 1   # Assurez-vous que le point de départ est accessible
    grid[goal[1]][goal[0]] = 1  # Assurez-vous que le point d'arrivée est accessible

    # Initialisation des objets de pathfinding
    finder = AStarFinder(diagonal_movement=DiagonalMovement.always)

    current_position = start
    dynamic_obstacles = []

    # Simulation des déplacements
    for step in range(50):
        print(f"Étape {step + 1} :")

        # Mettre à jour les obstacles dynamiques
        dynamic_obstacles.extend(update_dynamic_obstacles(grid, num_obstacles=1))
        for obs in dynamic_obstacles:
            grid[obs[1]][obs[0]] = 0  # Ajouter les obstacles dynamiques à la grille

        # Recalculer le chemin
        grid_obj = Grid(matrix=grid)
        start_obj = grid_obj.node(*current_position)
        end_obj = grid_obj.node(goal[0], goal[1])
        start_time = time.time()
        path, _ = finder.find_path(start_obj, end_obj, grid_obj)
        print(f"Temps de calcul du chemin : {(time.time() - start_time)*1000:.2f} ms")

        if path:
            print(f"Chemin trouvé : {path}")
            visualize_path(grid, path, start=current_position, goal=goal, dynamic_obstacles=dynamic_obstacles)

            # Avancer vers la prochaine position
            current_position = path[1] if len(path) > 1 else current_position
        else:
            print("Aucun chemin trouvé !")
            break

        # Nettoyer les obstacles dynamiques pour la prochaine étape
        for obs in dynamic_obstacles:
            grid[obs[1]][obs[0]] = 1  # Suppression des obstacles dynamiques actuels
