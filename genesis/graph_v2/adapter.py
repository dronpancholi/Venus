"""
UnifiedGraph Adapter — Wrap any graph implementation into the UnifiedGraph interface.

Each legacy graph becomes a GraphLayer within a UnifiedGraph, preserving its
native API while providing canonical access through traversal/search/transform.

Usage:
    adapter = GraphAdapter(unified_graph)
    legacy_layer = adapter.wrap(legacy_graph_instance, "legacy_name", LayerType.KNOWLEDGE)
    # Now accessible via:
    unified_graph.get_layer("legacy_name")  # → GraphLayer
    traversal.bfs(root)                     # → works across all layers
"""

from __future__ import annotations

import time
from typing import Any, Callable

from genesis.graph_v2.core import (
    GraphEdge, GraphLayer, GraphNode, GraphSnapshot,
    LayerType, UnifiedGraph,
)
from genesis.graph_v2.traversal import GraphTraversal


class GraphAdapterError(Exception):
    """Raised when graph adapter encounters an unsupported operation."""


def _legacy_to_graph_node(
    legacy_id: str,
    name: str = "",
    node_type: str = "legacy",
    properties: dict | None = None,
    labels: list[str] | None = None,
) -> GraphNode:
    return GraphNode(
        id=str(legacy_id),
        name=name or str(legacy_id),
        node_type=node_type,
        properties=properties or {},
        labels=labels or [],
    )


def _legacy_to_graph_edge(
    source_id: str,
    target_id: str,
    edge_type: str = "related",
    properties: dict | None = None,
    bidirectional: bool = False,
) -> GraphEdge:
    return GraphEdge(
        source_id=str(source_id),
        target_id=str(target_id),
        edge_type=edge_type,
        properties=properties or {},
        bidirectional=bidirectional,
    )


class GraphAdapter:
    """Adapts external graph implementations into the UnifiedGraph framework."""

    def __init__(self, unified_graph: UnifiedGraph | None = None):
        self.graph = unified_graph or UnifiedGraph()
        self.traversal = GraphTraversal(self.graph)
        self._adapters: dict[str, _BaseAdapter] = {}

    def wrap(self, legacy_graph: Any, layer_name: str,
             layer_type: LayerType = LayerType.KNOWLEDGE) -> GraphLayer:
        """Wrap a legacy graph as a named layer in the unified graph."""
        adapter = _detect_adapter(legacy_graph, layer_name, layer_type)
        layer = adapter.sync(self.graph)
        self._adapters[layer_name] = adapter
        return layer

    def sync_all(self):
        for name, adapter in self._adapters.items():
            nodes, edges = adapter._extract()
            layer = self.graph.get_layer(name)
            if layer is None:
                layer = self.graph.create_layer(name, adapter.layer_type)
            for n in nodes:
                if not layer.get_node(n.id):
                    layer.add_node(n)
            for e in edges:
                try:
                    layer.add_edge(e)
                except ValueError:
                    pass

    def list_adapters(self) -> dict[str, str]:
        return {name: type(adapter).__name__ for name, adapter in self._adapters.items()}

    def summary(self) -> dict[str, Any]:
        layers = self.graph.list_layers()
        if isinstance(layers, list):
            layer_names = [l.name if hasattr(l, "name") else str(l) for l in layers]
        elif isinstance(layers, dict):
            layer_names = list(layers.keys())
        else:
            layer_names = []
        return {
            "total_adapters": len(self._adapters),
            "adapters": self.list_adapters(),
            "graph_layers": layer_names,
        }


class _BaseAdapter:
    """Base adapter — implement _extract_nodes_edges() for each legacy graph type."""

    def __init__(self, legacy: Any, layer_name: str, layer_type: LayerType):
        self.legacy = legacy
        self.layer_name = layer_name
        self.layer_type = layer_type

    def sync(self, graph: UnifiedGraph) -> GraphLayer:
        existing = None
        for name in (self.layer_name,):
            try:
                existing = graph.get_layer(name)
            except Exception:
                pass
        if existing is not None:
            layer = existing
        else:
            layer = graph.create_layer(self.layer_name, self.layer_type)
        nodes, edges = self._extract()
        for n in nodes:
            layer.add_node(n)
        for e in edges:
            try:
                layer.add_edge(e)
            except ValueError:
                pass
        return layer

    def _extract(self) -> tuple[list[GraphNode], list[GraphEdge]]:
        """Override in subclass — return (nodes, edges) from legacy graph."""
        return [], []


