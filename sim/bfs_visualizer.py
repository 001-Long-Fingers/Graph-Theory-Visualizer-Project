import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt # pyright: ignore[reportMissingModuleSource]
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg # pyright: ignore[reportMissingModuleSource]
import networkx as nx # pyright: ignore[reportMissingModuleSource]
import re
from collections import deque, OrderedDict

BG        = "#1E1E2E"
SURFACE   = "#313244"
SURFACE2  = "#181825"
OVERLAY   = "#45475A"
TEXT      = "#CDD6F4"
SUBTEXT   = "#6C7086"
BLUE      = "#89B4FA"
GREEN     = "#A6E3A1"
YELLOW    = "#F9E2AF"
RED       = "#F38BA8"
MAUVE     = "#CBA6F7"
TEAL      = "#94E2D5"

# BFS node colouring
BFS_COLORS = [
    "#F38BA8", "#FAB387", "#F9E2AF", "#A6E3A1",
    "#94E2D5", "#89DCEB", "#89B4FA", "#CBA6F7",
    "#EBA0AC", "#74C7EC",
]



class Graph:
    def __init__(self, V, E):
        self.V = sorted(V)
        self.E = E
        self.adj = self.build_adjacency_list()

    def build_adjacency_list(self):
        adj = OrderedDict((v, sorted(set())) for v in self.V)
        for edge in self.E:
            u, v = tuple(edge)
            if v not in adj[u]:
                adj[u].append(v)
            if u not in adj[v]:
                adj[v].append(u)

        for v in adj:
            adj[v] = sorted(adj[v])
        return adj


def parse_graph(vertex_text, edge_text):
    try:
        vertex_numbers = re.findall(r'\d+', vertex_text)
        if not vertex_numbers:
            raise ValueError("No vertices found.")
        V = set(map(int, vertex_numbers))
        edge_pairs = re.findall(r'\{(\d+),\s*(\d+)\}', edge_text)
        E = set()
        for u, v in edge_pairs:
            E.add(frozenset({int(u), int(v)}))
        return V, E
    except Exception as e:
        messagebox.showerror("Parsing Error", str(e))
        return None, None


def bfs(graph, start):

    visited   = set()
    queue     = deque([start])
    visited.add(start)
    rows      = []
    step      = 1
    order     = []

    while queue:
        node = queue.popleft()
        order.append(node)
        newly_added = []

        for neighbour in graph.adj[node]:
            if neighbour not in visited:
                visited.add(neighbour)
                queue.append(neighbour)
                newly_added.append(neighbour)

        rows.append({
            "step":        step,
            "node":        node,
            "neighbours":  graph.adj[node],
            "newly_added": newly_added,
            "queue_after": list(queue),
            "visited":     list(order),
        })
        step += 1

    return rows, order


current_graph = None
pos_cache     = {}


def draw_graph():
    global canvas, current_graph, pos_cache

    vertex_text = vertex_entry.get("1.0", tk.END)
    edge_text   = edge_entry.get("1.0", tk.END)
    V, E = parse_graph(vertex_text, edge_text)
    if V is None:
        return

    current_graph = Graph(V, E)
    ax.clear()
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    G = nx.Graph()
    for v in current_graph.V:
        G.add_node(v)
    for edge in current_graph.E:
        u, v = tuple(edge)
        G.add_edge(u, v)

    key = (frozenset(current_graph.V), frozenset(current_graph.E))
    if key not in pos_cache:
        pos_cache.clear()
        pos_cache[key] = nx.spring_layout(G, seed=7)
    pos = pos_cache[key]

    nx.draw_networkx_nodes(G, pos, ax=ax, node_size=1400,
                           node_color=BLUE, linewidths=2,
                           edgecolors="#5594d4")
    nx.draw_networkx_labels(G, pos, ax=ax,
                            font_size=12, font_color="black", font_weight="bold")
    nx.draw_networkx_edges(G, pos, ax=ax,
                           edge_color="#555555", width=2.0, alpha=0.9)

    ax.set_title("Graph Visualisation", fontsize=13,
                 color="black", pad=12, fontfamily="monospace")
    ax.axis("off")
    canvas.draw()


