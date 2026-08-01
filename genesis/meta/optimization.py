"""
GENESIS XI: Workspace-level optimization passes.
"""

from __future__ import annotations

import time
from collections import defaultdict
from typing import Any, Callable

from genesis.meta.workspace import Workspace
from genesis.meta.graph import WorkspaceDependencyGraph


class WorkspaceOptimizer:
    """Applies optimization passes to workspace structure and compilation."""

    def __init__(self, workspace: Workspace):
        self._workspace = workspace
        self._passes: list[dict[str, Any]] = []
        self._history: list[dict[str, Any]] = []

    def register_pass(self, name: str, fn: Callable,
                       description: str = ""):
        self._passes.append({
            "name": name,
            "fn": fn,
            "description": description,
        })

    def optimize(self, pass_name: str = "") -> dict[str, Any]:
        if pass_name:
            targets = [p for p in self._passes if p["name"] == pass_name]
        else:
            targets = list(self._passes)
        results: dict[str, Any] = {}
        for p in targets:
            start = time.time()
            try:
                result = p["fn"](self._workspace)
                elapsed = time.time() - start
                results[p["name"]] = {
                    "status": "completed",
                    "result": result,
                    "duration_ms": elapsed * 1000,
                }
                self._history.append({
                    "pass": p["name"],
                    "status": "completed",
                    "duration_ms": elapsed * 1000,
                    "timestamp": time.time(),
                })
            except Exception as e:
                elapsed = time.time() - start
                results[p["name"]] = {
                    "status": "failed",
                    "error": str(e),
                    "duration_ms": elapsed * 1000,
                }
                self._history.append({
                    "pass": p["name"],
                    "status": "failed",
                    "error": str(e),
                    "duration_ms": elapsed * 1000,
                    "timestamp": time.time(),
                })
        return results

    def register_default_passes(self):
        def deduplicate_dependencies(ws: Workspace) -> dict[str, Any]:
            removed = 0
            for repo in ws.all_repositories():
                before = len(repo.dependencies)
                repo.dependencies = list(set(repo.dependencies))
                removed += before - len(repo.dependencies)
            return {"deduplicated": removed}

        def sort_dependencies(ws: Workspace) -> dict[str, Any]:
            dep_graph = WorkspaceDependencyGraph(ws)
            order = dep_graph.topological_order()
            return {"topological_order": order}

        def detect_orphan_repos(ws: Workspace) -> dict[str, Any]:
            dep_graph = WorkspaceDependencyGraph(ws)
            orphans = [r.name for r in dep_graph.leaf_repositories()
                      if not r.dependencies]
            return {"orphan_count": len(orphans), "orphans": orphans}

        def prune_inactive(ws: Workspace) -> dict[str, Any]:
            removed = []
            for repo in ws.all_repositories():
                if not repo.healthy and repo.last_synced == 0:
                    ws.remove_repository(repo.id)
                    removed.append(repo.name)
            return {"removed": removed}

        self.register_pass("deduplicate_dependencies", deduplicate_dependencies,
                           "Remove duplicate dependency entries")
        self.register_pass("sort_dependencies", sort_dependencies,
                           "Topological sort of dependency graph")
        self.register_pass("detect_orphan_repos", detect_orphan_repos,
                           "Find repositories with no dependents or dependencies")
        self.register_pass("prune_inactive", prune_inactive,
                           "Remove unregistered repositories")

    def optimization_history(self) -> list[dict[str, Any]]:
        return list(self._history)

    def available_passes(self) -> list[dict[str, str]]:
        return [{"name": p["name"], "description": p["description"]}
                for p in self._passes]

    def summary(self) -> dict[str, Any]:
        return {
            "registered_passes": len(self._passes),
            "executed_passes": len(self._history),
            "successful": sum(1 for h in self._history if h["status"] == "completed"),
            "failed": sum(1 for h in self._history if h["status"] == "failed"),
        }
