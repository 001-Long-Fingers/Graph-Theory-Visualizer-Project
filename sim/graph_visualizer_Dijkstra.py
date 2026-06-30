import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import networkx as nx
import re
import heapq

# GRAPH CLASS
class Graph:
    def __init__(self, V, E):
        self.V = V
        self.E = E
        self.adj = self.build_adjacency_list()

    def build_adjacency_list(self):
        adj = {v: set() for v in self.V}
        for edge in self.E:
            u, v = tuple(edge)
            adj[u].add(v)
            adj[v].add(u)
        return adj


# DIJKSTRA'S ALGORITHM (returns ALL shortest paths)
def dijkstra_all_paths(graph, source, target):
    # dist[v] = shortest distance from source to v
    dist = {v: float('inf') for v in graph.V}
    dist[source] = 0

    # predecessors[v] = list of nodes that lead to v on a shortest path
    predecessors = {v: [] for v in graph.V}

    # Min-heap: (distance, node)
    heap = [(0, source)]

    while heap:
        d, u = heapq.heappop(heap)
        if d > dist[u]:
            continue
        for neighbor in graph.adj[u]:
            new_dist = dist[u] + 1  # unweighted: each edge has weight 1
            if new_dist < dist[neighbor]:
                dist[neighbor] = new_dist
                predecessors[neighbor] = [u]
                heapq.heappush(heap, (new_dist, neighbor))
            elif new_dist == dist[neighbor]:
                predecessors[neighbor].append(u)

    # Reconstruct all shortest paths via backtracking
    if dist[target] == float('inf'):
        return [], dist[target]

    all_paths = []

    def backtrack(node, path):
        if node == source:
            all_paths.append(list(reversed(path)))
            return
        for pred in predecessors[node]:
            backtrack(pred, path + [pred])

    backtrack(target, [target])
    return all_paths, dist[target]


# PARSER
def parse_graph(vertex_text, edge_text):
    try:
        vertex_numbers = re.findall(r'\d+', vertex_text)
        V = set(map(int, vertex_numbers))
        edge_pairs = re.findall(r'\{(\d+),(\d+)\}', edge_text)
        E = set()
        for u, v in edge_pairs:
            edge = frozenset({int(u), int(v)})
            E.add(edge)
        return V, E
    except Exception as e:
        messagebox.showerror("Parsing Error", str(e))
        return None, None


# Shared graph state
current_graph = None


# DRAW GRAPH (optionally highlight a path)
def draw_graph(highlight_edges=None, highlight_nodes=None):
    global canvas, current_graph
    vertex_text = vertex_entry.get("1.0", tk.END)
    edge_text = edge_entry.get("1.0", tk.END)
    V, E = parse_graph(vertex_text, edge_text)
    if V is None:
        return

    current_graph = Graph(V, E)
    ax.clear()

    G = nx.Graph()
    for v in current_graph.V:
        G.add_node(v)
    for edge in current_graph.E:
        u, v = tuple(edge)
        G.add_edge(u, v)

    pos = nx.spring_layout(G, seed=42)

    # Default colors
    node_colors = []
    for node in G.nodes():
        if highlight_nodes and node in highlight_nodes:
            node_colors.append("#FF6B6B")
        else:
            node_colors.append("#4A90D9")

    # Edge colors
    edge_colors = []
    for u, v in G.edges():
        if highlight_edges and (
            (u, v) in highlight_edges or (v, u) in highlight_edges
        ):
            edge_colors.append("#FF6B6B")
        else:
            edge_colors.append("#888888")

    edge_widths = []
    for u, v in G.edges():
        if highlight_edges and (
            (u, v) in highlight_edges or (v, u) in highlight_edges
        ):
            edge_widths.append(4.0)
        else:
            edge_widths.append(1.5)

    nx.draw(
        G, pos, ax=ax,
        with_labels=True,
        node_size=1200,
        font_size=12,
        node_color=node_colors,
        edge_color=edge_colors,
        width=edge_widths,
        font_color="white",
        font_weight="bold"
    )
    ax.set_title("Graph Visualization", fontsize=14)
    canvas.draw()