def refresh_adj_panel():
    adj_text.config(state=tk.NORMAL)
    adj_text.delete("1.0", tk.END)
    if current_graph is None:
        adj_text.config(state=tk.DISABLED)
        return
    for v in current_graph.V:
        neighbours = current_graph.adj[v]
        nbr_str    = " → ".join(map(str, neighbours)) if neighbours else "∅"
        line       = f"  {v:>3}  │  {nbr_str}\n"
        adj_text.insert(tk.END, line)
    adj_text.config(state=tk.DISABLED)


def run_bfs():
    global current_graph

    vertex_text = vertex_entry.get("1.0", tk.END)
    edge_text   = edge_entry.get("1.0", tk.END)
    V, E = parse_graph(vertex_text, edge_text)
    if V is None:
        return
    current_graph = Graph(V, E)
    refresh_adj_panel()

    # Parse start node
    start_raw = start_entry.get("1.0", tk.END).strip()
    match     = re.findall(r'\d+', start_raw)
    if not match:
        messagebox.showerror("Input Error", "Enter a starting node number.")
        return
    start = int(match[0])
    if start not in current_graph.V:
        messagebox.showerror("Input Error",
                             f"Node {start} is not in the graph.")
        return

    rows, order = bfs(current_graph, start)

    draw_graph()

    #Populate BFS table
    for row in bfs_tree.get_children():
        bfs_tree.delete(row)

    for r in rows:
        nbr_str   = ", ".join(map(str, r["neighbours"]))   or "—"
        added_str = ", ".join(map(str, r["newly_added"]))  or "—"
        queue_str = " → ".join(map(str, r["queue_after"])) or "empty"
        visit_str = " → ".join(map(str, r["visited"]))

        tag = "even" if r["step"] % 2 == 0 else "odd"
        bfs_tree.insert("", tk.END, values=(
            r["step"],
            r["node"],
            nbr_str,
            added_str,
            queue_str,
            visit_str,
        ), tags=(tag,))

    # Summary
    summary_var.set(
        f"BFS order:  " + " → ".join(map(str, order))
    )


def on_draw():
    vertex_text = vertex_entry.get("1.0", tk.END)
    edge_text   = edge_entry.get("1.0", tk.END)
    V, E = parse_graph(vertex_text, edge_text)
    if V is None:
        return
    global current_graph
    current_graph = Graph(V, E)
    draw_graph()
    refresh_adj_panel()
    # Clear table
    for row in bfs_tree.get_children():
        bfs_tree.delete(row)
    summary_var.set("")



root = tk.Tk()
root.title("BFS Graph Visualiser")
root.geometry("1480x820")
root.configure(bg=BG)


left_col = tk.Frame(root, bg=BG, width=310)
left_col.pack(side=tk.LEFT, fill=tk.Y, padx=(12, 0), pady=12)
left_col.pack_propagate(False)


def section_header(parent, text, color=BLUE):
    tk.Label(parent, text=text, font=("Courier", 13, "bold"),
             bg=BG, fg=color).pack(anchor="w", padx=4, pady=(14, 4))

def field_label(parent, text):
    tk.Label(parent, text=text, font=("Courier", 10),
             bg=BG, fg=SUBTEXT).pack(anchor="w", padx=4)

def text_box(parent, height, default=""):
    t = tk.Text(parent, height=height, width=34,
                font=("Courier", 12), bg=SURFACE, fg=TEXT,
                insertbackground=TEXT, relief=tk.FLAT,
                padx=8, pady=6, wrap=tk.WORD)
    t.pack(padx=4, pady=(2, 8))
    if default:
        t.insert(tk.END, default)
    return t

def accent_button(parent, label, cmd, color=BLUE):
    tk.Button(parent, text=label, font=("Courier", 12, "bold"),
              bg=color, fg=BG, relief=tk.FLAT,
              padx=8, pady=6, cursor="hand2", command=cmd
              ).pack(fill=tk.X, padx=4, pady=(0, 6))


section_header(left_col, "Graph Input")

