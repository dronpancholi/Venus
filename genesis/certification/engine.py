"""
VENUS-CERT-01: CertificationEngine — Artifact certification.

Validates artifacts against platform standards and assigns certification state.
Wire: EventBus for observability, MemoryStore for persistence.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from genesis.events.bus import EventBus
from genesis.persistence import MemoryStore


class CertificationEngine:
    """Artifact certification — validates and certifies platform artifacts."""

    CERTIFICATION_LEVELS = ["uncertified", "bronze", "silver", "gold", "platinum"]

    def __init__(self, event_bus: EventBus | None = None, memory_store: MemoryStore | None = None):
        self._bus = event_bus
        self._store = memory_store
        self._certifications: dict[str, dict[str, Any]] = {}
        if self._store is not None:
            for entry in self._store.list_namespace("certifications"):
                data = entry.get("value")
                if data and data.get("artifact_id"):
                    self._certifications[data["artifact_id"]] = data

    def _emit(self, event_type: str, data: dict[str, Any] | None = None) -> None:
        if self._bus is not None:
            self._bus.emit(event_type, data or {})

    def certify(self, artifact_id: str, level: str = "bronze") -> dict[str, Any] | None:
        if level not in self.CERTIFICATION_LEVELS:
            return None
        record = {
            "artifact_id": artifact_id,
            "level": level,
            "certified_at": datetime.now(timezone.utc).isoformat(),
        }
        self._certifications[artifact_id] = record
        if self._store is not None:
            self._store.store("certifications", artifact_id, record)
        self._emit("artifact.certified", record)
        return record

    def revoke(self, artifact_id: str) -> bool:
        if artifact_id in self._certifications:
            del self._certifications[artifact_id]
            if self._store is not None:
                self._store.forget("certifications", artifact_id)
            self._emit("artifact.certification.revoked", {"artifact_id": artifact_id})
            return True
        return False

    def get_certification(self, artifact_id: str) -> dict[str, Any] | None:
        return self._certifications.get(artifact_id)

    def list_by_level(self, level: str) -> list[dict[str, Any]]:
        return [r for r in self._certifications.values() if r.get("level") == level]
