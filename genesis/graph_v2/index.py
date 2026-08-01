from __future__ import annotations

from collections import defaultdict
from typing import Any

from genesis.graph_v2.core import GraphLayer


class GraphIndex:
    """Cross-layer graph indexing for fast lookups."""

    def __init__(self):
        self._global_node_index: dict[str, dict[str, Any]] = {}
        self._type_index: dict[str, set[str]] = defaultdict(set)
        self._label_index: dict[str, set[str]] = defaultdict(set)
        self._property_index: dict[str, dict[Any, set[str]]] = defaultdict(lambda: defaultdict(set))

    def index_layer(self, layer: GraphLayer):
        for node in layer._nodes.values():
            self._global_node_index[node.id] = {
                "name": node.name,
                "type": node.node_type,
                "labels": list(node.labels),
                "properties": dict(node.properties),
                "layer": layer.name,
            }
            self._type_index[node.node_type].add(node.id)
            for label in node.labels:
                self._label_index[label].add(node.id)
            for k, v in node.properties.items():
                self._property_index[k][v].add(node.id)

    def find_by_type(self, node_type: str) -> list[dict[str, Any]]:
        ids = self._type_index.get(node_type, set())
        return [self._global_node_index[nid] for nid in ids if nid in self._global_node_index]

    def find_by_label(self, label: str) -> list[dict[str, Any]]:
        ids = self._label_index.get(label, set())
        return [self._global_node_index[nid] for nid in ids if nid in self._global_node_index]

    def find_by_property(self, key: str, value: Any) -> list[dict[str, Any]]:
        ids = self._property_index.get(key, {}).get(value, set())
        return [self._global_node_index[nid] for nid in ids if nid in self._global_node_index]

    def search(self, query: str) -> list[dict[str, Any]]:
        q = query.lower()
        results: list[dict[str, Any]] = []
        for nid, data in self._global_node_index.items():
            if q in data["name"].lower() or q in str(data["properties"]).lower():
                results.append(data)
        return results

    def clear(self):
        self._global_node_index.clear()
        self._type_index.clear()
        self._label_index.clear()
        self._property_index.clear()

    def summary(self) -> dict[str, Any]:
        return {
            "indexed_nodes": len(self._global_node_index),
            "unique_types": len(self._type_index),
            "unique_labels": len(self._label_index),
            "indexed_properties": sum(len(v) for v in self._property_index.values()),
        }
