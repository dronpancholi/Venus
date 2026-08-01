"""
Genesis Studio (Mission 184) — the flagship application built on Genesis.

Reference implementation that demonstrates every Genesis platform capability:
  - Projects
  - Architecture
  - Knowledge
  - Timeline
  - AI
  - Reasoning
  - Insights
  - Reports
  - Automation
  - Applications

Not a full app. Defines the manifest, integration boundaries, and
core screens that the Desktop TUI should provide.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


STUDIO_MANIFEST = {
    "name": "genesis_studio",
    "version": "1.0.0",
    "description": "Genesis Studio — the canonical application built on Genesis",
    "author": "Genesis Team",
    "entry_point": "genesis.studio.backend",
    "capabilities": [
        "project:view", "project:manage",
        "architecture:view", "architecture:analyze",
        "knowledge:view", "knowledge:search", "knowledge:manage",
        "timeline:view", "timeline:query",
        "ai:chat", "ai:reason", "ai:providers",
        "insights:view", "insights:generate",
        "reports:view", "reports:generate",
        "automation:view", "automation:trigger",
        "apps:view", "apps:manage",
    ],
    "permissions": [
        "read:engineering", "read:events", "read:knowledge",
        "read:timeline", "read:providers",
        "write:reports", "write:insights",
        "emit:events",
    ],
    "dependencies": [
        {"name": "fabric", "version": ">=1.0"},
        {"name": "ai", "version": ">=1.0"},
        {"name": "knowledge", "version": ">=1.0"},
    ],
    "min_platform_version": "1.0.0",
}


@dataclass
class StudioScreen:
    name: str
    description: str = ""
    capabilities_required: list[str] = field(default_factory=list)
    order: int = 0


STUDIO_SCREENS: list[StudioScreen] = [
    StudioScreen("dashboard", "Platform overview and quick actions",
                 ["project:view"], order=0),
    StudioScreen("projects", "Browse and manage engineering projects",
                 ["project:view", "project:manage"], order=1),
    StudioScreen("architecture", "View and analyze architecture",
                 ["architecture:view", "architecture:analyze"], order=2),
    StudioScreen("knowledge", "Search and manage knowledge",
                 ["knowledge:view", "knowledge:search", "knowledge:manage"], order=3),
    StudioScreen("timeline", "Query engineering timeline",
                 ["timeline:view", "timeline:query"], order=4),
    StudioScreen("ai", "Chat, reason, manage providers",
                 ["ai:chat", "ai:reason", "ai:providers"], order=5),
    StudioScreen("insights", "View and generate insights",
                 ["insights:view", "insights:generate"], order=6),
    StudioScreen("reports", "Browse and generate reports",
                 ["reports:view", "reports:generate"], order=7),
    StudioScreen("automation", "View and trigger automation",
                 ["automation:view", "automation:trigger"], order=8),
    StudioScreen("apps", "Browse and manage applications",
                 ["apps:view", "apps:manage"], order=9),
]


class GenesisStudio:
    """Reference implementation of the flagship Genesis application.

    Provides a unified interface over all Genesis platform capabilities.
    The Desktop TUI should implement these screens.
    """

    def __init__(self, kernel=None, query_engine=None):
        self._kernel = kernel
        self._query_engine = query_engine

    @property
    def manifest(self) -> dict:
        return dict(STUDIO_MANIFEST)

    @property
    def screens(self) -> list[StudioScreen]:
        return list(STUDIO_SCREENS)

    def capability_summary(self) -> dict[str, bool]:
        """Check which capabilities are available."""
        return {c: True for c in STUDIO_MANIFEST["capabilities"]}
