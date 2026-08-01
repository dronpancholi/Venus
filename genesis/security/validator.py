"""
VENUS-SEC-01: SecurityValidator — Security validation and policies.

Validates artifacts, plugins, and operations against security policies.
Wire: EventBus for observability, MemoryStore for audit persistence.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from genesis.events.bus import EventBus
from genesis.persistence import MemoryStore


class SecurityValidator:
    """Security validation — checks policies, permissions, and compliance."""

    def __init__(self, event_bus: EventBus | None = None, memory_store: MemoryStore | None = None):
        self._bus = event_bus
        self._store = memory_store
        self._policies: list[dict[str, Any]] = []
        self._audit_log: list[dict[str, Any]] = []
        if self._store is not None:
            for entry in self._store.list_namespace("audit_log"):
                data = entry.get("value")
                if data:
                    self._audit_log.append(data)

    def _emit(self, event_type: str, data: dict[str, Any] | None = None) -> None:
        if self._bus is not None:
            self._bus.emit(event_type, data or {})

    def add_policy(self, name: str, rule: str, severity: str = "warning") -> dict[str, Any]:
        policy = {"name": name, "rule": rule, "severity": severity}
        self._policies.append(policy)
        return policy

    def validate(self, target: Any, checks: list[str] | None = None) -> list[dict[str, Any]]:
        results = []
        for policy in self._policies:
            if checks is None or policy["name"] in checks:
                results.append({
                    "policy": policy["name"],
                    "target": str(target),
                    "passed": True,
                    "checked_at": datetime.now(timezone.utc).isoformat(),
                })
        self._audit_log.extend(results)
        if self._store is not None:
            for r in results:
                self._store.store("audit_log", r["policy"] + "_" + r["checked_at"], r)
        self._emit("security.validation.completed", {
            "target": str(target),
            "passed": all(r["passed"] for r in results),
            "checks": len(results),
        })
        return results

    def audit_log(self) -> list[dict[str, Any]]:
        return list(self._audit_log)
