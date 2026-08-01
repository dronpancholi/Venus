from __future__ import annotations

import time
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from threading import RLock
from typing import Any

from genesis.utils.identity import generate_id


class LayerType(Enum):
    STRUCTURAL = "structural"
    SEMANTIC = "semantic"
    CAPABILITY = "capability"
    ARCHITECTURE = "architecture"
    RUNTIME = "runtime"
    DEPENDENCY = "dependency"
    KNOWLEDGE = "knowledge"
    MEMORY = "memory"
    EVOLUTION = "evolution"
    EXPERIMENT = "experiment"
    RESEARCH = "research"
    ORGANIZATION = "organization"


@dataclass
class GraphNode:
    id: str = ""
    name: str = ""
    node_type: str = "entity"
    properties: dict[str, Any] = field(default_factory=dict)
    labels: list[str] = field(default_factory=list)
    weight: float = 1.0
    created_at: float = 0.0

    def __post_init__(self):
        if not self.id:
            self.id = generate_id("gn", 12)
        if not self.created_at:
            self.created_at = time.time()

    def has_label(self, label: str) -> bool:
        return label in self.labels


@dataclass
class GraphEdge:
    id: str = ""
    source_id: str = ""
    target_id: str = ""
    edge_type: str = "related"
    properties: dict[str, Any] = field(default_factory=dict)
    weight: float = 1.0
    bidirectional: bool = False
    created_at: float = 0.0

    def __post_init__(self):
        if not self.id:
            self.id = generate_id("ge", 12)
        if not self.created_at:
            self.created_at = time.time()


@dataclass
class GraphSnapshot:
    id: str = ""
    layer: str = ""
    node_count: int = 0
    edge_count: int = 0
    timestamp: float = 0.0
    checksum: str = ""

    def __post_init__(self):
        if not self.id:
            self.id = generate_id("gsnap", 12)
        if not self.timestamp:
            self.timestamp = time.time()


class GraphEntity:
    """A node with its connected edges within a layer."""

    def __init__(self, node: GraphNode, edges: list[GraphEdge] | None = None):
        self.node = node
        self.edges = edges or []


class GraphLayer:
    """A single typed layer within the unified graph."""

    def __init__(self, name: str, layer_type: LayerType):
        self.name = name
        self.layer_type = layer_type
        self._nodes: dict[str, GraphNode] = {}
        self._edges: dict[str, GraphEdge] = {}
        self._outgoing: dict[str, list[str]] = defaultdict(list)
        self._incoming: dict[str, list[str]] = defaultdict(list)
        self._label_index: dict[str, set[str]] = defaultdict(set)
        self._lock = RLock()

    def add_node(self, node: GraphNode) -> str:
        with self._lock:
            self._nodes[node.id] = node
            for label in node.labels:
                self._label_index[label].add(node.id)
            return node.id

    def get_node(self, node_id: str) -> GraphNode | None:
        return self._nodes.get(node_id)

    def remove_node(self, node_id: str) -> bool:
        with self._lock:
            node = self._nodes.pop(node_id, None)
            if not node:
                return False
            for label in node.labels:
                self._label_index[label].discard(node_id)
            edges = list(self._outgoing.get(node_id, []))
            edges += list(self._incoming.get(node_id, []))
            for eid in set(edges):
                self.remove_edge(eid)
            self._outgoing.pop(node_id, None)
            self._incoming.pop(node_id, None)
            return True

    def add_edge(self, edge: GraphEdge) -> str:
        with self._lock:
            if edge.source_id not in self._nodes or edge.target_id not in self._nodes:
                raise ValueError("Both source and target nodes must exist in this layer")
            self._edges[edge.id] = edge
            self._outgoing[edge.source_id].append(edge.id)
            self._incoming[edge.target_id].append(edge.id)
            if edge.bidirectional:
                self._outgoing[edge.target_id].append(edge.id)
                self._incoming[edge.source_id].append(edge.id)
            return edge.id

    def get_edge(self, edge_id: str) -> GraphEdge | None:
        return self._edges.get(edge_id)

    def remove_edge(self, edge_id: str) -> bool:
        with self._lock:
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

    def find_nodes(self, property_filter: dict[str, Any] | None = None,
                   labels: list[str] | None = None) -> list[GraphNode]:
        results: list[GraphNode] = []
        for node in self._nodes.values():
            if labels and not any(l in node.labels for l in labels):
                continue
            if property_filter:
                match = True
                for k, v in property_filter.items():
                    if node.properties.get(k) != v:
                        match = False
                        break
                if not match:
                    continue
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

    def node_count(self) -> int:
        return len(self._nodes)

    def edge_count(self) -> int:
        return len(self._edges)

    def snapshot(self) -> GraphSnapshot:
        import hashlib
        content = f"{self.node_count()}:{self.edge_count()}:{time.time()}"
        return GraphSnapshot(
            layer=self.name,
            node_count=self.node_count(),
            edge_count=self.edge_count(),
            checksum=hashlib.md5(content.encode()).hexdigest()[:16],
        )

    def summary(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "type": self.layer_type.value,
            "nodes": self.node_count(),
            "edges": self.edge_count(),
            "labels": {l: len(ids) for l, ids in self._label_index.items()},
        }


class UnifiedGraph:
    """Multi-layer graph platform supporting all graph layers."""

    def __init__(self):
        self._layers: dict[str, GraphLayer] = {}
        self._snapshots: list[GraphSnapshot] = []
        self._lock = RLock()

    def create_layer(self, name: str, layer_type: LayerType) -> GraphLayer:
        with self._lock:
            if name in self._layers:
                raise ValueError(f"Layer '{name}' already exists")
            layer = GraphLayer(name, layer_type)
            self._layers[name] = layer
            return layer

    def get_layer(self, name: str) -> GraphLayer | None:
        return self._layers.get(name)

    def remove_layer(self, name: str) -> bool:
        with self._lock:
            return self._layers.pop(name, None) is not None

    def list_layers(self, layer_type: LayerType | None = None) -> list[GraphLayer]:
        if layer_type:
            return [l for l in self._layers.values() if l.layer_type == layer_type]
        return list(self._layers.values())

    def layer_count(self) -> int:
        return len(self._layers)

    def snapshot(self) -> GraphSnapshot:
        total_nodes = sum(l.node_count() for l in self._layers.values())
        total_edges = sum(l.edge_count() for l in self._layers.values())
        import hashlib
        content = f"{total_nodes}:{total_edges}:{time.time()}"
        snap = GraphSnapshot(
            id=generate_id("gsnap", 16),
            layer="__all__",
            node_count=total_nodes,
            edge_count=total_edges,
            checksum=hashlib.md5(content.encode()).hexdigest()[:16],
        )
        self._snapshots.append(snap)
        return snap

    def summary(self) -> dict[str, Any]:
        return {
            "layers": self.layer_count(),
            "by_type": {t.value: sum(1 for l in self._layers.values() if l.layer_type == t)
                       for t in LayerType},
            "total_nodes": sum(l.node_count() for l in self._layers.values()),
            "total_edges": sum(l.edge_count() for l in self._layers.values()),
            "snapshots": len(self._snapshots),
        }
