from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import json
from tasks.base_task.task_planner_solution import TaskPlannerSolution
import networkx as nx
import matplotlib.pyplot as plt


class TaskPlanner:  # TODO: test solution saving and loading
    def __init__(
        self,
        tasks_scores,
        tasks_duration_sec,
        travels_duration_matrix_sec,
        max_time_sec,
        solve_limit_sec=10,
        start_node=0,
        end_node=None,
    ):
        self.num_tasks = len(tasks_scores)
        self.tasks_scores = tasks_scores
        self.tasks_duration_sec = tasks_duration_sec
        self.travels_duration_matrix_sec = travels_duration_matrix_sec
        self.max_time_sec = max_time_sec
        self.num_nodes = self.num_tasks + 2  # Including start and end nodes
        self.start_node = start_node
        self.end_node = self.num_tasks + 1 if end_node is None else end_node
        self.solve_limit_seconds = solve_limit_sec
        self.solution = None

        # Initialize routing index manager
        self.manager = pywrapcp.RoutingIndexManager(
            self.num_nodes, 1, [self.start_node], [self.end_node]
        )

        # Create routing model
        self.routing = pywrapcp.RoutingModel(self.manager)

        # Register transit callback for time dimension
        def transit_callback(from_index, to_index):
            from_node = self.manager.IndexToNode(from_index)
            to_node = self.manager.IndexToNode(to_index)

            service_time = 0
            if from_node != self.start_node and from_node != self.end_node:
                service_time = self.tasks_duration_sec[from_node - 1]

            travel_time = self.travels_duration_matrix_sec[from_node][to_node]
            return service_time + travel_time

        transit_callback_index = self.routing.RegisterTransitCallback(transit_callback)

        # Add time dimension constraint
        self.routing.AddDimension(
            transit_callback_index,
            0,  # No slack
            self.max_time_sec,  # Maximum time allowed
            True,  # Start cumul to zero
            "Time",
        )

        # Set penalties for disjunctions (prizes)
        for node in range(1, self.num_tasks + 1):
            index = self.manager.NodeToIndex(node)
            self.routing.AddDisjunction([index], self.tasks_scores[node - 1])

        # Set arc cost to constant zero to focus on maximizing collected scores
        def cost_callback(from_index, to_index):
            return 0

        cost_callback_index = self.routing.RegisterTransitCallback(cost_callback)
        self.routing.SetArcCostEvaluatorOfAllVehicles(cost_callback_index)

    def solve(self, time_limit_seconds=None, save_mode=False):
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC  # May need adjustment
        )
        search_parameters.local_search_metaheuristic = (
            routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
        )
        search_parameters.time_limit.seconds = (
            time_limit_seconds or self.solve_limit_seconds
        )

        solution = self.routing.SolveWithParameters(search_parameters)

        if solution:
            route = []
            total_score = sum(self.tasks_scores) - solution.ObjectiveValue()
            time_dimension = self.routing.GetDimensionOrDie("Time")
            index = self.routing.Start(0)

            while not self.routing.IsEnd(index):
                node = self.manager.IndexToNode(index)
                route.append(node)
                index = solution.Value(self.routing.NextVar(index))

            route.append(self.manager.IndexToNode(index))
            total_time = solution.Min(time_dimension.CumulVar(self.routing.End(0)))

            self.solution = TaskPlannerSolution(
                ordered_tasks=route, score=total_score, duration=total_time
            )

            if save_mode:
                with open("task_planner_solution.json", "w") as f:
                    json.dump(
                        {
                            "route": route,
                            "score": total_score,
                            "duration": total_time,
                        },
                        f,
                    )
            else:
                return self.solution
        else:
            return {"message": "no solution found"}

    def visualize_solution(self, display_all_edges=False, display_all_vertices=False):
        plt.close("all")  # Fermer toutes les figures existantes
        num_nodes = len(self.travels_duration_matrix_sec)

        # Création du graphe complet pour le layout
        G = nx.DiGraph()
        for i in range(num_nodes):
            for j in range(num_nodes):
                if i != j and self.travels_duration_matrix_sec[i][j] > 0:
                    G.add_edge(i, j, weight=self.travels_duration_matrix_sec[i][j])

        pos = nx.spring_layout(G, seed=42)  # Layout basé sur le graphe complet

        plt.figure(figsize=(15, 5))
        if self.solution:
            # Extraction du chemin solution
            solution_nodes = self.solution.ordered_tasks
            solution_edges = list(zip(solution_nodes[:-1], solution_nodes[1:]))

            # Définir les sommets à afficher
            if display_all_vertices:
                nodes_to_display = list(range(num_nodes))
                node_colors = [
                    "red" if n in solution_nodes else "lightgray"
                    for n in nodes_to_display
                ]
                display_pos = pos
            else:
                nodes_to_display = solution_nodes
                node_colors = ["red"] * len(nodes_to_display)
                display_pos = {n: pos[n] for n in nodes_to_display}

            # Préparation des labels pour les sommets à afficher
            display_labels = {
                n: (
                    (
                        "Start"
                        if n == self.start_node
                        else (
                            "End"
                            if n == self.end_node
                            else f"{n}\nS: {self.tasks_scores[n - 1]}\nD: {self.tasks_duration_sec[n - 1]}s"
                        )
                    )
                    if (
                        n == self.start_node
                        or n == self.end_node
                        or (n > 0 and n < len(self.tasks_scores) + 1)
                    )
                    else f"{n}"
                )
                for n in nodes_to_display
            }

            # Dessin des nœuds et des labels
            nx.draw_networkx_nodes(
                G,
                display_pos,
                nodelist=nodes_to_display,
                node_color=node_colors,
                node_size=2000,
            )
            nx.draw_networkx_labels(G, display_pos, labels=display_labels, font_size=10)

            # Définir les arêtes à afficher
            if display_all_edges:
                # Afficher toutes les arêtes entre les sommets affichés
                if display_all_vertices:
                    all_edges = [
                        (u, v)
                        for u, v in G.edges()
                        if u in nodes_to_display and v in nodes_to_display
                    ]
                    nx.draw_networkx_edges(
                        G,
                        display_pos,
                        edgelist=all_edges,
                        edge_color="lightgray",
                        width=1,
                        arrows=True,
                    )
                else:
                    # Si on n'affiche que les sommets de la solution, on peut avoir des arêtes supplémentaires
                    all_solution_edges = [
                        (u, v)
                        for u, v in G.edges()
                        if u in solution_nodes and v in solution_nodes
                    ]
                    nx.draw_networkx_edges(
                        G,
                        display_pos,
                        edgelist=all_solution_edges,
                        edge_color="lightgray",
                        width=1,
                        arrows=True,
                    )

                # Surligner les arêtes de la solution
                nx.draw_networkx_edges(
                    G,
                    display_pos,
                    edgelist=solution_edges,
                    edge_color="red",
                    width=2,
                    arrows=True,
                )
            else:
                # Afficher uniquement les arêtes de la solution
                nx.draw_networkx_edges(
                    G,
                    display_pos,
                    edgelist=solution_edges,
                    edge_color="red",
                    width=2,
                    arrows=True,
                )

            # Ajout des temps de trajet pour les arêtes de la solution
            edge_labels = {
                (u, v): f"{self.travels_duration_matrix_sec[u][v]}s"
                for u, v in solution_edges
            }
            nx.draw_networkx_edge_labels(
                G, display_pos, edge_labels=edge_labels, font_color="red"
            )

            plt.title(
                f"Optimal solution : {self.solution.score} points in {self.solution.duration}s"
            )
        else:
            # Affichage normal si pas de solution
            labels = {
                i: (
                    (
                        "Start"
                        if i == self.start_node
                        else (
                            "End"
                            if i == self.end_node
                            else f"{i}\nS: {self.tasks_scores[i - 1]}\nD: {self.tasks_duration_sec[i - 1]}s"
                        )
                    )
                    if (
                        i == self.start_node
                        or i == self.end_node
                        or (i > 0 and i < len(self.tasks_scores) + 1)
                    )
                    else f"{i}"
                )
                for i in range(num_nodes)
            }
            nx.draw(
                G,
                pos,
                with_labels=True,
                labels=labels,
                node_color="lightblue",
                node_size=2000,
                font_size=10,
                arrows=True,
            )
        plt.tight_layout()
        plt.show()
