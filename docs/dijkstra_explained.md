# Dijkstra's Algorithm — `heapq`, the Relaxation Table, and Time Complexity

---

## 1. The `heapq` Module

### What it is

`heapq` is Python's built-in module for **binary min-heaps** built on top of a plain `list`. A heap keeps the smallest element accessible in O(1), and insertion/removal in O(log n) — exactly the access pattern Dijkstra needs: *"give me the unvisited node with the smallest tentative distance."*

```python
import heapq
```

### Why not just scan a list for the minimum?

| Approach | Find-min | Insert | Decrease-key |
|---|---|---|---|
| Plain list, linear scan | O(n) | O(1) | O(1) |
| Binary heap (`heapq`) | O(1) | O(log n) | not directly — push a new entry instead |

A linear scan over `n` nodes every time you need the minimum is what makes the **naive O(V²)** version of Dijkstra slow. A heap turns "find the minimum" from O(n) into O(log n), which is the single change that produces the faster **O((V + E) log V)** version.

### Core operations

| Function | Description | Time |
|---|---|---|
| `heapq.heappush(heap, item)` | Push `item` onto the heap, maintaining heap order | O(log n) |
| `heapq.heappop(heap)` | Pop and return the smallest item | O(log n) |
| `heap[0]` | Peek at the smallest item without removing it | O(1) |
| `heapq.heapify(list)` | Convert a list into a heap in place | O(n) |

`heapq` operates on tuples by comparing element-by-element, so `(distance, node)` tuples naturally sort by distance first:

```python
heap = []
heapq.heappush(heap, (5, 'C'))
heapq.heappush(heap, (2, 'A'))
heapq.heappush(heap, (3, 'B'))

heapq.heappop(heap)   # (2, 'A')  ← smallest distance first
heapq.heappop(heap)   # (3, 'B')
heapq.heappop(heap)   # (5, 'C')
```

### The "lazy deletion" trick

Python's `heapq` has **no built-in decrease-key operation** — you cannot efficiently update a node's priority once it's in the heap. Dijkstra works around this with **lazy deletion**: instead of updating an entry, simply push a *new* entry with the better distance, and skip stale entries when they're popped.

```python
if u in visited:
    continue          # this is a stale, outdated entry — ignore it
visited.add(u)
```

This means the heap can contain multiple entries for the same node, but each is processed only once — the first (smallest) pop for a given node is the only one that does real work; later pops for the same node are discarded in O(1).

---

## 2. What Dijkstra's Algorithm Does

**Dijkstra's algorithm** finds the shortest distance from a single **source** node to every other node in a graph with non-negative edge weights. In the unweighted version used here, every edge has weight 1, so Dijkstra reduces to BFS in spirit — but the heap-based mechanism generalises directly to weighted graphs.

```
Graph:

      2
   1 --- 3
   |     |
 1 |     | 1
   |     |
   2 --- 6
      ...
```

The algorithm grows a "settled" region outward from the source, always finalising the **closest unsettled node next** — never revisiting a node once it's settled.

### Key invariant

> Once a node is popped from the heap with its true minimum distance, that distance is final and will never improve.

This holds *only* because edge weights are non-negative — a shorter path could never be found later by going through a longer one.

---

## 3. The Algorithm Step by Step

```
Initialise:
  dist[source] = 0
  dist[v]      = ∞   for all other v
  predecessor[v] = None  for all v
  visited = {}
  heap = [(0, source)]

While heap is not empty:
  1. (d, u) ← heap.pop_min()           ← smallest tentative distance
  2. if u already visited: skip (stale entry, lazy deletion)
  3. mark u visited                    ← u's distance is now final
  4. for each neighbour v of u:
       new_dist = dist[u] + weight(u, v)
       if new_dist < dist[v]:
         dist[v]        = new_dist     ← relax the edge
         predecessor[v] = u
         heap.push((new_dist, v))
```

Step 4 — **relaxation** — is the heart of the algorithm: it asks *"can I reach v more cheaply by going through u?"* and updates if so.

---

## 4. The Dijkstra Table — Column by Column

Each row corresponds to one node being **finalised** (popped from the heap and marked visited).

