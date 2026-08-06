# Interactive Graph Theory Visualizer — How It Works

A Tkinter + NetworkX + Matplotlib desktop app for building an undirected graph from text input, rendering it, and highlighting specific vertices or a path through it.

---

## 1. Overview

The app has two halves:

- **Left panel (input/controls):** text boxes for vertices and edges, an "Enter" button to draw the graph, and a "Highlight" section for coloring vertices or a path.
- **Right panel (display):** a Matplotlib figure embedded in the Tkinter window via `FigureCanvasTkAgg`, showing the current graph layout.

The core idea: parse user text → build a graph → lay it out once → redraw (with or without highlights) without recomputing the layout every time.

---

## 2. Example Screenshot

<img width="1918" height="1078" alt="image" src="https://github.com/user-attachments/assets/dc727291-e507-44c9-924c-a76b00cc5939" />


*Replace `screenshot.png` above with an actual capture of the app — e.g. the default graph `{1,2,3,4}` / `{{1,2},{2,3},{3,4},{4,1},{1,3}}` with a highlighted path — placed in the same folder as this file.*

---

## 3. Data Model — `Graph` class

```python
class Graph:
    def __init__(self, V, E):
        self.V = V
        self.E = E
        self.adj = self.build_adjacency_list()
```

- `V` is a `set` of integer vertex labels.
- `E` is a `set` of `frozenset({u, v})` pairs (using `frozenset` so edges are unordered and hashable/deduplicated automatically).
- `build_adjacency_list()` builds a dict mapping each vertex to the `set` of its neighbors, by iterating over `E` and adding both directions.

This class is a lightweight internal representation; it's converted into a `networkx.Graph` immediately after being built (see §5).

---

## 4. Parsing Functions

All parsing is regex-based and tolerant of loose formatting (extra spaces, curly braces, etc.).

| Function | Input example | Output |
|---|---|---|
| `parse_graph(vertex_text, edge_text)` | `"{1,2,3,4}"`, `"{{1,2},{2,3}}"` | `(V, E)` — a set of ints and a set of `frozenset` edges |
| `parse_highlight_vertices(text)` | `"{1,3}"` | `{1, 3}` |
| `parse_highlight_path(text)` | `"1,2,3,4"` | `[1, 2, 3, 4]` (ordered list, not a set) |

Key details:
- `parse_graph` uses `re.findall(r'\d+', vertex_text)` to just grab every number for vertices, and `re.findall(r'\{(\d+),(\d+)\}', edge_text)` to grab `{u,v}` pairs for edges.
- Any parsing exception pops up a `messagebox.showerror` and returns `None` (or `None, None`), which callers check before proceeding.
- Path parsing preserves **order**, since a path's edges depend on the sequence of vertices, not just membership.

---

## 5. Global State & Rendering Pipeline

```python
current_G = None
current_pos = None
```

These two globals hold the **already-built** NetworkX graph and its **spring layout** (node positions). They exist so that clicking "Highlight" doesn't rebuild the graph or recompute `spring_layout` (which is randomized/expensive) — it just redraws the same graph with different colors.

### `draw_graph()` — full rebuild
1. Reads both text boxes.
2. Parses them into `V`, `E` via `parse_graph`.
3. Builds a `Graph` instance, then converts it into an `nx.Graph` (`G`) by adding all nodes and edges.
4. Computes `nx.spring_layout(G)` once and stores it in `current_pos`.
5. Stores `G` in `current_G`.
6. Calls `render_graph()` with no highlights.

### `render_graph(highlight_nodes=None, highlight_edges=None)` — the actual drawing
1. Clears the Matplotlib axis (`ax.clear()`).
2. Builds a per-node color list: red if the node is in `highlight_nodes`, else sky blue (`#87CEEB`).
3. Builds per-edge color/width lists: red and thick (`3.0`) if the edge is in `highlight_edges` (compared as `frozenset({u,v})`), else black and thin (`1.0`).
4. Calls `nx.draw(...)` with those colors onto the stored `current_pos` layout.
5. Sets the title and calls `canvas.draw()` to refresh the embedded Tkinter canvas.

