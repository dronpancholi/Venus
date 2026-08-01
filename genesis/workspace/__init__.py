"""
Workspace Manager (Mission 181) — Desktop 2.0 enhancements.

Adds workspace templates, layout management, and session state
to the existing Genesis Desktop.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from threading import RLock
from typing import Any


@dataclass
class WorkspaceLayout:
    name: str
    screens: list[str] = field(default_factory=list)
    active_screen: str = ""
    layout_type: str = "single"  # single | split | grid
    split_direction: str = "horizontal"
    split_ratio: float = 0.5


@dataclass
class WorkspaceTemplate:
    name: str
    description: str = ""
    default_layout: WorkspaceLayout = field(default_factory=WorkspaceLayout)
    watchers: list[str] = field(default_factory=list)
    pinned_projects: list[str] = field(default_factory=list)
    quick_actions: list[str] = field(default_factory=list)


BUILTIN_TEMPLATES: list[WorkspaceTemplate] = [
    WorkspaceTemplate(
        name="engineering",
        description="Full engineering workspace — events, agents, knowledge",
        default_layout=WorkspaceLayout(
            name="engineering", screens=["home", "agents", "events", "knowledge"],
            active_screen="home", layout_type="grid",
        ),
        watchers=["filesystem", "git"],
    ),
    WorkspaceTemplate(
        name="review",
        description="Architecture review workspace",
        default_layout=WorkspaceLayout(
            name="review", screens=["events", "knowledge"],
            active_screen="events", layout_type="split",
        ),
    ),
    WorkspaceTemplate(
        name="minimal",
        description="Minimal workspace — just the home screen",
        default_layout=WorkspaceLayout(
            name="minimal", screens=["home"],
            active_screen="home",
        ),
    ),
]


class WorkspaceManager:
    """Manages workspace layouts, templates, and session state."""

    def __init__(self):
        self._templates: dict[str, WorkspaceTemplate] = {t.name: t for t in BUILTIN_TEMPLATES}
        self._layouts: dict[str, WorkspaceLayout] = {}
        self._current_layout: str = "minimal"
        self._pinned_projects: list[str] = []
        self._recent_work: list[str] = []
        self._lock = RLock()

    def templates(self) -> list[WorkspaceTemplate]:
        return list(self._templates.values())

    def apply_template(self, name: str) -> WorkspaceLayout | None:
        tmpl = self._templates.get(name)
        if not tmpl:
            return None
        with self._lock:
            self._layouts[name] = tmpl.default_layout
            self._current_layout = name
            self._pinned_projects = list(tmpl.pinned_projects)
        return tmpl.default_layout

    @property
    def current_layout(self) -> str:
        return self._current_layout

    def layout(self, name: str | None = None) -> WorkspaceLayout | None:
        return self._layouts.get(name or self._current_layout)

    def pin_project(self, project: str):
        if project not in self._pinned_projects:
            self._pinned_projects.append(project)

    def unpin_project(self, project: str):
        if project in self._pinned_projects:
            self._pinned_projects.remove(project)

    @property
    def pinned_projects(self) -> list[str]:
        return list(self._pinned_projects)

    def add_recent(self, item: str):
        with self._lock:
            if item in self._recent_work:
                self._recent_work.remove(item)
            self._recent_work.insert(0, item)
            if len(self._recent_work) > 20:
                self._recent_work.pop()

    @property
    def recent_work(self) -> list[str]:
        return list(self._recent_work)
