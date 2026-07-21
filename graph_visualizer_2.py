import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import networkx as nx
import re

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


# PARSER (graph)
def parse_graph(vertex_text, edge_text):
    try:
        # Extract vertices
        vertex_numbers = re.findall(r'\d+', vertex_text)
        V = set(map(int, vertex_numbers))
        # Extract edges
        edge_pairs = re.findall(r'\{(\d+),(\d+)\}', edge_text)
        E = set()
        for u, v in edge_pairs:
            edge = frozenset({int(u), int(v)})
            E.add(edge)
        return V, E
    except Exception as e:
        messagebox.showerror("Parsing Error", str(e))
        return None, None


# PARSER (highlight vertices, e.g. "{1,3,4}")
def parse_highlight_vertices(text):
    try:
        numbers = re.findall(r'\d+', text)
        return set(map(int, numbers))
    except Exception as e:
        messagebox.showerror("Parsing Error", str(e))
        return None


# PARSER (highlight path, e.g. "1,2,3,4" -> sequence of vertices)
def parse_highlight_path(text):
    try:
        numbers = re.findall(r'\d+', text)
        return [int(n) for n in numbers]
    except Exception as e:
        messagebox.showerror("Parsing Error", str(e))
        return None


# GLOBAL STATE (kept so highlighting reuses the same graph/layout
# instead of re-parsing / re-computing spring_layout each time)
current_G = None
current_pos = None


# CORE RENDER FUNCTION
def render_graph(highlight_nodes=None, highlight_edges=None):
    """Draws current_G / current_pos onto ax, coloring any requested
    nodes/edges red. highlight_edges should be a set of frozenset({u, v})."""
    global canvas

    if current_G is None:
        return

    highlight_nodes = highlight_nodes or set()
    highlight_edges = highlight_edges or set()

    ax.clear()

    node_colors = [
        "red" if n in highlight_nodes else "#87CEEB"
        for n in current_G.nodes()
    ]
    edge_colors = []
    edge_widths = []
    for u, v in current_G.edges():
        if frozenset({u, v}) in highlight_edges:
            edge_colors.append("red")
            edge_widths.append(3.0)
        else:
            edge_colors.append("black")
            edge_widths.append(1.0)

    nx.draw(
        current_G,
        current_pos,
        ax=ax,
        with_labels=True,
        node_size=1200,
        font_size=12,
        node_color=node_colors,
        edge_color=edge_colors,
        width=edge_widths,
    )
    ax.set_title("Graph Visualization")
    canvas.draw()


# DRAW GRAPH (parses text boxes, rebuilds graph + layout from scratch)
def draw_graph():
    global current_G, current_pos

    vertex_text = vertex_entry.get("1.0", tk.END)
    edge_text = edge_entry.get("1.0", tk.END)

    V, E = parse_graph(vertex_text, edge_text)
    if V is None:
        return

    graph = Graph(V, E)

    G = nx.Graph()
    for v in graph.V:
        G.add_node(v)
    for edge in graph.E:
        u, v = tuple(edge)
        G.add_edge(u, v)

    current_G = G
    current_pos = nx.spring_layout(G)

    render_graph()  # no highlights on a fresh draw


# HIGHLIGHT GRAPH (re-renders the *existing* graph/layout with highlights)
def highlight_graph():
    if current_G is None:
        messagebox.showinfo("No Graph", "Draw a graph first (click Enter).")
        return

    mode = highlight_mode.get()

    if mode == "none":
        render_graph()
        return

    if mode == "vertices":
        text = highlight_vertex_entry.get("1.0", tk.END)
        nodes = parse_highlight_vertices(text)
        if nodes is None:
            return
        # only keep nodes that actually exist in the graph
        nodes = {n for n in nodes if n in current_G.nodes()}
        render_graph(highlight_nodes=nodes)

    elif mode == "path":
        text = highlight_path_entry.get("1.0", tk.END)
        path = parse_highlight_path(text)
        if path is None:
            return

        nodes = {n for n in path if n in current_G.nodes()}

        edges = set()
        missing_edges = []
        for u, v in zip(path, path[1:]):
            if current_G.has_edge(u, v):
                edges.add(frozenset({u, v}))
            else:
                missing_edges.append((u, v))

        if missing_edges:
            messagebox.showwarning(
                "Missing Edges",
                "The following consecutive pairs in the path are not edges "
                f"in the graph and were skipped: {missing_edges}",
            )

        render_graph(highlight_nodes=nodes, highlight_edges=edges)


