"""
UCOS: CapabilityResolver — Dependency resolution and topological ordering.
"""

from __future__ import annotations

from collections import defaultdict, deque
from typing import Any

from genesis.ucos.capability import Capability, CapabilityDefinition, CapabilityState


class CapabilityDependencyError(Exception):
    pass


class CapabilityCycleError(CapabilityDependencyError):
    pass


class CapabilityMissingError(CapabilityDependencyError):
    pass


class CapabilityStateError(CapabilityDependencyError):
    pass


class CapabilityResolver:
    """Resolves capability dependency graphs with cycle detection and ordering."""

    def __init__(self, registry):
        self._registry = registry

    def resolve(self, capability_id: str,
                required_state: CapabilityState = CapabilityState.READY,
                include_optional: bool = False) -> list[Capability]:
        deps = self._registry.resolve_dependencies(capability_id)
        for dep in deps:
            if dep.state.value < required_state.value:
                raise CapabilityStateError(
                    f"Capability '{dep.name}' ({dep.id}) is in state {dep.state.value}, "
                    f"required {required_state.value}"
                )
        return deps

    def topological_sort(self, capability_ids: list[str]) -> list[Capability]:
        graph: dict[str, set[str]] = {}
        for cid in capability_ids:
            cap = self._registry.get(cid)
            if cap:
                graph[cid] = set(cap.definition.dependencies)

        in_degree: dict[str, int] = {n: 0 for n in graph}
        for n in graph:
            for dep in graph[n]:
                if dep in in_degree:
                    in_degree[n] += 1

        queue = deque([n for n in in_degree if in_degree[n] == 0])
        sorted_ids = []
        while queue:
            n = queue.popleft()
            sorted_ids.append(n)
            for m in graph:
                if n in graph[m]:
                    in_degree[m] -= 1
                    if in_degree[m] == 0:
                        queue.append(m)

        if len(sorted_ids) != len(graph):
            raise CapabilityCycleError(
                f"Cycle detected among {len(graph) - len(sorted_ids)} capabilities"
            )

        return [self._registry.get(cid) for cid in sorted_ids if self._registry.get(cid)]

    def validate_all_dependencies(self) -> list[str]:
        errors = []
        for cap in self._registry.all:
            for dep_id in cap.definition.dependencies:
                dep = self._registry.get(dep_id)
                if not dep:
                    errors.append(
                        f"Capability '{cap.name}' depends on missing '{dep_id}'"
                    )
                    continue
                if dep.state == CapabilityState.DORMANT:
                    errors.append(
                        f"Capability '{cap.name}' depends on dormant '{dep.name}'"
                    )
        return errors

    def detect_cycles(self) -> list[list[str]]:
        graph: dict[str, list[str]] = {}
        for cap in self._registry.all:
            graph[cap.id] = list(cap.definition.dependencies)

        WHITE, GRAY, BLACK = 0, 1, 2
        color: dict[str, int] = {n: WHITE for n in graph}
        cycles: list[list[str]] = []
        path_stack: list[str] = []

        def dfs(n: str):
            color[n] = GRAY
            path_stack.append(n)
            for dep in graph.get(n, []):
                if dep in graph:
                    if color[dep] == GRAY:
                        cycle_start = path_stack.index(dep)
                        cycles.append(path_stack[cycle_start:] + [dep])
                    elif color[dep] == WHITE:
                        dfs(dep)
            path_stack.pop()
            color[n] = BLACK

        for n in graph:
            if color[n] == WHITE:
                dfs(n)
        return cycles

    def compute_boot_order(self) -> list[Capability]:
        all_ids = [c.id for c in self._registry.all]
        try:
            return self.topological_sort(all_ids)
        except CapabilityCycleError:
            bootable = []
            for cap in self._registry.all:
                ready = True
                for dep_id in cap.definition.dependencies:
                    dep = self._registry.get(dep_id)
                    if not dep or dep.state == CapabilityState.DORMANT:
                        ready = False
                        break
                if ready:
                    bootable.append(cap)
            return bootable

    def dependency_depth(self, capability_id: str) -> int:
        cap = self._registry.get(capability_id)
        if not cap:
            return -1
        visited = set()
        def depth(cid: str) -> int:
            if cid in visited:
                return 0
            visited.add(cid)
            c = self._registry.get(cid)
            if not c or not c.definition.dependencies:
                return 1
            return 1 + max(depth(d) for d in c.definition.dependencies)
        return depth(capability_id)

    def leaf_capabilities(self) -> list[Capability]:
        return [c for c in self._registry.all if not c.definition.dependencies]

    def root_capabilities(self) -> list[Capability]:
        all_deps: set[str] = set()
        for cap in self._registry.all:
            all_deps.update(cap.definition.dependencies)
        return [c for c in self._registry.all if c.id not in all_deps]
