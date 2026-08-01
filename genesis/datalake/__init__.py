"""
Engineering Data Lake — versioned, queryable, historically persistent entity store.

Every entity version is preserved.
Every mutation is recorded.
Every query is temporal.
"""

from __future__ import annotations

import json
import time
import uuid
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Generator

from typing import Any

from genesis.metamodel.entity import EntityType, EntityRelation, UnifiedEntity
from genesis.metamodel.graph import UnifiedGraph
from genesis.utils.identity import generate_id


def _resolve_graph(graph: Any) -> UnifiedGraph:
    if isinstance(graph, UnifiedGraph):
        return graph
    if hasattr(graph, 'unified_graph'):
        return graph.unified_graph
    raise TypeError(f"Expected UnifiedGraph or CanonicalGraph, got {type(graph).__name__}")


# ── Data Lake Entity ──

@dataclass
class DataLakeEntity:
    """A versioned entity in the data lake. Every mutation creates a new version."""
    uid: str = ""
    name: str = ""
    entity_type: EntityType = EntityType.ENTITY_TYPE_DEF
    description: str = ""
    source: str = ""
    confidence: float = 1.0
    tags: list[str] = field(default_factory=list)
    attributes: dict[str, Any] = field(default_factory=dict)
    version: int = 1
    created_at: float = 0.0
    updated_at: float = 0.0
    snapshot_id: str = ""

    def __post_init__(self):
        now = time.time()
        if not self.created_at:
            self.created_at = now
        if not self.updated_at:
            self.updated_at = now
        if not self.snapshot_id:
            self.snapshot_id = generate_id("snap", 8)

    def to_unified_entity(self) -> UnifiedEntity:
        entity = UnifiedEntity(
            uid=self.uid,
            name=self.name,
            entity_type=self.entity_type,
            description=self.description,
        )
        entity.metadata.source = self.source
        entity.metadata.confidence = self.confidence
        entity.metadata.tags = list(self.tags)
        entity.metadata.version = f"{self.version}.0.0"
        entity.metadata.properties["snapshot_id"] = self.snapshot_id
        entity.metadata.properties["version"] = self.version
        entity.metadata.properties["created_at"] = self.created_at
        entity.attributes = dict(self.attributes)
        return entity

    @classmethod
    def from_unified_entity(cls, entity: UnifiedEntity, version: int = 1) -> DataLakeEntity:
        return cls(
            uid=entity.uid,
            name=entity.name,
            entity_type=entity.entity_type,
            description=entity.description,
            source=entity.metadata.source,
            confidence=entity.metadata.confidence,
            tags=list(entity.metadata.tags),
            attributes=dict(entity.attributes),
            version=version,
            created_at=entity.metadata.created_at,
            updated_at=entity.metadata.updated_at,
            snapshot_id=entity.metadata.properties.get("snapshot_id", ""),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "uid": self.uid,
            "name": self.name,
            "entity_type": self.entity_type.value,
            "description": self.description,
            "source": self.source,
            "confidence": self.confidence,
            "tags": list(self.tags),
            "attributes": dict(self.attributes),
            "version": self.version,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "snapshot_id": self.snapshot_id,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> DataLakeEntity:
        return cls(
            uid=d["uid"],
            name=d.get("name", ""),
            entity_type=EntityType(d.get("entity_type", "entity_type_definition")),
            description=d.get("description", ""),
            source=d.get("source", ""),
            confidence=d.get("confidence", 1.0),
            tags=list(d.get("tags", [])),
            attributes=dict(d.get("attributes", {})),
            version=d.get("version", 1),
            created_at=d.get("created_at", 0),
            updated_at=d.get("updated_at", 0),
            snapshot_id=d.get("snapshot_id", ""),
        )

    def __repr__(self) -> str:
        return f"<DL:{self.entity_type.value}:{self.name}:v{self.version}>"


# ── Versioned Store ──

@dataclass
class VersionRecord:
    """A single version record pointing to a snapshot."""
    version: int = 1
    snapshot_id: str = ""
    timestamp: float = 0.0
    mutation_type: str = "create"  # create, update, merge, archive
    mutation_source: str = ""
    diff_summary: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "snapshot_id": self.snapshot_id,
            "timestamp": self.timestamp,
            "mutation_type": self.mutation_type,
            "mutation_source": self.mutation_source,
            "diff_summary": self.diff_summary,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> VersionRecord:
        return cls(
            version=d.get("version", 1),
            snapshot_id=d.get("snapshot_id", ""),
            timestamp=d.get("timestamp", 0),
            mutation_type=d.get("mutation_type", "create"),
            mutation_source=d.get("mutation_source", ""),
            diff_summary=d.get("diff_summary", ""),
        )


class VersionedStore:
    """
    Versioned entity store — every mutation creates a version.

    Stores:
      - snapshots/uid/v_N.json — per-version entity state
      - index/uid.json — version manifest for each entity
      - changelog.json — global mutation log
    """

    def __init__(self, base_path: str = ""):
        self.base_path = Path(base_path or "~/.venus/datalake").expanduser()
        self.snapshots_path = self.base_path / "snapshots"
        self.index_path = self.base_path / "index"
        self.changelog_path = self.base_path / "changelog.json"
        self.graph: UnifiedGraph | None = None
        self._cache: dict[str, list[VersionRecord]] = {}
        self._setup()

    def _setup(self):
        self.snapshots_path.mkdir(parents=True, exist_ok=True)
        self.index_path.mkdir(parents=True, exist_ok=True)

    def set_graph(self, graph: Any):
        self.graph = _resolve_graph(graph)

    def store(self, entity: DataLakeEntity, mutation_type: str = "create",
              mutation_source: str = "", diff_summary: str = "") -> DataLakeEntity:
        if not entity.uid:
            entity.uid = generate_id(entity.entity_type.value, 12)
        if not entity.snapshot_id:
            entity.snapshot_id = generate_id("snap", 8)

        # Determine version
        existing = self.get_versions(entity.uid)
        entity.version = (existing[-1].version + 1) if existing else 1
        entity.updated_at = time.time()

        # Store snapshot
        snap_dir = self.snapshots_path / entity.uid
        snap_dir.mkdir(parents=True, exist_ok=True)
        snap_file = snap_dir / f"v{entity.version}.json"
        snap_file.write_text(json.dumps(entity.to_dict(), indent=2, default=str))

        # Update version index
        version_record = VersionRecord(
            version=entity.version,
            snapshot_id=entity.snapshot_id,
            timestamp=entity.updated_at,
            mutation_type=mutation_type,
            mutation_source=mutation_source,
            diff_summary=diff_summary,
        )
        self._add_version_record(entity.uid, version_record)

        # Update changelog
        self._append_changelog(entity.uid, version_record)

        # Mirror to UnifiedGraph if available
        if self.graph is not None:
            ue = entity.to_unified_entity()
            existing_entity = self.graph.get_entity(entity.uid)
            if existing_entity:
                self.graph.remove_entity(entity.uid)
            self.graph.add_entity(ue)

        return entity

    def get(self, uid: str, version: int | None = None) -> DataLakeEntity | None:
        if version is not None:
            snap_file = self.snapshots_path / uid / f"v{version}.json"
            if not snap_file.exists():
                return None
            return DataLakeEntity.from_dict(json.loads(snap_file.read_text()))
        return self.get_latest(uid)

    def get_latest(self, uid: str) -> DataLakeEntity | None:
        versions = self.get_versions(uid)
        if not versions:
            return None
        latest = versions[-1]
        return self.get(uid, latest.version)

    def get_versions(self, uid: str) -> list[VersionRecord]:
        if uid in self._cache:
            return self._cache[uid]
        idx_file = self.index_path / f"{uid}.json"
        if not idx_file.exists():
            return []
        data = json.loads(idx_file.read_text())
        records = [VersionRecord.from_dict(r) for r in data.get("versions", [])]
        self._cache[uid] = records
        return records

    def list_entities(self) -> list[dict[str, Any]]:
        result = []
        for idx_file in sorted(self.index_path.iterdir()):
            if idx_file.suffix == ".json":
                data = json.loads(idx_file.read_text())
                records = data.get("versions", [])
                if records:
                    latest = records[-1]
                    result.append({
                        "uid": idx_file.stem,
                        "version_count": len(records),
                        "latest_version": latest.get("version", 0),
                        "last_updated": latest.get("timestamp", 0),
                    })
        return sorted(result, key=lambda x: x["last_updated"], reverse=True)

    def delete(self, uid: str):
        """Archive an entity (soft delete)."""
        entity = self.get_latest(uid)
        if entity:
            self.store(entity, mutation_type="archive", mutation_source="system",
                       diff_summary="Entity archived")

    def query(self, entity_type: EntityType | None = None,
              name_contains: str = "", tag: str = "",
              min_confidence: float = 0.0, limit: int = 100) -> list[DataLakeEntity]:
        results: list[DataLakeEntity] = []
        for idx_file in sorted(self.index_path.iterdir()):
            if idx_file.suffix != ".json":
                continue
            if len(results) >= limit:
                break
            uid = idx_file.stem
            entity = self.get_latest(uid)
            if not entity:
                continue
            if entity_type and entity.entity_type != entity_type:
                continue
            if name_contains and name_contains.lower() not in entity.name.lower():
                continue
            if tag and tag not in entity.tags:
                continue
            if entity.confidence < min_confidence:
                continue
            results.append(entity)
        return results

    def count(self) -> int:
        return len(list(self.index_path.iterdir()))

    def summary(self) -> dict[str, Any]:
        entity_count = self.count()
        total_versions = 0
        changelog = self._read_changelog()
        return {
            "entity_count": entity_count,
            "total_versions": len(changelog),
            "avg_versions_per_entity": round(len(changelog) / max(entity_count, 1), 2),
            "latest_entities": self.list_entities()[:10],
        }

    def _add_version_record(self, uid: str, record: VersionRecord):
        self._cache.pop(uid, None)
        idx_file = self.index_path / f"{uid}.json"
        existing = {"uid": uid, "versions": []}
        if idx_file.exists():
            existing = json.loads(idx_file.read_text())
        existing["versions"].append(record.to_dict())
        idx_file.write_text(json.dumps(existing, indent=2, default=str))

    def _append_changelog(self, uid: str, record: VersionRecord):
        changelog = self._read_changelog()
        changelog.append({
            "uid": uid,
            "version": record.version,
            "snapshot_id": record.snapshot_id,
            "timestamp": record.timestamp,
            "mutation_type": record.mutation_type,
            "mutation_source": record.mutation_source,
        })
        self.changelog_path.write_text(json.dumps(changelog, indent=2, default=str))

    def _read_changelog(self) -> list[dict[str, Any]]:
        if self.changelog_path.exists():
            return json.loads(self.changelog_path.read_text())
        return []


# ── Data Lake Query ──

class DataLakeQuery:
    """Fluent query builder for the Engineering Data Lake."""

    def __init__(self, store: VersionedStore):
        self._store = store
        self._entity_type: EntityType | None = None
        self._name_contains: str = ""
        self._tag: str = ""
        self._min_confidence: float = 0.0
        self._limit: int = 100
        self._version: int | None = None
        self._uid: str = ""

    def of_type(self, entity_type: EntityType) -> DataLakeQuery:
        self._entity_type = entity_type
        return self

    def named(self, name_contains: str) -> DataLakeQuery:
        self._name_contains = name_contains
        return self

    def with_tag(self, tag: str) -> DataLakeQuery:
        self._tag = tag
        return self

    def with_confidence(self, min_conf: float) -> DataLakeQuery:
        self._min_confidence = min_conf
        return self

    def limit(self, n: int) -> DataLakeQuery:
        self._limit = n
        return self

    def at_version(self, version: int) -> DataLakeQuery:
        self._version = version
        return self

    def with_uid(self, uid: str) -> DataLakeQuery:
        self._uid = uid
        return self

    def execute(self) -> list[DataLakeEntity]:
        if self._uid:
            entity = self._store.get(self._uid, self._version)
            return [entity] if entity else []
        return self._store.query(
            entity_type=self._entity_type,
            name_contains=self._name_contains,
            tag=self._tag,
            min_confidence=self._min_confidence,
            limit=self._limit,
        )

    def first(self) -> DataLakeEntity | None:
        results = self.execute()
        return results[0] if results else None

    def count(self) -> int:
        return len(self.execute())

    def exists(self) -> bool:
        return self.first() is not None

    def history(self, uid: str) -> list[VersionRecord]:
        return self._store.get_versions(uid)

    def diff(self, uid: str, v1: int, v2: int) -> dict[str, Any]:
        e1 = self._store.get(uid, v1)
        e2 = self._store.get(uid, v2)
        if not e1 or not e2:
            return {"error": "Version not found"}
        changes: dict[str, Any] = {}
        for key in ["name", "description", "source", "confidence", "entity_type"]:
            v1_val = getattr(e1, key)
            v2_val = getattr(e2, key)
            if v1_val != v2_val:
                changes[key] = {"from": str(v1_val), "to": str(v2_val)}
        if e1.attributes != e2.attributes:
            changes["attributes"] = {
                "added": list(set(e2.attributes.keys()) - set(e1.attributes.keys())),
                "removed": list(set(e1.attributes.keys()) - set(e2.attributes.keys())),
                "changed": {
                    k: {"from": e1.attributes[k], "to": e2.attributes[k]}
                    for k in e1.attributes if k in e2.attributes and e1.attributes[k] != e2.attributes[k]
                },
            }
        if e1.tags != e2.tags:
            changes["tags"] = {"from": e1.tags, "to": e2.tags}
        return changes

    def timeline(self, uid: str) -> list[dict[str, Any]]:
        records = self._store.get_versions(uid)
        result = []
        for r in records:
            entity = self._store.get(uid, r.version)
            result.append({
                "version": r.version,
                "snapshot_id": r.snapshot_id,
                "timestamp": r.timestamp,
                "mutation_type": r.mutation_type,
                "mutation_source": r.mutation_source,
                "entity_name": entity.name if entity else "",
            })
        return result


# ── Data Lake Manager ──

class DataLakeManager:
    """
    Top-level manager for the Engineering Data Lake.

    Integrates with:
      - VersionedStore (persistence)
      - UnifiedGraph (runtime mirror)
      - Acquisition pipeline (ingestion)
    """

    def __init__(self, base_path: str = "", graph: Any = None):
        self.store = VersionedStore(base_path=base_path)
        if graph is not None:
            self.store.set_graph(graph)
        self.query = DataLakeQuery(self.store)
        self._ingestion_hooks: list[Callable] = []

    def ingest(self, entity: DataLakeEntity | UnifiedEntity, source: str = "",
               diff_summary: str = "") -> DataLakeEntity:
        if isinstance(entity, UnifiedEntity):
            dle = DataLakeEntity.from_unified_entity(entity)
        else:
            dle = entity
        result = self.store.store(dle, mutation_type="create" if dle.version == 1 else "update",
                                  mutation_source=source, diff_summary=diff_summary)
        for hook in self._ingestion_hooks:
            hook(result)
        return result

    def ingest_many(self, entities: list[DataLakeEntity | UnifiedEntity],
                    source: str = "") -> list[DataLakeEntity]:
        return [self.ingest(e, source=source) for e in entities]

    def register_ingestion_hook(self, hook: Callable):
        self._ingestion_hooks.append(hook)

    def get_latest(self, uid: str) -> DataLakeEntity | None:
        return self.store.get_latest(uid)

    def get_at_version(self, uid: str, version: int) -> DataLakeEntity | None:
        return self.store.get(uid, version)

    def summary(self) -> dict[str, Any]:
        return self.store.summary()
