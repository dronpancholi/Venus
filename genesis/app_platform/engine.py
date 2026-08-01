from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

from genesis.engineering import EngineeringObject, EngineeringObjectType, get_registry
from genesis.state import get_state


@dataclass
class AppManifest:
    name: str
    description: str
    version: str = "1.0.0"
    author: str = ""
    dependencies: list[str] = field(default_factory=list)
    permissions: list[str] = field(default_factory=list)
    entry_points: list[str] = field(default_factory=list)


@dataclass
class GenesisApp:
    manifest: AppManifest
    status: str = "registered"
    started_at: float = 0.0
    health: str = "unknown"


class GenesisAppPlatform:
    def __init__(self, kernel=None):
        self._kernel = kernel
        self._registry = get_registry()
        self._state = get_state()
        self._apps: dict[str, GenesisApp] = {}
        self._ap_obj: EngineeringObject | None = None

    def boot(self):
        self._ap_obj = EngineeringObject(
            object_type=EngineeringObjectType.APP,
            name="GenesisAppPlatform",
            description="Platform capable of hosting applications on Genesis infrastructure",
            tags=["platform", "apps"],
        )
        self._registry.register(self._ap_obj)
        self._state.set("app_platform", "apps", 0)
        self._register_builtin_apps()

    def _register_builtin_apps(self):
        builtins = [
            AppManifest("buildit", "BuildIT — Engineering build system", "1.0.0",
                        dependencies=["engineering", "knowledge", "twin"],
                        permissions=["read:repository", "write:engineering"],
                        entry_points=["buildit.run"]),
            AppManifest("venus", "Venus Platform — Strategic engineering platform", "1.0.0",
                        dependencies=["engineering", "ai", "twin", "automation"],
                        permissions=["read:*", "write:engineering", "emit:events"],
                        entry_points=["venus.run"]),
            AppManifest("architecture_studio", "Architecture Studio — Design and visualize architecture", "1.0.0",
                        dependencies=["architecture", "engineering", "search"],
                        permissions=["read:architecture", "read:engineering"],
                        entry_points=["architecture_studio.run"]),
            AppManifest("deployment_studio", "Deployment Studio — Manage deployments", "1.0.0",
                        dependencies=["automation", "workflows", "engineering"],
                        permissions=["read:workflows", "write:workflows"],
                        entry_points=["deployment_studio.run"]),
            AppManifest("documentation_studio", "Documentation Studio — Auto-generate documentation",
                        dependencies=["knowledge", "engineering", "search"],
                        permissions=["read:knowledge", "read:engineering"],
                        entry_points=["documentation_studio.run"]),
            AppManifest("agentos", "AgentOS — Agent Operating System", "2.0.0",
                        dependencies=["engineering", "ai", "knowledge", "memory_v2",
                                      "twin", "automation", "workflows", "insight",
                                      "reasoning", "copilot_v2", "search"],
                        permissions=["read:*", "write:*", "emit:events", "manage:agents"],
                        entry_points=["agentos.run"]),
        ]
        for manifest in builtins:
            self.register(manifest)

    def register(self, manifest: AppManifest) -> GenesisApp:
        app = GenesisApp(manifest=manifest, status="registered")
        self._apps[manifest.name] = app
        self._state.set("app_platform", "apps", len(self._apps))
        obj = EngineeringObject(
            object_type=EngineeringObjectType.APP,
            name=manifest.name,
            description=manifest.description[:200],
            tags=["app", manifest.name],
            metadata={"version": manifest.version, "dependencies": manifest.dependencies},
        )
        self._registry.register(obj)
        if self._kernel:
            self._kernel.emit("app.registered", {"name": manifest.name, "version": manifest.version},
                              origin="app_platform", tags=["app"])
        return app

    def get(self, name: str) -> GenesisApp | None:
        return self._apps.get(name)

    def start(self, name: str) -> bool:
        app = self._apps.get(name)
        if not app or app.status == "running":
            return False
        app.status = "running"
        app.started_at = time.time()
        app.health = "healthy"
        if self._kernel:
            self._kernel.emit("app.started", {"name": name}, origin="app_platform", tags=["app"])
        return True

    def stop(self, name: str) -> bool:
        app = self._apps.get(name)
        if not app or app.status != "running":
            return False
        app.status = "stopped"
        app.health = "unknown"
        return True

    def list(self) -> list[dict[str, Any]]:
        return [
            {"name": a.manifest.name, "description": a.manifest.description,
             "version": a.manifest.version, "status": a.status,
             "dependencies": a.manifest.dependencies}
            for a in self._apps.values()
        ]

    def stats(self) -> dict[str, Any]:
        return {
            "total": len(self._apps),
            "running": sum(1 for a in self._apps.values() if a.status == "running"),
            "registered": sum(1 for a in self._apps.values() if a.status == "registered"),
        }