field_label(left_col, "Vertices V")
vertex_entry = text_box(left_col, 2, "{1,2,3,4,5,6,7}")

field_label(left_col, "Edges E")
edge_entry = text_box(left_col, 7,
    "{{1,2},{1,3},{2,4},{2,5},{3,6},{3,7}}")

accent_button(left_col, "Draw Graph", on_draw, BLUE)


tk.Frame(left_col, height=1, bg=OVERLAY).pack(fill=tk.X, padx=4, pady=4)

section_header(left_col, "BFS Traversal", GREEN)

field_label(left_col, "Start node")
start_entry = text_box(left_col, 1, "1")

accent_button(left_col, "Run BFS", run_bfs, GREEN)

tk.Frame(left_col, height=1, bg=OVERLAY).pack(fill=tk.X, padx=4, pady=4)

section_header(left_col, "Adjacency List", MAUVE)

tk.Label(left_col, text="  node │  neighbours",
         font=("Courier", 10), bg=SURFACE2, fg=SUBTEXT,
         anchor="w").pack(fill=tk.X, padx=4)

adj_text = tk.Text(left_col, height=12, width=34,
                   font=("Courier", 12), bg=SURFACE2, fg=MAUVE,
                   insertbackground=MAUVE, relief=tk.FLAT,
                   padx=6, pady=6, state=tk.DISABLED)
adj_text.pack(padx=4, pady=(0, 6))

right_col = tk.Frame(root, bg=BG)
right_col.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True,
               padx=12, pady=12)


fig, ax = plt.subplots(figsize=(6.5, 4.5))
fig.patch.set_facecolor("white")
ax.set_facecolor("white")

canvas = FigureCanvasTkAgg(fig, master=right_col)
canvas_widget = canvas.get_tk_widget()
canvas_widget.pack(fill=tk.BOTH, expand=True)
canvas_widget.configure(bg="white", highlightthickness=0)
table_header = tk.Frame(right_col, bg=BG)
table_header.pack(fill=tk.X, pady=(10, 0))

tk.Label(table_header, text="BFS Traversal Table",
         font=("Courier", 13, "bold"), bg=BG, fg=GREEN).pack(side=tk.LEFT)

summary_var = tk.StringVar(value="")
tk.Label(table_header, textvariable=summary_var,
         font=("Courier", 11), bg=BG, fg=YELLOW).pack(side=tk.LEFT, padx=20)

# Treeview styling
style = ttk.Style()
style.theme_use("default")
style.configure("BFS.Treeview",
                background=SURFACE2,
                foreground=TEXT,
                fieldbackground=SURFACE2,
                rowheight=26,
                font=("Courier", 11),
                borderwidth=0)
style.configure("BFS.Treeview.Heading",
                background=SURFACE,
                foreground=BLUE,
                font=("Courier", 11, "bold"),
                relief="flat")
style.map("BFS.Treeview",
          background=[("selected", OVERLAY)],
          foreground=[("selected", TEXT)])
style.map("BFS.Treeview.Heading",
          background=[("active", OVERLAY)])

cols = ("Step", "Node", "Neighbours", "Newly Enqueued", "Queue After", "Visited So Far")
col_widths = (52, 58, 140, 150, 200, 280)

bfs_frame = tk.Frame(right_col, bg=BG)
bfs_frame.pack(fill=tk.BOTH, expand=False, pady=(4, 0))

bfs_tree = ttk.Treeview(bfs_frame, columns=cols, show="headings",
                         height=10, style="BFS.Treeview")
for col, w in zip(cols, col_widths):
    bfs_tree.heading(col, text=col)
    bfs_tree.column(col, width=w, anchor="center", stretch=False)

bfs_tree.tag_configure("odd",  background=SURFACE2)
bfs_tree.tag_configure("even", background="#252535")

vsb = ttk.Scrollbar(bfs_frame, orient="vertical", command=bfs_tree.yview)
bfs_tree.configure(yscrollcommand=vsb.set)
bfs_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
vsb.pack(side=tk.RIGHT, fill=tk.Y)


def main():
    on_draw()
    root.mainloop()

if __name__ == "__main__":
    main()
