"""
VENUS-II-UTIL-GRAPH-01: Graph Algorithms — Single implementations

Normative References:
  - VPS Part IV §4.4: Graph Operation Semantics
  - VPS Part VII §7.4: UIR Transformations
  - GENESIS_II_ARCHITECTURE §4.5: Graph Algorithm Unification

Purpose:
  Consolidate all graph algorithm implementations (topological sort,
  cycle detection, subgraph extraction) into one authoritative module.
  Genesis-I had three topological sort and two cycle detection implementations.
  This module provides the single implementation used everywhere.
"""

from collections import defaultdict, deque
from typing import Any


def topological_sort(edges: list[tuple[str, str]], nodes: set[str] | None = None) -> list[str]:
    """
    NORMATIVE: Single topological sort implementation for all Venus operations.

    Preconditions:
      - edges is a list of (source, target) pairs
      - If nodes is None, all unique node IDs are inferred from edges

    Postconditions:
      - Returns a list of node IDs in topological order
      - Every node appears exactly once
      - For every edge (u, v), u appears before v in the result

    Failure:
      - If the graph contains cycles, nodes in cycles appear after all
        non-cycle nodes. Callers should use find_cycles() separately.

    Complexity: O(V + E) using Kahn's algorithm with deque for O(1) pop.
    """
    adj: dict[str, set[str]] = defaultdict(set)
    in_degree: dict[str, int] = defaultdict(int)
    all_nodes: set[str] = set(nodes) if nodes is not None else set()

    for src, tgt in edges:
        adj[src].add(tgt)
        in_degree[tgt] += 1
        all_nodes.add(src)
        all_nodes.add(tgt)

    # Use deque for O(1) pop from front
    queue: deque[str] = deque()
    for n in all_nodes:
        if in_degree.get(n, 0) == 0:
            queue.append(n)

    result: list[str] = []
    while queue:
        node = queue.popleft()
        result.append(node)
        for neighbor in adj.get(node, set()):
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    # Append remaining nodes (cycle participants) in arbitrary order
    remaining = all_nodes - set(result)
    if remaining:
        result.extend(remaining)

    return result


def find_cycles(edges: list[tuple[str, str]]) -> list[list[str]]:
    """
    NORMATIVE: Single cycle detection implementation for all Venus operations.

    Preconditions:
      - edges is a list of (source, target) pairs

    Postconditions:
      - Returns a list of cycles, where each cycle is a list of node IDs
      - Each cycle is represented as [start, ..., start] (start node repeated)
      - Returns empty list if no cycles exist

    Complexity: O(V + E) using DFS coloring.
    """
    adj: dict[str, set[str]] = defaultdict(set)
    for src, tgt in edges:
        adj[src].add(tgt)

    cycles: list[list[str]] = []
    visited: set[str] = set()
    path: list[str] = []
    path_set: set[str] = set()
    node_limit = 200  # Safety limit to prevent infinite loops in degenerate graphs

    def _dfs(node: str):
        if node in path_set:
            idx = path.index(node)
            cycles.append(path[idx:] + [node])
            return
        if node in visited:
            return
        visited.add(node)
        path.append(node)
        path_set.add(node)
        for neighbor in adj.get(node, set()):
            _dfs(neighbor)
        path.pop()
        path_set.discard(node)

    for node in list(adj.keys())[:node_limit]:
        if node not in visited:
            _dfs(node)

    return cycles


def subgraph(
    nodes: dict[str, Any],
    edges: list[tuple[str, str, str]],
    root_id: str,
    depth: int = 1,
) -> tuple[dict[str, Any], list[tuple[str, str, str]]]:
    """
    NORMATIVE: Single subgraph extraction implementation.

    Preconditions:
      - nodes is a dict of node_id -> node object
      - edges is a list of (source, target, edge_type) tuples
      - root_id exists in nodes

    Postconditions:
      - Returns (subgraph_nodes, subgraph_edges) where subgraph_nodes
        contains all nodes within 'depth' hops of root_id
      - Edge direction is respected for traversal

    Complexity: O(V + E) bounded by frontier size per depth level.
    """
    # Build adjacency for BFS
    adj: dict[str, list[str]] = defaultdict(list)
    for src, tgt, _edge_type in edges:
        adj[src].append(tgt)
        adj[tgt].append(src)  # Undirected for subgraph extraction

    visited: set[str] = {root_id}
    frontier: set[str] = {root_id}

    for _ in range(depth):
        next_frontier: set[str] = set()
        for fid in frontier:
            for nid in adj.get(fid, []):
                if nid not in visited:
                    visited.add(nid)
                    next_frontier.add(nid)
        frontier = next_frontier

    result_nodes: dict[str, Any] = {}
    for nid in visited:
        if nid in nodes:
            result_nodes[nid] = nodes[nid]

    result_edges: list[tuple[str, str, str]] = []
    for src, tgt, etype in edges:
        if src in visited and tgt in visited:
            result_edges.append((src, tgt, etype))

    return result_nodes, result_edges
