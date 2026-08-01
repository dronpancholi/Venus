"""
VRIP Phase 2 — Repository Knowledge Graph

Unified graph of all repository knowledge:
files, classes, capabilities, specs, requirements, ADRs, events, tests.

Every entity in the repository is represented as a node.
Every relationship is represented as an edge.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


class KNode:
    """A node in the repository knowledge graph."""

    def __init__(self, node_id: str, kind: str, label: str = "", **attrs):
        self.node_id = node_id
        self.kind = kind
        self.label = label or node_id
        self.attrs: dict[str, Any] = dict(attrs)
        self.created_at = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict[str, Any]:
        return {
            "node_id": self.node_id,
            "kind": self.kind,
            "label": self.label,
            "attrs": dict(self.attrs),
        }


class KEdge:
    """An edge in the repository knowledge graph."""

    def __init__(self, source: str, target: str, kind: str, **attrs):
        self.source = source
        self.target = target
        self.kind = kind
        self.attrs: dict[str, Any] = dict(attrs)

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "target": self.target,
            "kind": self.kind,
            "attrs": dict(self.attrs),
        }


class KnowledgeGraph:
    """Repository knowledge graph. The canonical model of the platform."""

    def __init__(self):
        self._store: dict[str, KNode] = {}
        self.edges: list[KEdge] = []

    def add_node(self, kind: str, node_id: str, label: str = "", **attrs) -> KNode:
        if node_id in self._store:
            existing = self._store[node_id]
            existing.attrs.update(attrs)
            return existing
        node = KNode(node_id, kind, label, **attrs)
        self._store[node_id] = node
        return node

    def add_edge(self, source: str, target: str, kind: str, **attrs) -> KEdge:
        edge = KEdge(source, target, kind, **attrs)
        self.edges.append(edge)
        return edge

    def get_node(self, node_id: str) -> KNode | None:
        return self._store.get(node_id)

    def find_nodes(self, kind: str | None = None, **attrs) -> list[KNode]:
        results = list(self._store.values())
        if kind:
            results = [n for n in results if n.kind == kind]
        for key, value in attrs.items():
            results = [n for n in results if n.attrs.get(key) == value]
        return results

    def find_edges(self, kind: str | None = None, source: str | None = None, target: str | None = None) -> list[KEdge]:
        results = list(self.edges)
        if kind:
            results = [e for e in results if e.kind == kind]
        if source:
            results = [e for e in results if e.source == source]
        if target:
            results = [e for e in results if e.target == target]
        return results

    def neighbors(self, node_id: str, edge_kind: str | None = None) -> list[KNode]:
        ids = set()
        for e in self.edges:
            if e.source == node_id and (edge_kind is None or e.kind == edge_kind):
                ids.add(e.target)
            if e.target == node_id and (edge_kind is None or e.kind == edge_kind):
                ids.add(e.source)
        return [self._store[nid] for nid in ids if nid in self._store]

    def count_by_kind(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for n in self._store.values():
            counts[n.kind] = counts.get(n.kind, 0) + 1
        return counts

    def count_edges_by_kind(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for e in self.edges:
            counts[e.kind] = counts.get(e.kind, 0) + 1
        return counts

    def summary(self) -> dict[str, Any]:
        return {
            "total_nodes": len(self._store),
            "total_edges": len(self.edges),
            "nodes_by_kind": self.count_by_kind(),
            "edges_by_kind": self.count_edges_by_kind(),
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "nodes": {nid: n.to_dict() for nid, n in self._store.items()},
            "edges": [e.to_dict() for e in self.edges],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "KnowledgeGraph":
        kg = cls()
        for nid, ndata in data.get("nodes", {}).items():
            kg._store[nid] = KNode(
                node_id=ndata["node_id"],
                kind=ndata["kind"],
                label=ndata["label"],
                **ndata.get("attrs", {}),
            )
        for edata in data.get("edges", []):
            kg.edges.append(KEdge(
                source=edata["source"],
                target=edata["target"],
                kind=edata["kind"],
                **edata.get("attrs", {}),
            ))
        return kg
