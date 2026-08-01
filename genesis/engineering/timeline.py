from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field
from typing import Any

from genesis.engineering.object import EngineeringObjectType
from genesis.engineering.registry import get_registry


@dataclass
class TimelineEntry:
    id: str = ""
    timestamp: float = 0.0
    entry_type: str = ""  # event, audit, session, report, object_created, event_type
    source: str = ""
    title: str = ""
    description: str = ""
    object_type: str = ""
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class UniversalTimeline:
    def __init__(self, kernel=None, max_entries: int = 10000):
        self._kernel = kernel
        self._max_entries = max_entries
        self._entries: list[TimelineEntry] = []
        self._lock = threading.RLock()
        self._refreshed = False

    def refresh(self):
        with self._lock:
            self._entries.clear()
            seen = set()
            registry = get_registry()

            for obj in registry._objects.values():
                key = f"obj:{obj.id}"
                if key not in seen:
                    seen.add(key)
                    self._entries.append(TimelineEntry(
                        id=obj.id,
                        timestamp=obj.created_at,
                        entry_type="object_created",
                        source="engineering",
                        title=f"{obj.object_type.value}: {obj.name}",
                        description=obj.description[:200],
                        object_type=obj.object_type.value,
                        tags=obj.tags,
                        metadata={"updated_at": obj.updated_at},
                    ))

            if self._kernel:
                try:
                    events = self._kernel.query_events(limit=200)
                    for ev in events:
                        key = f"evt:{ev.id}"
                        if key not in seen:
                            seen.add(key)
                            self._entries.append(TimelineEntry(
                                id=ev.id,
                                timestamp=ev.timestamp,
                                entry_type="event",
                                source=ev.origin,
                                title=f"event: {ev.type}",
                                description=str(ev.payload)[:200] if ev.payload else "",
                                tags=ev.tags,
                                metadata={"severity": ev.severity.value, "priority": ev.priority.value},
                            ))
                except Exception:
                    pass

                try:
                    for sid, ctx in self._kernel._contexts.items():
                        key = f"sess:{sid}"
                        if key not in seen:
                            seen.add(key)
                            self._entries.append(TimelineEntry(
                                id=sid,
                                timestamp=ctx.get("started_at", time.time()),
                                entry_type="session",
                                source="kernel",
                                title=f"session: {ctx.get('session_type', 'engineering')}",
                                tags=[ctx.get("session_type", "engineering")],
                            ))
                except Exception:
                    pass
            self._entries.sort(key=lambda e: e.timestamp, reverse=True)
            if len(self._entries) > self._max_entries:
                self._entries = self._entries[:self._max_entries]
            self._refreshed = True

    def query(self, entry_type: str = "", source: str = "",
              object_type: str = "", limit: int = 100,
              since: float = 0.0, until: float = 0.0,
              tags: list[str] | None = None) -> list[TimelineEntry]:
        if not self._refreshed:
            self.refresh()
        with self._lock:
            results = list(self._entries)
        if entry_type:
            results = [e for e in results if e.entry_type == entry_type]
        if source:
            results = [e for e in results if e.source == source]
        if object_type:
            results = [e for e in results if e.object_type == object_type]
        if since > 0:
            results = [e for e in results if e.timestamp >= since]
        if until > 0:
            results = [e for e in results if e.timestamp <= until]
        if tags:
            results = [e for e in results if any(t in e.tags for t in tags)]
        results.sort(key=lambda e: e.timestamp, reverse=True)
        return results[:limit]

    def get_by_id(self, entry_id: str) -> TimelineEntry | None:
        if not self._refreshed:
            self.refresh()
        with self._lock:
            for e in self._entries:
                if e.id == entry_id:
                    return e
        return None

    def get_types(self) -> dict[str, int]:
        if not self._refreshed:
            self.refresh()
        with self._lock:
            counts = {}
            for e in self._entries:
                counts[e.entry_type] = counts.get(e.entry_type, 0) + 1
            return counts

    def summary(self) -> dict[str, Any]:
        if not self._refreshed:
            self.refresh()
        with self._lock:
            return {
                "total_entries": len(self._entries),
                "by_type": self.get_types(),
                "oldest": min(e.timestamp for e in self._entries) if self._entries else 0,
                "newest": max(e.timestamp for e in self._entries) if self._entries else 0,
                "range_seconds": max(e.timestamp for e in self._entries) - min(e.timestamp for e in self._entries) if self._entries else 0,
            }
