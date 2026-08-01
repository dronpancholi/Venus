from __future__ import annotations

import copy
import hashlib
import time
from dataclasses import dataclass, field
from threading import RLock
from typing import Any

from genesis.graph_v2.core import GraphEdge, GraphLayer, GraphNode, GraphSnapshot, UnifiedGraph
from genesis.utils.identity import generate_id


@dataclass
class GraphDiff:
    nodes_added: list[GraphNode] = field(default_factory=list)
    nodes_removed: list[str] = field(default_factory=list)
    nodes_modified: list[tuple[str, dict[str, Any], dict[str, Any]]] = field(default_factory=list)
    edges_added: list[GraphEdge] = field(default_factory=list)
    edges_removed: list[str] = field(default_factory=list)

    @property
    def total_changes(self) -> int:
        return (len(self.nodes_added) + len(self.nodes_removed) +
                len(self.nodes_modified) + len(self.edges_added) +
                len(self.edges_removed))

    def summary(self) -> dict[str, Any]:
        return {
            "nodes_added": len(self.nodes_added),
            "nodes_removed": len(self.nodes_removed),
            "nodes_modified": len(self.nodes_modified),
            "edges_added": len(self.edges_added),
            "edges_removed": len(self.edges_removed),
            "total_changes": self.total_changes,
        }


class GraphMerge:
    """Merges graph versions or layers."""

    def __init__(self):
        self._conflicts: list[dict[str, Any]] = []

    def merge_layers(self, base: GraphLayer, overlay: GraphLayer) -> GraphLayer:
        result_name = f"merged_{base.name}_{overlay.name}"
        result = GraphLayer(result_name, base.layer_type)
        for node in base._nodes.values():
            result.add_node(copy.deepcopy(node))
        for edge in base._edges.values():
            result.add_edge(copy.deepcopy(edge))
        for node in overlay._nodes.values():
            if node.id in result._nodes:
                existing = result._nodes[node.id]
                if existing != node:
                    self._conflicts.append({
                        "type": "node_conflict",
                        "id": node.id,
                        "existing": copy.deepcopy(existing),
                        "incoming": copy.deepcopy(node),
                    })
                    result._nodes[node.id] = node
            else:
                result.add_node(copy.deepcopy(node))
        for edge in overlay._edges.values():
            if edge.id in result._edges:
                continue
            try:
                result.add_edge(copy.deepcopy(edge))
            except ValueError:
                pass
        return result

    def conflicts(self) -> list[dict[str, Any]]:
        return list(self._conflicts)


class GraphVersioning:
    """Version control for graph layers with diff, merge, and snapshots."""

    def __init__(self):
        self._versions: dict[str, list[GraphSnapshot]] = {}
        self._layer_snapshots: dict[str, dict[str, tuple[dict, dict]]] = {}
        self._lock = RLock()

    def snapshot_layer(self, layer: GraphLayer) -> GraphSnapshot:
        snap = layer.snapshot()
        with self._lock:
            self._versions.setdefault(layer.name, []).append(snap)
            nodes_data = {nid: (n.name, n.node_type, dict(n.properties), list(n.labels))
                         for nid, n in layer._nodes.items()}
            edges_data = {eid: (e.source_id, e.target_id, e.edge_type, dict(e.properties))
                         for eid, e in layer._edges.items()}
            self._layer_snapshots.setdefault(layer.name, {})[snap.id] = (nodes_data, edges_data)
        return snap

    def diff(self, layer_name: str, snap_id_a: str, snap_id_b: str) -> GraphDiff:
        snapshots = self._layer_snapshots.get(layer_name, {})
        data_a = snapshots.get(snap_id_a)
        data_b = snapshots.get(snap_id_b)
        if not data_a or not data_b:
            return GraphDiff()
        nodes_a, edges_a = data_a
        nodes_b, edges_b = data_b
        diff = GraphDiff()
        for nid in nodes_b:
            if nid not in nodes_a:
                diff.nodes_added.append(GraphNode(id=nid, name=nodes_b[nid][0]))
            elif nodes_a[nid] != nodes_b[nid]:
                diff.nodes_modified.append((nid, dict(zip(["name", "type", "props", "labels"], nodes_a[nid])),
                                            dict(zip(["name", "type", "props", "labels"], nodes_b[nid]))))
        for nid in nodes_a:
            if nid not in nodes_b:
                diff.nodes_removed.append(nid)
        for eid in edges_b:
            if eid not in edges_a:
                diff.edges_added.append(GraphEdge(id=eid, source_id=edges_b[eid][0],
                                                   target_id=edges_b[eid][1],
                                                   edge_type=edges_b[eid][2]))
        for eid in edges_a:
            if eid not in edges_b:
                diff.edges_removed.append(eid)
        return diff

    def list_versions(self, layer_name: str) -> list[GraphSnapshot]:
        return list(self._versions.get(layer_name, []))

    def summary(self) -> dict[str, Any]:
        return {
            "layers": len(self._versions),
            "versions": sum(len(v) for v in self._versions.values()),
        }
