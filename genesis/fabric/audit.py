from __future__ import annotations

import time
from dataclasses import dataclass, field
from threading import RLock
from typing import Any

from genesis.utils.identity import generate_id


@dataclass
class AuditEntry:
    id: str = ""
    action: str = ""
    actor: str = ""
    resource: str = ""
    detail: dict[str, Any] = field(default_factory=dict)
    timestamp: float = 0.0
    severity: str = "info"
    correlation_id: str = ""
    session_id: str = ""

    def __post_init__(self):
        if not self.id:
            self.id = generate_id("audit", 16)
        if not self.timestamp:
            self.timestamp = time.time()


class AuditLog:
    """Append-only audit log for the fabric."""

    def __init__(self, max_entries: int = 100000, kernel=None):
        self._entries: list[AuditEntry] = []
        self._max_entries = max_entries
        self._lock = RLock()
        self._index_by_action: dict[str, list[int]] = {}
        self._index_by_actor: dict[str, list[int]] = {}
        self._kernel = kernel

    def log(self, action: str, detail: dict[str, Any] | None = None,
            actor: str = "system", resource: str = "",
            severity: str = "info",
            correlation_id: str = "",
            session_id: str = "") -> AuditEntry:
        with self._lock:
            entry = AuditEntry(
                action=action,
                actor=actor,
                resource=resource,
                detail=detail or {},
                severity=severity,
                correlation_id=correlation_id,
                session_id=session_id,
            )
            idx = len(self._entries)
            self._entries.append(entry)
            self._index_by_action.setdefault(action, []).append(idx)
            if actor:
                self._index_by_actor.setdefault(actor, []).append(idx)
            if len(self._entries) > self._max_entries:
                trimmed = self._entries[:len(self._entries) - self._max_entries]
                self._entries = self._entries[-self._max_entries:]
        if self._kernel and self._kernel.storage and self._kernel.storage.connected:
            self._kernel.storage.store_audit_entry({
                "id": entry.id, "action": action,
                "actor": actor, "resource": resource,
                "detail": detail or {}, "timestamp": entry.timestamp,
                "severity": severity,
                "correlation_id": correlation_id,
                "session_id": session_id,
            })
        return entry

    def query(self, action: str | None = None, actor: str | None = None,
              limit: int = 100) -> list[AuditEntry]:
        with self._lock:
            indices: set[int] = set()
            if action:
                indices.update(self._index_by_action.get(action, []))
            if actor:
                indices.update(self._index_by_actor.get(actor, []))
            if not action and not actor:
                indices = set(range(len(self._entries)))
            results = [self._entries[i] for i in sorted(indices, reverse=True)]
            return results[:limit]

    def search(self, query_str: str, limit: int = 50) -> list[AuditEntry]:
        with self._lock:
            q = query_str.lower()
            results = []
            for entry in reversed(self._entries):
                if (q in entry.action.lower() or
                    q in entry.actor.lower() or
                    q in str(entry.detail).lower()):
                    results.append(entry)
                    if len(results) >= limit:
                        break
            return results

    def count(self) -> int:
        return len(self._entries)

    def summary(self) -> dict[str, Any]:
        with self._lock:
            actions: dict[str, int] = {}
            severities: dict[str, int] = {}
            for e in self._entries:
                actions[e.action] = actions.get(e.action, 0) + 1
                severities[e.severity] = severities.get(e.severity, 0) + 1
            return {
                "total_entries": len(self._entries),
                "unique_actions": len(actions),
                "by_action": actions,
                "by_severity": severities,
            }
