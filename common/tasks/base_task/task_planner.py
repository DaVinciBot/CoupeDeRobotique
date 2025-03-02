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
        plt.close("all")  # Close all existing figures
        num_nodes = len(self.travels_duration_matrix_sec)

        # Create complete graph for layout
        G = nx.DiGraph()
        for i in range(num_nodes):
            G.add_node(i)
            for j in range(num_nodes):
                if i != j:
                    G.add_edge(i, j, weight=self.travels_duration_matrix_sec[i][j])

        # Add end node if it's not already in the graph
        if self.end_node not in G.nodes():
            G.add_node(self.end_node)
            for i in range(num_nodes):
                G.add_edge(
                    i,
                    self.end_node,
                    weight=self.travels_duration_matrix_sec[i][self.end_node],
                )
                G.add_edge(
                    self.end_node,
                    i,
                    weight=self.travels_duration_matrix_sec[self.end_node][i],
                )

        # Use a different layout algorithm with more spacing and iterations
        pos = (
            nx.kamada_kawai_layout(G)
            if num_nodes < 50
            else nx.spring_layout(G, k=1.5, iterations=100, seed=42)
        )

        plt.figure(figsize=(15, 10))  # Larger figure
        if self.solution:
            # Extract solution path
            solution_nodes = self.solution.ordered_tasks
            solution_edges = list(zip(solution_nodes[:-1], solution_nodes[1:]))

            # Define vertices to display
            if display_all_vertices:
                nodes_to_display = list(range(num_nodes))
                if self.end_node >= num_nodes:  # Add end node if it's not in the range
                    nodes_to_display.append(self.end_node)
                node_colors = [
                    "red" if n in solution_nodes else "lightgray"
                    for n in nodes_to_display
                ]
            else:
                nodes_to_display = solution_nodes
                node_colors = ["red"] * len(nodes_to_display)

            # Only keep positions for nodes to display
            display_pos = {n: pos[n] for n in nodes_to_display if n in pos}

            # If nodes are still clustered, adjust positions
            if not display_all_vertices and len(solution_nodes) > 3:
                # Create a simple layout for just the solution path
                solution_G = nx.DiGraph()
                for edge in solution_edges:
                    if edge[0] in pos and edge[1] in pos:
                        solution_G.add_edge(edge[0], edge[1])

                # If we have nodes in the solution graph, create a more stretched layout
                if solution_G.number_of_nodes() > 0:
                    if (
                        len(solution_nodes) <= 8
                    ):  # For smaller paths, use circular layout
                        solution_pos = nx.circular_layout(solution_G, scale=2.0)
                    else:  # For larger paths, try to make it more linear
                        solution_pos = nx.shell_layout(solution_G, scale=2.0)

                    # Update display positions
                    display_pos.update(solution_pos)

            # Prepare labels for vertices to display
            display_labels = {}
            for n in nodes_to_display:
                if n == self.start_node:
                    display_labels[n] = "Start"
                elif n == self.end_node:
                    display_labels[n] = "End"
                elif 0 < n < len(self.tasks_scores) + 1:
                    display_labels[n] = (
                        f"{n}\nS: {self.tasks_scores[n-1]}\nD: {self.tasks_duration_sec[n-1]}s"
                    )
                else:
                    display_labels[n] = f"{n}"

            # Draw nodes and labels
            nx.draw_networkx_nodes(
                G,
                display_pos,
                nodelist=[n for n in nodes_to_display if n in display_pos],
                node_color=node_colors,
                node_size=2000,
                alpha=0.9,
            )
            nx.draw_networkx_labels(
                G, display_pos, labels=display_labels, font_size=10, font_weight="bold"
            )

            # Define edges to display
            if display_all_edges:
                # Display all edges between displayed vertices
                if display_all_vertices:
                    all_edges = [
                        (u, v)
                        for u, v in G.edges()
                        if u in nodes_to_display and v in nodes_to_display
                    ]
                    nx.draw_networkx_edges(
                        G,
                        display_pos,
                        edgelist=[
                            e
                            for e in all_edges
                            if e[0] in display_pos and e[1] in display_pos
                        ],
                        edge_color="lightgray",
                        width=1,
                        arrows=True,
                        alpha=0.3,
                    )
                else:
                    # If only displaying solution vertices, show possible edges between them
                    all_solution_edges = [
                        (u, v)
                        for u, v in G.edges()
                        if u in solution_nodes and v in solution_nodes
                    ]
                    nx.draw_networkx_edges(
                        G,
                        display_pos,
                        edgelist=[
                            e
                            for e in all_solution_edges
                            if e[0] in display_pos and e[1] in display_pos
                        ],
                        edge_color="lightgray",
                        width=1,
                        arrows=True,
                        alpha=0.5,
                    )

            # Always highlight solution edges
            valid_solution_edges = [
                e for e in solution_edges if e[0] in display_pos and e[1] in display_pos
            ]
            nx.draw_networkx_edges(
                G,
                display_pos,
                edgelist=valid_solution_edges,
                edge_color="red",
                width=2,
                arrows=True,
                arrowsize=15,
            )

            # Add travel times for solution edges
            edge_labels = {
                (u, v): f"{self.travels_duration_matrix_sec[u][v]}s"
                for u, v in valid_solution_edges
            }
            nx.draw_networkx_edge_labels(
                G, display_pos, edge_labels=edge_labels, font_color="red", font_size=9
            )

            plt.title(
                f"Optimal solution: {self.solution.score} points in {self.solution.duration}s",
                fontsize=14,
                fontweight="bold",
            )
        else:
            # Normal display if no solution
            labels = {}
            for i in G.nodes():
                if i == self.start_node:
                    labels[i] = "Start"
                elif i == self.end_node:
                    labels[i] = "End"
                elif 0 < i < len(self.tasks_scores) + 1:
                    labels[i] = (
                        f"{i}\nS: {self.tasks_scores[i-1]}\nD: {self.tasks_duration_sec[i-1]}s"
                    )
                else:
                    labels[i] = f"{i}"

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
        plt.axis("off")  # Hide axes
        plt.show()
