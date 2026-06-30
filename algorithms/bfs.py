from collections import deque, OrderedDict


def bfs_table(adj: dict, start: int) -> None:
    """
    Run BFS from `start` on the graph described by `adj`
    and print the traversal table to the terminal.

    Parameters
    ----------
    adj   : dict mapping each node to a list/set of neighbours
            e.g. {1: [2, 3], 2: [1, 4], ...}
    start : starting node (must be a key in adj)
    """

    if start not in adj:
        print(f"Error: node {start} is not in the adjacency list.")
        return

    visited = set([start])
    queue   = deque([start])
    rows    = []
    order   = []
    step    = 1

    while queue:
        node        = queue.popleft()
        order.append(node)
        newly_added = []

        for neighbour in sorted(adj[node]):      # sorted for determinism
            if neighbour not in visited:
                visited.add(neighbour)
                queue.append(neighbour)
                newly_added.append(neighbour)

        rows.append({
            "step":        step,
            "node":        node,
            "neighbours":  sorted(adj[node]),
            "newly_added": newly_added,
            "queue_after": list(queue),
            "visited":     list(order),
        })
        step += 1

    def fmt_list(lst, sep=", "):
        return sep.join(map(str, lst)) if lst else "—"

    def fmt_arrow(lst):
        return " → ".join(map(str, lst)) if lst else "empty"

    headers = ["Step", "Node", "Neighbours", "Newly Enqueued",
               "Queue After", "Visited So Far"]

    table_rows = []
    for r in rows:
        table_rows.append([
            str(r["step"]),
            str(r["node"]),
            fmt_list(r["neighbours"]),
            fmt_list(r["newly_added"]),
            fmt_arrow(r["queue_after"]),
            fmt_arrow(r["visited"]),
        ])

    col_widths = [len(h) for h in headers]
    for row in table_rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(cell))

    sep = "─┼─".join("─" * w for w in col_widths)
    sep = "─" + sep + "─"

    def fmt_row(cells, widths):
        return "│ " + " │ ".join(c.ljust(w) for c, w in zip(cells, widths)) + " │"

    header_line = fmt_row(headers, col_widths)
    top    = "┌" + "┬".join("─" * (w + 2) for w in col_widths) + "┐"
    mid    = "├" + "┼".join("─" * (w + 2) for w in col_widths) + "┤"
    bottom = "└" + "┴".join("─" * (w + 2) for w in col_widths) + "┘"

    print(f"\nBFS Traversal  (start = {start})\n")
    print(top)
    print(header_line)
    print(mid)
    for row in table_rows:
        print(fmt_row(row, col_widths))
    print(bottom)
    print(f"\nBFS order:  {fmt_arrow(order)}\n")


if __name__ == "__main__":
    adj = {
        1: [2, 3],
        2: [1, 4, 5],
        3: [1, 6, 7],
        4: [2],
        5: [2],
        6: [3],
        7: [3],
    }
    bfs_table(adj, start=1)