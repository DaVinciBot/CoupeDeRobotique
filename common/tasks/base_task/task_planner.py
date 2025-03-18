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

    def solve(
        self, time_limit_seconds=None, save_mode=False
    ):  # TODO: fix issue : if not path is found from A->B travel time is 0 instead of inf
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
            return self.solution
        else:
            return {"message": "no solution found"}

    def visualize_solution(
        self, display_all_edges=False, display_all_vertices=True
    ):  # TODO: improve visualisation, put int 2f dor travel time
        plt.close("all")
        num_nodes = len(self.travels_duration_matrix_sec)

        # Create directed graph with explicit nodes and valid edges
        G = nx.DiGraph()
        G.add_nodes_from(range(num_nodes))

        # Add edges with validation
        valid_edges = [
            (i, j)
            for i in range(num_nodes)
            for j in range(num_nodes)
            if i != j  # and self.travels_duration_matrix_sec[i][j] > 0
        ]
        G.add_edges_from(valid_edges)

        # Create layout with guaranteed spacing
        pos = nx.spring_layout(G, seed=42, k=1.5)

        plt.figure(figsize=(12, 8))
        ax = plt.gca()

        # Draw base nodes
        base_node_color = "#e0e0e0" if display_all_vertices else "white"
        nx.draw_networkx_nodes(
            G,
            pos,
            node_size=1500,
            node_color=base_node_color,
            edgecolors="black",
            ax=ax,
        )

        # Draw all edges if requested
        if display_all_edges:
            # Draw edges with curved arrows for bidirectional connections
            for u, v in valid_edges:
                connectionstyle = None
                if G.has_edge(v, u):  # Bidirectional edge
                    # Add curvature to separate directions
                    connectionstyle = f"arc3,rad={0.3 if u < v else -0.3}"

                plt.annotate(
                    "",
                    xy=pos[v],
                    xytext=pos[u],
                    arrowprops=dict(
                        arrowstyle="->",
                        color="#808080",
                        lw=1,
                        shrinkA=15,
                        shrinkB=15,
                        connectionstyle=connectionstyle,
                    ),
                )
                # Add duration text offset from center
                if display_all_edges:
                    mid_point = [
                        (pos[u][0] + pos[v][0]) / 2,
                        (pos[u][1] + pos[v][1]) / 2,
                    ]
                    offset = (0, 0.1) if u < v else (0, -0.1)
                    plt.text(
                        mid_point[0] + offset[0],
                        mid_point[1] + offset[1],
                        f"{self.travels_duration_matrix_sec[u][v]:2f}s",
                        color="#404040",
                        fontsize=8,
                        ha="center",
                        va="center",
                    )

        # Draw solution path if available
        if self.solution:
            solution_nodes = self.solution.ordered_tasks
            solution_edges = list(zip(solution_nodes[:-1], solution_nodes[1:]))

            # Highlight solution nodes
            nx.draw_networkx_nodes(
                G,
                pos,
                nodelist=solution_nodes,
                node_color="#ff4444",
                node_size=1500,
                edgecolors="black",
                ax=ax,
            )

            # Draw solution edges with straight arrows
            for u, v in solution_edges:
                if (u, v) not in valid_edges:
                    continue

                plt.annotate(
                    "",
                    xy=pos[v],
                    xytext=pos[u],
                    arrowprops=dict(
                        arrowstyle="->", color="#ff4444", lw=3, shrinkA=15, shrinkB=15
                    ),
                )
                # Add duration label
                mid_point = [(pos[u][0] + pos[v][0]) / 2, (pos[u][1] + pos[v][1]) / 2]
                plt.text(
                    mid_point[0],
                    mid_point[1],
                    f"{self.travels_duration_matrix_sec[u][v]:2f}s",
                    color="#ff4444",
                    backgroundcolor="white",
                    ha="center",
                    va="center",
                )

        # Node labels
        labels = {}
        for node in G.nodes():
            if node == self.start_node:
                labels[node] = "START"
            elif node == self.end_node:
                labels[node] = "END"
            elif 1 <= node <= self.num_tasks:
                labels[node] = (
                    f"Task {node}\nScore: {self.tasks_scores[node-1]}\nDuration: {self.tasks_duration_sec[node-1]}s"
                )
            else:
                labels[node] = f"Node {node}"

        nx.draw_networkx_labels(G, pos, labels, ax=ax, font_size=9)

        plt.title(
            f"Optimal Solution: {self.solution.score} points"
            + (f" in {self.solution.duration}s" if self.solution else "")
            + "\n(Red shows solution path)"
            if self.solution
            else ""
        )
        plt.axis("off")
        plt.tight_layout()
        plt.show()
