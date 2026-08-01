"""
BrainEntity — The universal entity in the Engineering Brain.

Every entity in the platform is represented as a BrainEntity with:
  identity, history, relationships, confidence, lineage, capabilities,
  evidence, runtime_state, research_state, and 5 embedding vectors.

This is the canonical representation. All subsystems compile into this.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class BrainEntityType(str, Enum):
    """All known entity types across the platform."""
    UNKNOWN = "unknown"
    # ——— Platform ———
    SERVICE = "service"
    COMPONENT = "component"
    PLUGIN = "plugin"
    CAPABILITY = "capability"
    POLICY = "policy"
    CONFIGURATION = "configuration"
    # ——— Code ———
    MODULE = "module"
    PACKAGE = "package"
    CLASS = "class"
    FUNCTION = "function"
    INTERFACE = "interface"
    METHOD = "method"
    VARIABLE = "variable"
    # ——— Knowledge ———
    KNOWLEDGE_NODE = "knowledge_node"
    FINDING = "finding"
    PAPER = "paper"
    REVIEW = "review"
    DEBATE = "debate"
    CITATION = "citation"
    DATASET = "dataset"
    EXPERIMENT = "experiment"
    # ——— Civilization ———
    AGENT = "agent"
    RESEARCHER = "researcher"
    DEPARTMENT = "department"
    PROJECT = "project"
    INSTITUTION = "institution"
    # ——— Runtime ———
    TASK = "task"
    JOB = "job"
    PROCESS = "process"
    WORKFLOW = "workflow"
    WATCHER = "watcher"
    CHECKPOINT = "checkpoint"
    # —── Digital Twin ———
    TWIN_NODE = "twin_node"
    ARCHITECTURE = "architecture"
    GENOME = "genome"
    CHROMOSOME = "chromosome"
    GENE = "gene"
    # ——— Persistence ———
    ARTIFACT = "artifact"
    METADATA_RECORD = "metadata_record"
    MEMORY_ENTRY = "memory_entry"
    # ——— Repository ———
    REPOSITORY = "repository"
    ORGANIZATION = "organization"
    TEAM = "team"
    DEVELOPER = "developer"
    LANGUAGE = "language"
    FRAMEWORK = "framework"
    STANDARD = "standard"
    PROTOCOL = "protocol"
    LIBRARY = "library"
    DATABASE = "database"
    CLOUD_PROVIDER = "cloud_provider"
    SECURITY_MODEL = "security_model"
    DEPLOYMENT_TOPOLOGY = "deployment_topology"
    # ——— Evolution ———
    VERSION = "version"
    COMMIT = "commit"
    RELEASE = "release"
    MIGRATION = "migration"
    REFACTORING = "refactoring"
    SECURITY_ADVISORY = "security_advisory"

    @classmethod
    def has_value(cls, value: str) -> bool:
        return any(value == e.value for e in cls)


@dataclass
class Relationship:
    """A typed edge between two BrainEntities in the Engineering Brain."""
    target_id: str = ""
    relation: str = "references"
    weight: float = 1.0
    label: str = ""
    created_at: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.created_at:
            self.created_at = time.time()

    def to_dict(self) -> dict[str, Any]:
        return {
            "target_id": self.target_id,
            "relation": self.relation,
            "weight": self.weight,
            "label": self.label,
            "created_at": self.created_at,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> Relationship:
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


@dataclass
class ChangeRecord:
    """A single change in the entity's history."""
    timestamp: float = 0.0
    field: str = ""
    old_value: Any = None
    new_value: Any = None
    reason: str = ""
    actor: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "field": self.field,
            "old_value": str(self.old_value) if self.old_value is not None else None,
            "new_value": str(self.new_value) if self.new_value is not None else None,
            "reason": self.reason,
            "actor": self.actor,
        }


@dataclass
class Confidence:
    """Confidence score with full breakdown."""
    overall: float = 1.0
    syntactic: float = 1.0
    semantic: float = 1.0
    structural: float = 1.0
    empirical: float = 0.0
    consensus: float = 0.0

    def to_dict(self) -> dict[str, float]:
        return {
            "overall": self.overall,
            "syntactic": self.syntactic,
            "semantic": self.semantic,
            "structural": self.structural,
            "empirical": self.empirical,
            "consensus": self.consensus,
        }

    @classmethod
    def from_dict(cls, d: dict[str, float]) -> Confidence:
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


@dataclass
class Lineage:
    """Derivation tracking for an entity."""
    parent_id: str = ""
    relation: str = ""
    evidence: str = ""
    derivation_path: list[str] = field(default_factory=list)
    confidence_inherited: float = 1.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "parent_id": self.parent_id,
            "relation": self.relation,
            "evidence": self.evidence,
            "derivation_path": list(self.derivation_path),
            "confidence_inherited": self.confidence_inherited,
        }