# FIND SHORTEST PATH
def find_shortest_path():
    global current_graph
    path_input = path_entry.get("1.0", tk.END).strip()

    # Re-parse graph in case it changed
    vertex_text = vertex_entry.get("1.0", tk.END)
    edge_text = edge_entry.get("1.0", tk.END)
    V, E = parse_graph(vertex_text, edge_text)
    if V is None:
        return
    current_graph = Graph(V, E)

    # Parse source and target
    match = re.findall(r'\d+', path_input)
    if len(match) < 2:
        path_result_text.config(state=tk.NORMAL)
        path_result_text.delete("1.0", tk.END)
        path_result_text.insert(tk.END, "⚠ Enter two node numbers,\ne.g.  3,6")
        path_result_text.config(state=tk.DISABLED)
        return

    source, target = int(match[0]), int(match[1])

    if source not in current_graph.V or target not in current_graph.V:
        path_result_text.config(state=tk.NORMAL)
        path_result_text.delete("1.0", tk.END)
        path_result_text.insert(
            tk.END,
            f"⚠ Node {source} or {target} not in graph."
        )
        path_result_text.config(state=tk.DISABLED)
        return

    if source == target:
        path_result_text.config(state=tk.NORMAL)
        path_result_text.delete("1.0", tk.END)
        path_result_text.insert(tk.END, f"Source and target are the same node ({source}).")
        path_result_text.config(state=tk.DISABLED)
        return

    all_paths, dist = dijkstra_all_paths(current_graph, source, target)

    path_result_text.config(state=tk.NORMAL)
    path_result_text.delete("1.0", tk.END)

    if not all_paths:
        path_result_text.insert(
            tk.END,
            f"No path found between {source} and {target}."
        )
        path_result_text.config(state=tk.DISABLED)
        draw_graph()
        return

    # Build result string
    result_lines = [
        f"Shortest distance: {dist}\n",
        f"Number of shortest paths: {len(all_paths)}\n",
        "─" * 28 + "\n"
    ]
    for i, path in enumerate(all_paths, 1):
        arrow_path = " → ".join(map(str, path))
        result_lines.append(f"Path {i}: {arrow_path}\n")

    path_result_text.insert(tk.END, "".join(result_lines))
    path_result_text.config(state=tk.DISABLED)

    # Highlight the first shortest path on the graph
    highlight_edges = set()
    first_path = all_paths[0]
    for i in range(len(first_path) - 1):
        highlight_edges.add((first_path[i], first_path[i + 1]))

    highlight_nodes = set(first_path)
    draw_graph(highlight_edges=highlight_edges, highlight_nodes=highlight_nodes)


# CLEAR HIGHLIGHT
def clear_highlight():
    path_result_text.config(state=tk.NORMAL)
    path_result_text.delete("1.0", tk.END)
    path_result_text.config(state=tk.DISABLED)
    path_entry.delete("1.0", tk.END)
    draw_graph()


# ─────────────────────────────────────────
# MAIN WINDOW
# ─────────────────────────────────────────
root = tk.Tk()
root.title("Interactive Graph Theory Visualizer")
root.geometry("1300x750")
root.configure(bg="#1E1E2E")

# ─── LEFT PANEL ───────────────────────────
left_frame = tk.Frame(root, width=420, bg="#1E1E2E")
left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(10, 0), pady=10)
left_frame.pack_propagate(False)

# ---------- Title ----------
title_label = tk.Label(
    left_frame,
    text="Graph Input",
    font=("Courier", 18, "bold"),
    bg="#1E1E2E",
    fg="#CDD6F4"
)
title_label.pack(pady=(20, 10))

# ---------- Vertex Input ----------
vertex_label = tk.Label(
    left_frame,
    text="Vertices V",
    font=("Courier", 11),
    bg="#1E1E2E",
    fg="#89B4FA"
)
vertex_label.pack(anchor="w", padx=20)

vertex_entry = tk.Text(
    left_frame,
    height=3,
    width=38,
    font=("Courier", 12),
    bg="#313244",
    fg="#CDD6F4",
    insertbackground="#CDD6F4",
    relief=tk.FLAT,
    padx=8,
    pady=6
)
vertex_entry.pack(pady=(4, 10), padx=20)
vertex_entry.insert(tk.END, "{1,2,3,4,5,6}")

# ---------- Edge Input ----------
edge_label = tk.Label(
    left_frame,
    text="Edges E",
    font=("Courier", 11),
    bg="#1E1E2E",
    fg="#89B4FA"
)
edge_label.pack(anchor="w", padx=20)

