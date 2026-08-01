"""
VENUS-PRJ-01: ProjectManager — Project lifecycle management.

Creates, configures, and manages Venus projects.
Coordinates Compiler, KnowledgeGraph, Metadata, and Validation.
Wire: EventBus for observability, MemoryStore for persistence.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from genesis.events.bus import EventBus
from genesis.persistence import MemoryStore


class ProjectManager:
    """Project lifecycle management for Venus."""

    def __init__(self, event_bus: EventBus | None = None, memory_store: MemoryStore | None = None):
        self._bus = event_bus
        self._store = memory_store
        self._projects: dict[str, dict[str, Any]] = {}
        if self._store is not None:
            for entry in self._store.list_namespace("projects"):
                data = entry.get("value")
                if data and data.get("name"):
                    self._projects[data["name"]] = data

    def _emit(self, event_type: str, data: dict[str, Any] | None = None) -> None:
        if self._bus is not None:
            self._bus.emit(event_type, data or {})

    def create_project(self, name: str, root: str | Path | None = None) -> dict[str, Any]:
        project = {
            "name": name,
            "root": str(root or Path.cwd() / name),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "status": "active",
        }
        self._projects[name] = project
        if self._store is not None:
            self._store.store("projects", name, project)
        self._emit("project.created", project)
        return project

    def get_project(self, name: str) -> dict[str, Any] | None:
        return self._projects.get(name)

    def list_projects(self) -> list[dict[str, Any]]:
        return list(self._projects.values())

    def close_project(self, name: str) -> bool:
        proj = self._projects.get(name)
        if proj:
            proj["status"] = "closed"
            proj["closed_at"] = datetime.now(timezone.utc).isoformat()
            self._emit("project.closed", {"name": name})
            return True
        return False
