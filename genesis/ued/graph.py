from __future__ import annotations

from collections import defaultdict, deque
from typing import Any

from genesis.ued.types import Query, QueryResult
from genesis.utils.identity import generate_id


class GraphNode:
    """A node in the property graph with labels and properties."""

    def __init__(self, id: str = "", labels: list[str] | None = None,
                 properties: dict[str, Any] | None = None):
        self.id = id or generate_id("gnode", 12)
        self.labels = labels or []
        self.properties = properties or {}

    def has_label(self, label: str) -> bool:
        return label in self.labels


class GraphEdge:
    """A directed edge between two graph nodes."""

    def __init__(self, id: str = "", source_id: str = "", target_id: str = "",
                 edge_type: str = "", properties: dict[str, Any] | None = None):
        self.id = id or generate_id("gedge", 12)
        self.source_id = source_id
        self.target_id = target_id
        self.edge_type = edge_type
        self.properties = properties or {}


class GraphStore:
    """Property graph storage with adjacency, traversal, and pattern matching."""

    def __init__(self):
        self._nodes: dict[str, GraphNode] = {}
        self._edges: dict[str, GraphEdge] = {}
        self._outgoing: dict[str, list[str]] = defaultdict(list)
        self._incoming: dict[str, list[str]] = defaultdict(list)
        self._label_index: dict[str, set[str]] = defaultdict(set)

    def add_node(self, node: GraphNode) -> str:
        self._nodes[node.id] = node
        for label in node.labels:
            self._label_index[label].add(node.id)
        return node.id

    def get_node(self, node_id: str) -> GraphNode | None:
        return self._nodes.get(node_id)

    def delete_node(self, node_id: str) -> bool:
        node = self._nodes.pop(node_id, None)
        if not node:
            return False
        for label in node.labels:
            self._label_index[label].discard(node_id)
        edges_to_remove = list(self._outgoing.get(node_id, []))
        edges_to_remove += list(self._incoming.get(node_id, []))
        for eid in set(edges_to_remove):
            self.delete_edge(eid)
        self._outgoing.pop(node_id, None)
        self._incoming.pop(node_id, None)
        return True

    def add_edge(self, edge: GraphEdge) -> str:
        if edge.source_id not in self._nodes or edge.target_id not in self._nodes:
            raise ValueError("Both source and target nodes must exist")
        self._edges[edge.id] = edge
        self._outgoing[edge.source_id].append(edge.id)
        self._incoming[edge.target_id].append(edge.id)
        return edge.id

    def get_edge(self, edge_id: str) -> GraphEdge | None:
        return self._edges.get(edge_id)

    def delete_edge(self, edge_id: str) -> bool:
        edge = self._edges.pop(edge_id, None)
        if not edge:
            return False
        outgoing = self._outgoing.get(edge.source_id, [])
        if edge_id in outgoing:
            outgoing.remove(edge_id)
        incoming = self._incoming.get(edge.target_id, [])
        if edge_id in incoming:
            incoming.remove(edge_id)
        return True

    def find_nodes_by_label(self, label: str) -> list[GraphNode]:
        ids = self._label_index.get(label, set())
        return [self._nodes[nid] for nid in ids if nid in self._nodes]

    def find_nodes(self, q: Query) -> list[GraphNode]:
        results: list[GraphNode] = []
        label_filter = None
        for field, op, value in q.filters:
            if field == "label" and op == "eq":
                label_filter = value
        candidates = (self.find_nodes_by_label(label_filter)
                     if label_filter else list(self._nodes.values()))
        for node in candidates:
            node_dict = {"id": node.id, "labels": node.labels, **node.properties}
            if q.matches(node_dict):
                results.append(node)
        return results

    def neighbors(self, node_id: str, edge_type: str | None = None) -> list[GraphNode]:
        neighbor_ids: set[str] = set()
        for eid in self._outgoing.get(node_id, []):
            e = self._edges[eid]
            if edge_type is None or e.edge_type == edge_type:
                neighbor_ids.add(e.target_id)
        for eid in self._incoming.get(node_id, []):
            e = self._edges[eid]
            if edge_type is None or e.edge_type == edge_type:
                neighbor_ids.add(e.source_id)
        return [self._nodes[nid] for nid in neighbor_ids if nid in self._nodes]

    def bfs(self, start_id: str, max_depth: int = 5) -> list[GraphNode]:
        visited: set[str] = {start_id}
        queue: deque[str] = deque([start_id])
        result: list[GraphNode] = []
        depth: dict[str, int] = {start_id: 0}
        while queue:
            current = queue.popleft()
            node = self._nodes.get(current)
            if node:
                result.append(node)
                if depth[current] >= max_depth:
                    continue
                for eid in self._outgoing.get(current, []):
                    e = self._edges[eid]
                    if e.target_id not in visited:
                        visited.add(e.target_id)
                        depth[e.target_id] = depth[current] + 1
                        queue.append(e.target_id)
        return result

    def dfs(self, start_id: str, max_depth: int = 10) -> list[GraphNode]:
        visited: set[str] = set()
        result: list[GraphNode] = []

        def _dfs(nid: str, d: int):
            if nid in visited or d > max_depth:
                return
            visited.add(nid)
            node = self._nodes.get(nid)
            if node:
                result.append(node)
            for eid in self._outgoing.get(nid, []):
                e = self._edges[eid]
                _dfs(e.target_id, d + 1)

        _dfs(start_id, 0)
        return result

    def shortest_path(self, from_id: str, to_id: str) -> list[GraphNode]:
        if from_id not in self._nodes or to_id not in self._nodes:
            return []
        visited: set[str] = {from_id}
        queue: deque[tuple[str, list[str]]] = deque([(from_id, [from_id])])
        while queue:
            current, path = queue.popleft()
            for eid in self._outgoing.get(current, []):
                e = self._edges[eid]
                if e.target_id == to_id:
                    path = path + [to_id]
                    return [self._nodes[nid] for nid in path if nid in self._nodes]
                if e.target_id not in visited:
                    visited.add(e.target_id)
                    queue.append((e.target_id, path + [e.target_id]))
        return []

    def find_paths(self, from_id: str, to_id: str, max_length: int = 5) -> list[list[GraphNode]]:
        paths: list[list[str]] = []

        def _dfs_paths(current: str, target: str, path: list[str], depth: int):
            if depth > max_length:
                return
            if current == target:
                paths.append(list(path))
                return
            for eid in self._outgoing.get(current, []):
                e = self._edges[eid]
                if e.target_id not in path:
                    _dfs_paths(e.target_id, target, path + [e.target_id], depth + 1)

        _dfs_paths(from_id, to_id, [from_id], 0)
        return [[self._nodes[nid] for nid in p if nid in self._nodes] for p in paths]

    def node_count(self) -> int:
        return len(self._nodes)

    def edge_count(self) -> int:
        return len(self._edges)

    def summary(self) -> dict[str, Any]:
        return {
            "nodes": self.node_count(),
            "edges": self.edge_count(),
            "labels": {l: len(ids) for l, ids in self._label_index.items()},
        }
