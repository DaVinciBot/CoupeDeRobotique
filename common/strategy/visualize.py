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
