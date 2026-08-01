from __future__ import annotations

import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Any, Callable

from genesis.graph_v2.core import GraphLayer, GraphNode, GraphEdge, LayerType, UnifiedGraph
from genesis.utils.graph_algorithms import subgraph as _extract_subgraph


@dataclass
class PathResult:
    nodes: list[GraphNode] = field(default_factory=list)
    edges: list[GraphEdge] = field(default_factory=list)
    total_weight: float = 0.0
    hops: int = 0


@dataclass
class TraversalConfig:
    max_depth: int = 10
    edge_types: list[str] | None = None
    node_filter: Callable[[GraphNode], bool] | None = None
    bidirectional: bool = False
    timeout_ms: float = 5000.0


@dataclass
class SearchResult:
    node: GraphNode
    score: float
    matches: dict[str, list[str]] = field(default_factory=dict)


@dataclass
class SubgraphDef:
    root_id: str
    depth: int = 1
    layer_name: str | None = None
    edge_types: list[str] | None = None


@dataclass
class GraphDiff:
    added_nodes: list[GraphNode] = field(default_factory=list)
    removed_nodes: list[GraphNode] = field(default_factory=list)
    added_edges: list[GraphEdge] = field(default_factory=list)
    removed_edges: list[GraphEdge] = field(default_factory=list)
    modified_nodes: list[tuple[GraphNode, GraphNode, list[str]]] = field(default_factory=list)