def _detect_adapter(legacy: Any, layer_name: str, layer_type: LayerType) -> _BaseAdapter:
    """Auto-detect the right adapter for a legacy graph instance."""
    cls_name = type(legacy).__name__

    # Pattern match on class name
    if "KnowledgeGraphEngine" in cls_name:
        return _KnowledgeGraphEngineAdapter(legacy, layer_name, layer_type)
    if "KnowledgeGraph" in cls_name and "Planetary" not in cls_name:
        return _KnowledgeGraphAdapter(legacy, layer_name, layer_type)
    if "PlanetaryKnowledgeGraph" in cls_name:
        return _PlanetaryKnowledgeGraphAdapter(legacy, layer_name, layer_type)
    if "HypergraphKnowledgeCore" in cls_name:
        return _HypergraphAdapter(legacy, layer_name, layer_type)
    if "ExecutionGraph" in cls_name:
        return _ExecutionGraphAdapter(legacy, layer_name, layer_type)
    if "EngineeringKnowledgeGraph" in cls_name or "RepositoryGraph" in cls_name:
        return _RepositoryGraphAdapter(legacy, layer_name, layer_type)
    if "BrainGraph" in cls_name:
        return _BrainGraphAdapter(legacy, layer_name, layer_type)
    if "UIRGraph" in cls_name:
        return _UIRGraphAdapter(legacy, layer_name, layer_type)
    if "USIRGraph" in cls_name:
        return _USIRGraphAdapter(legacy, layer_name, layer_type)
    if "WorkspaceDependencyGraph" in cls_name or "WorkspaceGraph" in cls_name:
        return _WorkspaceGraphAdapter(legacy, layer_name, layer_type)
    if "BuildGraph" in cls_name:
        return _BuildGraphAdapter(legacy, layer_name, layer_type)
    if "CapabilityDependencyGraph" in cls_name:
        return _CapabilityGraphAdapter(legacy, layer_name, layer_type)
    if "WorldGraph" in cls_name:
        return _WorldGraphAdapter(legacy, layer_name, layer_type)
    if "ObservatoryGraph" in cls_name:
        return _ObservatoryGraphAdapter(legacy, layer_name, layer_type)
    if "PersistentTaskGraph" in cls_name:
        return _TaskGraphAdapter(legacy, layer_name, layer_type)

    return _GenericAdapter(legacy, layer_name, layer_type)


class _GenericAdapter(_BaseAdapter):
    """Fallback — tries common graph interfaces (.nodes, .edges, .get_node, etc)."""

    def _extract(self) -> tuple[list[GraphNode], list[GraphEdge]]:
        nodes: list[GraphNode] = []
        edges: list[GraphEdge] = []
        g = self.legacy

        raw_nodes = getattr(g, "nodes", None) or getattr(g, "_nodes", None) or {}
        if isinstance(raw_nodes, dict):
            for nid, ndata in raw_nodes.items():
                props = {}
                if isinstance(ndata, dict):
                    props = {k: v for k, v in ndata.items() if k != "name" and k != "type"}
                    name = str(ndata.get("name", nid))
                    ntype = str(ndata.get("type", "unknown"))
                else:
                    name = str(ndata) if not isinstance(ndata, str) else ndata
                    ntype = "unknown"
                nodes.append(_legacy_to_graph_node(
                    str(nid), name=name, node_type=ntype, properties=props,
                ))

        raw_edges = getattr(g, "edges", None) or getattr(g, "_edges", None) or []
        if isinstance(raw_edges, dict):
            for eid, edata in raw_edges.items():
                if isinstance(edata, dict):
                    edges.append(_legacy_to_graph_edge(
                        str(edata.get("source", "")),
                        str(edata.get("target", "")),
                        edge_type=str(edata.get("type", "related")),
                        properties={k: v for k, v in edata.items()
                                     if k not in ("source", "target", "type")},
                    ))
        elif isinstance(raw_edges, list):
            for edata in raw_edges:
                if isinstance(edata, dict):
                    edges.append(_legacy_to_graph_edge(
                        str(edata.get("source", "")),
                        str(edata.get("target", "")),
                    ))

        return nodes, edges


