"""
GENESIS XI: Repository federation — sync and link across workspace boundaries.
"""

from __future__ import annotations

import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any

from genesis.meta.workspace import Repository, Workspace, WorkspaceScope
from genesis.utils.identity import generate_id


@dataclass
class FederationLink:
    id: str = ""
    source_workspace_id: str = ""
    target_workspace_id: str = ""
    source_repo_id: str = ""
    target_repo_id: str = ""
    sync_frequency_seconds: float = 3600.0
    last_synced: float = 0.0
    status: str = "active"
    mapping: dict[str, str] = field(default_factory=dict)
    created_at: float = 0.0

    def __post_init__(self):
        if not self.id:
            self.id = generate_id("fed", 12)
        if not self.created_at:
            self.created_at = time.time()


class RepositoryFederation:
    """Manages federation links between workspaces and repositories."""

    def __init__(self):
        self._links: dict[str, FederationLink] = {}
        self._workspaces: dict[str, Workspace] = {}
        self._history: list[dict[str, Any]] = []

    def register_workspace(self, workspace: Workspace):
        self._workspaces[workspace.id] = workspace

    def unregister_workspace(self, workspace_id: str) -> bool:
        return self._workspaces.pop(workspace_id, None) is not None

    def get_workspace(self, workspace_id: str) -> Workspace | None:
        return self._workspaces.get(workspace_id)

    def all_workspaces(self) -> list[Workspace]:
        return list(self._workspaces.values())

    def link(self, source_workspace_id: str, target_workspace_id: str,
             source_repo_id: str, target_repo_id: str,
             mapping: dict[str, str] | None = None) -> FederationLink | None:
        if source_workspace_id not in self._workspaces:
            return None
        if target_workspace_id not in self._workspaces:
            return None
        link = FederationLink(
            source_workspace_id=source_workspace_id,
            target_workspace_id=target_workspace_id,
            source_repo_id=source_repo_id,
            target_repo_id=target_repo_id,
            mapping=mapping or {},
        )
        self._links[link.id] = link
        self._history.append({
            "action": "link",
            "link_id": link.id,
            "source": source_workspace_id,
            "target": target_workspace_id,
            "source_repo": source_repo_id,
            "target_repo": target_repo_id,
            "timestamp": time.time(),
        })
        return link

    def unlink(self, link_id: str) -> bool:
        link = self._links.pop(link_id, None)
        if link:
            self._history.append({
                "action": "unlink",
                "link_id": link_id,
                "timestamp": time.time(),
            })
            return True
        return False

    def sync(self, link_id: str) -> bool:
        link = self._links.get(link_id)
        if not link or link.status != "active":
            return False
        link.last_synced = time.time()
        self._history.append({
            "action": "sync",
            "link_id": link_id,
            "timestamp": time.time(),
        })
        return True

    def sync_all(self) -> int:
        count = 0
        for link in self._links.values():
            if link.status == "active":
                if time.time() - link.last_synced > link.sync_frequency_seconds:
                    self.sync(link.id)
                    count += 1
        return count

    def links_for_workspace(self, workspace_id: str) -> list[FederationLink]:
        return [l for l in self._links.values()
                if l.source_workspace_id == workspace_id
                or l.target_workspace_id == workspace_id]

    def links_for_repo(self, repo_id: str) -> list[FederationLink]:
        return [l for l in self._links.values()
                if l.source_repo_id == repo_id or l.target_repo_id == repo_id]

    def resolve_federated_repo(self, repo_id: str) -> list[tuple[str, str]]:
        results: list[tuple[str, str]] = []
        for link in self._links.values():
            if link.source_repo_id == repo_id:
                ws = self._workspaces.get(link.target_workspace_id)
                repo = ws.get_repository(link.target_repo_id) if ws else None
                if repo:
                    results.append((link.target_workspace_id, repo.name))
        return results

    def federated_graph(self) -> dict[str, list[str]]:
        graph: dict[str, list[str]] = defaultdict(list)
        for link in self._links.values():
            key = f"{link.source_workspace_id}:{link.source_repo_id}"
            val = f"{link.target_workspace_id}:{link.target_repo_id}"
            graph[key].append(val)
        return dict(graph)

    def summary(self) -> dict[str, Any]:
        return {
            "workspaces": len(self._workspaces),
            "links": len(self._links),
            "active_links": sum(1 for l in self._links.values() if l.status == "active"),
            "syncs_performed": sum(1 for h in self._history if h["action"] == "sync"),
            "total_operations": len(self._history),
        }