class GraphTraversal:
    def __init__(self, graph: UnifiedGraph):
        self._graph = graph

    def bfs(self, start_node_id: str, config: TraversalConfig | None = None) -> list[GraphNode]:
        cfg = config or TraversalConfig()
        visited: set[str] = set()
        queue: deque[tuple[str, int]] = deque()
        queue.append((start_node_id, 0))
        visited.add(start_node_id)
        result: list[GraphNode] = []
        started = time.time()

        while queue:
            if cfg.timeout_ms > 0 and (time.time() - started) * 1000 > cfg.timeout_ms:
                break
            current_id, depth = queue.popleft()
            if depth > cfg.max_depth:
                continue
            node = self._find_node(current_id)
            if node:
                result.append(node)
            neighbors = self._get_neighbors(current_id, cfg)
            for nid in neighbors:
                if nid not in visited:
                    visited.add(nid)
                    queue.append((nid, depth + 1))
        return result

    def dfs(self, start_node_id: str, config: TraversalConfig | None = None) -> list[GraphNode]:
        cfg = config or TraversalConfig()
        visited: set[str] = set()
        result: list[GraphNode] = []
        started = time.time()

        def _dfs(current_id: str, depth: int):
            if cfg.timeout_ms > 0 and (time.time() - started) * 1000 > cfg.timeout_ms:
                return
            if depth > cfg.max_depth:
                return
            if current_id in visited:
                return
            visited.add(current_id)
            node = self._find_node(current_id)
            if node:
                result.append(node)
            for nid in self._get_neighbors(current_id, cfg):
                _dfs(nid, depth + 1)

        _dfs(start_node_id, 0)
        return result

    def shortest_path(self, start_id: str, end_id: str,
                      config: TraversalConfig | None = None) -> PathResult | None:
        cfg = config or TraversalConfig()
        if start_id == end_id:
            node = self._find_node(start_id)
            if node:
                return PathResult(nodes=[node], hops=0)
            return None

        visited: set[str] = {start_id}
        parent: dict[str, tuple[str | None, str | None]] = {start_id: (None, None)}
        queue: deque[str] = deque([start_id])
        started = time.time()

        while queue:
            if cfg.timeout_ms > 0 and (time.time() - started) * 1000 > cfg.timeout_ms:
                return None
            current = queue.popleft()
            for nid in self._get_neighbors(current, cfg):
                if nid not in visited:
                    visited.add(nid)
                    parent[nid] = (current, self._get_edge_id(current, nid, cfg))
                    queue.append(nid)
                    if nid == end_id:
                        return self._reconstruct_path(start_id, end_id, parent)
        return None

    def all_paths(self, start_id: str, end_id: str,
                  config: TraversalConfig | None = None,
                  max_paths: int = 10) -> list[PathResult]:
        cfg = config or TraversalConfig()
        results: list[PathResult] = []
        started = time.time()

        def _dfs_paths(current: str, target: str, visited: set[str],
                        path_nodes: list[GraphNode], path_edges: list[GraphEdge],
                        weight: float):
            if len(results) >= max_paths:
                return
            if cfg.timeout_ms > 0 and (time.time() - started) * 1000 > cfg.timeout_ms:
                return
            if len(path_nodes) > cfg.max_depth:
                return
            if current == target:
                results.append(PathResult(
                    nodes=list(path_nodes),
                    edges=list(path_edges),
                    total_weight=weight,
                    hops=len(path_nodes) - 1,
                ))
                return
            for nid in self._get_neighbors(current, cfg):
                if nid not in visited:
                    node = self._find_node(nid)
                    edge = self._get_edge(current, nid, cfg)
                    visited.add(nid)
                    path_nodes.append(node)
                    if edge:
                        path_edges.append(edge)
                    _dfs_paths(nid, target, visited, path_nodes, path_edges,
                               weight + (edge.weight if edge else 1.0))
                    path_nodes.pop()
                    if edge and path_edges and path_edges[-1] == edge:
                        path_edges.pop()
                    visited.discard(nid)

        start_node = self._find_node(start_id)
        if not start_node:
            return []
        _dfs_paths(start_id, end_id, {start_id}, [start_node], [], 0.0)
        results.sort(key=lambda r: (r.hops, r.total_weight))
        return results

    def _find_node(self, node_id: str) -> GraphNode | None:
        for layer in self._graph._layers.values():
            node = layer.get_node(node_id)
            if node:
                return node
        return None

    def _find_layer_of(self, node_id: str) -> GraphLayer | None:
        for layer in self._graph._layers.values():
            if layer.get_node(node_id):
                return layer
        return None

    def _get_neighbors(self, node_id: str, cfg: TraversalConfig) -> list[str]:
        nids: set[str] = set()
        for layer in self._graph._layers.values():
            for edge in layer._edges.values():
                if edge.source_id == node_id:
                    if cfg.edge_types is None or edge.edge_type in cfg.edge_types:
                        target = layer.get_node(edge.target_id)
                        if target and (cfg.node_filter is None or cfg.node_filter(target)):
                            nids.add(edge.target_id)
                if cfg.bidirectional and edge.target_id == node_id:
                    if cfg.edge_types is None or edge.edge_type in cfg.edge_types:
                        source = layer.get_node(edge.source_id)
                        if source and (cfg.node_filter is None or cfg.node_filter(source)):
                            nids.add(edge.source_id)
        return list(nids)

    def _get_edge_id(self, source_id: str, target_id: str, cfg: TraversalConfig) -> str | None:
        for layer in self._graph._layers.values():
            for eid, edge in layer._edges.items():
                if edge.source_id == source_id and edge.target_id == target_id:
                    if cfg.edge_types is None or edge.edge_type in cfg.edge_types:
                        return eid
        return None

    def _get_edge(self, source_id: str, target_id: str, cfg: TraversalConfig) -> GraphEdge | None:
        for layer in self._graph._layers.values():
            for edge in layer._edges.values():
                if edge.source_id == source_id and edge.target_id == target_id:
                    if cfg.edge_types is None or edge.edge_type in cfg.edge_types:
                        return edge
        return None

    def _reconstruct_path(self, start_id: str, end_id: str,
                          parent: dict[str, tuple[str | None, str | None]]) -> PathResult:
        path_nodes: list[GraphNode] = []
        path_edges: list[GraphEdge] = []
        current: str | None = end_id
        while current is not None:
            node = self._find_node(current)
            if node:
                path_nodes.append(node)
            p, eid = parent.get(current, (None, None))
            if eid:
                for layer in self._graph._layers.values():
                    edge = layer.get_edge(eid)
                    if edge:
                        path_edges.append(edge)
                        break
            current = p
        path_nodes.reverse()
        path_edges.reverse()
        total_weight = sum(e.weight for e in path_edges)
        return PathResult(
            nodes=path_nodes, edges=path_edges,
            total_weight=total_weight, hops=len(path_nodes) - 1,
        )


