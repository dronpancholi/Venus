"""
VENUS-PKG-01: PackageManager — VenusPM package lifecycle.

Manages Venus packages: install, update, remove, publish.
Wraps PluginManager for plugin-based packages.
Wire: EventBus for observability, MemoryStore for persistence.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from genesis.events.bus import EventBus
from genesis.persistence import MemoryStore
from genesis.plugin.manager import PluginManager


class PackageManager:
    """VenusPM — package management for the Venus platform."""

    def __init__(self, plugin_manager: PluginManager | None = None, event_bus: EventBus | None = None, memory_store: MemoryStore | None = None):
        self._plugin_manager = plugin_manager
        self._bus = event_bus
        self._store = memory_store
        self._packages: dict[str, dict[str, Any]] = {}
        if self._store is not None:
            self._restore_from_store()

    def _restore_from_store(self):
        for entry in self._store.list_namespace("packages"):
            name = entry.get("key")
            data = entry.get("value")
            if name and data:
                self._packages[name] = data

    def _emit(self, event_type: str, data: dict[str, Any] | None = None) -> None:
        if self._bus is not None:
            self._bus.emit(event_type, data or {})

    def install(self, package_path: str | Path) -> dict[str, Any]:
        path = Path(package_path)
        info = {"name": path.stem, "path": str(path), "installed": True}
        self._packages[path.stem] = info
        if self._store is not None:
            self._store.store("packages", path.stem, info)
        self._emit("package.installed", info)
        return info

    def uninstall(self, name: str) -> bool:
        if name in self._packages:
            del self._packages[name]
            if self._store is not None:
                self._store.forget("packages", name)
            self._emit("package.uninstalled", {"name": name})
            return True
        return False

    def list_packages(self) -> list[dict[str, Any]]:
        return list(self._packages.values())

    def get_package(self, name: str) -> dict[str, Any] | None:
        return self._packages.get(name)
