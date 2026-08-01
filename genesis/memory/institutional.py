"""
EngineeringMemory Evolution (Mission 23) — Connected Institutional Knowledge.

Extends EngineeringMemory with:
- KnowledgeObject: typed, versioned, evidence-backed knowledge units
- KnowledgeRelations: causal, dependency, supersession, derivation links
- TimelineQueries: temporal reconstruction, lineage, impact analysis
- SemanticSearch: cross-session knowledge retrieval with scoring
"""

from __future__ import annotations

import time
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from threading import RLock
from typing import Any, Callable

from genesis.memory.engineering import EngineeringMemory
from genesis.memory_system import MemoryType
from genesis.utils.identity import generate_id


class KnowledgeType(Enum):
    ARCHITECTURE = "architecture"
    SUBSYSTEM = "subsystem"
    CAPABILITY = "capability"
    REPORT = "report"
    EVIDENCE = "evidence"
    EXPERIMENT = "experiment"
    BENCHMARK = "benchmark"
    DECISION = "decision"
    MIGRATION_PLAN = "migration_plan"
    GOVERNANCE_FINDING = "governance_finding"
    API_HISTORY = "api_history"
    VERSION_HISTORY = "version_history"
    REPOSITORY_TIMELINE = "repository_timeline"
    ARCHITECTURAL_EVOLUTION = "architectural_evolution"
    TECHNICAL_DEBT = "technical_debt"
    PERFORMANCE_HISTORY = "performance_history"
    GOAL = "goal"
    RISK = "risk"
    PROOF = "proof"
    SIMULATION = "simulation"


class RelationType(Enum):
    DEPENDS_ON = "depends_on"
    CAUSES = "causes"
    SUPERSEDES = "supersedes"
    DERIVED_FROM = "derived_from"
    VALIDATED_BY = "validated_by"
    IMPLEMENTED_BY = "implemented_by"
    MENTIONED_IN = "mentioned_in"
    USED_BY = "used_by"
    DEPRECATED_BY = "deprecated_by"
    RELATED_TO = "related_to"
    EVIDENCE_FOR = "evidence_for"
    CONTRADICTS = "contradicts"


@dataclass
class KnowledgeObject:
    id: str = ""
    knowledge_type: KnowledgeType = KnowledgeType.ARCHITECTURE
    name: str = ""
    version: str = "1.0.0"
    confidence: float = 0.5
    content: str = ""
    tags: list[str] = field(default_factory=list)
    source: str = ""
    evidence: list[str] = field(default_factory=list)
    superseded_by: str = ""
    derived_from: str = ""
    validated_by: list[str] = field(default_factory=list)
    implemented_by: list[str] = field(default_factory=list)
    created_at: float = 0.0
    updated_at: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.id:
            self.id = generate_id("ko", 14)
        now = time.time()
        if not self.created_at:
            self.created_at = now
        if not self.updated_at:
            self.updated_at = now


@dataclass
class KnowledgeRelation:
    id: str = ""
    source_id: str = ""
    target_id: str = ""
    relation_type: RelationType = RelationType.RELATED_TO
    weight: float = 1.0
    evidence: str = ""
    created_at: float = 0.0

    def __post_init__(self):
        if not self.id:
            self.id = generate_id("kr", 12)
        if not self.created_at:
            self.created_at = time.time()


@dataclass
class TimelineEntry:
    timestamp: float = 0.0
    object_id: str = ""
    event: str = ""
    detail: str = ""


@dataclass
class SearchResult:
    object: KnowledgeObject | None = None
    score: float = 0.0
    matched_terms: list[str] = field(default_factory=list)


