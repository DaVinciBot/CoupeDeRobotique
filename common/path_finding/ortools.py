from ortools.constraint_solver import pywrapcp, routing_enums_pb2
import numpy as np


def ortools_pathfinding(grid, start, goal):
    """
    Utilise OR-Tools pour résoudre un problème de plus court chemin sur une grille.

    :param grid: Grille contenant les obstacles (0 = obstacle, 1 = libre).
    :param start: Tuple (x, y) pour la position de départ.
    :param goal: Tuple (x, y) pour la position d'arrivée.
    :return: Liste des coordonnées [(x1, y1), ...] pour le chemin trouvé.
    """
    height, width = len(grid), len(grid[0])

    # Conversion 2D -> 1D
    def node_id(x, y):
        return y * width + x

    # Création d'une matrice de distance
    num_nodes = height * width
    distances = np.full((num_nodes, num_nodes), np.inf)

    for y in range(height):
        for x in range(width):
            if grid[y][x] == 1:  # Cellule libre
                node = node_id(x, y)
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:  # Haut, Bas, Gauche, Droite
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < width and 0 <= ny < height and grid[ny][nx] == 1:
                        neighbor = node_id(nx, ny)
                        distances[node][neighbor] = 1  # Coût unitaire pour avancer

    # Initialiser le solveur
    manager = pywrapcp.RoutingIndexManager(num_nodes, 1, [node_id(*start)], [node_id(*goal)])
    routing = pywrapcp.RoutingModel(manager)

    # Fonction de coût (distance entre les nœuds)
    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return distances[from_node, to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Chercher la solution
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)

    solution = routing.SolveWithParameters(search_parameters)
    if not solution:
        print("Pas de solution trouvée.")
        return None

    # Extraire le chemin
    index = routing.Start(0)
    path = []
    while not routing.IsEnd(index):
        node = manager.IndexToNode(index)
        x, y = node % width, node // width
        path.append((x, y))
        index = solution.Value(routing.NextVar(index))
    path.append((goal[0], goal[1]))  # Ajouter la destination finale
    return path


def update_grid_for_dynamic_obstacles(grid, dynamic_obstacles):
    """
    Met à jour la grille pour ajouter des obstacles dynamiques.

    :param grid: Grille contenant les obstacles statiques.
    :param dynamic_obstacles: Liste de positions [(x1, y1), ...] représentant les obstacles dynamiques.
    :return: Nouvelle grille avec les obstacles dynamiques ajoutés.
    """
    updated_grid = np.array(grid)
    for x, y in dynamic_obstacles:
        if 0 <= y < updated_grid.shape[0] and 0 <= x < updated_grid.shape[1]:
            updated_grid[y][x] = 0  # Marquer comme obstacle
    return updated_grid


def ortools_dynamic_pathfinding(grid, start, goal, dynamic_obstacles=None):
    """
    Résout le problème de pathfinding en tenant compte des obstacles dynamiques.

    :param grid: Grille contenant les obstacles statiques.
    :param start: Tuple (x, y) pour la position de départ.
    :param goal: Tuple (x, y) pour la position d'arrivée.
    :param dynamic_obstacles: Liste des positions des obstacles dynamiques.
    :return: Liste des coordonnées [(x1, y1), (x2, y2), ...] pour le chemin trouvé.
    """
    if dynamic_obstacles:
        grid = update_grid_for_dynamic_obstacles(grid, dynamic_obstacles)

    return ortools_pathfinding(grid, start, goal)
