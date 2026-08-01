"""
GENESIS XI: Workspace Twin — Digital twin of the entire workspace.
"""

from __future__ import annotations

import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any

from genesis.meta.graph import WorkspaceGraph
from genesis.meta.irep import WorkspaceIR, WorkspaceIRNode
from genesis.meta.workspace import Repository, Workspace, RepositoryType
from genesis.utils.identity import generate_id


@dataclass
class TwinEntity:
    id: str = ""
    name: str = ""
    entity_type: str = "repository"
    repository_id: str = ""
    state: dict[str, Any] = field(default_factory=dict)
    metrics: dict[str, float] = field(default_factory=dict)
    history: list[dict[str, Any]] = field(default_factory=list)
    predictions: dict[str, Any] = field(default_factory=dict)
    health: float = 1.0
    created_at: float = 0.0
    updated_at: float = 0.0

    def __post_init__(self):
        if not self.id:
            self.id = generate_id("twin", 12)
        if not self.created_at:
            self.created_at = time.time()
        if not self.updated_at:
            self.updated_at = self.created_at


class WorkspaceTwin:
    """Digital twin of an entire workspace with state, metrics, and predictions."""

    def __init__(self, workspace: Workspace):
        self._workspace = workspace
        self._entities: dict[str, TwinEntity] = {}
        self._ir: WorkspaceIR | None = None
        self._graph: WorkspaceGraph | None = None
        self._snapshots: list[dict[str, Any]] = []
        self._created_at = time.time()

    @property
    def workspace(self) -> Workspace:
        return self._workspace

    def attach_ir(self, ir: WorkspaceIR):
        self._ir = ir

    def attach_graph(self, graph: WorkspaceGraph):
        self._graph = graph

    def build_entities(self):
        for repo in self._workspace.all_repositories():
            entity = TwinEntity(
                name=repo.name,
                entity_type=repo.repo_type.value,
                repository_id=repo.id,
                state={
                    "language": repo.language,
                    "branch": repo.default_branch,
                    "head_commit": repo.head_commit[:8] if repo.head_commit else "",
                    "healthy": repo.healthy,
                },
                metrics={
                    "files": float(repo.file_count),
                    "modules": float(repo.module_count),
                    "size_bytes": float(repo.size_bytes),
                    "dependencies": float(len(repo.dependencies)),
                    "capabilities_provided": float(len(repo.capabilities_provided)),
                    "capabilities_consumed": float(len(repo.capabilities_consumed)),
                },
                health=1.0 if repo.healthy else 0.0,
            )
            self._entities[entity.id] = entity

    def update_repo(self, repo_id: str):
        repo = self._workspace.get_repository(repo_id)
        if not repo:
            return
        for entity in self._entities.values():
            if entity.repository_id == repo_id:
                entity.updated_at = time.time()
                entity.state["head_commit"] = repo.head_commit[:8] if repo.head_commit else ""
                entity.health = 1.0 if repo.healthy else 0.0
                entity.metrics["files"] = float(repo.file_count)
                entity.history.append({
                    "timestamp": time.time(),
                    "event": "update",
                    "head": repo.head_commit[:8] if repo.head_commit else "",
                })

    def get_entity(self, entity_id: str) -> TwinEntity | None:
        return self._entities.get(entity_id)

    def find_by_repo(self, repo_id: str) -> TwinEntity | None:
        for entity in self._entities.values():
            if entity.repository_id == repo_id:
                return entity
        return None

    def snapshot(self) -> dict[str, Any]:
        snapshot = {
            "timestamp": time.time(),
            "workspace": self._workspace.summary(),
            "entities": len(self._entities),
            "ir": self._ir.to_dict() if self._ir else None,
            "graph": self._graph.summary() if self._graph else None,
            "health": self.aggregate_health(),
        }
        self._snapshots.append(snapshot)
        return snapshot

    def aggregate_health(self) -> dict[str, float]:
        if not self._entities:
            return {"average": 1.0, "min": 1.0, "max": 1.0, "healthy_count": 0, "total": 0}
        healths = [e.health for e in self._entities.values()]
        return {
            "average": sum(healths) / len(healths),
            "min": min(healths),
            "max": max(healths),
            "healthy_count": sum(1 for h in healths if h > 0.5),
            "total": len(healths),
        }

    def compare(self, other: WorkspaceTwin) -> dict[str, Any]:
        changes = []
        my_repos = {e.repository_id: e for e in self._entities.values()}
        other_repos = {e.repository_id: e for e in other._entities.values()}
        for repo_id, my_entity in my_repos.items():
            other_entity = other_repos.get(repo_id)
            if other_entity:
                if my_entity.health != other_entity.health:
                    changes.append({
                        "repository_id": repo_id,
                        "type": "health_change",
                        "from": other_entity.health,
                        "to": my_entity.health,
                    })
                if my_entity.state.get("head_commit") != other_entity.state.get("head_commit"):
                    changes.append({
                        "repository_id": repo_id,
                        "type": "commit_change",
                        "from": other_entity.state.get("head_commit"),
                        "to": my_entity.state.get("head_commit"),
                    })
            else:
                changes.append({
                    "repository_id": repo_id,
                    "type": "added",
                })
        for repo_id in other_repos:
            if repo_id not in my_repos:
                changes.append({
                    "repository_id": repo_id,
                    "type": "removed",
                })
        return {
            "changes": len(changes),
            "details": changes,
            "timestamp": time.time(),
        }

    def summary(self) -> dict[str, Any]:
        return {
            "workspace": self._workspace.name,
            "entities": len(self._entities),
            "has_ir": self._ir is not None,
            "has_graph": self._graph is not None,
            "health": self.aggregate_health(),
            "snapshots": len(self._snapshots),
            "age_seconds": time.time() - self._created_at,
        }
