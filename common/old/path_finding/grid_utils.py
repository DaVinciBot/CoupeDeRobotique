import random

import matplotlib.pyplot as plt
import numpy as np


def generate_grid(width_cm, height_cm, chunk_size_cm, obstacle_ratio=0.2):
    """
    Génère une grille avec des dimensions spécifiées et des obstacles aléatoires.

    :param width_cm: Largeur de la grille en cm.
    :param height_cm: Hauteur de la grille en cm.
    :param chunk_size_cm: Taille de chaque chunk (cellule) en cm.
    :param obstacle_ratio: Proportion de cellules qui sont des obstacles (0 à 1).
    :return: Liste de listes représentant la grille, où 0 = interdit et 1 = autorisé.
    """
    # Dimensions de la grille en nombre de chunks
    width_chunks = width_cm // chunk_size_cm
    height_chunks = height_cm // chunk_size_cm

    # Générer la grille avec des 1 (tous les chunks sont autorisés par défaut)
    grid = [[1 for _ in range(width_chunks)] for _ in range(height_chunks)]

    # Ajouter des obstacles aléatoires
    num_obstacles = int(obstacle_ratio * width_chunks * height_chunks)
    for _ in range(num_obstacles):
        x = random.randint(0, width_chunks - 1)
        y = random.randint(0, height_chunks - 1)
        grid[y][x] = 0  # 0 = interdit

    return grid


def display_grid(grid):
    """
    Affiche la grille de manière lisible.

    :param grid: Grille à afficher (liste de listes).
    """
    for row in grid:
        print("".join(["■" if cell == 0 else " " for cell in row]))


def can_move(grid, current_position, new_position):
    """
    Vérifie si le déplacement vers une nouvelle position est possible.

    :param grid: Grille représentant le terrain.
    :param current_position: Position actuelle (x, y).
    :param new_position: Nouvelle position (x, y).
    :return: True si le déplacement est autorisé, False sinon.
    """
    x, y = new_position
    if 0 <= y < len(grid) and 0 <= x < len(
        grid[0]
    ):  # Vérifier que la position est dans la grille
        return grid[y][x] == 1  # 1 = autorisé
    return False


def convert_to_grid_coordinates(x_cm, y_cm, chunk_size_cm):
    """
    Convertit les coordonnées en cm en indices de la grille.

    :param x_cm: Coordonnée X en cm.
    :param y_cm: Coordonnée Y en cm.
    :param chunk_size_cm: Taille d'un chunk en cm.
    :return: Coordonnées en indices de la grille (x, y).
    """
    return int(x_cm // chunk_size_cm), int(y_cm // chunk_size_cm)


def convert_to_real_coordinates(x_grid, y_grid, chunk_size_cm):
    """
    Convertit des indices de la grille en coordonnées réelles (cm).

    :param x_grid: Coordonnée X en indices de la grille.
    :param y_grid: Coordonnée Y en indices de la grille.
    :param chunk_size_cm: Taille d'un chunk en cm.
    :return: Coordonnées en cm (x, y).
    """
    return x_grid * chunk_size_cm, y_grid * chunk_size_cm


def visualize_path(grid, path=None, start=None, goal=None, dynamic_obstacles=None):
    """
    Visualise la grille avec la trajectoire calculée, le point de départ, l'arrivée, et des obstacles dynamiques.

    :param grid: Grille contenant les obstacles.
    :param path: Liste des cases du chemin [(x1, y1), ...]. Peut être None si aucun chemin n'est fourni.
    :param start: Position de départ (x, y).
    :param goal: Position d'arrivée (x, y).
    :param dynamic_obstacles: Liste de coordonnées [(x1, y1), ...] pour les obstacles ajoutés dynamiquement.
    """
    grid_with_path = np.array(grid)
    grid_with_path = (
        1 - grid_with_path
    )  # Inverser les valeurs pour afficher les obstacles en noir

    # Marquer la trajectoire si un chemin est fourni
    if path:
        for x, y in path:
            grid_with_path[y][x] = 2  # Marquer la trajectoire avec un 2

    # Préparer l'affichage avec des couleurs spécifiques
    cmap = plt.get_cmap("binary")  # Colormap noir et blanc
    cmap.set_over("blue")  # Couleur pour les chemins marqués (2)
    cmap.set_under("red")  # Couleur pour les points de départ et arrivée

    plt.figure(figsize=(10, 10))
    plt.imshow(grid_with_path, cmap=cmap, origin="upper", vmin=0, vmax=2)

    # Ajouter les obstacles dynamiques avec une couleur distincte
    if dynamic_obstacles:
        for x, y in dynamic_obstacles:
            plt.scatter(x, y, color="orange", label="Obstacle Dynamique", s=100)

    # Ajouter les points de départ et d'arrivée
    if start:
        plt.scatter(
            start[0], start[1], color="green", label="Départ", s=100, edgecolor="black"
        )
    if goal:
        plt.scatter(
            goal[0], goal[1], color="red", label="Arrivée", s=100, edgecolor="black"
        )

    # Ajouter les titres, labels et légendes
    plt.title("Grille avec Trajectoire et Obstacles Dynamiques")
    plt.xlabel("X (chunks)")
    plt.ylabel("Y (chunks)")
    plt.colorbar(label="0: Obstacle (Noir), 1: Libre (Blanc), 2: Chemin (Bleu)")
    plt.legend(loc="upper right")
    plt.show()


def visualize_grid(grid, chunk_size_cm=10):
    """
    Visualise la grille avec des obstacles.

    :param grid: Grille à visualiser (liste de listes contenant 0 et 1).
    :param chunk_size_cm: Taille d'un chunk en cm (optionnel, pour l'échelle).
    """
    grid_array = np.array(
        grid
    )  # Convertir en numpy array pour faciliter la manipulation
    grid_array = 1 - grid_array
    height, width = grid_array.shape

    # Créer une figure
    fig, ax = plt.subplots(figsize=(10, 10))

    # Afficher la grille avec une carte de couleurs
    ax.imshow(
        grid_array,
        cmap="Greys",
        origin="upper",
        extent=[0, width * chunk_size_cm, 0, height * chunk_size_cm],
    )

    # Ajouter une grille
    ax.set_xticks(np.arange(0, width * chunk_size_cm, chunk_size_cm))
    ax.set_yticks(np.arange(0, height * chunk_size_cm, chunk_size_cm))
    ax.set_xticklabels([])  # Désactiver les étiquettes si non nécessaire
    ax.set_yticklabels([])
    ax.grid(color="black", linestyle="-", linewidth=0.5)

    # Ajouter des labels
    ax.set_title("Grille avec Obstacles")
    ax.set_xlabel("X (cm)")
    ax.set_ylabel("Y (cm)")
    plt.show()
