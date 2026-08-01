"""
GENESIS XI: Workspace — collection of repositories and their metadata.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

from genesis.utils.identity import generate_id


class RepositoryType(Enum):
    SOURCE = "source"
    LIBRARY = "library"
    SERVICE = "service"
    TOOL = "tool"
    CONFIG = "config"
    INFRASTRUCTURE = "infrastructure"
    DOCUMENTATION = "documentation"
    RESEARCH = "research"
    NOTEBOOK = "notebook"
    PACKAGE = "package"
    UNKNOWN = "unknown"


class WorkspaceScope(Enum):
    LOCAL = "local"
    TEAM = "team"
    ORGANIZATION = "organization"
    FEDERATED = "federated"


@dataclass
class Repository:
    """A single repository within a workspace."""
    id: str = ""
    name: str = ""
    url: str = ""
    local_path: str = ""
    repo_type: RepositoryType = RepositoryType.SOURCE
    language: str = ""
    description: str = ""
    default_branch: str = "main"
    head_commit: str = ""
    tags: list[str] = field(default_factory=list)
    capabilities_provided: list[str] = field(default_factory=list)
    capabilities_consumed: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    federated_sources: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    discovered_at: float = 0.0
    last_synced: float = 0.0
    size_bytes: int = 0
    file_count: int = 0
    module_count: int = 0
    healthy: bool = True

    def __post_init__(self):
        if not self.id:
            self.id = generate_id("repo", 12)
        if not self.discovered_at:
            self.discovered_at = time.time()

    def touch(self):
        self.last_synced = time.time()

    def summary(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "type": self.repo_type.value,
            "language": self.language,
            "branch": self.default_branch,
            "head": self.head_commit[:8] if self.head_commit else "",
            "capabilities": {
                "provided": len(self.capabilities_provided),
                "consumed": len(self.capabilities_consumed),
            },
            "dependencies": len(self.dependencies),
            "files": self.file_count,
            "modules": self.module_count,
            "healthy": self.healthy,
        }


@dataclass
class WorkspaceManifest:
    """Declarative workspace definition."""
    id: str = ""
    name: str = ""
    version: str = "1.0.0"
    scope: WorkspaceScope = WorkspaceScope.LOCAL
    description: str = ""
    root_path: str = ""
    repositories: list[Repository] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    environment: dict[str, str] = field(default_factory=dict)
    settings: dict[str, Any] = field(default_factory=dict)
    created_at: float = 0.0
    updated_at: float = 0.0

    def __post_init__(self):
        now = time.time()
        if not self.id:
            self.id = generate_id("ws", 10)
        if not self.created_at:
            self.created_at = now
        if not self.updated_at:
            self.updated_at = now

    def add_repository(self, repo: Repository):
        existing = {r.id for r in self.repositories}
        if repo.id not in existing:
            self.repositories.append(repo)
            self.updated_at = time.time()

    def remove_repository(self, repo_id: str) -> bool:
        before = len(self.repositories)
        self.repositories = [r for r in self.repositories if r.id != repo_id]
        if len(self.repositories) < before:
            self.updated_at = time.time()
            return True
        return False

    def get_repository(self, repo_id: str) -> Repository | None:
        for r in self.repositories:
            if r.id == repo_id:
                return r
        return None

    def find_by_name(self, name: str) -> list[Repository]:
        return [r for r in self.repositories if name.lower() in r.name.lower()]

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "version": self.version,
            "scope": self.scope.value,
            "description": self.description,
            "root_path": self.root_path,
            "repositories": [r.summary() for r in self.repositories],
            "tags": self.tags,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


class Workspace:
    """A workspace is a managed collection of repositories."""

    def __init__(self, manifest: WorkspaceManifest | None = None, name: str = "default"):
        self.manifest = manifest or WorkspaceManifest(name=name)
        self._repos: dict[str, Repository] = {}
        for repo in self.manifest.repositories:
            self._repos[repo.id] = repo
        self._history: list[dict[str, Any]] = []

    @property
    def id(self) -> str:
        return self.manifest.id

    @property
    def name(self) -> str:
        return self.manifest.name

    @property
    def repository_count(self) -> int:
        return len(self._repos)

    def add_repository(self, repo: Repository):
        self._repos[repo.id] = repo
        self.manifest.add_repository(repo)
        self._history.append({
            "action": "add_repository",
            "repo_id": repo.id,
            "name": repo.name,
            "timestamp": time.time(),
        })

    def remove_repository(self, repo_id: str) -> bool:
        if self._repos.pop(repo_id, None):
            self.manifest.remove_repository(repo_id)
            self._history.append({
                "action": "remove_repository",
                "repo_id": repo_id,
                "timestamp": time.time(),
            })
            return True
        return False

    def get_repository(self, repo_id: str) -> Repository | None:
        return self._repos.get(repo_id)

    def find_by_name(self, name: str) -> list[Repository]:
        return [r for r in self._repos.values() if name.lower() in r.name.lower()]

    def find_by_type(self, repo_type: RepositoryType) -> list[Repository]:
        return [r for r in self._repos.values() if r.repo_type == repo_type]

    def find_by_language(self, language: str) -> list[Repository]:
        return [r for r in self._repos.values() if r.language.lower() == language.lower()]

    def all_repositories(self) -> list[Repository]:
        return list(self._repos.values())

    def dependency_graph(self) -> dict[str, list[str]]:
        graph: dict[str, list[str]] = {}
        for repo in self._repos.values():
            graph[repo.id] = list(repo.dependencies)
        return graph

    def capability_map(self) -> dict[str, list[str]]:
        mapping: dict[str, list[str]] = {}
        for repo in self._repos.values():
            for cap in repo.capabilities_provided:
                mapping.setdefault(cap, []).append(repo.id)
        return mapping

    def total_files(self) -> int:
        return sum(r.file_count for r in self._repos.values())

    def total_modules(self) -> int:
        return sum(r.module_count for r in self._repos.values())

    def total_size_bytes(self) -> int:
        return sum(r.size_bytes for r in self._repos.values())

    def languages(self) -> list[str]:
        return list({r.language for r in self._repos.values() if r.language})

    def unhealthy_repositories(self) -> list[Repository]:
        return [r for r in self._repos.values() if not r.healthy]

    def summary(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "scope": self.manifest.scope.value,
            "repositories": self.repository_count,
            "languages": self.languages(),
            "total_files": self.total_files(),
            "total_modules": self.total_modules(),
            "total_size_bytes": self.total_size_bytes(),
            "dependency_count": sum(len(r.dependencies) for r in self._repos.values()),
            "capabilities_provided": sum(len(r.capabilities_provided) for r in self._repos.values()),
            "capabilities_consumed": sum(len(r.capabilities_consumed) for r in self._repos.values()),
            "unhealthy": len(self.unhealthy_repositories()),
            "history_size": len(self._history),
        }