# MAIN WINDOW
root = tk.Tk()
root.title("Interactive Graph Theory Visualizer")
root.geometry("1300x700")

# LEFT PANEL (SCRIPTING)
left_frame = tk.Frame(root, width=420, bg="#FFFCFC")
left_frame.pack(side=tk.LEFT, fill=tk.Y)

# ---------- Title ----------
title_label = tk.Label(left_frame, text="Graph Input", font=("Arial", 18), bg="#FFFCFC")
title_label.pack(pady=20)

# ---------- Vertex Input ----------
vertex_label = tk.Label(left_frame, text="Vertices V", bg="#FFFCFC")
vertex_label.pack()
vertex_entry = tk.Text(left_frame, height=3, width=35, font=("Consolas", 12))
vertex_entry.pack(pady=10)
vertex_entry.insert(tk.END, "{1,2,3,4}")

# ---------- Edge Input ----------
edge_label = tk.Label(left_frame, text="Edges E", bg="#FFFCFC")
edge_label.pack()
edge_entry = tk.Text(left_frame, height=10, width=35, font=("Bookman", 12))
edge_entry.pack(pady=10)
edge_entry.insert(tk.END, "{{1,2},{2,3},{3,4},{4,1},{1,3}}")

# ---------- Enter Button ----------
draw_button = tk.Button(
    left_frame, text="Enter", font=("Arial", 14), command=draw_graph
)
draw_button.pack(pady=10)

# ---------- Separator ----------
separator = tk.Frame(left_frame, height=2, bg="#cccccc", width=380)
separator.pack(pady=15, fill=tk.X, padx=10)

# ---------- Highlight Section ----------
highlight_title = tk.Label(
    left_frame, text="Highlight", font=("Arial", 18), bg="#FFFCFC"
)
highlight_title.pack(pady=(0, 10))

highlight_mode = tk.StringVar(value="none")

mode_frame = tk.Frame(left_frame, bg="#FFFCFC")
mode_frame.pack(pady=5)

none_radio = tk.Radiobutton(
    mode_frame, text="None", variable=highlight_mode, value="none", bg="#FFFCFC"
)
vertices_radio = tk.Radiobutton(
    mode_frame, text="Vertices", variable=highlight_mode, value="vertices", bg="#FFFCFC"
)
path_radio = tk.Radiobutton(
    mode_frame, text="Path", variable=highlight_mode, value="path", bg="#FFFCFC"
)
none_radio.pack(side=tk.LEFT, padx=5)
vertices_radio.pack(side=tk.LEFT, padx=5)
path_radio.pack(side=tk.LEFT, padx=5)

# ---------- Highlight Vertices Input ----------
highlight_vertex_label = tk.Label(
    left_frame, text="Vertices to highlight, e.g. {1,3}", bg="#FFFCFC"
)
highlight_vertex_label.pack(pady=(10, 0))
highlight_vertex_entry = tk.Text(left_frame, height=2, width=35, font=("Consolas", 12))
highlight_vertex_entry.pack(pady=5)
highlight_vertex_entry.insert(tk.END, "{1,3}")

# ---------- Highlight Path Input ----------
highlight_path_label = tk.Label(
    left_frame, text="Path to highlight, e.g. 1,2,3,4", bg="#FFFCFC"
)
highlight_path_label.pack(pady=(10, 0))
highlight_path_entry = tk.Text(left_frame, height=2, width=35, font=("Consolas", 12))
highlight_path_entry.pack(pady=5)
highlight_path_entry.insert(tk.END, "1,2,3,4")

# ---------- Highlight Button ----------
highlight_button = tk.Button(
    left_frame, text="Highlight", font=("Arial", 14), command=highlight_graph
)
highlight_button.pack(pady=15)

# RIGHT PANEL (GRAPH DISPLAY)
right_frame = tk.Frame(root)
right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

# ---------- Matplotlib Figure ----------
fig, ax = plt.subplots(figsize=(7, 7))
canvas = FigureCanvasTkAgg(fig, master=right_frame)
canvas_widget = canvas.get_tk_widget()
canvas_widget.pack(fill=tk.BOTH, expand=True)

def main():
    print("starting draw_graph")
    draw_graph()
    print("starting mainloop")
    root.mainloop()
    print("mainloop exited")

if __name__ == "__main__":
    main()
