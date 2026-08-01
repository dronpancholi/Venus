"""
VENUS-MEM-01: MemoryEngine — Institutional memory management.

Persists and retrieves platform knowledge across sessions.
Backed by MemoryStore (SQLite key-value by namespace).
Wire: EventBus for observability, MemoryStore for persistence.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from genesis.events.bus import EventBus
from genesis.persistence import MemoryStore


class MemoryEngine:
    """Institutional memory — persists platform knowledge across sessions."""

    def __init__(self, memory_store: MemoryStore | None = None, event_bus: EventBus | None = None):
        self._store = memory_store
        self._bus = event_bus
        self._cache: dict[str, dict[str, Any]] = {}

    def _emit(self, event_type: str, data: dict[str, Any] | None = None) -> None:
        if self._bus is not None:
            self._bus.emit(event_type, data or {})

    def store(self, key: str, value: Any, namespace: str = "default") -> None:
        if self._store is not None:
            self._store.store(namespace, key, value)
        self._cache[f"{namespace}:{key}"] = value
        self._emit("memory.stored", {"key": key, "namespace": namespace})

    def recall(self, key: str, namespace: str = "default") -> Any | None:
        cache_key = f"{namespace}:{key}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        if self._store is not None:
            value = self._store.recall(namespace, key)
            if value is not None:
                self._cache[cache_key] = value
                return value
        return None

    def forget(self, key: str, namespace: str = "default") -> bool:
        cache_key = f"{namespace}:{key}"
        removed = self._cache.pop(cache_key, None)
        store_removed = False
        if self._store is not None:
            store_removed = self._store.forget(namespace, key)
        if removed is not None or store_removed:
            self._emit("memory.forgotten", {"key": key, "namespace": namespace})
            return True
        return False

    def list_namespace(self, namespace: str = "default") -> list[dict[str, Any]]:
        if self._store is not None:
            return self._store.list_namespace(namespace)
        return [
            {"key": k.split(":", 1)[1], "value": v}
            for k, v in self._cache.items()
            if k.startswith(f"{namespace}:")
        ]
