"""
UCOS: CapabilityDependencyGraph — Complete dependency graph analysis.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from genesis.ucos.capability import Capability, CapabilityState
from genesis.utils.graph_algorithms import find_cycles, topological_sort


class CapabilityDependencyGraph:
    """Full dependency graph analysis with metrics and visualization data."""

    def __init__(self, registry):
        self._registry = registry

    def _build_edges(self) -> list[tuple[str, str]]:
        edges = []
        for cap in self._registry.all:
            for dep_id in cap.definition.dependencies:
                if self._registry.get(dep_id):
                    edges.append((dep_id, cap.id))
        return edges

    def _build_adjacency(self) -> dict[str, set[str]]:
        adj: dict[str, set[str]] = defaultdict(set)
        for cap in self._registry.all:
            for dep_id in cap.definition.dependencies:
                if self._registry.get(dep_id):
                    adj[cap.id].add(dep_id)
        return dict(adj)

    def cycles(self) -> list[list[str]]:
        return find_cycles(self._build_edges())

    def has_cycles(self) -> bool:
        return len(self.cycles()) > 0

    def topsort(self) -> list[str]:
        edges = self._build_edges()
        ts = topological_sort(edges)
        return [n for n in ts if n in {c.id for c in self._registry.all}]

    def fan_in(self, capability_id: str) -> int:
        count = 0
        for cap in self._registry.all:
            if capability_id in cap.definition.dependencies:
                count += 1
        return count

    def fan_out(self, capability_id: str) -> int:
        cap = self._registry.get(capability_id)
        return len(cap.definition.dependencies) if cap else 0

    def degree(self, capability_id: str) -> int:
        return self.fan_in(capability_id) + self.fan_out(capability_id)

    def dependency_depth(self, capability_id: str) -> int:
        memo: dict[str, int] = {}

        def depth(cid: str) -> int:
            if cid in memo:
                return memo[cid]
            cap = self._registry.get(cid)
            if not cap or not cap.definition.dependencies:
                memo[cid] = 0
            else:
                memo[cid] = 1 + max(depth(d) for d in cap.definition.dependencies)
            return memo[cid]

        return depth(capability_id)

    def critical_path(self) -> list[str]:
        max_depth = 0
        critical = []
        for cap in self._registry.all:
            d = self.dependency_depth(cap.id)
            if d > max_depth:
                max_depth = d
                critical = [cap.id]
            elif d == max_depth:
                critical.append(cap.id)
        return critical

    def dependency_subgraph(self, capability_id: str) -> list[str]:
        sub = []
        visited = set()
        queue = [capability_id]
        while queue:
            cid = queue.pop(0)
            if cid in visited:
                continue
            visited.add(cid)
            cap = self._registry.get(cid)
            if cap:
                sub.append(cid)
                queue.extend(cap.definition.dependencies)
        return sub

    def consumer_subgraph(self, capability_id: str) -> list[str]:
        consumers = []
        for cap in self._registry.all:
            if capability_id in cap.definition.dependencies:
                consumers.append(cap.id)
                consumers.extend(self.consumer_subgraph(cap.id))
        return list(set(consumers))

    def orphan_capabilities(self) -> list[Capability]:
        return [c for c in self._registry.all
                if not c.definition.dependencies
                and not any(c.id in cap.definition.dependencies for cap in self._registry.all)]

    def layer_assignment(self) -> dict[str, int]:
        layers: dict[str, int] = {}
        adj = self._build_adjacency()
        for cid in self.topsort():
            if cid not in adj or not adj[cid]:
                layers[cid] = 0
            else:
                max_dep_layer = max(layers.get(d, -1) for d in adj[cid])
                layers[cid] = max_dep_layer + 1
        return layers

    def summary(self) -> dict[str, Any]:
        return {
            "total_nodes": self._registry.count,
            "total_edges": sum(len(c.definition.dependencies) for c in self._registry.all),
            "has_cycles": self.has_cycles(),
            "cycle_count": len(self.cycles()),
            "max_depth": max((self.dependency_depth(c.id) for c in self._registry.all), default=0),
            "orphans": len(self.orphan_capabilities()),
            "mean_fan_in": sum(self.fan_in(c.id) for c in self._registry.all) / max(self._registry.count, 1),
            "mean_fan_out": sum(self.fan_out(c.id) for c in self._registry.all) / max(self._registry.count, 1),
        }