| Column | What it shows |
|---|---|
| **Node** | The node whose distance is being finalised |
| **dist(source, v)** | The final shortest distance from `source` to this node |
| **Predecessor** | The node immediately before this one on the shortest path |
| **Shortest Path** | Reconstructed by walking the predecessor chain back to source |
| **Neighbours Relaxed** | Neighbours whose tentative distance was *improved* when this node was finalised |
| **Finalised (#)** | The order in which nodes were settled — the wavefront expansion order |

The **Shortest Path** column is read directly off the **Predecessor** column — once every node has a predecessor, every path is just a backward walk, which is why no separate "destination" needs to be supplied: the full table answers the query for *every* possible destination at once.

---

## 5. Worked Example

Graph: `V = {1,2,3,4,5,6}`, unweighted edges, source = 1.

```
adj = {
    1: [2, 3],
    2: [1, 3, 4, 5],
    3: [1, 2, 6],
    4: [2, 5],
    5: [2, 4, 6],
    6: [3, 5],
}
```

**Initial state**

```
dist    = {1: 0, 2: ∞, 3: ∞, 4: ∞, 5: ∞, 6: ∞}
heap    = [(0, 1)]
visited = {}
```

**Step 1 — pop (0, 1)**

```
node 1 finalised, dist = 0
relax 2: dist[2] = 1, pred[2] = 1   → push (1, 2)
relax 3: dist[3] = 1, pred[3] = 1   → push (1, 3)
```

| Node | dist(1,v) | Pred | Path | Relaxed | Order |
|---|---|---|---|---|---|
| 1 | 0 | — | 1 | 2, 3 | 1 |

**Step 2 — pop (1, 2)**

```
node 2 finalised, dist = 1
neighbours: 1 (visited, skip), 3 (1+1=2, not < dist[3]=1, skip),
            4 (1+1=2 < ∞)  → relax, push (2, 4)
            5 (1+1=2 < ∞)  → relax, push (2, 5)
```

| Node | dist(1,v) | Pred | Path | Relaxed | Order |
|---|---|---|---|---|---|
| 2 | 1 | 1 | 1 → 2 | 4, 5 | 2 |

**Step 3 — pop (1, 3)**

```
node 3 finalised, dist = 1
neighbours: 1 (visited), 2 (visited),
            6 (1+1=2 < ∞)  → relax, push (2, 6)
```

| Node | dist(1,v) | Pred | Path | Relaxed | Order |
|---|---|---|---|---|---|
| 3 | 1 | 1 | 1 → 3 | 6 | 3 |

**Steps 4–6 — pop (2, 4), (2, 5), (2, 6)**

All remaining neighbours are already visited or offer no improvement; nothing is relaxed.

| Node | dist(1,v) | Pred | Path | Relaxed | Order |
|---|---|---|---|---|---|
| 4 | 2 | 2 | 1 → 2 → 4 | — | 4 |
| 5 | 2 | 2 | 1 → 2 → 5 | — | 5 |
| 6 | 2 | 3 | 1 → 3 → 6 | — | 6 |

**Final table**

```
┌──────┬────────────┬─────────────┬───────────────┬────────────────────┬───────────────┐
│ Node │ dist(1, v) │ Predecessor │ Shortest Path │ Neighbours Relaxed │ Finalised (#) │
├──────┼────────────┼─────────────┼───────────────┼────────────────────┼───────────────┤
│ 1    │ 0          │ —           │ 1             │ 2, 3               │ 1             │
│ 2    │ 1          │ 1           │ 1 → 2         │ 4, 5               │ 2             │
│ 3    │ 1          │ 1           │ 1 → 3         │ 6                  │ 3             │
│ 4    │ 2          │ 2           │ 1 → 2 → 4     │ —                  │ 4             │
│ 5    │ 2          │ 2           │ 1 → 2 → 5     │ —                  │ 5             │
│ 6    │ 2          │ 3           │ 1 → 3 → 6     │ —                  │ 6             │
└──────┴────────────┴─────────────┴───────────────┴────────────────────┴───────────────┘
```

---

## 6. Time Complexity — Full Derivation

Let `V` = number of vertices, `E` = number of edges.

### 6.1 Operations counted

| Operation | How many times it happens | Cost per operation |
|---|---|---|
| `heappop` | At most once per edge relaxation + once per vertex = O(V + E), but bounded by total pushes, which is O(E) | O(log E) = O(log V) since E ≤ V² |
| `heappush` | Once per successful relaxation, at most once per edge (each edge can relax its endpoint once per direction) = O(E) | O(log E) = O(log V) |
| Visited check (`in visited`) | Once per pop = O(E) total pops in the worst case | O(1) (set lookup) |
| Neighbour scan (`for v in adj[u]`) | Every adjacency list traversed exactly once across the whole run | Sums to O(E) total |

### 6.2 Putting it together

```
Total heap operations  =  O(E) pushes + O(E) pops
                        =  O(E) operations, each O(log E)
                        =  O(E log E)

Since the graph is simple, E ≤ V²  ⟹  log E ≤ log(V²) = 2 log V = O(log V)

So:   O(E log E)  =  O(E log V)
```

Adding the unavoidable O(V) cost of initialising `dist` and `predecessor` for every vertex:

```
Total time  =  O(V)            ← initialisation
            +  O(E log V)      ← heap pushes/pops across all relaxations
            =  O((V + E) log V)
```

### 6.3 Why this is the standard bound

| Implementation | Find-min | Decrease-key | Total complexity |
|---|---|---|---|
| Array / linear scan (naive Dijkstra) | O(V) | O(1) | O(V²) |
| Binary heap (`heapq`, lazy deletion) | O(log V) | O(log V) (via re-push) | **O((V + E) log V)** |
| Fibonacci heap (theoretical) | O(log V) amortised | O(1) amortised | O(E + V log V) |

For **sparse graphs** (E ≈ V), `O((V + E) log V)` beats `O(V²)` significantly. For **dense graphs** (E ≈ V²), the two become comparable, and the simpler array-based version can even win in practice due to lower constant overhead — but `heapq` is the standard choice because most real-world graphs are sparse.

### 6.4 Space complexity

```
dist          : O(V)
predecessor   : O(V)
visited       : O(V)
heap          : O(E)   ← worst case, one entry pushed per edge
adjacency list: O(V + E)

Total space = O(V + E)
```

---

## 7. Summary

| Aspect | Result |
|---|---|
| Time complexity | O((V + E) log V) |
| Space complexity | O(V + E) |
| Why a heap | Turns "find next closest node" from O(V) into O(log V) |
| Why lazy deletion | `heapq` has no decrease-key; stale entries are pushed over and skipped on pop |
| Why no destination needed | The predecessor table answers shortest path to *every* node in one run — picking a single destination would only mean stopping early, not a different algorithm |
