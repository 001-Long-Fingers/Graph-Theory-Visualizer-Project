def bellman_ford_table(adj: dict, source: int) -> None:
    """
    Run the Bellman-Ford algorithm from `source` and print the
    classic Bellman-Ford relaxation table: one row per iteration,
    one column per node, showing how the distance estimate evolves.

    Also detects and reports negative-weight cycles.

    Parameters
    ----------
    adj    : dict mapping each node to a list of (neighbour, weight) tuples
             e.g. {1: [(2, 4), (3, 1)], 2: [(3, -2)], ...}
             Edges are directed: adj[u] = [(v, w), ...] means an edge u → v
             with weight w. For an undirected graph, add both directions
             when building adj.
    source : starting node (must be a key in adj)
    """

    if source not in adj:
        print(f"Error: node {source} is not in the adjacency list.")
        return

    nodes = sorted(adj.keys())
    V     = len(nodes)

    # Flatten into an edge list (u, v, w)
    edges = []
    for u in nodes:
        for (v, w) in adj[u]:
            edges.append((u, v, w))

    # Initialise
    dist        = {v: float('inf') for v in nodes}
    predecessor = {v: None         for v in nodes}
    dist[source] = 0

    # Iteration log
    # snapshot[i] = dict of dist values after iteration i  (i = 0 is initial state)
    snapshots         = [dict(dist)]
    relaxed_log       = []          # relaxed_log[i] = list of nodes updated in iteration i
    last_changed_iter = 0           # which iteration was the last to change anything

    # Main relaxation loop: V - 1 passes
    for i in range(1, V):
        updated_this_round = []
        for (u, v, w) in edges:
            if dist[u] != float('inf') and dist[u] + w < dist[v]:
                dist[v]        = dist[u] + w
                predecessor[v] = u
                updated_this_round.append(v)

        snapshots.append(dict(dist))
        relaxed_log.append(updated_this_round)

        if updated_this_round:
            last_changed_iter = i

        # Early exit: if nothing changed this round, the table has converged
        if not updated_this_round:
            break

    # Negative-cycle check: one extra pass
    negative_cycle_nodes = set()
    for (u, v, w) in edges:
        if dist[u] != float('inf') and dist[u] + w < dist[v]:
            negative_cycle_nodes.add(v)

    # Reconstruct path for any node
    def reconstruct(target):
        if dist[target] == float('inf'):
            return None
        path, cur, guard = [], target, 0
        while cur is not None and guard <= V:
            path.append(cur)
            cur = predecessor[cur]
            guard += 1
        return list(reversed(path))

    # Format helpers
    def fmt_val(x):
        return "∞" if x == float('inf') else str(x)

    def fmt_row(cells, widths):
        return "│ " + " │ ".join(c.ljust(w) for c, w in zip(cells, widths)) + " │"

    def make_border(widths, left, mid, right):
        return left + mid.join("─" * (w + 2) for w in widths) + right

    # Table 1: iteration-by-iteration distance evolution
    headers = ["Iteration"] + [f"dist[{v}]" for v in nodes]
    table_rows = []
    for i, snap in enumerate(snapshots):
        row = [str(i) if i > 0 else "0 (init)"]
        for v in nodes:
            row.append(fmt_val(snap[v]))
        table_rows.append(row)

    col_widths = [len(h) for h in headers]
    for row in table_rows:
        for idx, cell in enumerate(row):
            col_widths[idx] = max(col_widths[idx], len(cell))

    print(f"\nBellman-Ford Algorithm  (source = {source})\n")
    print(f"Graph has {V} nodes and {len(edges)} directed edges. "
          f"Runs {V - 1} relaxation passes (V - 1).\n")

    top = make_border(col_widths, "┌", "┬", "┐")
    mid = make_border(col_widths, "├", "┼", "┤")
    bot = make_border(col_widths, "└", "┴", "┘")

    print(top)
    print(fmt_row(headers, col_widths))
    print(mid)
    for row in table_rows:
        print(fmt_row(row, col_widths))
    print(bot)

    print(f"\nDistances stabilised after iteration {last_changed_iter} "
          f"(no further relaxations needed).\n")

    # Table 2: final per-node summary
    headers2 = ["Node", "Distance", "Predecessor", "Shortest Path"]
    rows2 = []
    for v in nodes:
        d_str    = fmt_val(dist[v])
        pred_str = str(predecessor[v]) if predecessor[v] is not None else ("—" if v == source else "∞")
        path     = reconstruct(v)
        path_str = " → ".join(map(str, path)) if path else "unreachable"
        flag     = "  ⚠ in negative cycle" if v in negative_cycle_nodes else ""
        rows2.append([v_str := str(v), d_str, pred_str, path_str + flag])

    col_widths2 = [len(h) for h in headers2]
    for row in rows2:
        for idx, cell in enumerate(row):
            col_widths2[idx] = max(col_widths2[idx], len(cell))

    top2 = make_border(col_widths2, "┌", "┬", "┐")
    mid2 = make_border(col_widths2, "├", "┼", "┤")
    bot2 = make_border(col_widths2, "└", "┴", "┘")

    print(top2)
    print(fmt_row(headers2, col_widths2))
    print(mid2)
    for row in rows2:
        print(fmt_row(row, col_widths2))
    print(bot2)

    if negative_cycle_nodes:
        print(f"\n⚠ Negative-weight cycle detected — it affects shortest paths "
              f"to: {', '.join(map(str, sorted(negative_cycle_nodes)))}")
        print("  Shortest path is undefined (can be made arbitrarily small) for these nodes.\n")
    else:
        print("\nNo negative-weight cycle detected.\n")


# Example

if __name__ == "__main__":
    # Directed, weighted graph with one negative edge (but no negative cycle)
    adj = {
        1: [(2, 4), (3, 1)],
        2: [(4, 1)],
        3: [(2, -2), (4, 5)],
        4: [],
    }
    bellman_ford_table(adj, source=1)

    print("=" * 70)

    # Example with a negative cycle: 1 → 2 → 3 → 1 has total weight -1
    adj_neg_cycle = {
        1: [(2, 1)],
        2: [(3, -3)],
        3: [(1, 1)],
    }
    bellman_ford_table(adj_neg_cycle, source=1)