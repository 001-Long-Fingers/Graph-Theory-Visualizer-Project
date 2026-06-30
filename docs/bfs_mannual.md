# `collections` — deque, OrderedDict, and BFS

---

## 1. The `collections` Module

Python's built-in `collections` module provides specialised container datatypes that extend the four basics — `list`, `dict`, `tuple`, `set`. Two of them are used directly in the BFS implementation: `deque` and `OrderedDict`.

```python
from collections import deque, OrderedDict
```

---

## 2. `deque` — Double-Ended Queue

### What it is

A `deque` (pronounced *deck*) is a sequence container that supports **O(1) appends and pops from both ends**. A regular Python `list` can only pop from the right in O(1); popping from the left (`list.pop(0)`) is O(n) because every remaining element shifts. `deque` avoids this entirely.

```
       left end                    right end
          │                            │
    ┌─────▼──────────────────────────▼─────┐
    │  ←  pop_left  │  data  │  pop_right →  │
    └──────────────────────────────────────┘
          │                            │
    appendleft(x)                 append(x)
```

### Core methods

| Method | Description | Time |
|---|---|---|
| `append(x)` | Add `x` to the right end | O(1) |
| `appendleft(x)` | Add `x` to the left end | O(1) |
| `pop()` | Remove and return from the right | O(1) |
| `popleft()` | Remove and return from the left | O(1) |
| `len(d)` | Number of elements | O(1) |

### Creating a deque

```python
from collections import deque

d = deque()            # empty
d = deque([1, 2, 3])   # from an iterable
d = deque(maxlen=5)    # bounded deque — old items drop off when full
```

### Example

```python
d = deque([10, 20, 30])

d.append(40)        # deque([10, 20, 30, 40])
d.appendleft(0)     # deque([0, 10, 20, 30, 40])
d.pop()             # returns 40  →  deque([0, 10, 20, 30])
d.popleft()         # returns 0   →  deque([10, 20, 30])
```

### Why it matters for BFS

BFS processes nodes in **first-in, first-out** order — exactly what a queue does. Using `deque` means:

- `append(node)` enqueues a node to the back — O(1).
- `popleft()` dequeues the front node for processing — O(1).

Using a `list` instead would make every `pop(0)` O(n), turning BFS from O(V + E) into O(V² + E) on large graphs.

```python
queue = deque([start])   # initialise with start node
node  = queue.popleft()  # dequeue front for processing
queue.append(neighbour)  # enqueue newly discovered neighbour
```

---

## 3. `OrderedDict` — Dictionary with Insertion Order

### What it is

An `OrderedDict` is a dictionary subclass that **remembers the order in which keys were inserted**. In CPython 3.7+ regular `dict` also preserves insertion order as an implementation detail, but `OrderedDict` makes this a **language-level guarantee** and adds a few extra methods.

```python
from collections import OrderedDict

od = OrderedDict()
od['a'] = 1
od['b'] = 2
od['c'] = 3

for k, v in od.items():
    print(k, v)
# a 1
# b 2
# c 3   ← guaranteed in insertion order
```

### Extra methods over plain `dict`

| Method | Description |
|---|---|
| `move_to_end(key, last=True)` | Move an existing key to the right end (or left if `last=False`) |
| `popitem(last=True)` | Remove and return the last (or first) `(key, value)` pair |

### `OrderedDict` vs plain `dict`

| | `dict` (3.7+) | `OrderedDict` |
|---|---|---|
| Preserves insertion order | Yes (impl. detail) | Yes (spec. guarantee) |
| `==` considers order | No | Yes |
| `move_to_end` | No | Yes |
| Memory overhead | Lower | Slightly higher |

```python
# Order matters for equality in OrderedDict
from collections import OrderedDict

a = OrderedDict([('x', 1), ('y', 2)])
b = OrderedDict([('y', 2), ('x', 1)])

a == b          # False — same keys/values, different order
dict(a) == dict(b)  # True  — plain dicts ignore order
```

### Why it is used for the adjacency list

The graph's adjacency list is built with:

```python
adj = OrderedDict((v, sorted(set())) for v in self.V)
```

Since `self.V = sorted(V)`, the nodes are inserted in ascending numerical order. Using `OrderedDict` guarantees that when the adjacency list is iterated — to print it, to build the BFS table — the nodes always appear in that same sorted order, independent of Python version or platform.

---

## 4. BFS and the Traversal Table