class GraphSearch:
    def __init__(self, graph: UnifiedGraph):
        self._graph = graph

    def search(self, query: str, layer_name: str | None = None,
               limit: int = 20, min_score: float = 0.0) -> list[SearchResult]:
        terms = query.lower().split()
        results: list[SearchResult] = []
        layers = [self._graph.get_layer(layer_name)] if layer_name else list(self._graph._layers.values())
        for layer in layers:
            if layer is None:
                continue
            for node in layer._nodes.values():
                score, matches = self._score_node(node, terms)
                if score >= min_score:
                    results.append(SearchResult(node=node, score=score, matches=dict(matches)))
        results.sort(key=lambda r: -r.score)
        return results[:limit]

    def search_by_property(self, key: str, value: Any,
                           layer_name: str | None = None) -> list[GraphNode]:
        layers = [self._graph.get_layer(layer_name)] if layer_name else list(self._graph._layers.values())
        results = []
        for layer in layers:
            if layer is None:
                continue
            for node in layer._nodes.values():
                if node.properties.get(key) == value:
                    results.append(node)
        return results

    def search_by_label(self, label: str, layer_name: str | None = None) -> list[GraphNode]:
        layers = [self._graph.get_layer(layer_name)] if layer_name else list(self._graph._layers.values())
        results = []
        for layer in layers:
            if layer is None:
                continue
            results.extend(layer.find_nodes_by_label(label))
        return results

    @staticmethod
    def _score_node(node: GraphNode, terms: list[str]) -> tuple[float, dict[str, list[str]]]:
        score = 0.0
        matches: dict[str, list[str]] = defaultdict(list)
        for term in terms:
            if term in node.name.lower():
                score += 3.0
                matches["name"].append(term)
            if term in node.node_type.lower():
                score += 2.0
                matches["type"].append(term)
            for label in node.labels:
                if term in label.lower():
                    score += 1.5
                    matches["labels"].append(term)
            for k, v in node.properties.items():
                if isinstance(v, str) and term in v.lower():
                    score += 1.0
                    matches["properties"].append(f"{k}={term}")
        return score, dict(matches)