### `highlight_graph()` — highlight without rebuilding
Triggered by the "Highlight" button. Branches on the selected radio mode (`highlight_mode`, a `tk.StringVar`):

- **`"none"`** → just calls `render_graph()` with no highlights (resets colors).
- **`"vertices"`** → parses the vertex-highlight text box, filters out any node not present in the current graph, and calls `render_graph(highlight_nodes=...)`.
- **`"path"`** → parses the path text box into an ordered list, then:
  - Builds `nodes` = the set of listed vertices that actually exist in the graph.
  - Walks consecutive pairs `zip(path, path[1:])`; for each pair, if `current_G.has_edge(u, v)` is true, adds `frozenset({u,v})` to the highlighted edge set — otherwise it's recorded as a "missing edge."
  - If any consecutive pair isn't a real edge, shows a warning listing them (so the user knows part of their "path" wasn't actually connected).
  - Calls `render_graph(highlight_nodes=nodes, highlight_edges=edges)`.

If no graph has been drawn yet, `highlight_graph()` shows an info dialog telling the user to draw one first.

---

## 6. UI Layout (Tkinter)

**Window:** `1300x700`, split into `left_frame` (fixed width, packed `LEFT`) and `right_frame` (expands to fill, packed `RIGHT`).

**Left frame contents (top to bottom):**
1. Title label — "Graph Input"
2. `vertex_entry` — multi-line `Text` box, default `{1,2,3,4}`
3. `edge_entry` — multi-line `Text` box, default `{{1,2},{2,3},{3,4},{4,1},{1,3}}`
4. **Enter** button → `draw_graph`
5. A thin separator `Frame`
6. "Highlight" section title
7. Radio buttons (`None` / `Vertices` / `Path`) bound to `highlight_mode`
8. `highlight_vertex_entry` — default `{1,3}`
9. `highlight_path_entry` — default `1,2,3,4`
10. **Highlight** button → `highlight_graph`

**Right frame contents:**
- A single Matplotlib `Figure`/`Axes` (`fig, ax`), embedded via `FigureCanvasTkAgg`, packed to fill the whole panel.

---

## 7. Program Entry Point

```python
def main():
    draw_graph()      # draws the default graph on startup
    root.mainloop()    # starts the Tkinter event loop
```

So the app boots with the default `{1,2,3,4}` / `{{1,2},{2,3},{3,4},{4,1},{1,3}}` graph already rendered, then waits for user interaction.

---

## 8. Typical Usage Flow

1. User edits the **Vertices** and **Edges** boxes, clicks **Enter** → `draw_graph()` parses input, rebuilds the graph, computes a fresh layout, and renders it in blue/black.
2. User selects a highlight mode (Vertices or Path), fills in the corresponding box, clicks **Highlight** → `highlight_graph()` re-renders the *same* graph/layout with the requested nodes/edges in red, without disturbing node positions.
3. Switching back to **None** and clicking **Highlight** clears all highlighting.

---

## 9. Notable Design Choices

- **Edges as `frozenset`:** makes `{1,2}` and `{2,1}` the same object, which naturally deduplicates and simplifies membership checks (`frozenset({u,v}) in highlight_edges`).
- **Layout caching (`current_pos`):** `spring_layout` is a force-directed algorithm with some randomness — recomputing it on every highlight would make nodes jump around. Caching it keeps the visualization stable while highlighting.
- **Graceful degradation for paths:** rather than failing outright when a path references a non-edge, the app highlights what it can and warns about the rest.
- **Separation of concerns:** parsing, data modeling (`Graph`), rendering (`render_graph`), and UI callbacks (`draw_graph`, `highlight_graph`) are all distinct, making the highlight/redraw logic reusable.
