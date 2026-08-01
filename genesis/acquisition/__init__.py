"""
Acquisition Framework — planetary knowledge acquisition subsystem.

Phases: collect → normalize → verify → store → index → notify
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

from genesis.metamodel.entity import EntityType, EntityMetadata
from genesis.metamodel.entity import UnifiedEntity as _UnifiedEntity
from genesis.utils.identity import generate_id


@dataclass
class AcquisitionRecord:
    """Raw acquisition record before transformation into UnifiedEntity."""
    source: str = ""
    entity_type: EntityType = EntityType.REPOSITORY
    external_id: str = ""
    name: str = ""
    description: str = ""
    raw_data: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0
    tags: list[str] = field(default_factory=list)
    collected_at: float = 0.0
    url: str = ""

    def __post_init__(self):
        if not self.collected_at:
            self.collected_at = time.time()


class AcquisitionSource:
    """Base class for all planetary knowledge acquisition sources."""

    source_name: str = ""
    entity_type: EntityType = EntityType.REPOSITORY
    base_url: str = ""
    interval_seconds: float = 86400.0
    confidence: float = 0.8

    def fetch(self) -> list[AcquisitionRecord]:
        raise NotImplementedError

    def fetch_one(self, external_id: str) -> AcquisitionRecord | None:
        raise NotImplementedError

    def to_entity(self, record: AcquisitionRecord) -> dict[str, Any]:
        return {
            "uid": record.external_id,
            "name": record.name,
            "entity_type": record.entity_type.value,
            "description": record.description,
            "metadata": {
                "source": record.source,
                "confidence": record.confidence,
                "tags": record.tags,
                "properties": dict(record.metadata),
            },
            "attributes": dict(record.raw_data),
        }

    def summary(self) -> dict[str, Any]:
        return {
            "source_name": self.source_name,
            "entity_type": self.entity_type.value,
            "base_url": self.base_url,
            "interval_seconds": self.interval_seconds,
        }


class AcquisitionPipeline:
    """Orchestrates multiple acquisition sources and stores into UnifiedGraph."""

    def __init__(self, graph=None):
        self.sources: dict[str, AcquisitionSource] = {}
        self.graph = graph
        self.history: dict[str, list[dict[str, Any]]] = {}

    def register(self, source: AcquisitionSource):
        self.sources[source.source_name] = source

    def register_many(self, *sources: AcquisitionSource):
        for s in sources:
            self.register(s)

    def acquire_all(self) -> dict[str, int]:
        results: dict[str, int] = {}
        for name, source in self.sources.items():
            count = self._acquire_source(source)
            results[name] = count
        return results

    def acquire_source(self, name: str) -> int:
        source = self.sources.get(name)
        if not source:
            raise ValueError(f"Unknown source: {name}")
        return self._acquire_source(source)

    def _acquire_source(self, source: AcquisitionSource) -> int:
        try:
            records = source.fetch()
        except Exception as e:
            self._record_history(source.source_name, "error", str(e))
            return 0
        count = 0
        for record in records:
            if self.graph is not None:
                entity_dict = source.to_entity(record)
                entity = _UnifiedEntity(
                    uid=entity_dict["uid"],
                    name=entity_dict["name"],
                    entity_type=EntityType(entity_dict["entity_type"]),
                    description=entity_dict["description"],
                )
                if entity_dict.get("metadata"):
                    md = entity_dict["metadata"]
                    entity.metadata.source = md.get("source", "")
                    entity.metadata.confidence = md.get("confidence", 1.0)
                    entity.metadata.tags = md.get("tags", [])
                    entity.metadata.properties.update(md.get("properties", {}))
                entity.attributes.update(entity_dict.get("attributes", {}))
                self.graph.add_entity(entity)
            count += 1
        self._record_history(source.source_name, "success", count)
        return count

    def _record_history(self, source: str, status: str, detail: Any):
        if source not in self.history:
            self.history[source] = []
        self.history[source].append({
            "timestamp": time.time(),
            "status": status,
            "detail": detail,
        })

    def list_sources(self) -> list[dict[str, Any]]:
        return [s.summary() for s in self.sources.values()]

    def summary(self) -> dict[str, Any]:
        return {
            "source_count": len(self.sources),
            "source_names": sorted(self.sources.keys()),
            "history": {k: v[-5:] for k, v in self.history.items()},
        }