@dataclass
class Capability:
    """A capability this entity provides or consumes."""
    name: str = ""
    interface: str = ""
    inputs: list[str] = field(default_factory=list)
    outputs: list[str] = field(default_factory=list)
    quality: float = 1.0
    available: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "interface": self.interface,
            "inputs": list(self.inputs),
            "outputs": list(self.outputs),
            "quality": self.quality,
            "available": self.available,
        }


@dataclass
class Evidence:
    """Provenance evidence for an entity's existence."""
    source_system: str = ""
    source_file: str = ""
    source_line: int = 0
    extractor: str = ""
    confidence: float = 1.0
    raw_data: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_system": self.source_system,
            "source_file": self.source_file,
            "source_line": self.source_line,
            "extractor": self.extractor,
            "confidence": self.confidence,
        }


@dataclass
class RuntimeState:
    """Runtime status of an entity."""
    status: str = "unknown"
    last_seen: float = 0.0
    health: str = "unknown"
    uptime: float = 0.0
    resource_usage: dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "last_seen": self.last_seen,
            "health": self.health,
            "uptime": self.uptime,
            "resource_usage": dict(self.resource_usage),
        }


@dataclass
class ResearchState:
    """Research-related state for knowledge entities."""
    findings_count: int = 0
    papers_count: int = 0
    reviews_count: int = 0
    citations_count: int = 0
    average_confidence: float = 0.0
    last_research_cycle: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "findings_count": self.findings_count,
            "papers_count": self.papers_count,
            "reviews_count": self.reviews_count,
            "citations_count": self.citations_count,
            "average_confidence": self.average_confidence,
            "last_research_cycle": self.last_research_cycle,
        }


@dataclass
class EntityEmbedding:
    """A single embedding vector for an entity."""
    vector: list[float] = field(default_factory=list)
    dimension: int = 0
    model: str = ""
    created_at: float = 0.0

    def __post_init__(self):
        if not self.created_at:
            self.created_at = time.time()
        if self.vector and not self.dimension:
            self.dimension = len(self.vector)

    def to_dict(self) -> dict[str, Any]:
        return {
            "vector": self.vector[:16] if len(self.vector) > 16 else self.vector,
            "dimension": self.dimension,
            "model": self.model,
            "created_at": self.created_at,
        }


