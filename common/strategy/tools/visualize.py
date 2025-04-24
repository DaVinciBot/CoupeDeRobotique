def visualize_graph_mermaid(start_node):
    """
    Parcourt récursivement tous les BaseTaskNode à partir de start_node,
    et génère un diagramme Mermaid (graph TD) listant :
     - chaque nœud avec son nom et le nom de sa Task
     - chaque transition (→)
    """
    # 1) Collecte de tous les nœuds
    visited = set()
    nodes = []

    def dfs(node):
        if node in visited:
            return
        visited.add(node)
        nodes.append(node)
        for t in node.transitions:
            dfs(t.target)

    dfs(start_node)

    # 2) Attribution d’un identifiant court à chaque nœud
    mapping = {node: f"N{i}" for i, node in enumerate(nodes)}

    # 3) Construction du texte Mermaid
    lines = ["graph TD"]
    for node, key in mapping.items():
        # on affiche nom_du_nœud\nnom_de_la_classe_de_Task
        label = f"{node.name}\\n{node.task.__class__.__name__}"
        lines.append(f'    {key}["{label}"]')
    for node in nodes:
        for t in node.transitions:
            lines.append(f"    {mapping[node]} --> {mapping[t.target]}")

    return "\n".join(lines)


from graphviz import Digraph


def visualize_task_graph(start_node, filename="task_graph", view=False):
    """
    Parcourt récursivement ton graphe de TaskNode à partir de start_node
    et génère un .png/.pdf (selon extension) avec Graphviz.

    - filename : nom du fichier sans extension
    - view     : si True, ouvre automatiquement le rendu
    """
    dot = Digraph(comment="Strategy Graph", format="png")
    seen = set()

    def dfs(node):
        # identifie chaque node par son id Python pour éviter collision de noms
        nid = str(id(node))
        if nid in seen:
            return
        seen.add(nid)

        # étiquette = nom du node + classe de la task
        label = f"{node.name}\\n<{node.task.__class__.__name__}>"
        dot.node(
            nid, label=label, shape="box", style="rounded,filled", fillcolor="lightblue"
        )

        for t in node.transitions:
            tgt_id = str(id(t.target))
            # assure-toi que la cible est aussi ajoutée
            dfs(t.target)
            # crée l'arête
            dot.edge(nid, tgt_id)

    dfs(start_node)

    # génère le fichier (PNG par défaut)
    out_path = dot.render(filename, cleanup=True)
    print(f"Graph rendered to {out_path}")
    if view:
        # tente d'ouvrir le PNG
        import webbrowser

        webbrowser.open(out_path)

    return dot


import networkx as nx
import matplotlib.pyplot as plt
from typing import Optional, Set
from strategy.core.task_nodes.base_task_node import BaseTaskNode
from strategy.core.tasks.status import TaskStatus
from strategy.core.sub_graphs import BaseSubGraph


def visualize_task_graph_from_node(subgraph: BaseSubGraph, title: str = "Full Strategy Graph"):
    import networkx as nx
    import matplotlib.pyplot as plt

    graph = nx.DiGraph()

    def get_status_color(status: TaskStatus) -> str:
        return {
            TaskStatus.PENDING: "#d3d3d3",
            TaskStatus.IN_PROGRESS: "#ffdd57",
            TaskStatus.DONE: "#6bcf63",
            TaskStatus.FAILED: "#ff6f69",
            TaskStatus.TIMEOUT: "#8e44ad"
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
    nx.draw_networkx_labels(graph, pos, font_size=10, font_weight='bold')
    nx.draw_networkx_edges(graph, pos, arrowstyle='-|>', arrowsize=20)
    nx.draw_networkx_edge_labels(graph, pos, edge_labels=nx.get_edge_attributes(graph, 'label'), font_color='gray',
                                 font_size=8)

    plt.title(title)
    plt.axis('off')
    plt.tight_layout()
    plt.show()