class _KnowledgeGraphEngineAdapter(_BaseAdapter):
    """Adapter for genesis.graph.engine.KnowledgeGraphEngine."""

    def _extract(self) -> tuple[list[GraphNode], list[GraphEdge]]:
        nodes: list[GraphNode] = []
        edges: list[GraphEdge] = []
        g = self.legacy
        if hasattr(g, "graph") and hasattr(g.graph, "nodes"):
            for nid, ndata in g.graph.nodes.items():
                nodes.append(_legacy_to_graph_node(
                    nid, name=str(ndata.get("name", nid)),
                    node_type=str(ndata.get("type", "entity")),
                    properties=ndata,
                ))
            if hasattr(g.graph, "edges"):
                for e in g.graph.edges:
                    if len(e) >= 2:
                        edges.append(_legacy_to_graph_edge(e[0], e[1]))
        return nodes, edges


class _KnowledgeGraphAdapter(_BaseAdapter):
    """Adapter for genesis.knowledge_graph.KnowledgeGraph."""

    def _extract(self) -> tuple[list[GraphNode], list[GraphEdge]]:
        nodes: list[GraphNode] = []
        edges: list[GraphEdge] = []
        g = self.legacy
        for attr in ("_entities", "entities", "_nodes"):
            raw = getattr(g, attr, None)
            if raw:
                if isinstance(raw, dict):
                    for eid, entity in raw.items():
                        nodes.append(_legacy_to_graph_node(
                            eid, name=getattr(entity, "name", str(eid)),
                            node_type=getattr(entity, "domain", "entity"),
                            properties=getattr(entity, "metadata", {}),
                        ))
                break
        for attr in ("_relationships", "relationships", "_edges"):
            raw = getattr(g, attr, None)
            if raw:
                if isinstance(raw, list):
                    for rel in raw:
                        src = getattr(rel, "source", "") or getattr(rel, "from_id", "")
                        tgt = getattr(rel, "target", "") or getattr(rel, "to_id", "")
                        if src and tgt:
                            edges.append(_legacy_to_graph_edge(src, tgt))
                break
        return nodes, edges


class _PlanetaryKnowledgeGraphAdapter(_BaseAdapter):
    """Adapter for genesis.knowledge_graph.PlanetaryKnowledgeGraph."""

    def _extract(self) -> tuple[list[GraphNode], list[GraphEdge]]:
        return _KnowledgeGraphAdapter(self.legacy, self.layer_name, self.layer_type)._extract()


class _HypergraphAdapter(_BaseAdapter):
    """Adapter for genesis.hypergraph.HypergraphKnowledgeCore."""

    def _extract(self) -> tuple[list[GraphNode], list[GraphEdge]]:
        nodes: list[GraphNode] = []
        edges: list[GraphEdge] = []
        g = self.legacy
        for raw_nodes_attr in ("_nodes", "nodes", "_entities"):
            raw = getattr(g, raw_nodes_attr, None)
            if raw and isinstance(raw, dict):
                for nid, ndata in raw.items():
                    name = getattr(ndata, "name", str(nid)) if not isinstance(ndata, dict) else str(ndata.get("name", nid))
                    nodes.append(_legacy_to_graph_node(
                        str(nid), name=str(name), node_type="hypernode",
                    ))
                break
        for raw_edges_attr in ("_edges", "_hyperedges", "edges"):
            raw = getattr(g, raw_edges_attr, None)
            if raw and isinstance(raw, dict):
                for eid, edata in raw.items():
                    src = getattr(edata, "source", str(eid))
                    tgt = getattr(edata, "target", str(eid))
                    edges.append(_legacy_to_graph_edge(str(src), str(tgt), edge_type="hyperedge"))
                break
        return nodes, edges


