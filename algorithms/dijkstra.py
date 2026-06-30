import heapq

def dijkstra_table(adj: dict, source: int) -> None:
    """
    Running Dijkstra's algorithm from `source` on an unweighted graph
    described by `adj`, then print the full shortest-path table.

    The table shows, for every node:
      - shortest distance from source
      - the predecessor on that shortest path
      - the full shortest path back to source

    Parameters
    ----------
    adj    : dict mapping each node to a list/set of neighbours
             e.g. {1: [2, 3], 2: [1, 4], ...}
    source : starting node (must be a key in adj)
    """

    if source not in adj:
        print(f"Error: node {source} is not in the adjacency list.")
        return

    nodes = sorted(adj.keys())

    
    dist        = {v: float('inf') for v in nodes}
    predecessor = {v: None         for v in nodes}
    visited     = set()
    dist[source] = 0

    heap = [(0, source)]   # (distance, node)

    
    # Each entry: (order_finalised, node, dist, predecessor, nodes_relaxed_this_step)
    log = []
    finalise_order = 0

    while heap:
        d, u = heapq.heappop(heap)

        if u in visited:
            continue
        visited.add(u)
        finalise_order += 1

        relaxed = []
        for v in sorted(adj[u]):         # sorted for determinism
            if v in visited:
                continue
            new_dist = dist[u] + 1       # unweighted: weight = 1 per edge
            if new_dist < dist[v]:
                dist[v]        = new_dist
                predecessor[v] = u
                heapq.heappush(heap, (new_dist, v))
                relaxed.append(v)

        log.append({
            "order":      finalise_order,
            "node":       u,
            "dist":       d,
            "pred":       predecessor[u],
            "relaxed":    relaxed,
        })

    # Reconstruct shortest path for every node
    def reconstruct(target):
        if dist[target] == float('inf'):
            return None
        path, cur = [], target
        while cur is not None:
            path.append(cur)
            cur = predecessor[cur]
        return list(reversed(path))

    
    #
    # Dijkstra table rows — one per node in the graph, sorted by distance then node id.
    # Columns:
    #   Node | Dist from source | Predecessor | Shortest Path | Nodes Relaxed When Finalised
    #
    # "Nodes Relaxed" = neighbours whose tentative distance was *improved*
    # when this node was popped from the heap.

    # Map node → log entry
    log_by_node = {entry["node"]: entry for entry in log}

    table_rows = []
    for v in sorted(nodes, key=lambda x: (dist[x], x)):
        path     = reconstruct(v)
        path_str = " → ".join(map(str, path)) if path else "unreachable"
        d_str    = str(dist[v]) if dist[v] != float('inf') else "∞"
        pred_str = str(predecessor[v]) if predecessor[v] is not None else ("—" if v == source else "∞")
        entry    = log_by_node.get(v)
        relaxed_str = ", ".join(map(str, entry["relaxed"])) if entry and entry["relaxed"] else "—"
        order_str   = str(entry["order"]) if entry else "—"

        table_rows.append([
            str(v),
            d_str,
            pred_str,
            path_str,
            relaxed_str,
            order_str,
        ])

    #Print the result
    headers = [
        "Node",
        f"dist({source}, v)",
        "Predecessor",
        "Shortest Path",
        "Neighbours Relaxed",
        "Finalised (#)",
    ]

    col_widths = [len(h) for h in headers]
    for row in table_rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(cell))

    def fmt_row(cells, widths):
        return "│ " + " │ ".join(c.ljust(w) for c, w in zip(cells, widths)) + " │"

    top    = "┌" + "┬".join("─" * (w + 2) for w in col_widths) + "┐"
    mid    = "├" + "┼".join("─" * (w + 2) for w in col_widths) + "┤"
    bottom = "└" + "┴".join("─" * (w + 2) for w in col_widths) + "┘"

    print(f"\nDijkstra's Algorithm  (source = {source})\n")
    print(top)
    print(fmt_row(headers, col_widths))
    print(mid)
    for row in table_rows:
        print(fmt_row(row, col_widths))
    print(bottom)

  
    print(f"\nShortest distances from node {source}:\n")
    for v in sorted(nodes):
        if v == source:
            continue
        path     = reconstruct(v)
        path_str = " → ".join(map(str, path)) if path else "unreachable"
        d_val    = dist[v] if dist[v] != float('inf') else "∞"
        print(f"  {source} → {v}  :  dist = {d_val}  │  {path_str}")
    print()

if __name__ == "__main__":
    adj = {
        1: [2, 3],
        2: [1, 3, 4, 5],
        3: [1, 2, 6],
        4: [2, 5],
        5: [2, 4, 6],
        6: [3, 5],
    }
    dijkstra_table(adj, source=1)
