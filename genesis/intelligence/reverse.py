"""
VRIP Phase 4 — Reverse Engineering

Infer architectural layers, subsystem boundaries, dependency graphs,
import graphs, runtime graphs, event graphs, persistence graphs,
capability graphs from source code analysis.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .kgraph import KnowledgeGraph


LAYER_NAMES = {
    1: "Foundation Utilities",
    2: "Core Ontology & Types",
    3: "Infrastructure (DI, Events, Persistence)",
    4: "Domain Services",
    5: "Application Interface",
}


class ReverseEngineer:
    """Phase 4: Infer architecture from implementation."""

    def __init__(self, kg: KnowledgeGraph):
        self.kg = kg

    def run(self) -> dict[str, Any]:
        return {
            "layers": self._analyze_layers(),
            "import_graph": self._import_graph_summary(),
            "event_graph": self._event_graph_summary(),
            "persistence_graph": self._persistence_graph_summary(),
        }

    def _analyze_layers(self) -> dict[str, Any]:
        nodes_by_layer: dict[int, list[str]] = {}
        for node in self.kg.find_nodes(kind="file"):
            layer = node.attrs.get("layer", 0) or node.attrs.get("layer_num", 0)
            if layer not in nodes_by_layer:
                nodes_by_layer[layer] = []
            nodes_by_layer[layer].append(node.node_id)

        result = {}
        for layer in sorted(nodes_by_layer.keys()):
            name = LAYER_NAMES.get(layer, f"Layer {layer}")
            systems = set()
            for nid in nodes_by_layer[layer]:
                n = self.kg.get_node(nid)
                if n:
                    systems.add(n.attrs.get("subsystem", ""))
            result[str(layer)] = {
                "name": name,
                "files": len(nodes_by_layer[layer]),
                "subsystems": sorted(systems),
            }
        return result

    def _import_graph_summary(self) -> dict[str, Any]:
        edges = self.kg.find_edges(kind="imports")
        return {
            "total_import_edges": len(edges),
        }

    def _event_graph_summary(self) -> dict[str, Any]:
        event_files = []
        for node in self.kg.find_nodes(kind="file"):
            if node.attrs.get("subsystem") in ("events",):
                event_files.append(node.label)
        # Files that reference EventBus
        for node in self.kg.find_nodes(kind="class"):
            if "EventBus" in node.attrs.get("bases", []):
                event_files.append(node.label)
        return {
            "event_aware_files": len(event_files),
        }

    def _persistence_graph_summary(self) -> dict[str, Any]:
        store_nodes = self.kg.find_nodes(kind="class")
        stores = [n for n in store_nodes if "Store" in n.label or "Repository" in n.label]
        return {
            "storage_providers": len(stores),
            "providers": [n.label for n in stores],
        }
