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

# PARSER

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

        messagebox.showerror(
            "Parsing Error",
            str(e)
        )

        return None, None

# DRAW GRAPH

def draw_graph():

    global canvas

    vertex_text = vertex_entry.get("1.0", tk.END)

    edge_text = edge_entry.get("1.0", tk.END)

    V, E = parse_graph(vertex_text, edge_text)

    if V is None:
        return

    graph = Graph(V, E)

    # Clear old figure
    ax.clear()

    # Create NetworkX graph
    G = nx.Graph()

    # Add vertices
    for v in graph.V:
        G.add_node(v)

    # Add edges
    for edge in graph.E:

        u, v = tuple(edge)

        G.add_edge(u, v)

    # Layout
    pos = nx.spring_layout(G)

    # Draw graph
    nx.draw(
        G,
        pos,
        ax=ax,
        with_labels=True,
        node_size=1200,
        font_size=12
    )

    ax.set_title("Graph Visualization")

    canvas.draw()

# MAIN WINDOW

root = tk.Tk()

root.title("Interactive Graph Theory Visualizer")

root.geometry("1200x700")

# LEFT PANEL (SCRIPTING)

left_frame = tk.Frame(
    root,
    width=400,
    bg="#FFFCFC"
)

left_frame.pack(
    side=tk.LEFT,
    fill=tk.Y
)


# ---------- Title ----------

title_label = tk.Label(
    left_frame,
    text="Graph Input",
    font=("Arial", 18)
)

title_label.pack(pady=20)


# ---------- Vertex Input ----------

vertex_label = tk.Label(
    left_frame,
    text="Vertices V"
)

vertex_label.pack()

vertex_entry = tk.Text(
    left_frame,
    height=3,
    width=35,
    font=("Consolas", 12)
)

vertex_entry.pack(pady=10)

vertex_entry.insert(
    tk.END,
    "{1,2,3,4}"
)


# ---------- Edge Input ----------

edge_label = tk.Label(
    left_frame,
    text="Edges E"
)

edge_label.pack()

edge_entry = tk.Text(
    left_frame,
    height=10,
    width=35,
    font=("Bookman", 12)
)

edge_entry.pack(pady=10)

edge_entry.insert(
    tk.END,
    "{{1,2},{2,3},{3,4},{4,1},{1,3}}"
)

# ---------- Enter Button ----------

draw_button = tk.Button(
    left_frame,
    text="Enter",
    font=("Arial", 14),
    command=draw_graph
)

draw_button.pack(pady=20)


# RIGHT PANEL (GRAPH DISPLAY)

right_frame = tk.Frame(root)

right_frame.pack(
    side=tk.RIGHT,
    fill=tk.BOTH,
    expand=True
)


# ---------- Matplotlib Figure ----------

fig, ax = plt.subplots(figsize=(7,7))

canvas = FigureCanvasTkAgg(
    fig,
    master=right_frame
)

canvas_widget = canvas.get_tk_widget()

canvas_widget.pack(
    fill=tk.BOTH,
    expand=True
)

def main():

    # Initial graph rendering
    draw_graph()

    # Start GUI loop
    root.mainloop()
