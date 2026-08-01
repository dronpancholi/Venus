from __future__ import annotations

from collections import defaultdict, deque
from typing import Any


class GraphAnalytics:
    """Analytics and metrics for graph layers."""

    @staticmethod
    def degree_centrality(layer) -> dict[str, float]:
        n = layer.node_count()
        if n == 0:
            return {}
        centrality: dict[str, float] = {}
        for node_id in layer._nodes:
            deg = len(layer._outgoing.get(node_id, [])) + len(layer._incoming.get(node_id, []))
            centrality[node_id] = deg / (n - 1) if n > 1 else 0.0
        return centrality

    @staticmethod
    def betweenness_centrality(layer) -> dict[str, float]:
        centrality: dict[str, float] = defaultdict(float)
        nodes = list(layer._nodes.keys())
        for s in nodes:
            stack: list[str] = []
            paths: dict[str, list[str]] = {s: [s]}
            distances: dict[str, int] = {s: 0}
            queue: deque[str] = deque([s])
            while queue:
                v = queue.popleft()
                stack.append(v)
                for eid in layer._outgoing.get(v, []):
                    edge = layer._edges.get(eid)
                    if edge and edge.target_id not in distances:
                        distances[edge.target_id] = distances[v] + 1
                        paths[edge.target_id] = [p + [edge.target_id] for p in paths.get(v, [v])]
                        queue.append(edge.target_id)
            if len(paths) <= 1:
                continue
            for t in nodes:
                if t == s or t not in paths:
                    continue
                shortest = paths[t]
                for node_on_path in shortest[1:-1]:
                    centrality[node_on_path] += 1.0 / len(shortest)
        n = len(nodes)
        if n <= 2:
            return dict(centrality)
        norm = 1.0 / ((n - 1) * (n - 2))
        return {k: v * norm for k, v in centrality.items()}

    @staticmethod
    def clustering_coefficient(layer) -> dict[str, float]:
        coeffs: dict[str, float] = {}
        for node_id in layer._nodes:
            neighbors: set[str] = set()
            for eid in layer._outgoing.get(node_id, []):
                edge = layer._edges.get(eid)
                if edge:
                    neighbors.add(edge.target_id)
            for eid in layer._incoming.get(node_id, []):
                edge = layer._edges.get(eid)
                if edge:
                    neighbors.add(edge.source_id)
            k = len(neighbors)
            if k < 2:
                coeffs[node_id] = 0.0
                continue
            edges_between = 0
            for n1 in neighbors:
                for n2 in neighbors:
                    if n1 < n2 and self._has_edge(layer, n1, n2):
                        edges_between += 1
            coeffs[node_id] = (2.0 * edges_between) / (k * (k - 1))
        return coeffs

    @staticmethod
    def _has_edge(layer, n1: str, n2: str) -> bool:
        for eid in layer._outgoing.get(n1, []):
            edge = layer._edges.get(eid)
            if edge and edge.target_id == n2:
                return True
        return False

    @staticmethod
    def density(layer) -> float:
        n = layer.node_count()
        if n <= 1:
            return 0.0
        max_edges = n * (n - 1)
        return layer.edge_count() / max_edges if max_edges > 0 else 0.0

    @staticmethod
    def component_analysis(layer) -> dict[str, Any]:
        visited: set[str] = set()
        components: list[list[str]] = []
        for node_id in layer._nodes:
            if node_id in visited:
                continue
            component: list[str] = []
            queue: deque[str] = deque([node_id])
            while queue:
                v = queue.popleft()
                if v in visited:
                    continue
                visited.add(v)
                component.append(v)
                for eid in list(layer._outgoing.get(v, [])) + list(layer._incoming.get(v, [])):
                    edge = layer._edges.get(eid)
                    if edge:
                        n = edge.target_id if edge.source_id == v else edge.source_id
                        if n not in visited:
                            queue.append(n)
            components.append(component)
        sizes = [len(c) for c in components]
        return {
            "component_count": len(components),
            "largest_component": max(sizes) if sizes else 0,
            "smallest_component": min(sizes) if sizes else 0,
            "average_component_size": sum(sizes) / max(len(components), 1),
        }

    @staticmethod
    def summary(layer) -> dict[str, Any]:
        return {
            "density": GraphAnalytics.density(layer),
            "components": GraphAnalytics.component_analysis(layer),
            "degree_cent": GraphAnalytics.degree_centrality(layer),
            "avg_clustering": sum(GraphAnalytics.clustering_coefficient(layer).values()) / max(layer.node_count(), 1),
        }
