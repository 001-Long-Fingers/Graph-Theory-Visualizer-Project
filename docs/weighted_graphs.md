# Weighted & Directed Graphs — Dijkstra, Bellman-Ford, Floyd-Warshall

---

## 1. From Unweighted to Weighted Graphs

The BFS and early Dijkstra implementations treated every edge as costing 1 — a hop count. This works when all edges are equal, but most real graphs are not equal: a road network has distances, a flight network has costs, a circuit has resistances.

**Unweighted adjacency list** (used in BFS and the first Dijkstra):

```python
adj = {
    1: [2, 3],
    2: [1, 4, 5],
}
```

**Weighted adjacency list** (used in Bellman-Ford and real Dijkstra):

```python
adj = {
    1: [(2, 4), (3, 1)],
    2: [(1, 4), (4, 7)],
}
# each entry is (neighbour, weight)
```

When weights are uniform, "fewest hops" and "lowest cost" are the same thing. The moment weights differ, they diverge — a 3-hop path costing 6 can easily beat a 1-hop path costing 14. All three algorithms in this document work on the weighted version.

---

## 2. Directed Graphs

An edge in an **undirected** graph goes both ways: `{1,2}` means you can travel 1→2 and also 2→1. A **directed** graph (digraph) has edges with a fixed direction: `(1,2)` means only 1→2.

```
Undirected:   1 ——— 2        Directed:   1 ——→ 2
              both ways                  one way only
```

In the weighted adjacency list, this is simply whether you add the reverse entry or not:

```python
# directed: 1 → 2 with weight 4 only
adj = {1: [(2, 4)], 2: []}

# undirected: 1 ↔ 2 with weight 4 in both directions
adj = {1: [(2, 4)], 2: [(1, 4)]}
```

Floyd-Warshall always operates on directed graphs — the adjacency matrix encodes direction by allowing `matrix[i][j] ≠ matrix[j][i]`. Dijkstra and Bellman-Ford work on both; the graph's directionality is entirely determined by what you put in the adjacency list.

---

## 3. Dijkstra's Algorithm — Weighted

### What changes from the unweighted version

The only line that changes is the relaxation:

```python
# unweighted (wrong for weighted graphs)
new_dist = dist[u] + 1

# weighted (correct)
new_dist = dist[u] + w      # w is the actual edge weight
```

This single change means a path with fewer hops is no longer automatically shorter. The heap now orders nodes by **accumulated cost**, not hop count.

### Why Dijkstra still cannot handle negative weights

The algorithm's correctness rests on one guarantee: once a node is popped from the min-heap, its distance is final. This holds only if no future path can offer a cheaper route — which is impossible when all weights are non-negative (you can only ever make a path more expensive by extending it). A single negative edge breaks this: a node finalised at cost 5 might later be reachable at cost 3 via a negative edge, but Dijkstra has already committed and moved on.

### Adjacency list format

```python
adj = {
    1: [(2, 7),  (3, 9),  (6, 14)],
    2: [(1, 7),  (3, 10), (4, 15)],
    3: [(1, 9),  (2, 10), (4, 11), (6, 2)],
    4: [(2, 15), (3, 11), (5, 6) ],
    5: [(4, 6),  (6, 9) ],
    6: [(1, 14), (3, 2),  (5, 9) ],
}
```

### Output table (source = 1)

```
┌──────┬────────────┬─────────────┬───────────────┬───────────────────────────────────────┬───────────────┐
│ Node │ dist(1, v) │ Predecessor │ Shortest Path │ Neighbours Relaxed (node(+w→newdist)) │ Finalised (#) │
├──────┼────────────┼─────────────┼───────────────┼───────────────────────────────────────┼───────────────┤
│ 1    │ 0          │ —           │ 1             │ 6(+14→14), 3(+9→9), 2(+7→7)           │ 1             │
│ 2    │ 7          │ 1           │ 1 → 2         │ 4(+15→22)                             │ 2             │
│ 3    │ 9          │ 1           │ 1 → 3         │ 6(+2→11), 4(+11→20)                   │ 3             │
│ 6    │ 11         │ 3           │ 1 → 3 → 6     │ 5(+9→20)                              │ 4             │
│ 4    │ 20         │ 3           │ 1 → 3 → 4     │ —                                     │ 5             │
│ 5    │ 20         │ 6           │ 1 → 3 → 6 → 5 │ —                                     │ 6             │
└──────┴────────────┴─────────────┴───────────────┴───────────────────────────────────────┴───────────────┘
```

The direct edge `1→6` costs 14, but `1→3→6` costs 11 — node 6 is reached via 3, not directly. The direct edge `1→2` costs 7 and is never beaten, so node 2 is finalised immediately as the closest node. The "Neighbours Relaxed" column shows exactly which estimates were improved when each node was finalised, and by how much.

---

## 4. Bellman-Ford — Negative Weights

### What Bellman-Ford trades for negative-weight support

Dijkstra is greedy — it finalises one node per heap pop and never revisits it. This speed comes at the cost of correctness on negative weights. Bellman-Ford abandons the greedy approach entirely: it makes **V−1 full passes** over every edge in the graph, relaxing every one of them each time. By the end of pass V−1, every shortest path is guaranteed to be found, because no simple path can have more than V−1 edges.