class _ExecutionGraphAdapter(_BaseAdapter):
    """Adapter for genesis.execution_graph.ExecutionGraph."""

    def _extract(self) -> tuple[list[GraphNode], list[GraphEdge]]:
        nodes: list[GraphNode] = []
        edges: list[GraphEdge] = []
        g = self.legacy
        raw_nodes = getattr(g, "_nodes", None) or getattr(g, "nodes", None) or {}
        for nid, ndata in raw_nodes.items():
            props = {}
            if isinstance(ndata, dict):
                props = ndata
            name = props.pop("name", str(nid)) if isinstance(ndata, dict) else str(nid)
            nodes.append(_legacy_to_graph_node(
                str(nid), name=str(name), node_type=getattr(ndata, "type", "task") if not isinstance(ndata, dict) else ndata.get("type", "task"),
                properties=props if isinstance(ndata, dict) else {},
            ))
        raw_edges = getattr(g, "_edges", None) or getattr(g, "edges", None) or {}
        for eid, edata in raw_edges.items():
            if isinstance(edata, dict):
                edges.append(_legacy_to_graph_edge(
                    str(edata.get("from", "")), str(edata.get("to", "")),
                    edge_type=str(edata.get("type", "dependency")),
                ))
        return nodes, edges


class _RepositoryGraphAdapter(_BaseAdapter):
    def _extract(self) -> tuple[list[GraphNode], list[GraphEdge]]:
        nodes: list[GraphNode] = []
        edges: list[GraphEdge] = []
        g = self.legacy
        for attr in ("_nodes", "nodes", "_graph", "graph"):
            raw = getattr(g, attr, None)
            if raw and isinstance(raw, dict):
                for nid, ndata in raw.items():
                    nodes.append(_legacy_to_graph_node(
                        str(nid), name=str(nid), node_type="repo_entity",
                    ))
                break
        return nodes, edges


class _BrainGraphAdapter(_BaseAdapter):
    def _extract(self) -> tuple[list[GraphNode], list[GraphEdge]]:
        nodes: list[GraphNode] = []
        edges: list[GraphEdge] = []
        g = self.legacy
        entities = getattr(g, "_entities", None) or getattr(g, "entities", None) or {}
        for eid, entity in entities.items():
            nodes.append(_legacy_to_graph_node(
                str(eid), name=getattr(entity, "name", str(eid)),
                node_type=getattr(entity, "type", "entity"),
            ))
        rels = getattr(g, "_relationships", None) or getattr(g, "relationships", None) or []
        for rel in rels:
            src = getattr(rel, "source", "") or getattr(rel, "from_id", "")
            tgt = getattr(rel, "target", "") or getattr(rel, "to_id", "")
            if src and tgt:
                edges.append(_legacy_to_graph_edge(str(src), str(tgt)))
        return nodes, edges


class _UIRGraphAdapter(_BaseAdapter):
    def _extract(self) -> tuple[list[GraphNode], list[GraphEdge]]:
        nodes: list[GraphNode] = []
        edges: list[GraphEdge] = []
        g = self.legacy
        raw_nodes = getattr(g, "_nodes", None) or getattr(g, "nodes", None) or {}
        for nid, ndata in raw_nodes.items():
            nodes.append(_legacy_to_graph_node(
                str(nid), name=getattr(ndata, "name", str(nid)) if not isinstance(ndata, dict) else ndata.get("name", str(nid)),
                node_type="uir",
            ))
        raw_edges = getattr(g, "_edges", None) or getattr(g, "edges", None) or []
        for e in raw_edges:
            if len(e) >= 2:
                edges.append(_legacy_to_graph_edge(str(e[0]), str(e[1]), edge_type="uir_dep"))
        return nodes, edges


