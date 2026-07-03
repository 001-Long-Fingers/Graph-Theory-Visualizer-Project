INF = float('inf')


def floyd_warshall(matrix: list) -> None:
    """
    Run Floyd-Warshall on a VxV adjacency matrix and print
    the distance matrix after each k pass, then a final path table.

    Parameters
    ----------
    matrix : VxV list of lists where
               matrix[i][j] = edge weight from node i to node j
               matrix[i][i] = 0
               matrix[i][j] = INF  if no direct edge exists

    Nodes are labelled 1..V for display.

    Example (4 nodes):
        INF = float('inf')
        matrix = [
            [0,   4,   1,   INF],
            [INF, 0,   INF, 1  ],
            [INF, -2,  0,   5  ],
            [INF, INF, INF, 0  ],
        ]
    """

    V    = len(matrix)
    dist = [row[:] for row in matrix]   # work on a copy
    pred = [[None] * V for _ in range(V)]

    for i in range(V):
        for j in range(V):
            if i != j and dist[i][j] != INF:
                pred[i][j] = i

    # helpers 
    def fmt(x):
        return "∞" if x == INF else str(x)

    def print_matrix(dist, label, k=None):
        col_w  = max(max(len(fmt(dist[i][j])) for i in range(V) for j in range(V)), 2) + 2
        node_w = len(str(V)) + 1
        header = " " * (node_w + 3) + "  ".join(str(j+1).center(col_w) for j in range(V))
        sep    = " " * (node_w + 1) + "┼" + "─" * (col_w * V + 2*(V-1) + 1)
        print(f"\n  {label}")
        print(header)
        print(sep)
        for i in range(V):
            row    = "  ".join(fmt(dist[i][j]).center(col_w) for j in range(V))
            marker = "  ◄" if k is not None and i == k else ""
            print(f"  {str(i+1):>{node_w}} │ {row}{marker}")

    def fmt_row(cells, widths):
        return "│ " + " │ ".join(c.ljust(w) for c, w in zip(cells, widths)) + " │"

    def border(widths, l, m, r):
        return l + m.join("─" * (w+2) for w in widths) + r

    def reconstruct(src, tgt):
        if dist[src][tgt] == INF:
            return None
        path, cur, guard = [tgt+1], tgt, 0
        while cur != src and guard <= V:
            cur = pred[src][cur]
            path.append(cur+1)
            guard += 1
        return list(reversed(path)) if guard <= V else None

    # initial matrix 
    print(f"\nFloyd-Warshall  (V = {V})\n")
    print_matrix(dist, "k = 0  (initial)")

    # main loop 
    for k in range(V):
        changed = []
        for i in range(V):
            for j in range(V):
                if dist[i][k] == INF or dist[k][j] == INF:
                    continue
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]
                    pred[i][j] = pred[k][j]
                    changed.append((i, j))

        note = f"{len(changed)} cell(s) updated" if changed else "no change"
        print_matrix(dist, f"k = {k+1}  —  {note}", k=k)
        for (i, j) in changed:
            print(f"      dist[{i+1}][{j+1}] = {fmt(dist[i][j])}")

    # negative cycle check
    neg_cycle = any(dist[i][i] < 0 for i in range(V))

    # final path table 
    rows = []
    for i in range(V):
        for j in range(V):
            if i == j:
                continue
            path     = reconstruct(i, j)
            path_str = " → ".join(map(str, path)) if path else "unreachable"
            rows.append([str(i+1), str(j+1), fmt(dist[i][j]), path_str])

    headers    = ["From", "To", "Distance", "Shortest Path"]
    col_widths = [len(h) for h in headers]
    for row in rows:
        for ci, cell in enumerate(row):
            col_widths[ci] = max(col_widths[ci], len(cell))

    print(f"\n\n  Final Shortest-Path Table\n")
    print(border(col_widths, "┌", "┬", "┐"))
    print(fmt_row(headers, col_widths))
    print(border(col_widths, "├", "┼", "┤"))
    for row in rows:
        print(fmt_row(row, col_widths))
    print(border(col_widths, "└", "┴", "┘"))

    if neg_cycle:
        print("\n  Negative-weight cycle detected — distances are undefined.\n")
    else:
        print("\nNo negative-weight cycle detected.\n")


# examples
if __name__ == "__main__":

    print("━" * 60)
    print("EXAMPLE 1 — directed graph with a negative edge")
    print("━" * 60)
    matrix1 = [
        [0,   4,   1,   INF],
        [INF, 0,   INF, 1  ],
        [INF, -2,  0,   5  ],
        [INF, INF, INF, 0  ],
    ]
    floyd_warshall(matrix1)

    print("━" * 60)
    print("EXAMPLE 2 — undirected weighted graph (Dijkstra image graph)")
    print("━" * 60)
    matrix2 = [
        [0,  7,  9,   INF, INF, 14 ],
        [7,  0,  10,  15,  INF, INF],
        [9,  10, 0,   11,  INF, 2  ],
        [INF,15, 11,  0,   6,   INF],
        [INF,INF,INF, 6,   0,   9  ],
        [14, INF,2,   INF, 9,   0  ],
    ]
    floyd_warshall(matrix2)