@dataclass
class BrainEntity:
    """
    The universal entity in the Engineering Brain.

    Every subsystem compiles its entities into BrainEntity.
    BrainEntity is the single source of truth for all entity data.
    """

    # ——— Identity ———
    brain_id: str = ""
    entity_type: str = "unknown"
    label: str = ""
    description: str = ""
    source_system: str = ""
    source_id: str = ""

    # ——— History ———
    created_at: float = 0.0
    updated_at: float = 0.0
    version: int = 1
    change_log: list[ChangeRecord] = field(default_factory=list)

    # ——— Relationships ———
    relationships: list[Relationship] = field(default_factory=list)

    # ——— Confidence ———
    confidence: Confidence = field(default_factory=Confidence)

    # ——— Lineage ———
    lineage: Lineage = field(default_factory=Lineage)

    # ——— Capabilities ———
    capabilities: list[Capability] = field(default_factory=list)

    # ——— Evidence ———
    evidence: Evidence = field(default_factory=Evidence)

    # ——— Runtime State ———
    runtime_state: RuntimeState = field(default_factory=RuntimeState)

    # ——— Research State ———
    research_state: ResearchState = field(default_factory=ResearchState)

    # ——— 5 Embedding Vectors ———
    semantic_embedding: EntityEmbedding = field(default_factory=EntityEmbedding)
    knowledge_embedding: EntityEmbedding = field(default_factory=EntityEmbedding)
    structural_embedding: EntityEmbedding = field(default_factory=EntityEmbedding)
    behavioral_embedding: EntityEmbedding = field(default_factory=EntityEmbedding)
    evolution_embedding: EntityEmbedding = field(default_factory=EntityEmbedding)

    # ——— Extensible attributes ———
    attributes: dict[str, Any] = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)

    def __post_init__(self):
        now = time.time()
        if not self.created_at:
            self.created_at = now
        if not self.updated_at:
            self.updated_at = now

    # ——— Identity ———

    @property
    def type_label(self) -> str:
        return f"{self.entity_type}:{self.label or self.brain_id}"

    # ——— Relationship management ———

    def add_relationship(self, target_id: str, relation: str = "references",
                         weight: float = 1.0, label: str = "", **metadata) -> Relationship:
        rel = Relationship(
            target_id=target_id, relation=relation,
            weight=weight, label=label, metadata=metadata,
        )
        self.relationships.append(rel)
        return rel

    def find_relationships(self, relation: str | None = None,
                           target_id: str | None = None) -> list[Relationship]:
        results = []
        for r in self.relationships:
            if relation and r.relation != relation:
                continue
            if target_id and r.target_id != target_id:
                continue
            results.append(r)
        return results

    # ——— History management ———

    def record_change(self, field: str, old_value: Any, new_value: Any,
                      reason: str = "", actor: str = "") -> ChangeRecord:
        record = ChangeRecord(
            timestamp=time.time(), field=field,
            old_value=old_value, new_value=new_value,
            reason=reason, actor=actor,
        )
        self.change_log.append(record)
        self.version += 1
        self.updated_at = time.time()
        return record

    # ——— Embedding management ———

    def set_embedding(self, kind: str, vector: list[float],
                      model: str = "") -> None:
        emb = EntityEmbedding(vector=vector, model=model)
        if kind == "semantic":
            self.semantic_embedding = emb
        elif kind == "knowledge":
            self.knowledge_embedding = emb
        elif kind == "structural":
            self.structural_embedding = emb
        elif kind == "behavioral":
            self.behavioral_embedding = emb
        elif kind == "evolution":
            self.evolution_embedding = emb

    def get_embedding(self, kind: str) -> EntityEmbedding | None:
        return {
            "semantic": self.semantic_embedding,
            "knowledge": self.knowledge_embedding,
            "structural": self.structural_embedding,
            "behavioral": self.behavioral_embedding,
            "evolution": self.evolution_embedding,
        }.get(kind)

    def has_embedding(self, kind: str) -> bool:
        emb = self.get_embedding(kind)
        return emb is not None and len(emb.vector) > 0

    # ——— Serialization ———

    def to_dict(self) -> dict[str, Any]:
        return {
            "brain_id": self.brain_id,
            "entity_type": self.entity_type,
            "label": self.label,
            "description": self.description,
            "source_system": self.source_system,
            "source_id": self.source_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "version": self.version,
            "change_log": [c.to_dict() for c in self.change_log[-10:]],
            "relationships": [r.to_dict() for r in self.relationships],
            "confidence": self.confidence.to_dict(),
            "lineage": self.lineage.to_dict(),
            "capabilities": [c.to_dict() for c in self.capabilities],
            "evidence": self.evidence.to_dict(),
            "runtime_state": self.runtime_state.to_dict(),
            "research_state": self.research_state.to_dict(),
            "has_semantic_embedding": self.has_embedding("semantic"),
            "has_knowledge_embedding": self.has_embedding("knowledge"),
            "has_structural_embedding": self.has_embedding("structural"),
            "has_behavioral_embedding": self.has_embedding("behavioral"),
            "has_evolution_embedding": self.has_embedding("evolution"),
            "attributes": dict(self.attributes),
            "tags": list(self.tags),
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> BrainEntity:
        e = cls(
            brain_id=d.get("brain_id", ""),
            entity_type=d.get("entity_type", "unknown"),
            label=d.get("label", ""),
            description=d.get("description", ""),
            source_system=d.get("source_system", ""),
            source_id=d.get("source_id", ""),
            created_at=d.get("created_at", 0.0),
            updated_at=d.get("updated_at", 0.0),
            version=d.get("version", 1),
            attributes=dict(d.get("attributes", {})),
            tags=list(d.get("tags", [])),
        )
        for r in d.get("relationships", []):
            e.relationships.append(Relationship.from_dict(r))
        conf = d.get("confidence", {})
        if isinstance(conf, dict):
            e.confidence = Confidence.from_dict(conf)
        lin = d.get("lineage", {})
        if isinstance(lin, dict):
            e.lineage = Lineage(**{k: v for k, v in lin.items() if k in Lineage.__dataclass_fields__})
        for c in d.get("capabilities", []):
            if isinstance(c, dict):
                e.capabilities.append(Capability(**{k: v for k, v in c.items() if k in Capability.__dataclass_fields__}))
        ev = d.get("evidence", {})
        if isinstance(ev, dict):
            e.evidence = Evidence(**{k: v for k, v in ev.items() if k in Evidence.__dataclass_fields__})
        rs = d.get("runtime_state", {})
        if isinstance(rs, dict):
            e.runtime_state = RuntimeState(**{k: v for k, v in rs.items() if k in RuntimeState.__dataclass_fields__})
        res = d.get("research_state", {})
        if isinstance(res, dict):
            e.research_state = ResearchState(**{k: v for k, v in res.items() if k in ResearchState.__dataclass_fields__})
        return e

    def __hash__(self):
        return hash(self.brain_id)

    def __repr__(self) -> str:
        return f"<BrainEntity:{self.entity_type}:{self.label or self.brain_id}>"