class GraphTransform:
    def __init__(self, graph: UnifiedGraph):
        self._graph = graph

    def extract_subgraph(self, defn: SubgraphDef) -> UnifiedGraph:
        source = self._graph.get_layer(defn.layer_name) if defn.layer_name else None
        layers = [source] if source else list(self._graph._layers.values())
        result = UnifiedGraph()
        for layer in layers:
            layer_type = layer.layer_type
            result_layer = result.create_layer(f"sub_{layer.name}", layer_type)
            nodes_dict = {nid: node for nid, node in layer._nodes.items()}
            edge_tuples = [
                (e.source_id, e.target_id, e.edge_type)
                for e in layer._edges.values()
                if defn.edge_types is None or e.edge_type in defn.edge_types
            ]
            snodes, sedges = _extract_subgraph(nodes_dict, edge_tuples, defn.root_id, defn.depth)
            for nid, node in snodes.items():
                result_layer._nodes[nid] = node
                for label in node.labels:
                    result_layer._label_index[label].add(nid)
            for src, tgt, etype in sedges:
                edge = GraphEdge(source_id=src, target_id=tgt, edge_type=etype)
                result_layer._edges[edge.id] = edge
                result_layer._outgoing[src].append(edge.id)
                result_layer._incoming[tgt].append(edge.id)
        return result

    def project(self, layer_name: str, node_type: str | None = None,
                labels: list[str] | None = None) -> UnifiedGraph:
        source = self._graph.get_layer(layer_name)
        if not source:
            raise ValueError(f"Layer '{layer_name}' not found")
        result = UnifiedGraph()
        result_layer = result.create_layer(f"proj_{layer_name}", source.layer_type)
        for node in source._nodes.values():
            if node_type and node.node_type != node_type:
                continue
            if labels and not any(l in node.labels for l in labels):
                continue
            result_layer._nodes[node.id] = node
            for label in node.labels:
                result_layer._label_index[label].add(node.id)
        for edge in source._edges.values():
            if edge.source_id in result_layer._nodes and edge.target_id in result_layer._nodes:
                result_layer._edges[edge.id] = edge
                result_layer._outgoing[edge.source_id].append(edge.id)
                result_layer._incoming[edge.target_id].append(edge.id)
        return result

    def diff(self, other: UnifiedGraph) -> GraphDiff:
        diff = GraphDiff()
        for layer in self._graph._layers.values():
            other_layer = other.get_layer(layer.name)
            if not other_layer:
                for node in layer._nodes.values():
                    diff.removed_nodes.append(node)
                for edge in layer._edges.values():
                    diff.removed_edges.append(edge)
                continue
            my_ids = set(layer._nodes.keys())
            other_ids = set(other_layer._nodes.keys())
            for nid in my_ids - other_ids:
                diff.removed_nodes.append(layer._nodes[nid])
            for nid in other_ids - my_ids:
                diff.added_nodes.append(other_layer._nodes[nid])
            for nid in my_ids & other_ids:
                a = layer._nodes[nid]
                b = other_layer._nodes[nid]
                changed = []
                for k in set(list(a.properties.keys()) + list(b.properties.keys())):
                    if a.properties.get(k) != b.properties.get(k):
                        changed.append(k)
                if changed or a.labels != b.labels:
                    diff.modified_nodes.append((a, b, changed))
            my_edges = {(e.source_id, e.target_id, e.edge_type) for e in layer._edges.values()}
            other_edges = {(e.source_id, e.target_id, e.edge_type) for e in other_layer._edges.values()}
            for ekey in my_edges - other_edges:
                edge = layer._edges.get(ekey[0])
                if edge:
                    diff.removed_edges.append(edge)
            for ekey in other_edges - my_edges:
                edge = other_layer._edges.get(ekey[0])
                if edge:
                    diff.added_edges.append(edge)
        return diff

    def merge(self, other: UnifiedGraph, conflict_resolution: str = "source_wins") -> UnifiedGraph:
        result = UnifiedGraph()
        for layer in list(self._graph._layers.values()) + list(other._layers.values()):
            if not result.get_layer(layer.name):
                result.create_layer(layer.name, layer.layer_type)
        source_layers = {l.name: l for l in self._graph._layers.values()}
        other_layers = {l.name: l for l in other._layers.values()}
        all_layer_names = set(source_layers.keys()) | set(other_layers.keys())
        for name in all_layer_names:
            sl = source_layers.get(name)
            ol = other_layers.get(name)
            primary = sl or ol
            rl = result.get_layer(name)
            for nid, node in primary._nodes.items():
                rl._nodes[nid] = GraphNode(
                    id=node.id, name=node.name, node_type=node.node_type,
                    properties=dict(node.properties), labels=list(node.labels),
                    weight=node.weight,
                )
                for label in node.labels:
                    rl._label_index[label].add(nid)
            for edge in primary._edges.values():
                if edge.source_id in rl._nodes and edge.target_id in rl._nodes:
                    rl._edges[edge.id] = GraphEdge(
                        id=edge.id, source_id=edge.source_id, target_id=edge.target_id,
                        edge_type=edge.edge_type, properties=dict(edge.properties),
                        weight=edge.weight, bidirectional=edge.bidirectional,
                    )
                    rl._outgoing[edge.source_id].append(edge.id)
                    rl._incoming[edge.target_id].append(edge.id)
            if sl and ol and conflict_resolution == "source_wins":
                for nid, node in ol._nodes.items():
                    if nid not in sl._nodes:
                        rl._nodes[nid] = node
                        for label in node.labels:
                            rl._label_index[label].add(nid)
                for edge in ol._edges.values():
                    if edge.source_id in rl._nodes and edge.target_id in rl._nodes:
                        if edge.id not in rl._edges:
                            rl._edges[edge.id] = edge
                            rl._outgoing[edge.source_id].append(edge.id)
                            rl._incoming[edge.target_id].append(edge.id)
        return result
