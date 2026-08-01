from __future__ import annotations

import time
from threading import RLock
from typing import Any

from genesis.graph_v2.core import GraphLayer, UnifiedGraph


class FederationLink:
    """A link between two federated graph instances."""

    def __init__(self, source: str, target: str,
                 layer_mappings: dict[str, str] | None = None):
        self.source = source
        self.target = target
        self.layer_mappings = layer_mappings or {}
        self.created_at = time.time()
        self.last_sync = 0.0


class GraphFederation:
    """Federation across multiple graph instances."""

    def __init__(self):
        self._graphs: dict[str, UnifiedGraph] = {}
        self._links: list[FederationLink] = []
        self._lock = RLock()

    def register(self, name: str, graph: UnifiedGraph):
        with self._lock:
            self._graphs[name] = graph

    def unregister(self, name: str) -> bool:
        with self._lock:
            return self._graphs.pop(name, None) is not None

    def link(self, source: str, target: str,
             layer_mappings: dict[str, str] | None = None) -> FederationLink:
        with self._lock:
            if source not in self._graphs or target not in self._graphs:
                raise ValueError("Both source and target graphs must be registered")
            link = FederationLink(source, target, layer_mappings)
            self._links.append(link)
            return link

    def sync(self, link: FederationLink) -> dict[str, int]:
        src_graph = self._graphs.get(link.source)
        tgt_graph = self._graphs.get(link.target)
        if not src_graph or not tgt_graph:
            return {}
        transferred = {}
        for src_layer_name, tgt_layer_name in (link.layer_mappings.items()
                                                if link.layer_mappings
                                                else [(n, n) for n in src_graph.list_layers()]):
            src_layer = src_graph.get_layer(src_layer_name)
            tgt_layer = tgt_graph.get_layer(tgt_layer_name)
            if not src_layer or not tgt_layer:
                continue
            nodes_added = 0
            edges_added = 0
            for node in src_layer._nodes.values():
                if node.id not in tgt_layer._nodes:
                    tgt_layer.add_node(node)
                    nodes_added += 1
            for edge in src_layer._edges.values():
                if edge.id not in tgt_layer._edges:
                    try:
                        tgt_layer.add_edge(edge)
                        edges_added += 1
                    except ValueError:
                        pass
            transferred[f"{src_layer_name}->{tgt_layer_name}"] = {
                "nodes": nodes_added,
                "edges": edges_added,
            }
        link.last_sync = time.time()
        return transferred

    def federated_graph(self) -> UnifiedGraph:
        merged = UnifiedGraph()
        for name, graph in self._graphs.items():
            for layer in graph.list_layers():
                existing = merged.get_layer(layer.name)
                if not existing:
                    merged.create_layer(layer.name, layer.layer_type)
                    existing = merged.get_layer(layer.name)
                for node in layer._nodes.values():
                    if node.id not in existing._nodes:
                        existing.add_node(node)
                for edge in layer._edges.values():
                    if edge.id not in existing._edges:
                        try:
                            existing.add_edge(edge)
                        except ValueError:
                            pass
        return merged

    def summary(self) -> dict[str, Any]:
        return {
            "graphs": len(self._graphs),
            "links": len(self._links),
            "graph_names": list(self._graphs.keys()),
        }
