import heapq


def dijkstra_real(adj: dict, source: int) -> None:
    """
    Run Dijkstra's algorithm on a WEIGHTED graph and print the
    full shortest-path table.

    Unlike the unweighted version (which assumes every edge costs 1),
    this uses the actual edge weights from the adjacency list — so a
    path with fewer hops is not necessarily the shortest path anymore.

    Parameters
    ----------
    adj    : dict mapping each node to a list of (neighbour, weight) tuples
             e.g. {1: [(2, 4), (3, 1)], 2: [(4, 1)], ...}
             Edges are directed: adj[u] = [(v, w), ...] means edge u → v
             with weight w. For an undirected graph, add both directions
             when building adj.
    source : starting node (must be a key in adj)

    Note: Dijkstra requires non-negative weights. If a negative weight
    is found, a warning is printed (use Bellman-Ford instead in that case).
    """

    if source not in adj:
        print(f"Error: node {source} is not in the adjacency list.")
        return

    nodes = sorted(adj.keys())

    # Validate: Dijkstra cannot handle negative weights correctly
    negative_edges = [(u, v, w) for u in adj for (v, w) in adj[u] if w < 0]
    if negative_edges:
        print("⚠ Warning: negative edge weight(s) detected — "
              "Dijkstra's results may be incorrect. Use Bellman-Ford instead.")
        for (u, v, w) in negative_edges:
            print(f"    {u} → {v}  (weight {w})")
        print()

    # Initialise 
    dist        = {v: float('inf') for v in nodes}
    predecessor = {v: None         for v in nodes}
    visited     = set()
    dist[source] = 0

    heap = [(0, source)]   # (distance, node)

    # Relaxation log — one entry per node finalised 
    log = []
    finalise_order = 0

    while heap:
        d, u = heapq.heappop(heap)

        if u in visited:
            continue          # stale entry — lazy deletion
        visited.add(u)
        finalise_order += 1

        relaxed = []
        for (v, w) in adj.get(u, []):
            if v in visited:
                continue
            new_dist = dist[u] + w          # actual edge weight, not +1
            if new_dist < dist[v]:
                dist[v]        = new_dist
                predecessor[v] = u
                heapq.heappush(heap, (new_dist, v))
                relaxed.append((v, w, new_dist))

        log.append({
            "order":   finalise_order,
            "node":    u,
            "dist":    d,
            "pred":    predecessor[u],
            "relaxed": relaxed,
        })

    # Reconstruct shortest path + total weight for any node 
    def reconstruct(target):
        if dist[target] == float('inf'):
            return None
        path, cur = [], target
        while cur is not None:
            path.append(cur)
            cur = predecessor[cur]
        return list(reversed(path))

    # Format helpers
    def fmt_row(cells, widths):
        return "│ " + " │ ".join(c.ljust(w) for c, w in zip(cells, widths)) + " │"

    def make_border(widths, left, mid, right):
        return left + mid.join("─" * (w + 2) for w in widths) + right

    log_by_node = {entry["node"]: entry for entry in log}

    # Table 1: final summary table
    table_rows = []
    for v in sorted(nodes, key=lambda x: (dist[x], x)):
        path     = reconstruct(v)
        path_str = " → ".join(map(str, path)) if path else "unreachable"
        d_str    = str(dist[v]) if dist[v] != float('inf') else "∞"
        pred_str = str(predecessor[v]) if predecessor[v] is not None else ("—" if v == source else "∞")
        entry    = log_by_node.get(v)
        relaxed_str = (
            ", ".join(f"{rv}(+{rw}→{rd})" for rv, rw, rd in entry["relaxed"])
            if entry and entry["relaxed"] else "—"
        )
        order_str = str(entry["order"]) if entry else "—"

        table_rows.append([
            str(v), d_str, pred_str, path_str, relaxed_str, order_str,
        ])

    headers = [
        "Node",
        f"dist({source}, v)",
        "Predecessor",
        "Shortest Path",
        "Neighbours Relaxed (node(+w→newdist))",
        "Finalised (#)",
    ]

    col_widths = [len(h) for h in headers]
    for row in table_rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(cell))

    top = make_border(col_widths, "┌", "┬", "┐")
    mid = make_border(col_widths, "├", "┼", "┤")
    bot = make_border(col_widths, "└", "┴", "┘")

    print(f"\nDijkstra's Algorithm — Weighted Graph  (source = {source})\n")
    print(top)
    print(fmt_row(headers, col_widths))
    print(mid)
    for row in table_rows:
        print(fmt_row(row, col_widths))
    print(bot)

    # Table 2: path + total cost summary 
    print(f"\nShortest paths and total cost from node {source}:\n")
    for v in sorted(nodes):
        if v == source:
            continue
        path = reconstruct(v)
        if path is None:
            print(f"  {source} → {v}  :  unreachable")
            continue
        path_str = " → ".join(map(str, path))
        print(f"  {source} → {v}  :  total cost = {dist[v]}  │  {path_str}")
    print()


# Example
if __name__ == "__main__":
    # Weighted, directed graph
    adj = {
        1: [(2, 4), (3, 1)],
        2: [(4, 1)],
        3: [(2, 2), (4, 5)],
        4: [],
    }
    dijkstra_real(adj, source=1)

    print("=" * 90)

    # Undirected weighted graph (edges added in both directions)
    adj_undirected = {
        1: [(2, 7), (3, 9), (6, 14)],
        2: [(1, 7), (3, 10), (4, 15)],
        3: [(1, 9), (2, 10), (4, 11), (6, 2)],
        4: [(2, 15), (3, 11), (5, 6)],
        5: [(4, 6), (6, 9)],
        6: [(1, 14), (3, 2), (5, 9)],
    }
    dijkstra_real(adj_undirected, source=1)