class _USIRGraphAdapter(_BaseAdapter):
    def _extract(self) -> tuple[list[GraphNode], list[GraphEdge]]:
        nodes: list[GraphNode] = []
        edges: list[GraphEdge] = []
        g = self.legacy
        raw_nodes = getattr(g, "_nodes", None) or getattr(g, "nodes", None) or {}
        for nid, ndata in raw_nodes.items():
            nodes.append(_legacy_to_graph_node(
                str(nid), name=str(nid), node_type="usir",
            ))
        raw_edges = getattr(g, "_edges", None) or getattr(g, "edges", None) or []
        for e in raw_edges:
            if len(e) >= 2:
                edges.append(_legacy_to_graph_edge(str(e[0]), str(e[1]), edge_type="usir_rel"))
        return nodes, edges


class _WorkspaceGraphAdapter(_BaseAdapter):
    def _extract(self) -> tuple[list[GraphNode], list[GraphEdge]]:
        nodes: list[GraphNode] = []
        edges: list[GraphEdge] = []
        g = self.legacy
        for nid in getattr(g, "_dependencies", None) or getattr(g, "dependencies", None) or {}:
            nodes.append(_legacy_to_graph_node(str(nid), name=str(nid), node_type="dependency"))
        deps = getattr(g, "_dependencies", None) or getattr(g, "dependencies", None) or {}
        for src, tgts in deps.items():
            for tgt in (tgts if isinstance(tgts, (list, set, tuple)) else [tgts]):
                edges.append(_legacy_to_graph_edge(str(src), str(tgt), edge_type="depends_on"))
        return nodes, edges


class _BuildGraphAdapter(_BaseAdapter):
    def _extract(self) -> tuple[list[GraphNode], list[GraphEdge]]:
        nodes: list[GraphNode] = []
        edges: list[GraphEdge] = []
        g = self.legacy
        raw_nodes = getattr(g, "_targets", None) or getattr(g, "targets", None) or {}
        for tid, tdata in raw_nodes.items():
            nodes.append(_legacy_to_graph_node(
                str(tid), name=getattr(tdata, "name", str(tid)) if not isinstance(tdata, dict) else tdata.get("name", str(tid)),
                node_type="build_target",
            ))
        return nodes, edges


class _CapabilityGraphAdapter(_BaseAdapter):
    def _extract(self) -> tuple[list[GraphNode], list[GraphEdge]]:
        nodes: list[GraphNode] = []
        edges: list[GraphEdge] = []
        g = self.legacy
        raw = getattr(g, "_graph", None) or getattr(g, "graph", None) or {}
        for nid in raw:
            nodes.append(_legacy_to_graph_node(str(nid), name=str(nid), node_type="capability"))
        for src, tgts in raw.items():
            for tgt in (tgts if isinstance(tgts, (list, set, tuple)) else [tgts]):
                edges.append(_legacy_to_graph_edge(str(src), str(tgt), edge_type="capability_dep"))
        return nodes, edges


class _WorldGraphAdapter(_BaseAdapter):
    def _extract(self) -> tuple[list[GraphNode], list[GraphEdge]]:
        g = self.legacy
        nodes = getattr(g, "_nodes", None) or getattr(g, "nodes", None) or {}
        return ([_legacy_to_graph_node(str(nid), node_type="world") for nid in nodes], [])


class _ObservatoryGraphAdapter(_BaseAdapter):
    def _extract(self) -> tuple[list[GraphNode], list[GraphEdge]]:
        g = self.legacy
        nodes = getattr(g, "_observations", None) or getattr(g, "observations", None) or []
        return ([_legacy_to_graph_node(str(i), node_type="observation") for i in range(len(nodes) if isinstance(nodes, list) else 0)], [])


class _TaskGraphAdapter(_BaseAdapter):
    def _extract(self) -> tuple[list[GraphNode], list[GraphEdge]]:
        g = self.legacy
        raw = getattr(g, "_tasks", None) or getattr(g, "tasks", None) or {}
        nodes = [_legacy_to_graph_node(str(tid), node_type="task") for tid in raw]
        edges = []
        for tid, task in raw.items():
            deps = getattr(task, "dependencies", []) if not isinstance(task, dict) else task.get("dependencies", [])
            for dep in deps:
                edges.append(_legacy_to_graph_edge(str(tid), str(dep), edge_type="task_dep"))
        return nodes, edges
