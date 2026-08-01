"""
GENESIS XI: Workspace dependency graph, capability map, and workspace graph.
"""

from __future__ import annotations

from collections import defaultdict, deque
from typing import Any

from genesis.meta.workspace import Repository, Workspace
from genesis.utils.graph_algorithms import topological_sort, find_cycles


class WorkspaceDependencyGraph:
    """Multi-repository dependency graph analysis."""

    def __init__(self, workspace: Workspace):
        self._workspace = workspace
        self._rebuild()

    def _rebuild(self):
        self._edges: list[tuple[str, str]] = []
        for repo in self._workspace.all_repositories():
            for dep_id in repo.dependencies:
                if self._workspace.get_repository(dep_id):
                    self._edges.append((dep_id, repo.id))

    def edges(self) -> list[tuple[str, str]]:
        return list(self._edges)

    def has_cycles(self) -> bool:
        return len(self.cycles()) > 0

    def cycles(self) -> list[list[str]]:
        return find_cycles(self._edges)

    def topological_order(self) -> list[str]:
        return topological_sort(self._edges)

    def fan_in(self, repo_id: str) -> int:
        return sum(1 for src, _ in self._edges if src == repo_id)

    def fan_out(self, repo_id: str) -> int:
        return sum(1 for _, tgt in self._edges if tgt == repo_id)

    def dependency_depth(self, repo_id: str) -> int:
        visited: set[str] = set()
        def depth(rid: str) -> int:
            if rid in visited:
                return 0
            visited.add(rid)
            repo = self._workspace.get_repository(rid)
            if not repo or not repo.dependencies:
                return 1
            return 1 + max(depth(d) for d in repo.dependencies
                          if self._workspace.get_repository(d))
        return depth(repo_id)

    def transitive_dependencies(self, repo_id: str) -> list[str]:
        result: list[str] = []
        visited: set[str] = set()
        queue: deque[str] = deque([repo_id])
        while queue:
            current = queue.popleft()
            repo = self._workspace.get_repository(current)
            if repo:
                for dep_id in repo.dependencies:
                    if dep_id not in visited and self._workspace.get_repository(dep_id):
                        visited.add(dep_id)
                        result.append(dep_id)
                        queue.append(dep_id)
        return result

    def leaf_repositories(self) -> list[Repository]:
        repo_ids = {r.id for r in self._workspace.all_repositories()}
        consumers: set[str] = set()
        for src, tgt in self._edges:
            consumers.add(tgt)
        return [r for r in self._workspace.all_repositories() if r.id not in consumers]

    def root_repositories(self) -> list[Repository]:
        repo_ids = {r.id for r in self._workspace.all_repositories()}
        providers: set[str] = set()
        for src, tgt in self._edges:
            providers.add(src)
        return [r for r in self._workspace.all_repositories() if r.id not in providers]

    def upstream(self, repo_id: str, max_depth: int = 10) -> list[str]:
        result: list[str] = []
        visited: set[str] = set()
        def walk(rid: str, depth: int):
            if rid in visited or depth > max_depth:
                return
            visited.add(rid)
            repo = self._workspace.get_repository(rid)
            if repo:
                for dep_id in repo.dependencies:
                    if self._workspace.get_repository(dep_id):
                        result.append(dep_id)
                        walk(dep_id, depth + 1)
        walk(repo_id, 0)
        return result

    def downstream(self, repo_id: str, max_depth: int = 10) -> list[str]:
        result: list[str] = []
        visited: set[str] = set()
        consumers: dict[str, list[str]] = defaultdict(list)
        for src, tgt in self._edges:
            consumers[src].append(tgt)
        def walk(rid: str, depth: int):
            if rid in visited or depth > max_depth:
                return
            visited.add(rid)
            for consumer_id in consumers.get(rid, []):
                result.append(consumer_id)
                walk(consumer_id, depth + 1)
        walk(repo_id, 0)
        return result

    def summary(self) -> dict[str, Any]:
        return {
            "total_repos": self._workspace.repository_count,
            "total_edges": len(self._edges),
            "has_cycles": self.has_cycles(),
            "cycle_count": len(self.cycles()),
            "leaf_count": len(self.leaf_repositories()),
            "root_count": len(self.root_repositories()),
        }


class WorkspaceCapabilityMap:
    """Maps capabilities to repositories across the workspace."""

    def __init__(self, workspace: Workspace):
        self._workspace = workspace

    def providers_of(self, capability: str) -> list[Repository]:
        return [r for r in self._workspace.all_repositories()
                if capability in r.capabilities_provided]

    def consumers_of(self, capability: str) -> list[Repository]:
        return [r for r in self._workspace.all_repositories()
                if capability in r.capabilities_consumed]

    def all_capabilities(self) -> list[str]:
        caps: set[str] = set()
        for r in self._workspace.all_repositories():
            caps.update(r.capabilities_provided)
            caps.update(r.capabilities_consumed)
        return sorted(caps)

    def unresolved_consumers(self) -> list[tuple[Repository, str]]:
        all_provided: set[str] = set()
        for r in self._workspace.all_repositories():
            all_provided.update(r.capabilities_provided)
        unresolved: list[tuple[Repository, str]] = []
        for r in self._workspace.all_repositories():
            for cap in r.capabilities_consumed:
                if cap not in all_provided:
                    unresolved.append((r, cap))
        return unresolved

    def orphan_providers(self) -> list[tuple[Repository, str]]:
        all_consumed: set[str] = set()
        for r in self._workspace.all_repositories():
            all_consumed.update(r.capabilities_consumed)
        orphans: list[tuple[Repository, str]] = []
        for r in self._workspace.all_repositories():
            for cap in r.capabilities_provided:
                if cap not in all_consumed:
                    orphans.append((r, cap))
        return orphans

    def coverage(self) -> dict[str, float]:
        all_caps = self.all_capabilities()
        resolved = 0
        for r in self._workspace.all_repositories():
            for cap in r.capabilities_consumed:
                if any(cap in p.capabilities_provided
                       for p in self._workspace.all_repositories()):
                    resolved += 1
        total_consumed = sum(len(r.capabilities_consumed) for r in self._workspace.all_repositories())
        return {
            "total_capabilities": len(all_caps),
            "total_consumed": total_consumed,
            "resolved": resolved,
            "coverage": resolved / max(total_consumed, 1),
            "unresolved": len(self.unresolved_consumers()),
            "orphans": len(self.orphan_providers()),
        }


class WorkspaceGraph:
    """Combined workspace graph: repos + capabilities + dependencies."""

    def __init__(self, workspace: Workspace):
        self._workspace = workspace
        self.dep_graph = WorkspaceDependencyGraph(workspace)
        self.cap_map = WorkspaceCapabilityMap(workspace)

    def summary(self) -> dict[str, Any]:
        return {
            "dependency_graph": self.dep_graph.summary(),
            "capability_map": self.cap_map.coverage(),
        }