The cost is time: O(VE) versus Dijkstra's O((V+E) log V). The gain is that negative weights are handled correctly, and a **V-th pass** can detect negative cycles (if anything still relaxes, a cycle of negative total weight exists).

### Adjacency list format

```python
adj = {
    1: [(2, 4), (3, 1)],
    2: [(4, 1)],
    3: [(2, -2), (4, 5)],   # negative weight on 3→2
    4: [],
}
```

### Output — the Bellman-Ford table

The classic Bellman-Ford table has one **row per pass** and one **column per node**, showing how each distance estimate tightens over successive passes:

```
┌───────────┬──────────┬──────────┬──────────┬──────────┐
│ Iteration │ dist[1]  │ dist[2]  │ dist[3]  │ dist[4]  │
├───────────┼──────────┼──────────┼──────────┼──────────┤
│ 0 (init)  │ 0        │ ∞        │ ∞        │ ∞        │
│ 1         │ 0        │ 4        │ 1        │ 5        │
│ 2         │ 0        │ -1       │ 1        │ 0        │
│ 3         │ 0        │ -1       │ 1        │ 0        │
└───────────┴──────────┴──────────┴──────────┴──────────┘

Distances stabilised after iteration 2.
```

After pass 1: dist[2] = 4 (via direct 1→2), dist[3] = 1 (via direct 1→3), dist[4] = 5 (via 1→2→4 or 1→3→4, whichever relaxes first).

After pass 2: the negative edge 3→2 (weight −2) is applied — `dist[3] + (−2) = −1 < 4` — so dist[2] drops to −1. This cascades: dist[4] via 2 is now −1+1 = 0. Pass 3 shows no further changes, confirming convergence.

Note that dist[2] went from 4 to −1 across two passes — this is impossible for Dijkstra, which would have committed to dist[2] = 4 in pass 1 and never revised it.

---

## 5. The Distance Matrix and Floyd-Warshall

### From source-to-all to all-pairs

Both Dijkstra and Bellman-Ford solve the **single-source** problem: pick one node, get the shortest path from it to every other node. To get shortest paths between *every* pair, you would run either algorithm V times (once per source), costing O(V·(V+E)logV) or O(V²E).

Floyd-Warshall solves **all-pairs** in a single O(V³) run by working directly on a **distance matrix** instead of an adjacency list.

### The distance matrix

A V×V matrix where entry `[i][j]` is the shortest known distance from node i to node j. It is initialised from the adjacency matrix:

```
           1    2    3    4
      1  [ 0    4    1    ∞  ]
      2  [ ∞    0    ∞    1  ]
      3  [ ∞   -2    0    5  ]
      4  [ ∞    ∞    ∞    0  ]
```

Diagonal is always 0 (distance from a node to itself). `∞` means no direct edge. After the algorithm runs, every `∞` that can be reached through intermediaries will be replaced by the true shortest distance.

### The key idea — intermediate nodes

Floyd-Warshall asks, for every pair (i, j) and every possible intermediate node k: *"is the path i → k → j cheaper than the current best i → j?"*

```
dist[i][j] = min(dist[i][j],  dist[i][k] + dist[k][j])
```

It iterates k from 1 to V, each time potentially improving all V² pairs. After considering k=1, every shortest path that routes through node 1 is known. After k=2, every path through nodes 1 or 2 is known. After k=V, all shortest paths are finalised.

### Output — matrix evolution

The matrix is printed after each value of k. The `◄` marks the current pivot row:

```
  k = 0  (initial)
       1     2     3     4
   ┼───────────────────────
   1 │  0     4     1     ∞
   2 │  ∞     0     ∞     1
   3 │  ∞    -2     0     5
   4 │  ∞     ∞     ∞     0

  k = 2  —  2 cell(s) updated
       1     2     3     4
   ┼───────────────────────
   1 │  0     4     1     5   ← dist[1][4] improved: 1→2→4 = 5
   2 │  ∞     0     ∞     1   ◄
   3 │  ∞    -2     0    -1   ← dist[3][4] improved: 3→2→4 = -1
   4 │  ∞     ∞     ∞     0

  k = 3  —  2 cell(s) updated
       1     2     3     4
   ┼───────────────────────
   1 │  0    -1     1     0   ← dist[1][2] = -1 via 1→3→2
   2 │  ∞     0     ∞     1
   3 │  ∞    -2     0    -1   ◄
   4 │  ∞     ∞     ∞     0
```

### Final path table

```
┌──────┬────┬──────────┬───────────────┐
│ From │ To │ Distance │ Shortest Path │
├──────┼────┼──────────┼───────────────┤
│ 1    │ 2  │ -1       │ 1 → 3 → 2     │
│ 1    │ 3  │ 1        │ 1 → 3         │
│ 1    │ 4  │ 0        │ 1 → 3 → 2 → 4 │
│ 2    │ 4  │ 1        │ 2 → 4         │
│ 3    │ 2  │ -2       │ 3 → 2         │
│ 3    │ 4  │ -1       │ 3 → 2 → 4     │
└──────┴────┴──────────┴───────────────┘
```

A **negative cycle** is detected by checking the diagonal after the run — if any `dist[i][i] < 0`, a negative cycle exists through node i and shortest paths involving it are undefined (can be made arbitrarily small by looping the cycle).

---

