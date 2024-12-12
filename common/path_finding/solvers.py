import heapq
import numpy as np


def heuristic(a, b):
    """
    Heuristique pour A* (distance de Manhattan).
    :param a: Tuple (x1, y1).
    :param b: Tuple (x2, y2).
    :return: Distance heuristique entre a et b.
    """
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def get_neighbors(grid, node):
    """
    Trouve les voisins autorisés (sans obstacles) d'une cellule.
    :param grid: Grille contenant les obstacles.
    :param node: Position actuelle (x, y).
    :return: Liste des voisins disponibles [(x1, y1), ...].
    """
    x, y = node
    neighbors = []
    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:  # Haut, Bas, Gauche, Droite
        nx, ny = x + dx, y + dy
        if (
            0 <= ny < len(grid) and 0 <= nx < len(grid[0]) and grid[ny][nx] == 1
        ):  # Vérifie si accessible
            neighbors.append((nx, ny))
    return neighbors


def a_star_pathfinding(grid, start, goal):
    """
    Implémentation de l'algorithme A* avec messages de debug.
    :param grid: Grille contenant les obstacles.
    :param start: Position de départ (x, y).
    :param goal: Position d'arrivée (x, y).
    :return: Liste des cases à parcourir pour atteindre la destination.
    """
    open_set = []
    heapq.heappush(open_set, (0, start))  # Priorité, Position
    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristic(start, goal)}

    print(f"Départ : {start}, Arrivée : {goal}")
    print("Initialisation de A*")

    while open_set:
        # Trier et explorer le nœud avec la plus petite f_score
        _, current = heapq.heappop(open_set)
        print(f"Exploration de : {current}")

        if current == goal:  # Chemin trouvé
            print("Chemin trouvé ! Reconstruction du chemin...")
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.reverse()
            print(f"Chemin : {path}")
            return path

        for neighbor in get_neighbors(grid, current):
            tentative_g_score = (
                g_score[current] + 1
            )  # Distance entre cellules adjacentes
            print(f"Voisin : {neighbor}, g_score potentiel : {tentative_g_score}")

            if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                if neighbor not in [i[1] for i in open_set]:
                    print(
                        f"Ajout au open_set : {neighbor} avec f_score : {f_score[neighbor]}"
                    )
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))

    print("Aucun chemin trouvé.")
    return []  # Aucun chemin trouvé


def d_star_lite(grid, start, goal, path=None):
    """
    Implémentation de l'algorithme D* Lite pour la replanification.
    :param grid: Grille contenant les obstacles.
    :param start: Position de départ (x, y).
    :param goal: Position d'arrivée (x, y).
    :param path: Chemin précédent pour réutilisation.
    :return: Nouveau chemin mis à jour.
    """
    if path is None:
        return a_star_pathfinding(grid, start, goal)

    # Replanification dynamique
    for idx, node in enumerate(path):
        if grid[node[1]][node[0]] == 0:  # Obstacle détecté
            new_start = path[max(0, idx - 1)]  # Retour au dernier nœud sûr
            return a_star_pathfinding(grid, new_start, goal)

    return path  # Pas de replanification nécessaire
