from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import json
from tasks.base_task.task_planner_solution import TaskPlannerSolution
import networkx as nx
import matplotlib.pyplot as plt


class TaskPlanner:
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

        # Register transit callback
        def transit_callback(from_index, to_index):
            from_node = self.manager.IndexToNode(from_index)
            to_node = self.manager.IndexToNode(to_index)

            if from_node == self.start_node or from_node == self.end_node:
                service_time = 0
            else:
                service_time = self.tasks_duration_sec[from_node - 1]

            return service_time + self.travels_duration_matrix_sec[from_node][to_node]

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

        # Set arc cost to transit callback (for routing logic)
        self.routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    def solve(self, time_limit_seconds=None, save_mode=False):
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
        )
        search_parameters.local_search_metaheuristic = (
            routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
        )
        if time_limit_seconds:
            search_parameters.time_limit.seconds = time_limit_seconds
        else:
            search_parameters.time_limit.seconds = self.solve_limit_seconds

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
                with open("solution.json", "w") as f:
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

    def visualize_solution(self):
        num_nodes = len(self.travels_duration_matrix_sec)
        G = nx.DiGraph()

        # Add edges with travel time weights
        for i in range(num_nodes):
            for j in range(i + 1, num_nodes):
                if self.travels_duration_matrix_sec[i][j] > 0:
                    G.add_edge(i, j, weight=self.travels_duration_matrix_sec[i][j])
                    G.add_edge(j, i, weight=self.travels_duration_matrix_sec[j][i])

        # Node positions for clearer display
        pos = nx.spring_layout(G, seed=42, k=0.5)  # Adjust 'k' to control node distance

        # Add task scores to corresponding nodes
        labels = {
            i: f"{i}:{self.tasks_scores[i-1]}" if 0 < i < num_nodes - 1 else str(i)
            for i in range(num_nodes)
        }

        plt.figure(figsize=(15, 5))

        if self.solution:
            # Draw graph with optimal solution highlighted
            G_opt = nx.DiGraph()
            for i in range(len(self.solution.ordered_tasks) - 1):
                G_opt.add_edge(
                    self.solution.ordered_tasks[i],
                    self.solution.ordered_tasks[i + 1],
                    weight=self.travels_duration_matrix_sec[
                        self.solution.ordered_tasks[i]
                    ][self.solution.ordered_tasks[i + 1]],
                )

            plt.subplot(1, 2, 2)
            nx.draw(
                G,
                pos,
                with_labels=True,
                labels=labels,
                node_color="lightblue",
                edge_color="gray",
                node_size=1000,
                font_size=10,
            )
            nx.draw_networkx_edges(
                G, pos, edgelist=G_opt.edges, edge_color="red", width=2
            )
            edge_labels_opt = {
                (i, j): self.travels_duration_matrix_sec[i][j] for i, j in G_opt.edges
            }
            nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels_opt)
            edge_labels = {
                (i, j): self.travels_duration_matrix_sec[i][j] for i, j in G.edges
            }
            nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
            plt.title(
                f"Graph with optimal solution highlighted, {self.solution.score} points in {self.solution.duration} sec"
            )
        else:
            # Draw input graph
            plt.subplot(1, 2, 1)
            nx.draw(
                G,
                pos,
                with_labels=True,
                labels=labels,
                node_color="lightblue",
                edge_color="gray",
                node_size=1000,
                font_size=10,
            )
            edge_labels = {
                (i, j): self.travels_duration_matrix_sec[i][j] for i, j in G.edges
            }
            nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
            plt.title("Graph with optimal solution")

        plt.show()