class InstitutionalMemory:
    """Institutional knowledge system built on EngineeringMemory."""

    def __init__(self, base: EngineeringMemory | None = None):
        self._base = base or EngineeringMemory()
        self._objects: dict[str, KnowledgeObject] = {}
        self._relations: list[KnowledgeRelation] = []
        self._by_type: dict[str, list[str]] = defaultdict(list)
        self._by_tag: dict[str, list[str]] = defaultdict(list)
        self._timeline: list[TimelineEntry] = []
        self._lock = RLock()

    def store(self, obj: KnowledgeObject) -> str:
        with self._lock:
            self._objects[obj.id] = obj
            self._by_type[obj.knowledge_type.value].append(obj.id)
            for tag in obj.tags:
                self._by_tag[tag].append(obj.id)
            self._timeline.append(TimelineEntry(
                timestamp=obj.created_at, object_id=obj.id,
                event="created", detail=obj.name,
            ))
            self._base.store(
                MemoryType.ARCHITECTURAL,
                obj.id,
                content=f"[{obj.knowledge_type.value}] {obj.name}: {obj.content[:200]}",
                tags=obj.tags + [obj.knowledge_type.value],
                source=f"institutional:{obj.id}",
            )
        return obj.id

    def relate(self, source_id: str, target_id: str,
               relation_type: RelationType = RelationType.RELATED_TO,
               evidence: str = "") -> str:
        with self._lock:
            rel = KnowledgeRelation(
                source_id=source_id, target_id=target_id,
                relation_type=relation_type, evidence=evidence,
            )
            self._relations.append(rel)
            self._timeline.append(TimelineEntry(
                timestamp=rel.created_at, object_id=source_id,
                event=f"related:{relation_type.value}", detail=target_id,
            ))
        return rel.id

    def get(self, object_id: str) -> KnowledgeObject | None:
        return self._objects.get(object_id)

    def get_by_type(self, ktype: KnowledgeType) -> list[KnowledgeObject]:
        return [self._objects[oid] for oid in self._by_type.get(ktype.value, [])
                if oid in self._objects]

    def get_by_tag(self, tag: str) -> list[KnowledgeObject]:
        return [self._objects[oid] for oid in self._by_tag.get(tag, [])
                if oid in self._objects]

    def get_relations(self, object_id: str) -> list[KnowledgeRelation]:
        return [r for r in self._relations
                if r.source_id == object_id or r.target_id == object_id]

    def search(self, query: str, min_score: float = 0.0) -> list[SearchResult]:
        query_lower = query.lower()
        terms = query_lower.split()
        results: list[SearchResult] = []
        with self._lock:
            for obj in self._objects.values():
                score = 0.0
                matched: list[str] = []
                text = f"{obj.name} {obj.content} {' '.join(obj.tags)}".lower()
                for term in terms:
                    if term in text:
                        score += 1.0
                        matched.append(term)
                if matched and score > 0:
                    normalized = score / max(len(terms), 1)
                    if normalized >= min_score:
                        results.append(SearchResult(object=obj, score=normalized, matched_terms=matched))
        results.sort(key=lambda r: -r.score)
        return results

    def get_impact(self, object_id: str) -> dict[str, list[KnowledgeObject]]:
        downstream: list[KnowledgeObject] = []
        upstream: list[KnowledgeObject] = []
        for rel in self._relations:
            if rel.source_id == object_id:
                tgt = self._objects.get(rel.target_id)
                if tgt:
                    downstream.append(tgt)
            if rel.target_id == object_id:
                src = self._objects.get(rel.source_id)
                if src:
                    upstream.append(src)
        return {"downstream": downstream, "upstream": upstream}

    def get_timeline(self, object_id: str | None = None) -> list[TimelineEntry]:
        if object_id:
            return [e for e in self._timeline if e.object_id == object_id]
        return list(self._timeline)

    def get_lineage(self, object_id: str) -> list[KnowledgeObject]:
        lineage: list[KnowledgeObject] = []
        visited: set[str] = set()
        current = self._objects.get(object_id)
        while current and current.id not in visited:
            visited.add(current.id)
            lineage.append(current)
            if current.derived_from:
                current = self._objects.get(current.derived_from)
            else:
                break
        return lineage

    def summary(self) -> dict[str, Any]:
        with self._lock:
            return {
                "total_objects": len(self._objects),
                "total_relations": len(self._relations),
                "by_type": {k: len(v) for k, v in self._by_type.items()},
                "timeline_entries": len(self._timeline),
            }

    def supersede(self, old_id: str, new_id: str) -> bool:
        with self._lock:
            old = self._objects.get(old_id)
            new_obj = self._objects.get(new_id)
            if not old or not new_obj:
                return False
            old.superseded_by = new_id
            new_obj.derived_from = old_id
            self.relate(old_id, new_id, RelationType.SUPERSEDES, "superseded by newer version")
            self._timeline.append(TimelineEntry(
                timestamp=time.time(), object_id=old_id,
                event="superseded", detail=new_id,
            ))
            return True
