# ====== Code Summary ======
# This module provides utilities for visualizing task graphs using both Graphviz and NetworkX.
# It includes functions to visualize individual task flows from a starting node or an entire subgraph.
# Nodes are rendered with their names and associated task types, and transitions are labeled by class name.
# Node statuses are visually encoded when using NetworkX visualizations.


import matplotlib.pyplot as plt
import networkx as nx
from graphviz import Digraph

from strategy.core.sub_graphs import BaseSubGraph
from strategy.core.task_nodes.base_task_node import BaseTaskNode
from strategy.core.tasks.base_task import BaseTask
from strategy.core.tasks.status import TaskStatus


def visualize_task_graph(
    start_node: BaseTaskNode,
    filename: str = "task_graph",
    view: bool = False,
) -> Digraph:
    """Recursively traverses a TaskNode graph and generates a Graphviz visual (.png).

    Args:
        start_node (BaseTaskNode): Entry point of the task graph.
        filename (str, optional): Output filename without extension. Defaults to "task_graph".
        view (bool, optional): If `True`, automatically opens the generated image. Defaults to `False`.

    Returns:
        Digraph: The generated Graphviz graph object.
    """
    dot = Digraph(comment="Strategy Graph", format="png")
    seen = set()

    def get_task_class_name(task_list: list[BaseTask] | BaseTask) -> str:
        """Get the class name of a task or a list of tasks.

        Args:
            task_list (list[BaseTask] | BaseTask): The task or list of tasks.

        Returns:
            str: The class name of the task or list of tasks.
        """
        if isinstance(task_list, list):
            return ", ".join([t.__class__.__name__ for t in task_list])
        return task_list.__class__.__name__

    def dfs(node: BaseTaskNode) -> None:
        nid = str(id(node))
        if nid in seen:
            return
        seen.add(nid)

        task_name = get_task_class_name(node.tasks)
        label = f"{node.name}\\n<{task_name}>"

        dot.node(
            nid,
            label=label,
            shape="box",
            style="rounded,filled",
            fillcolor="lightblue",
        )

        for t in node.transitions:
            target = t.target
            target_id = str(id(target))
            dfs(target)
            dot.edge(nid, target_id, label=t.__class__.__name__)

    dfs(start_node)

    out_path = dot.render(filename, cleanup=True)
    print(f"Graph rendered to {out_path}")
    if view:
        import webbrowser

        webbrowser.open(out_path)

    return dot


def visualize_entire_subgraph(
    subgraph: BaseSubGraph,
    filename: str = "full_graph",
    view: bool = False,
) -> Digraph:
    """Generates a full Graphviz visualization for a given subgraph.

    Args:
        subgraph (BaseSubGraph): Subgraph containing all task nodes.
        filename (str, optional): Output filename without extension. Defaults to "full_graph".
        view (bool, optional): If `True`, automatically opens the generated image. Defaults to `False`.

    Returns:
        Digraph: The generated Graphviz graph object.
    """
    dot = Digraph(comment="Full Strategy Graph", format="png")
    seen = set()

    def get_task_class_name(task_list: list[BaseTask] | BaseTask) -> str:
        """Get the class name of a task or a list of tasks.

        Args:
            task_list (list[BaseTask] | BaseTask): The task or list of tasks.

        Returns:
            str: The class name of the task or list of tasks.
        """
        if isinstance(task_list, list):
            return ", ".join([t.__class__.__name__ for t in task_list])
        return task_list.__class__.__name__

    def add_node(node: BaseTaskNode) -> None:
        nid = str(id(node))
        if nid in seen:
            return
        seen.add(nid)

        label = f"{node.name}\\n<{get_task_class_name(node.tasks)}>"
        dot.node(
            nid,
            label=label,
            shape="box",
            style="rounded,filled",
            fillcolor="lightblue",
        )

        for t in node.transitions:
            target = t.target
            dot.edge(nid, str(id(target)), label=t.__class__.__name__)
            add_node(target)

    for node in subgraph.get_all_nodes():
        add_node(node)

    out_path = dot.render(filename, cleanup=True)
    print(f"Graph rendered to {out_path}")
    if view:
        import webbrowser

        webbrowser.open(out_path)

    return dot


def visualize_task_graph_from_node(
    subgraph: BaseSubGraph,
    title: str = "Full Strategy Graph",
) -> None:
    """Uses NetworkX and Matplotlib to visualize the task graph with color-coded node statuses.

    Args:
        subgraph (BaseSubGraph): Subgraph containing all task nodes.
        title (str): Title for the Matplotlib plot.
    """
    graph = nx.DiGraph()

    def get_status_color(status: TaskStatus) -> str:
        return {
            TaskStatus.PENDING: "#d3d3d3",
            TaskStatus.IN_PROGRESS: "#ffdd57",
            TaskStatus.DONE: "#6bcf63",
            TaskStatus.FAILED: "#ff6f69",
            TaskStatus.TIMEOUT: "#8e44ad",
        }.get(status, "#d3d3d3")

    for node in subgraph.get_all_nodes():
        graph.add_node(node.name, status=node.status.name.lower())
        for t in node.transitions:
            graph.add_edge(node.name, t.target.name, label=t.__class__.__name__)

    pos = nx.spring_layout(graph, seed=42)
    node_colors = [
        get_status_color(TaskStatus[graph.nodes[n].get("status", "PENDING").upper()])
        for n in graph.nodes
    ]

    plt.figure(figsize=(10, 7))
    nx.draw_networkx_nodes(graph, pos, node_color=node_colors, node_size=800)
    nx.draw_networkx_labels(graph, pos, font_size=10, font_weight="bold")
    nx.draw_networkx_edges(graph, pos, arrowstyle="-|>", arrowsize=20)
    nx.draw_networkx_edge_labels(
        graph,
        pos,
        edge_labels=nx.get_edge_attributes(graph, "label"),
        font_color="gray",
        font_size=8,
    )

    plt.title(title)
    plt.axis("off")
    plt.tight_layout()
    plt.show()
