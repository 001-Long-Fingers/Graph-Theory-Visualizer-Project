# Graph Traversal and Path-Finding Algorithms

This document outlines the graph algorithms implemented or planned for the Interactive Graph Theory project.

The goal of these implementations is not only to compute graph properties but also to visualize algorithm execution and develop an interactive graph theory learning environment.

---

# Implemented Algorithms

## Dijkstra's Shortest Path Algorithm

<img width="1920" height="1080" alt="Traversal" src="https://github.com/user-attachments/assets/bc3d8730-03ed-42a2-a78b-03dd067529ca" />



**Status:** Implemented

Dijkstra's Algorithm computes the shortest path from a source vertex to all other vertices in a weighted graph with non-negative edge weights.

### Features

* Single-source shortest paths
* Path reconstruction
* Interactive visualization support
* Compatible with weighted graphs

### Time Complexity

| Data Structure | Complexity       |
| -------------- | ---------------- |
| Array          | O(V²)            |
| Priority Queue | O((V + E) log V) |

### Applications

* Routing systems
* Network optimization
* Navigation problems
* Graph analysis

---

## Breadth-First Search (BFS)

<img width="1308" height="841" alt="BFSvis" src="https://github.com/user-attachments/assets/c464d9f0-9e9b-4202-a464-ded03629686f" />




**Status:** Implemented

Breadth-First Search explores a graph level by level, visiting all vertices at distance 1 before distance 2, and so on.

### Planned Features

* BFS traversal visualization
* Connected component discovery
* Unweighted shortest paths
* Layer visualization

### Time Complexity

| Operation | Complexity |
| --------- | ---------- |
| BFS       | O(V + E)   |

### Applications

* Shortest paths in unweighted graphs
* Network exploration
* Connectivity testing

---

# Work In Progress

## Bellman-Ford Algorithm

**Status:** Planned

Bellman-Ford computes shortest paths from a single source and can handle negative edge weights.

Unlike Dijkstra's algorithm, Bellman-Ford can detect negative-weight cycles.

### Planned Features

* Negative edge support
* Negative cycle detection
* Path reconstruction
* Step-by-step visualization

### Time Complexity

| Operation    | Complexity |
| ------------ | ---------- |
| Bellman-Ford | O(VE)      |

### Applications

* Currency arbitrage detection
* Economic models
* General weighted graphs

---

## Floyd-Warshall Algorithm

**Status:** Planned

Floyd-Warshall computes shortest paths between every pair of vertices in a graph.

It is an all-pairs shortest-path algorithm based on dynamic programming.

### Planned Features

* All-pairs shortest paths
* Distance matrix visualization
* Path reconstruction
* Matrix update visualization

### Time Complexity

| Operation      | Complexity |
| -------------- | ---------- |
| Floyd-Warshall | O(V³)      |

### Applications

* Network analysis
* Routing tables
* Dense graph optimization

---

# Future Algorithms

The project may later expand to include:

* Depth-First Search (DFS)
* Graph Coloring
* Connected Components
* Cycle Detection
* Strongly Connected Components

---

# Project Vision

The long-term goal is to transform this repository from a graph visualization tool into an interactive graph theory laboratory capable of:

* Constructing graphs
* Running algorithms
* Visualizing execution
* Comparing algorithm performance
* Exploring graph-theoretic concepts interactively

Each algorithm will be developed as an independent module inside the `algorithms/` directory and integrated into the visualization framework as the project evolves.