### 4.1 What BFS does

**Breadth-First Search** explores a graph level by level, starting from a source node. It visits every node reachable from the source, and does so in order of increasing distance (number of edges) from the source.

```
Graph (binary tree):

        1
       / \
      2   3
     / \ / \
    4  5 6  7

BFS from 1:

  Level 0 → visit 1
  Level 1 → visit 2, 3
  Level 2 → visit 4, 5, 6, 7
```

### 4.2 The algorithm step by step

```
Initialise:
  visited = {start}
  queue   = deque([start])
  order   = []

While queue is not empty:
  1. node ← queue.popleft()          ← dequeue the front node
  2. order.append(node)              ← record visit
  3. For each neighbour of node:
       if neighbour not in visited:
         visited.add(neighbour)
         queue.append(neighbour)     ← enqueue for later
  4. Record the step in the table
```

The `visited` set is updated **at enqueue time** (step 3), not at dequeue time. This is critical — it prevents the same node from being enqueued multiple times when it has several neighbours that have already been processed.

### 4.3 The traversal table — column by column

Each row of the table corresponds to one iteration of the while loop — one node being dequeued and processed.

| Column | What it shows |
|---|---|
| **Step** | Which iteration of the loop this is (1-indexed) |
| **Node** | The node dequeued and currently being processed |
| **Neighbours** | Every neighbour of the current node (from the adjacency list) |
| **Newly Enqueued** | The subset of neighbours that were not yet visited and were added to the queue this step |
| **Queue After** | The contents of the queue *after* processing this node (left = next to be dequeued) |
| **Visited So Far** | All nodes that have been fully processed up to and including this step |

### 4.4 Worked example

Graph: `V = {1,2,3,4,5,6,7}`, edges forming a binary tree, BFS from node 1.

```
Initial state
  visited = {1}
  queue   = [1]
```

**Step 1 — dequeue 1**

```
  node        = 1
  neighbours  = [2, 3]
  enqueue 2 and 3  →  visited = {1,2,3},  queue = [2, 3]
```

| Step | Node | Neighbours | Newly Enqueued | Queue After | Visited So Far |
|---|---|---|---|---|---|
| 1 | 1 | 2, 3 | 2, 3 | 2 → 3 | 1 |

**Step 2 — dequeue 2**

```
  node        = 2
  neighbours  = [1, 4, 5]
  1 already visited
  enqueue 4 and 5  →  visited = {1,2,3,4,5},  queue = [3, 4, 5]
```

| Step | Node | Neighbours | Newly Enqueued | Queue After | Visited So Far |
|---|---|---|---|---|---|
| 2 | 2 | 1, 4, 5 | 4, 5 | 3 → 4 → 5 | 1 → 2 |

**Step 3 — dequeue 3**

```
  node        = 3
  neighbours  = [1, 6, 7]
  1 already visited
  enqueue 6 and 7  →  visited = {1,2,3,4,5,6,7},  queue = [4, 5, 6, 7]
```

| Step | Node | Neighbours | Newly Enqueued | Queue After | Visited So Far |
|---|---|---|---|---|---|
| 3 | 3 | 1, 6, 7 | 6, 7 | 4 → 5 → 6 → 7 | 1 → 2 → 3 |

**Steps 4–7 — dequeue 4, 5, 6, 7**

All their neighbours are already visited. Queue drains to empty.

| Step | Node | Neighbours | Newly Enqueued | Queue After | Visited So Far |
|---|---|---|---|---|---|
| 4 | 4 | 2 | — | 5 → 6 → 7 | 1 → 2 → 3 → 4 |
| 5 | 5 | 2 | — | 6 → 7 | 1 → 2 → 3 → 4 → 5 |
| 6 | 6 | 3 | — | 7 | 1 → 2 → 3 → 4 → 5 → 6 |
| 7 | 7 | 3 | — | empty | 1 → 2 → 3 → 4 → 5 → 6 → 7 |

**Final BFS order: 1 → 2 → 3 → 4 → 5 → 6 → 7**

### 4.5 Time and space complexity

| | Complexity | Reason |
|---|---|---|
| **Time** | O(V + E) | Every vertex dequeued once; every edge inspected once |
| **Space** | O(V) | Queue and visited set each hold at most V nodes |

Using `deque` for the queue preserves the O(V + E) time bound. A `list` with `pop(0)` would make each dequeue O(V), pushing total time to O(V² + E).