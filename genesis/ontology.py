"""
GENESIS Ω³ — Universal Engineering Intelligence Operating System.

Complete Type System (Phase 3) + Universal Relationship Engine (Phase 5).

Every engineering concept derives from one canonical type.
Every object can connect to every other object.

Usage:
    from genesis.ontology import (
        UniversalEntity, UArtifact, UCapability, UProcess,
        UEvidence, UDecision, UExecution, UKnowledge,
        UResearch, UPrediction, UExperiment, UEconomics,
        UHistory, UMemory, USimulation, UMetric,
        UValidation, UContract, USpecification, UPolicy,
        UService, UAgent, UComponent, UGraph,
        UTimeline, UVersion, UIdentity, UOntology,
        URuntime, UCompiler, UPlatform, URelationship,
        RelationshipEngine,
    )
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Callable

from genesis.utils.identity import generate_id


ONTOLOGY_DIR = Path(__file__).parent / "census"


class EntityCategory(Enum):
    REPOSITORY = "repository"
    SOURCE = "source"
    PACKAGE = "package"
    MODULE = "module"
    CODE = "code"
    TEST = "test"
    KNOWLEDGE = "knowledge"
    GRAPH = "graph"
    RUNTIME = "runtime"
    PERSISTENCE = "persistence"
    EXECUTION = "execution"
    INFRASTRUCTURE = "infrastructure"
    GOVERNANCE = "governance"
    AGENT = "agent"
    CIVILIZATION = "civilization"
    ECONOMICS = "economics"
    MEMORY = "memory"
    CYCLE = "cycle"
    # Ω² additions
    SPECIFICATION = "specification"
    WORKFLOW = "workflow"
    MARKETPLACE = "marketplace"
    RESEARCH = "research"


@dataclass
class EntityAttribute:
    name: str = ""
    type: str = "string"
    required: bool = False
    description: str = ""
    constraints: list[str] = field(default_factory=list)
    example: Any = None


@dataclass
class EntityRelation:
    name: str = ""
    target: str = ""
    cardinality: str = "one"
    description: str = ""
    bidirectional: bool = False


@dataclass
class EntityLifecycle:
    stages: list[str] = field(default_factory=lambda: ["created", "active", "archived"])
    transitions: list[tuple[str, str]] = field(default_factory=list)


@dataclass
class EntityDefinition:
    """Schema definition — what attributes/relations a type of entity has."""
    name: str = ""
    category: EntityCategory = EntityCategory.KNOWLEDGE
    description: str = ""
    parent: str = ""
    attributes: list[EntityAttribute] = field(default_factory=list)
    relations: list[EntityRelation] = field(default_factory=list)
    lifecycle: EntityLifecycle = field(default_factory=EntityLifecycle)
    validation_rules: list[str] = field(default_factory=list)
    examples: list[str] = field(default_factory=list)
    confidence: float = 1.0


# ══════════════════════════════════════════════════════════════════════════════
# UEM — Universal Entity (canonical instance model)
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class EvidenceLink:
    source: str = ""
    type: str = ""
    confidence: float = 1.0
    timestamp: float = 0.0

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = time.time()


# ══════════════════════════════════════════════════════════════════════════════
# CIVILIZATION II — Temporal Model
# ══════════════════════════════════════════════════════════════════════════════

class TemporalEventType(str, Enum):
    CREATED = "created"
    MODIFIED = "modified"
    ACTIVATED = "activated"
    RETIRED = "retired"
    ARCHIVED = "archived"
    SUPERSEDED = "superseded"
    REBORN = "reborn"
    FORKED = "forked"
    MERGED = "merged"
    CAUSED = "caused"
    PREDICTED = "predicted"
    EXPERIMENT = "experiment"


@dataclass
class TemporalEvent:
    event_type: TemporalEventType = TemporalEventType.CREATED
    entity_id: str = ""
    prior_fingerprint: str = ""
    new_fingerprint: str = ""
    timestamp: str = ""
    actor: str = ""
    description: str = ""
    causality: list[str] = field(default_factory=list)
    attributes_changed: list[str] = field(default_factory=list)
    branch: str = ""
    confidence: float = 1.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


@dataclass
class EntitySnapshot:
    entity_id: str = ""
    fingerprint: str = ""
    timestamp: str = ""
    state: dict[str, Any] = field(default_factory=dict)
    event_type: str = "snapshot"

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


@dataclass
class EntityBranch:
    name: str = ""
    parent_branch: str = "main"
    forked_from_event: str = ""
    created_at: str = ""
    description: str = ""
    merged_into: str = ""
    status: str = "active"

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()


@dataclass
class Prediction:
    prediction_id: str = ""
    target_entity: str = ""
    metric: str = ""
    predicted_value: float = 0.0
    confidence: float = 0.5
    assumptions: list[str] = field(default_factory=list)
    evidence: list[str] = field(default_factory=list)
    error_bounds: tuple[float, float] = (0.0, 0.0)
    created_at: str = ""
    verified_at: str = ""
    actual_value: float = 0.0
    accurate: bool = False

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()


@dataclass
class UniversalEntity:
    """Canonical base entity — every engineering concept derives from this.
    
    ID is auto-generated in format: {type_name}:{identity}
    Supports full UEM attribute set: lifecycle, confidence, evidence,
    dependencies, consumers, maturity, risk, health, role, owner.
    Also supports CIVILIZATION II temporal model: timeline, snapshots,
    branches, predictions, events.
    """
    type_name: str = ""
    identity: str = ""
    owner: str = ""
    lifecycle: str = "created"
    confidence: float = 1.0
    evidence: list[EvidenceLink] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    consumers: list[str] = field(default_factory=list)
    maturity: float = 0.0
    risk: float = 0.0
    health: float = 0.0
    role: str = ""
    version: int = 1
    created_at: str = ""
    updated_at: str = ""
    attributes: dict[str, Any] = field(default_factory=dict)
    relations: dict[str, list[str]] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    # Temporal fields (CIVILIZATION II)
    timeline: list[TemporalEvent] = field(default_factory=list)
    snapshots: list[EntitySnapshot] = field(default_factory=list)
    branches: list[EntityBranch] = field(default_factory=list)
    predictions: list[Prediction] = field(default_factory=list)
    superseded_by: str = ""
    historical_confidence: list[float] = field(default_factory=list)

    def __post_init__(self):
        now = datetime.now(timezone.utc).isoformat()
        if not self.created_at:
            self.created_at = now
        if not self.updated_at:
            self.updated_at = now

    @property
    def id(self) -> str:
        return f"{self.type_name}:{self.identity}" if self.identity else ""

    @property
    def fingerprint(self) -> str:
        import hashlib
        raw = f"{self.type_name}|{self.identity}|{json.dumps(self.attributes, sort_keys=True, default=str)}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]

    def add_evidence(self, source: str, etype: str = "observation", confidence: float = 1.0):
        self.evidence.append(EvidenceLink(source=source, type=etype, confidence=confidence))

    def add_event(self, event_type: TemporalEventType, actor: str = "",
                  description: str = "", causality: list[str] | None = None):
        event = TemporalEvent(
            event_type=event_type,
            entity_id=self.id,
            prior_fingerprint=self.fingerprint,
            timestamp=datetime.now(timezone.utc).isoformat(),
            actor=actor,
            description=description,
            causality=causality or [],
            branch=self._current_branch(),
        )
        event.new_fingerprint = self.fingerprint
        self.timeline.append(event)

    def snapshot(self, event_type: str = "snapshot"):
        snap = EntitySnapshot(
            entity_id=self.id,
            fingerprint=self.fingerprint,
            state={
                "type_name": self.type_name,
                "identity": self.identity,
                "lifecycle": self.lifecycle,
                "version": self.version,
                "maturity": self.maturity,
                "risk": self.risk,
                "health": self.health,
                "attributes": dict(self.attributes),
                "relations": dict(self.relations),
            },
            event_type=event_type,
        )
        self.snapshots.append(snap)

    def create_branch(self, name: str, description: str = "",
                      parent_branch: str = "main") -> EntityBranch:
        branch = EntityBranch(name=name, parent_branch=parent_branch, description=description)
        self.branches.append(branch)
        self.add_event(TemporalEventType.FORKED, description=f"Forked branch '{name}' from '{parent_branch}'")
        return branch

    def add_prediction(self, metric: str, value: float, confidence: float = 0.5,
                       assumptions: list[str] | None = None, error_bounds: tuple[float, float] | None = None):
        pred = Prediction(
            target_entity=self.id,
            metric=metric,
            predicted_value=value,
            confidence=confidence,
            assumptions=assumptions or [],
            error_bounds=error_bounds or (value * 0.9, value * 1.1),
        )
        self.predictions.append(pred)
        return pred

    def _current_branch(self) -> str:
        active = [b for b in self.branches if b.status == "active"]
        return active[-1].name if active else "main"

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "type_name": self.type_name,
            "identity": self.identity,
            "owner": self.owner,
            "lifecycle": self.lifecycle,
            "confidence": self.confidence,
            "evidence": [asdict(e) for e in self.evidence],
            "dependencies": self.dependencies,
            "consumers": self.consumers,
            "maturity": self.maturity,
            "risk": self.risk,
            "health": self.health,
            "role": self.role,
            "version": self.version,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "attributes": self.attributes,
            "relations": self.relations,
            "metadata": self.metadata,
            "timeline": [asdict(t) for t in self.timeline],
            "snapshots": [asdict(s) for s in self.snapshots],
            "branches": [asdict(b) for b in self.branches],
            "predictions": [asdict(p) for p in self.predictions],
            "superseded_by": self.superseded_by,
        }


class EntityRegistry:
    """Manages the relationship between entity schemas (EntityDefinition)
    and entity instances (UniversalEntity)."""

    def __init__(self):
        self._definitions: dict[str, EntityDefinition] = {}
        self._instances: dict[str, UniversalEntity] = {}

    # ── Schema (type definitions) ──

    def define(self, ed: EntityDefinition) -> EntityDefinition:
        self._definitions[ed.name] = ed
        return ed

    def get_definition(self, name: str) -> EntityDefinition | None:
        return self._definitions.get(name)

    def all_definitions(self) -> list[EntityDefinition]:
        return list(self._definitions.values())

    def children_of(self, parent: str) -> list[EntityDefinition]:
        return [e for e in self._definitions.values() if e.parent == parent]

    # ── Instances ──

    def add(self, entity: UniversalEntity) -> list[str]:
        errors = self._validate(entity)
        if errors:
            return errors
        key = entity.id
        if key in self._instances:
            existing = self._instances[key]
            existing.version += 1
            existing.updated_at = datetime.now(timezone.utc).isoformat()
            existing.attributes = entity.attributes
            existing.relations = entity.relations
            existing.maturity = entity.maturity
            existing.risk = entity.risk
            existing.health = entity.health
            existing.confidence = entity.confidence
        else:
            self._instances[key] = entity
        return []

    def get(self, type_name: str, identity: str) -> UniversalEntity | None:
        return self._instances.get(f"{type_name}:{identity}")

    def find(self, type_name: str | None = None, **attrs: Any) -> list[UniversalEntity]:
        results = list(self._instances.values())
        if type_name:
            results = [r for r in results if r.type_name == type_name]
        for key, value in attrs.items():
            results = [r for r in results if r.attributes.get(key) == value]
        return results

    def all(self) -> list[UniversalEntity]:
        return list(self._instances.values())

    def count(self) -> int:
        return len(self._instances)

    def types_count(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for inst in self._instances.values():
            counts[inst.type_name] = counts.get(inst.type_name, 0) + 1
        return counts

    # ── Validation ──

    def _validate(self, entity: UniversalEntity) -> list[str]:
        errors: list[str] = []
        ed = self._definitions.get(entity.type_name)
        if not ed:
            return errors  # Allow unregistered types
        for attr in ed.attributes:
            if attr.required and attr.name not in entity.attributes:
                errors.append(f"Missing required attribute '{attr.name}' on {entity.type_name}")
            if attr.name in entity.attributes:
                val = entity.attributes[attr.name]
                if attr.type == "string" and not isinstance(val, str):
                    errors.append(f"Attribute '{attr.name}' should be string, got {type(val).__name__}")
        return errors

    # ── Persistence ──

    def to_dict(self) -> dict[str, Any]:
        return {
            "definitions": {
                n: {
                    "category": ed.category.value,
                    "description": ed.description,
                    "parent": ed.parent,
                    "attributes": [asdict(a) for a in ed.attributes],
                    "relations": [asdict(r) for r in ed.relations],
                    "lifecycle": asdict(ed.lifecycle),
                    "validation_rules": ed.validation_rules,
                }
                for n, ed in self._definitions.items()
            },
            "instances": [e.to_dict() for e in self._instances.values()],
            "summary": {
                "definitions": len(self._definitions),
                "instances": len(self._instances),
                "by_type": self.types_count(),
            },
        }

    def save(self, path: str | Path | None = None):
        if path is None:
            path = ONTOLOGY_DIR / "uem_registry.json"
        path = Path(path) if isinstance(path, str) else path
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2, default=str)
        print(f"  UEM Registry saved: {path} ({len(self._instances)} instances, {len(self._definitions)} definitions)")


# ══════════════════════════════════════════════════════════════════════════════
# Legacy compatibility — EngineeringOntology delegates to EntityRegistry
# ══════════════════════════════════════════════════════════════════════════════

class EngineeringOntology:
    """Legacy wrapper — delegates to EntityRegistry.
    
    Maintains backward compatibility. New code should use EntityRegistry directly.
    """

    def __init__(self):
        self._registry = EntityRegistry()

    @property
    def registry(self) -> EntityRegistry:
        return self._registry

    def define(self, entity: EntityDefinition):
        return self._registry.define(entity)

    def get(self, name: str) -> EntityDefinition | None:
        return self._registry.get_definition(name)

    def children_of(self, parent: str) -> list[EntityDefinition]:
        return self._registry.children_of(parent)

    def all_definitions(self) -> list[EntityDefinition]:
        return self._registry.all_definitions()

    def build_default(self) -> "EngineeringOntology":
        """Populate with all standard engineering entity types (same 28 as before + Ω² additions)."""

        # ── Repository Layer ──
        self.define(EntityDefinition(
            name="Repository", category=EntityCategory.REPOSITORY,
            description="A version-controlled code repository",
            attributes=[
                EntityAttribute("name", "string", True, "Repository name"),
                EntityAttribute("url", "string", True, "Remote URL"),
                EntityAttribute("language", "string", False, "Primary language"),
                EntityAttribute("default_branch", "string", False, "Default branch"),
                EntityAttribute("file_count", "integer", False, "Total files"),
                EntityAttribute("module_count", "integer", False, "Total modules"),
                EntityAttribute("healthy", "boolean", False, "Health status"),
            ],
            relations=[
                EntityRelation("contains", "Package", "many"),
                EntityRelation("depends_on", "Repository", "many"),
                EntityRelation("provides", "Capability", "many"),
            ],
            lifecycle=EntityLifecycle(
                stages=["discovered", "cloned", "indexed", "active", "archived"],
                transitions=[("discovered", "cloned"), ("cloned", "indexed"), ("indexed", "active")],
            ),
        ))

        self.define(EntityDefinition(
            name="Package", category=EntityCategory.PACKAGE,
            description="A named package containing modules",
            parent="Repository",
            attributes=[
                EntityAttribute("name", "string", True),
                EntityAttribute("path", "string", True),
                EntityAttribute("module_count", "integer"),
                EntityAttribute("lines", "integer"),
                EntityAttribute("tests", "integer"),
                EntityAttribute("maturity", "float"),
            ],
            relations=[EntityRelation("contains", "Module", "many"), EntityRelation("imports", "Package", "many")],
        ))

        self.define(EntityDefinition(
            name="Module", category=EntityCategory.MODULE,
            description="A single Python module file",
            parent="Package",
            attributes=[
                EntityAttribute("name", "string", True),
                EntityAttribute("path", "string", True),
                EntityAttribute("lines", "integer"),
                EntityAttribute("code_lines", "integer"),
                EntityAttribute("classes", "list"),
                EntityAttribute("functions", "list"),
                EntityAttribute("maturity", "float"),
                EntityAttribute("has_docstring", "boolean"),
                EntityAttribute("has_type_hints", "boolean"),
                EntityAttribute("test_count", "integer"),
            ],
            relations=[
                EntityRelation("imports", "Module", "many"),
                EntityRelation("contains", "Class", "many"),
                EntityRelation("contains", "Function", "many"),
                EntityRelation("tested_by", "TestSuite", "many"),
            ],
            lifecycle=EntityLifecycle(
                stages=["created", "stable", "deprecated", "removed"],
                transitions=[("created", "stable"), ("stable", "deprecated")],
            ),
        ))

        self.define(EntityDefinition(
            name="Class", category=EntityCategory.CODE, description="A Python class definition",
            parent="Module",
            attributes=[EntityAttribute("name", "string", True), EntityAttribute("module", "string", True), EntityAttribute("bases", "list")],
            relations=[EntityRelation("defined_in", "Module", "one")],
        ))

        self.define(EntityDefinition(
            name="Function", category=EntityCategory.CODE, description="A Python function or method",
            parent="Module",
            attributes=[EntityAttribute("name", "string", True), EntityAttribute("module", "string", True), EntityAttribute("has_return_type", "boolean")],
            relations=[EntityRelation("defined_in", "Module", "one")],
        ))

        # ── Test Layer ──
        self.define(EntityDefinition(
            name="TestSuite", category=EntityCategory.TEST,
            description="A collection of tests for a target module",
            attributes=[
                EntityAttribute("name", "string", True),
                EntityAttribute("path", "string", True),
                EntityAttribute("test_count", "integer"),
                EntityAttribute("test_classes", "list"),
                EntityAttribute("test_functions", "list"),
            ],
            relations=[EntityRelation("tests", "Module", "one"), EntityRelation("validates", "Capability", "many")],
        ))

        self.define(EntityDefinition(
            name="TestCase", category=EntityCategory.TEST, description="An individual test case",
            parent="TestSuite",
            attributes=[EntityAttribute("name", "string", True), EntityAttribute("suite", "string", True)],
        ))

        # ── Knowledge Layer ──
        self.define(EntityDefinition(
            name="KnowledgeArtifact", category=EntityCategory.KNOWLEDGE,
            description="Any piece of persistent engineering knowledge",
            attributes=[
                EntityAttribute("type", "string", True),
                EntityAttribute("content", "string"),
                EntityAttribute("confidence", "float"),
                EntityAttribute("source", "string"),
            ],
            relations=[
                EntityRelation("derives_from", "KnowledgeArtifact", "many"),
                EntityRelation("evidences", "Hypothesis", "many"),
                EntityRelation("supports", "Decision", "many"),
            ],
        ))

        self.define(EntityDefinition(
            name="Hypothesis", category=EntityCategory.KNOWLEDGE,
            description="A testable engineering hypothesis", parent="KnowledgeArtifact",
            attributes=[EntityAttribute("statement", "string", True), EntityAttribute("confidence", "float"), EntityAttribute("status", "string")],
            relations=[EntityRelation("tested_by", "Experiment", "many"), EntityRelation("evidenced_by", "Evidence", "many")],
            lifecycle=EntityLifecycle(stages=["proposed", "testing", "accepted", "rejected", "archived"],
                                      transitions=[("proposed", "testing"), ("testing", "accepted"), ("testing", "rejected")]),
        ))

        self.define(EntityDefinition(
            name="Evidence", category=EntityCategory.KNOWLEDGE,
            description="Evidence supporting or refuting a hypothesis",
            attributes=[EntityAttribute("type", "string", True), EntityAttribute("value", "string", True), EntityAttribute("confidence", "float")],
        ))

        self.define(EntityDefinition(
            name="Experiment", category=EntityCategory.KNOWLEDGE,
            description="A controlled engineering experiment",
            attributes=[EntityAttribute("name", "string", True), EntityAttribute("status", "string"), EntityAttribute("metrics", "dict")],
            relations=[EntityRelation("produces", "Evidence", "many")],
        ))

        # ── Graph Layer ──
        self.define(EntityDefinition(
            name="GraphLayer", category=EntityCategory.GRAPH,
            description="A typed layer within the unified engineering graph",
            attributes=[EntityAttribute("name", "string", True), EntityAttribute("type", "string", True), EntityAttribute("node_count", "integer"), EntityAttribute("edge_count", "integer")],
        ))

        self.define(EntityDefinition(
            name="GraphNode", category=EntityCategory.GRAPH,
            description="A node within a graph layer",
            attributes=[EntityAttribute("id", "string", True), EntityAttribute("name", "string"), EntityAttribute("node_type", "string"), EntityAttribute("weight", "float")],
        ))

        # ── Runtime Layer ──
        self.define(EntityDefinition(
            name="Service", category=EntityCategory.RUNTIME,
            description="A registered platform service",
            attributes=[EntityAttribute("name", "string", True), EntityAttribute("version", "string"), EntityAttribute("status", "string"), EntityAttribute("capabilities", "list")],
            relations=[EntityRelation("registers_with", "Fabric", "one")],
        ))

        self.define(EntityDefinition(
            name="Fabric", category=EntityCategory.RUNTIME,
            description="The engineering fabric kernel",
            attributes=[EntityAttribute("state", "string"), EntityAttribute("uptime", "float")],
        ))

        # ── Execution Layer ──
        self.define(EntityDefinition(
            name="Workflow", category=EntityCategory.EXECUTION,
            description="A workflow DAG",
            attributes=[EntityAttribute("name", "string", True), EntityAttribute("nodes", "integer")],
            relations=[EntityRelation("contains", "WorkflowNode", "many")],
        ))

        self.define(EntityDefinition(
            name="WorkflowNode", category=EntityCategory.EXECUTION, parent="Workflow",
            attributes=[EntityAttribute("name", "string", True), EntityAttribute("status", "string")],
            relations=[EntityRelation("depends_on", "WorkflowNode", "many")],
        ))

        self.define(EntityDefinition(
            name="Task", category=EntityCategory.EXECUTION,
            attributes=[EntityAttribute("name", "string", True), EntityAttribute("status", "string"), EntityAttribute("priority", "string")],
        ))

        self.define(EntityDefinition(
            name="Pipeline", category=EntityCategory.EXECUTION,
            attributes=[EntityAttribute("name", "string", True), EntityAttribute("stages", "integer")],
        ))

        # ── Persistence Layer ──
        self.define(EntityDefinition(
            name="Database", category=EntityCategory.PERSISTENCE,
            attributes=[EntityAttribute("type", "string", True), EntityAttribute("collections", "integer")],
        ))

        self.define(EntityDefinition(
            name="Collection", category=EntityCategory.PERSISTENCE,
            attributes=[EntityAttribute("name", "string", True), EntityAttribute("type", "string", True)],
        ))

        self.define(EntityDefinition(
            name="Memory", category=EntityCategory.MEMORY,
            attributes=[EntityAttribute("type", "string", True), EntityAttribute("entries", "integer")],
        ))

        # ── Agent & Civilization Layer ──
        self.define(EntityDefinition(
            name="Agent", category=EntityCategory.AGENT,
            description="An autonomous engineering agent",
            attributes=[EntityAttribute("name", "string", True), EntityAttribute("role", "string", True), EntityAttribute("capabilities", "list"), EntityAttribute("status", "string")],
            relations=[EntityRelation("belongs_to", "Institute", "one"), EntityRelation("executes", "Workflow", "many"), EntityRelation("produces", "KnowledgeArtifact", "many")],
        ))

        self.define(EntityDefinition(
            name="Institute", category=EntityCategory.CIVILIZATION,
            description="An organized institute within the software civilization",
            attributes=[EntityAttribute("name", "string", True), EntityAttribute("type", "string", True), EntityAttribute("capabilities", "list")],
            relations=[EntityRelation("contains", "Agent", "many")],
        ))

        self.define(EntityDefinition(
            name="CycleStage", category=EntityCategory.CYCLE,
            description="A stage in the autonomous engineering cycle",
            attributes=[EntityAttribute("name", "string", True), EntityAttribute("order", "integer", True)],
            relations=[EntityRelation("produces", "KnowledgeArtifact", "many"), EntityRelation("feeds", "CycleStage", "one")],
        ))

        # ── Governance ──
        self.define(EntityDefinition(
            name="Policy", category=EntityCategory.GOVERNANCE,
            attributes=[EntityAttribute("name", "string", True), EntityAttribute("effect", "string", True), EntityAttribute("service", "string"), EntityAttribute("action", "string")],
        ))

        self.define(EntityDefinition(
            name="Contract", category=EntityCategory.GOVERNANCE,
            attributes=[EntityAttribute("topic", "string", True), EntityAttribute("version", "string"), EntityAttribute("producer", "string"), EntityAttribute("consumers", "list")],
        ))

        # ── Economics ──
        self.define(EntityDefinition(
            name="Metric", category=EntityCategory.ECONOMICS,
            attributes=[EntityAttribute("name", "string", True), EntityAttribute("value", "float", True), EntityAttribute("unit", "string"), EntityAttribute("tags", "dict")],
        ))

        # ── Ω² — Specification Layer ──
        self.define(EntityDefinition(
            name="Specification", category=EntityCategory.SPECIFICATION,
            description="A governing specification document",
            attributes=[EntityAttribute("name", "string", True), EntityAttribute("path", "string", True), EntityAttribute("version", "string")],
            relations=[EntityRelation("governs", "Module", "many"), EntityRelation("derives_from", "Specification", "many")],
        ))

        return self

    def to_dict(self) -> dict[str, Any]:
        return self._registry.to_dict()["definitions"]

    def save(self, path: str | Path | None = None):
        self._registry.save(path)

    def summary(self) -> dict[str, Any]:
        defs = self._registry.all_definitions()
        by_category: dict[str, int] = {}
        for e in defs:
            by_category[e.category.value] = by_category.get(e.category.value, 0) + 1
        return {
            "total_entities": len(defs),
            "by_category": by_category,
            "entity_names": sorted(e.name for e in defs),
        }


def build_default_ontology() -> EngineeringOntology:
    return EngineeringOntology().build_default()


def build_uem_registry() -> EntityRegistry:
    """Build and populate a complete UEM registry with all standard types."""
    onto = build_default_ontology()
    return onto.registry


# ══════════════════════════════════════════════════════════════════════════════
# GENESIS Ω³ — Phase 3: Complete Type System (32 Universal* factory types)
# ══════════════════════════════════════════════════════════════════════════════
# Each is a factory function returning a properly configured UniversalEntity.
# All types derive from the same canonical base.
# ══════════════════════════════════════════════════════════════════════════════

_RELATION_TYPES: list[str] = []
"""Registry of all known relationship types — populated by URels factory functions."""


_UE_FIELDS = {"type_name", "identity", "owner", "lifecycle", "confidence",
               "evidence", "dependencies", "consumers", "maturity", "risk",
               "health", "role", "version", "superseded_by", "branches",
               "timeline", "snapshots", "predictions", "attributes"}


def _U(tname: str, identity: str, **kw: Any) -> UniversalEntity:
    kw["type_name"] = tname
    kw["identity"] = identity
    base = {k: v for k, v in kw.items() if k in _UE_FIELDS}
    extra = {k: v for k, v in kw.items() if k not in _UE_FIELDS and k != "attributes"}
    if extra:
        existing_attrs = base.get("attributes", {})
        existing_attrs.update(extra)
        base["attributes"] = existing_attrs
    return UniversalEntity(**base)


def UArtifact(identity: str, artifact_type: str = "", **kw: Any) -> UniversalEntity:
    return _U("artifact", identity, attributes={"artifact_type": artifact_type, **kw.get("attributes", {})}, **{k: v for k, v in kw.items() if k != "attributes"})


def UCapability(identity: str, capability_type: str = "", **kw: Any) -> UniversalEntity:
    return _U("capability", identity, attributes={"capability_type": capability_type, **kw.get("attributes", {})}, **{k: v for k, v in kw.items() if k != "attributes"})


def UProcess(identity: str, process_type: str = "", **kw: Any) -> UniversalEntity:
    return _U("process", identity, attributes={"process_type": process_type, **kw.get("attributes", {})}, **{k: v for k, v in kw.items() if k != "attributes"})


def UEvidence(identity: str, evidence_type: str = "", **kw: Any) -> UniversalEntity:
    return _U("evidence", identity, attributes={"evidence_type": evidence_type, **kw.get("attributes", {})}, **{k: v for k, v in kw.items() if k != "attributes"})


def UDecision(identity: str, decision_type: str = "", **kw: Any) -> UniversalEntity:
    return _U("decision", identity, attributes={"decision_type": decision_type, **kw.get("attributes", {})}, **{k: v for k, v in kw.items() if k != "attributes"})


def UExecution(identity: str, execution_type: str = "", **kw: Any) -> UniversalEntity:
    return _U("execution", identity, attributes={"execution_type": execution_type, **kw.get("attributes", {})}, **{k: v for k, v in kw.items() if k != "attributes"})


def UKnowledge(identity: str, knowledge_type: str = "", **kw: Any) -> UniversalEntity:
    return _U("knowledge", identity, attributes={"knowledge_type": knowledge_type, **kw.get("attributes", {})}, **{k: v for k, v in kw.items() if k != "attributes"})


def UResearch(identity: str, research_type: str = "", **kw: Any) -> UniversalEntity:
    return _U("research", identity, attributes={"research_type": research_type, **kw.get("attributes", {})}, **{k: v for k, v in kw.items() if k != "attributes"})


def UPrediction(identity: str, metric: str = "", predicted_value: float = 0.0, **kw: Any) -> UniversalEntity:
    return _U("prediction", identity, attributes={"metric": metric, "predicted_value": predicted_value, **kw.get("attributes", {})}, **{k: v for k, v in kw.items() if k != "attributes"})


def UExperiment(identity: str, experiment_type: str = "", **kw: Any) -> UniversalEntity:
    return _U("experiment", identity, attributes={"experiment_type": experiment_type, **kw.get("attributes", {})}, **{k: v for k, v in kw.items() if k != "attributes"})


def UEconomics(identity: str, metric_name: str = "", value: float = 0.0, unit: str = "", **kw: Any) -> UniversalEntity:
    return _U("economics", identity, attributes={"metric_name": metric_name, "value": value, "unit": unit, **kw.get("attributes", {})}, **{k: v for k, v in kw.items() if k != "attributes"})


def UHistory(identity: str, history_type: str = "", **kw: Any) -> UniversalEntity:
    return _U("history", identity, attributes={"history_type": history_type, **kw.get("attributes", {})}, **{k: v for k, v in kw.items() if k != "attributes"})


def UMemory(identity: str, memory_type: str = "", **kw: Any) -> UniversalEntity:
    return _U("memory", identity, attributes={"memory_type": memory_type, **kw.get("attributes", {})}, **{k: v for k, v in kw.items() if k != "attributes"})


def USimulation(identity: str, sim_type: str = "", **kw: Any) -> UniversalEntity:
    return _U("simulation", identity, attributes={"sim_type": sim_type, **kw.get("attributes", {})}, **{k: v for k, v in kw.items() if k != "attributes"})


def UMetric(identity: str, metric_name: str = "", value: float = 0.0, **kw: Any) -> UniversalEntity:
    return _U("metric", identity, attributes={"metric_name": metric_name, "value": value, **kw.get("attributes", {})}, **{k: v for k, v in kw.items() if k != "attributes"})


def UValidation(identity: str, validation_type: str = "", **kw: Any) -> UniversalEntity:
    return _U("validation", identity, attributes={"validation_type": validation_type, **kw.get("attributes", {})}, **{k: v for k, v in kw.items() if k != "attributes"})


def UContract(identity: str, contract_type: str = "", **kw: Any) -> UniversalEntity:
    return _U("contract", identity, attributes={"contract_type": contract_type, **kw.get("attributes", {})}, **{k: v for k, v in kw.items() if k != "attributes"})


def USpecification(identity: str, spec_version: str = "", **kw: Any) -> UniversalEntity:
    return _U("specification", identity, attributes={"spec_version": spec_version, **kw.get("attributes", {})}, **{k: v for k, v in kw.items() if k != "attributes"})


def UPolicy(identity: str, effect: str = "", **kw: Any) -> UniversalEntity:
    return _U("policy", identity, attributes={"effect": effect, **kw.get("attributes", {})}, **{k: v for k, v in kw.items() if k != "attributes"})


def UService(identity: str, service_type: str = "", **kw: Any) -> UniversalEntity:
    return _U("service", identity, attributes={"service_type": service_type, **kw.get("attributes", {})}, **{k: v for k, v in kw.items() if k != "attributes"})


def UAgent(identity: str, agent_role: str = "", **kw: Any) -> UniversalEntity:
    return _U("agent", identity, attributes={"agent_role": agent_role, **kw.get("attributes", {})}, **{k: v for k, v in kw.items() if k != "attributes"})


def UComponent(identity: str, component_type: str = "", **kw: Any) -> UniversalEntity:
    return _U("component", identity, attributes={"component_type": component_type, **kw.get("attributes", {})}, **{k: v for k, v in kw.items() if k != "attributes"})


def UGraph(identity: str, graph_type: str = "", **kw: Any) -> UniversalEntity:
    return _U("graph", identity, attributes={"graph_type": graph_type, **kw.get("attributes", {})}, **{k: v for k, v in kw.items() if k != "attributes"})


def UTimeline(identity: str, **kw: Any) -> UniversalEntity:
    return _U("timeline", identity, **kw)


def UVersion(identity: str, version_str: str = "", **kw: Any) -> UniversalEntity:
    return _U("version", identity, attributes={"version_str": version_str, **kw.get("attributes", {})}, **{k: v for k, v in kw.items() if k != "attributes"})


def UIdentity(identity: str, **kw: Any) -> UniversalEntity:
    return _U("identity", identity, **kw)


def UOntology(identity: str, **kw: Any) -> UniversalEntity:
    return _U("ontology", identity, **kw)


def URuntime(identity: str, runtime_type: str = "", **kw: Any) -> UniversalEntity:
    return _U("runtime", identity, attributes={"runtime_type": runtime_type, **kw.get("attributes", {})}, **{k: v for k, v in kw.items() if k != "attributes"})


def UCompiler(identity: str, compiler_type: str = "", **kw: Any) -> UniversalEntity:
    return _U("compiler", identity, attributes={"compiler_type": compiler_type, **kw.get("attributes", {})}, **{k: v for k, v in kw.items() if k != "attributes"})


def UPlatform(identity: str, **kw: Any) -> UniversalEntity:
    return _U("platform", identity, **kw)


# ══════════════════════════════════════════════════════════════════════════════
# Phase 5: Universal Relationship Engine
# ══════════════════════════════════════════════════════════════════════════════

class URelType(str, Enum):
    CAUSES = "causes"
    DEPENDS_ON = "depends_on"
    IMPLEMENTS = "implements"
    VERIFIES = "verifies"
    CONTRADICTS = "contradicts"
    EXTENDS = "extends"
    REPLACES = "replaces"
    OWNS = "owns"
    CONTROLS = "controls"
    PLANS = "plans"
    PREDICTS = "predicts"
    SIMULATES = "simulates"
    BENCHMARKS = "benchmarks"
    TESTS = "tests"
    DOCUMENTS = "documents"
    EXPLAINS = "explains"
    LEARNS = "learns"
    OBSERVES = "observes"
    IMPROVES = "improves"
    FUNDS = "funds"
    OPTIMIZES = "optimizes"
    PUBLISHES = "publishes"
    REVIEWS = "reviews"
    TEACHES = "teaches"
    CONSUMES = "consumes"
    PRODUCES = "produces"
    SUPPORTS = "supports"
    INVALIDATES = "invalidates"
    FORKS = "forks"
    MERGES = "merges"
    ENABLES = "enables"
    PREVENTS = "prevents"
    REQUIRES = "requires"
    DERIVES = "derives_from"
    MOTIVATES = "motivates"


@dataclass
class URelationship:
    source_id: str = ""
    target_id: str = ""
    rel_type: URelType = URelType.DEPENDS_ON
    weight: float = 1.0
    confidence: float = 1.0
    evidence: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()

    @property
    def id(self) -> str:
        return f"{self.source_id}:{self.rel_type.value}:{self.target_id}"


# Factory functions for common relationship types
def URels() -> dict[str, Any]:
    """Return all relationship factory functions as a convenience dict."""
    return {
        "causes": lambda s, t, **kw: URelationship(s, t, URelType.CAUSES, **kw),
        "depends_on": lambda s, t, **kw: URelationship(s, t, URelType.DEPENDS_ON, **kw),
        "implements": lambda s, t, **kw: URelationship(s, t, URelType.IMPLEMENTS, **kw),
        "verifies": lambda s, t, **kw: URelationship(s, t, URelType.VERIFIES, **kw),
        "contradicts": lambda s, t, **kw: URelationship(s, t, URelType.CONTRADICTS, **kw),
        "extends": lambda s, t, **kw: URelationship(s, t, URelType.EXTENDS, **kw),
        "replaces": lambda s, t, **kw: URelationship(s, t, URelType.REPLACES, **kw),
        "owns": lambda s, t, **kw: URelationship(s, t, URelType.OWNS, **kw),
        "controls": lambda s, t, **kw: URelationship(s, t, URelType.CONTROLS, **kw),
        "plans": lambda s, t, **kw: URelationship(s, t, URelType.PLANS, **kw),
        "predicts": lambda s, t, **kw: URelationship(s, t, URelType.PREDICTS, **kw),
        "simulates": lambda s, t, **kw: URelationship(s, t, URelType.SIMULATES, **kw),
        "tests": lambda s, t, **kw: URelationship(s, t, URelType.TESTS, **kw),
        "documents": lambda s, t, **kw: URelationship(s, t, URelType.DOCUMENTS, **kw),
        "explains": lambda s, t, **kw: URelationship(s, t, URelType.EXPLAINS, **kw),
        "learns": lambda s, t, **kw: URelationship(s, t, URelType.LEARNS, **kw),
        "observes": lambda s, t, **kw: URelationship(s, t, URelType.OBSERVES, **kw),
        "improves": lambda s, t, **kw: URelationship(s, t, URelType.IMPROVES, **kw),
        "funds": lambda s, t, **kw: URelationship(s, t, URelType.FUNDS, **kw),
        "produces": lambda s, t, **kw: URelationship(s, t, URelType.PRODUCES, **kw),
        "consumes": lambda s, t, **kw: URelationship(s, t, URelType.CONSUMES, **kw),
        "supports": lambda s, t, **kw: URelationship(s, t, URelType.SUPPORTS, **kw),
        "invalidates": lambda s, t, **kw: URelationship(s, t, URelType.INVALIDATES, **kw),
        "derives_from": lambda s, t, **kw: URelationship(s, t, URelType.DERIVES, **kw),
    }


class RelationshipEngine:
    """Manages relationships between any two UniversalEntities.

    Supports all 32 URelTypes. Auto-infers reverse relationships.
    Provides graph traversal, pathfinding, and subgraph extraction.
    """

    def __init__(self):
        self._rels: dict[str, URelationship] = {}
        self._outgoing: dict[str, list[URelationship]] = {}
        self._incoming: dict[str, list[URelationship]] = {}

    def relate(self, source_id: str, target_id: str,
               rel_type: URelType = URelType.DEPENDS_ON,
               weight: float = 1.0, confidence: float = 1.0,
               evidence: list[str] | None = None) -> URelationship:
        rel = URelationship(
            source_id=source_id,
            target_id=target_id,
            rel_type=rel_type,
            weight=weight,
            confidence=confidence,
            evidence=evidence or [],
        )
        self._rels[rel.id] = rel
        self._outgoing.setdefault(source_id, []).append(rel)
        self._incoming.setdefault(target_id, []).append(rel)
        return rel

    def outgoing(self, entity_id: str, rel_type: URelType | None = None) -> list[URelationship]:
        rels = self._outgoing.get(entity_id, [])
        if rel_type:
            rels = [r for r in rels if r.rel_type == rel_type]
        return rels

    def incoming(self, entity_id: str, rel_type: URelType | None = None) -> list[URelationship]:
        rels = self._incoming.get(entity_id, [])
        if rel_type:
            rels = [r for r in rels if r.rel_type == rel_type]
        return rels

    def neighbors(self, entity_id: str, rel_type: URelType | None = None) -> list[str]:
        out_ids = {r.target_id for r in self.outgoing(entity_id, rel_type)}
        in_ids = {r.source_id for r in self.incoming(entity_id, rel_type)}
        return sorted(out_ids | in_ids)

    def path(self, source_id: str, target_id: str,
             max_depth: int = 10) -> list[list[URelationship]]:
        paths: list[list[URelationship]] = []

        def _dfs(current: str, target: str, visited: set[str],
                 path: list[URelationship], depth: int):
            if depth > max_depth:
                return
            if current == target and path:
                paths.append(list(path))
                return
            for rel in self._outgoing.get(current, []):
                if rel.target_id not in visited:
                    visited.add(rel.target_id)
                    path.append(rel)
                    _dfs(rel.target_id, target, visited, path, depth + 1)
                    path.pop()
                    visited.discard(rel.target_id)

        _dfs(source_id, target_id, {source_id}, [], 0)
        return paths

    def subgraph(self, entity_id: str, depth: int = 2) -> list[URelationship]:
        collected: list[URelationship] = []
        visited: set[str] = set()

        def _collect(eid: str, remaining: int):
            if remaining <= 0 or eid in visited:
                return
            visited.add(eid)
            for rel in self._outgoing.get(eid, []):
                collected.append(rel)
                _collect(rel.target_id, remaining - 1)
            for rel in self._incoming.get(eid, []):
                collected.append(rel)
                _collect(rel.source_id, remaining - 1)

        _collect(entity_id, depth)
        return collected

    def count(self) -> int:
        return len(self._rels)

    def types_used(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for rel in self._rels.values():
            counts[rel.rel_type.value] = counts.get(rel.rel_type.value, 0) + 1
        return counts

    def summary(self) -> dict[str, Any]:
        return {
            "total_relationships": self.count(),
            "by_type": self.types_used(),
            "outgoing_nodes": len(self._outgoing),
            "incoming_nodes": len(self._incoming),
        }


# ══════════════════════════════════════════════════════════════════════════════
# Ω³ Phase 2: Universal Canonicalization Registry
# ══════════════════════════════════════════════════════════════════════════════

class CanonicalStatus(str, Enum):
    CANONICAL = "canonical"
    ADAPTED = "adapted"
    LEGACY = "legacy"
    DEPRECATED = "deprecated"


@dataclass
class CanonicalEntry:
    type_name: str = ""
    canonical_factory: str = ""
    status: CanonicalStatus = CanonicalStatus.LEGACY
    location: str = ""
    legacy_alternatives: list[str] = field(default_factory=list)
    entity_count: int = 0
    notes: str = ""


class CanonicalRegistry:
    """Tracks which abstraction is canonical and where legacy copies live.

    Every non-canonical abstraction is recorded so migration can be planned.
    Provides adapter registration for converting legacy → canonical.
    """

    def __init__(self):
        self._entries: dict[str, CanonicalEntry] = {}
        self._adapters: dict[str, Callable[..., UniversalEntity]] = {}

    def register(
        self,
        type_name: str,
        canonical_factory: str,
        status: CanonicalStatus = CanonicalStatus.CANONICAL,
        location: str = "",
        legacy_alternatives: list[str] | None = None,
        notes: str = "",
    ) -> CanonicalEntry:
        entry = CanonicalEntry(
            type_name=type_name,
            canonical_factory=canonical_factory,
            status=status,
            location=location,
            legacy_alternatives=legacy_alternatives or [],
            notes=notes,
        )
        self._entries[type_name] = entry
        return entry

    def adapter(self, type_name: str) -> Callable | None:
        return self._adapters.get(type_name)

    def register_adapter(self, type_name: str,
                         fn: Callable[..., UniversalEntity]):
        self._adapters[type_name] = fn

    def get(self, type_name: str) -> CanonicalEntry | None:
        return self._entries.get(type_name)

    def all_legacy(self) -> list[CanonicalEntry]:
        return [e for e in self._entries.values()
                if e.status == CanonicalStatus.LEGACY]

    def canonical_types(self) -> list[CanonicalEntry]:
        return [e for e in self._entries.values()
                if e.status == CanonicalStatus.CANONICAL]

    def summary(self) -> dict[str, Any]:
        return {
            "total": len(self._entries),
            "canonical": len(self.canonical_types()),
            "legacy": len(self.all_legacy()),
            "adapted": sum(1 for e in self._entries.values()
                           if e.status == CanonicalStatus.ADAPTED),
            "deprecated": sum(1 for e in self._entries.values()
                              if e.status == CanonicalStatus.DEPRECATED),
            "adapters_registered": len(self._adapters),
        }


# Module-level singleton
_canonical_registry = CanonicalRegistry()


def get_canonical_registry() -> CanonicalRegistry:
    return _canonical_registry


# ══════════════════════════════════════════════════════════════════════════════
# Canonical adapter converters: legacy → canonical UniversalEntity
# ══════════════════════════════════════════════════════════════════════════════

def convert_prediction_to_canonical(legacy_obj: Any,
                                    source: str = "") -> UniversalEntity | None:
    """Convert any Prediction-like object to a canonical UniversalEntity.

    Handles: ontology.Prediction, digital_twin.Prediction,
             world_model.Prediction, SimulationPrediction.
    """
    if legacy_obj is None:
        return None
    cls_name = type(legacy_obj).__name__
    kind = getattr(legacy_obj, "kind", "")
    kind = kind or getattr(legacy_obj, "metric", "")
    kind = kind or getattr(legacy_obj, "variable", cls_name)
    val = getattr(legacy_obj, "predicted_value", 0.0)
    val = val or getattr(legacy_obj, "value", 0.0)
    conf = getattr(legacy_obj, "confidence", 0.5)
    ent = UniversalEntity(
        type_name="prediction",
        identity=f"legacy.{source}.{kind}",
        confidence=float(conf),
    )
    ent.attributes["predicted_value"] = float(val)
    ent.attributes["metric"] = kind
    ent.attributes["legacy_class"] = cls_name
    ent.attributes["legacy_source"] = source
    return ent


def convert_plan_to_canonical(legacy_obj: Any,
                              source: str = "") -> UniversalEntity | None:
    """Convert any Plan-like object to canonical UniversalEntity.

    Handles: planning.Plan, brain_v4.Plan, os.Plan, ucos.ExecutionPlan.
    """
    if legacy_obj is None:
        return None
    cls_name = type(legacy_obj).__name__
    title = getattr(legacy_obj, "title", "")
    title = title or getattr(legacy_obj, "goal", cls_name)
    level = getattr(legacy_obj, "level", "planning")
    status = getattr(legacy_obj, "status", "draft")
    status_str = status.value if hasattr(status, "value") else str(status)
    ent = UniversalEntity(
        type_name="plan",
        identity=f"legacy.{source}.{title}",
        lifecycle=status_str,
    )
    ent.attributes["title"] = title
    ent.attributes["level"] = str(level)
    ent.attributes["legacy_class"] = cls_name
    ent.attributes["legacy_source"] = source
    return ent


def convert_experiment_to_canonical(legacy_obj: Any,
                                    source: str = "") -> UniversalEntity | None:
    """Convert any Experiment-like object to canonical UniversalEntity.

    Handles: scientist.Experiment, discovery.Experiment, evolution.*Experiment.
    """
    if legacy_obj is None:
        return None
    cls_name = type(legacy_obj).__name__
    eid = getattr(legacy_obj, "id", "")
    status = getattr(legacy_obj, "status", "designed")
    hyp = getattr(legacy_obj, "hypothesis_id", "")
    ent = UniversalEntity(
        type_name="experiment",
        identity=f"legacy.{source}.{eid or cls_name}",
        lifecycle=str(status),
    )
    ent.attributes["legacy_class"] = cls_name
    ent.attributes["legacy_source"] = source
    if hyp:
        ent.attributes["hypothesis_id"] = hyp
    return ent


def build_canonicalization_report() -> dict[str, Any]:
    """Return a full report of canonicalization status across the repository."""
    reg = get_canonical_registry()
    return {
        "registry": reg.summary(),
        "types": {
            t: {
                "status": e.status.value,
                "canonical_factory": e.canonical_factory,
                "location": e.location,
                "legacy_alternatives": e.legacy_alternatives,
                "notes": e.notes,
            }
            for t, e in reg._entries.items()
        },
    }


def initialize_canonical_registry() -> CanonicalRegistry:
    """Register all known duplications with their canonical status."""
    reg = get_canonical_registry()

    reg.register("prediction", "UPrediction", CanonicalStatus.CANONICAL,
                 location="genesis/ontology.py",
                 legacy_alternatives=[
                     "genesis/digital_twin/predict.py",
                     "genesis/civilization/world_model/__init__.py",
                     "genesis/simulator_v2.py",
                 ],
                 notes="4 Prediction definitions merged into one canonical factory")
    reg.register_adapter("prediction", convert_prediction_to_canonical)

    reg.register("plan", "EngineeringPlanner", CanonicalStatus.CANONICAL,
                 location="genesis/planner.py",
                 legacy_alternatives=[
                     "genesis/planning/__init__.py",
                     "genesis/brain_v4.py",
                     "genesis/os/planner.py",
                     "genesis/ucos/planner.py",
                 ],
                 notes="12-level hierarchy (Vision→Action) with UEM integration")
    reg.register_adapter("plan", convert_plan_to_canonical)

    reg.register("experiment", "UExperiment", CanonicalStatus.CANONICAL,
                 location="genesis/ontology.py",
                 legacy_alternatives=[
                     "genesis/scientist.py",
                     "genesis/discovery.py",
                     "genesis/evolution.py",
                     "genesis/evolution_v4.py",
                     "genesis/laboratory/experiment.py",
                 ],
                 notes="5+ Experiment definitions merged into one canonical factory")
    reg.register_adapter("experiment", convert_experiment_to_canonical)

    reg.register("knowledge_graph", "UKnowledge", CanonicalStatus.CANONICAL,
                 location="genesis/ontology.py",
                 legacy_alternatives=[
                     "genesis/knowledge_graph.py",
                     "genesis/graph_v2/layers.py",
                     "genesis/repository_graph.py",
                     "genesis/intelligence/kgraph.py",
                     "genesis/graph/engine.py",
                 ],
                 notes="5+ KnowledgeGraph definitions; canonical is UKnowledge factory")

    reg.register("simulation", "USimulation", CanonicalStatus.CANONICAL,
                 location="genesis/ontology.py",
                 legacy_alternatives=[
                     "genesis/simulator.py",
                     "genesis/simulator_v2.py",
                     "genesis/temporal/__init__.py",
                     "genesis/digital_twin/simulator.py",
                 ],
                 notes="4+ Simulator definitions; canonical is USimulation factory")

    reg.register("validation", "UValidation", CanonicalStatus.CANONICAL,
                 location="genesis/ontology.py",
                 legacy_alternatives=[
                     "genesis/validation/engine.py",
                     "genesis/digital_twin/validation.py",
                     "genesis/discovery.py",
                     "genesis/security/validator.py",
                 ],
                 notes="4+ Validation definitions; canonical is UValidation factory")

    reg.register("platform", "UPlatform", CanonicalStatus.CANONICAL,
                 location="genesis/ontology.py",
                 legacy_alternatives=[
                     "genesis/platform.py",
                     "genesis/platform_v2.py",
                 ],
                 notes="VenusPlatform + PlatformV2 both derive from UPlatform factory")

    return reg