edge_entry = tk.Text(
    left_frame,
    height=8,
    width=38,
    font=("Courier", 12),
    bg="#313244",
    fg="#CDD6F4",
    insertbackground="#CDD6F4",
    relief=tk.FLAT,
    padx=8,
    pady=6
)
edge_entry.pack(pady=(4, 10), padx=20)
edge_entry.insert(
    tk.END,
    "{{1,2},{2,3},{3,4},{4,1},{1,3},{3,6},{4,5},{5,6}}"
)

# ---------- Draw Button ----------
draw_button = tk.Button(
    left_frame,
    text="Draw Graph",
    font=("Courier", 13, "bold"),
    bg="#89B4FA",
    fg="#1E1E2E",
    relief=tk.FLAT,
    padx=10,
    pady=6,
    cursor="hand2",
    command=lambda: draw_graph()
)
draw_button.pack(pady=(6, 20), padx=20, fill=tk.X)

# ─── SEPARATOR ────────────────────────────
sep = tk.Frame(left_frame, height=2, bg="#45475A")
sep.pack(fill=tk.X, padx=20, pady=(0, 16))

# ─── SHORTEST PATH PANEL ──────────────────
sp_title = tk.Label(
    left_frame,
    text="Find Shortest Path",
    font=("Courier", 16, "bold"),
    bg="#1E1E2E",
    fg="#A6E3A1"
)
sp_title.pack(pady=(0, 6))

sp_subtitle = tk.Label(
    left_frame,
    text="Uses Dijkstra's Algorithm",
    font=("Courier", 9),
    bg="#1E1E2E",
    fg="#6C7086"
)
sp_subtitle.pack(pady=(0, 12))

path_label = tk.Label(
    left_frame,
    text="Source, Target  (e.g. 3,6)",
    font=("Courier", 11),
    bg="#1E1E2E",
    fg="#89B4FA"
)
path_label.pack(anchor="w", padx=20)

path_entry = tk.Text(
    left_frame,
    height=2,
    width=38,
    font=("Courier", 13),
    bg="#313244",
    fg="#A6E3A1",
    insertbackground="#A6E3A1",
    relief=tk.FLAT,
    padx=8,
    pady=6
)
path_entry.pack(pady=(4, 10), padx=20)

# Button row
btn_row = tk.Frame(left_frame, bg="#1E1E2E")
btn_row.pack(fill=tk.X, padx=20)

find_button = tk.Button(
    btn_row,
    text="Find Path",
    font=("Courier", 12, "bold"),
    bg="#A6E3A1",
    fg="#1E1E2E",
    relief=tk.FLAT,
    padx=10,
    pady=6,
    cursor="hand2",
    command=find_shortest_path
)
find_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 6))

clear_button = tk.Button(
    btn_row,
    text="Clear",
    font=("Courier", 12),
    bg="#45475A",
    fg="#CDD6F4",
    relief=tk.FLAT,
    padx=10,
    pady=6,
    cursor="hand2",
    command=clear_highlight
)
clear_button.pack(side=tk.LEFT, expand=True, fill=tk.X)

# Result box
path_result_text = tk.Text(
    left_frame,
    height=9,
    width=38,
    font=("Courier", 11),
    bg="#181825",
    fg="#CDD6F4",
    relief=tk.FLAT,
    padx=10,
    pady=8,
    state=tk.DISABLED,
    wrap=tk.WORD
)
path_result_text.pack(pady=(12, 10), padx=20)

# Tag for distance highlight
path_result_text.tag_configure("distance", foreground="#F38BA8", font=("Courier", 11, "bold"))

# ─── RIGHT PANEL ──────────────────────────
right_frame = tk.Frame(root, bg="#1E1E2E")
right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

fig, ax = plt.subplots(figsize=(8, 7))
fig.patch.set_facecolor("#1E1E2E")
ax.set_facecolor("#1E1E2E")

canvas = FigureCanvasTkAgg(fig, master=right_frame)
canvas_widget = canvas.get_tk_widget()
canvas_widget.pack(fill=tk.BOTH, expand=True)


def main():
    draw_graph()
    root.mainloop()


if __name__ == "__main__":
    main()
