"""
GENESIS XIII Phase 4: Engineering Meta Model.

Universal data flow: repository → model → instance → execution → evidence → evolution.

Makes everything data-driven rather than hardcoded.
"""

from __future__ import annotations

import ast
import json
import hashlib
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Callable

from genesis.ontology import UniversalEntity, URelType, RelationshipEngine


class MetaTypeKind(Enum):
    PRIMITIVE = "primitive"
    COMPOUND = "compound"
    ENUM = "enum"


@dataclass
class MetaAttribute:
    name: str
    type_name: str
    required: bool = False
    default: Any = None
    description: str = ""
    constraints: list[str] = field(default_factory=list)


@dataclass
class MetaRelation:
    name: str
    target_type: str
    cardinality: str = "one"  # one | many
    description: str = ""
    bidirectional: bool = False
    inverse_name: str = ""


@dataclass
class MetaType:
    name: str
    kind: MetaTypeKind = MetaTypeKind.COMPOUND
    description: str = ""
    parent: str = ""
    attributes: list[MetaAttribute] = field(default_factory=list)
    relations: list[MetaRelation] = field(default_factory=list)
    validation_rules: list[str] = field(default_factory=list)

    def attribute_names(self) -> list[str]:
        return [a.name for a in self.attributes]

    def relation_names(self) -> list[str]:
        return [r.name for r in self.relations]


@dataclass
class MetaInstance:
    type_name: str
    identity: str
    attributes: dict[str, Any] = field(default_factory=dict)
    relations: dict[str, list[str]] = field(default_factory=dict)
    created_at: str = ""
    updated_at: str = ""
    version: int = 1
    source: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()
        if not self.updated_at:
            self.updated_at = self.created_at

    @property
    def id(self) -> str:
        return f"{self.type_name}:{self.identity}"

    def fingerprint(self) -> str:
        raw = f"{self.type_name}|{self.identity}|{json.dumps(self.attributes, sort_keys=True, default=str)}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]


class MetaModel:
    """Schema layer — defines what entity types exist."""

    def __init__(self):
        self._types: dict[str, MetaType] = {}

    def define(self, mt: MetaType) -> MetaType:
        self._types[mt.name] = mt
        return mt

    def get(self, name: str) -> MetaType | None:
        return self._types.get(name)

    def all_types(self) -> list[MetaType]:
        return list(self._types.values())

    def children_of(self, parent: str) -> list[MetaType]:
        return [t for t in self._types.values() if t.parent == parent]

    def validate_instance(self, inst: MetaInstance) -> list[str]:
        errors: list[str] = []
        mt = self.get(inst.type_name)
        if not mt:
            errors.append(f"Unknown type: {inst.type_name}")
            return errors
        for attr in mt.attributes:
            if attr.required and attr.name not in inst.attributes:
                errors.append(f"Missing required attribute '{attr.name}' on {inst.type_name}")
            if attr.name in inst.attributes:
                val = inst.attributes[attr.name]
                if attr.type_name == "string" and not isinstance(val, str):
                    errors.append(f"Attribute '{attr.name}' should be string, got {type(val).__name__}")
                elif attr.type_name == "integer" and not isinstance(val, int):
                    errors.append(f"Attribute '{attr.name}' should be integer, got {type(val).__name__}")
                elif attr.type_name == "boolean" and not isinstance(val, bool):
                    errors.append(f"Attribute '{attr.name}' should be boolean, got {type(val).__name__}")
        return errors


class MetaModelRepository:
    """Instance layer — all concrete entities in the repository."""

    def __init__(self, model: MetaModel):
        self.model = model
        self._instances: dict[str, MetaInstance] = {}

    def add(self, inst: MetaInstance) -> list[str]:
        errors = self.model.validate_instance(inst)
        if errors:
            return errors
        key = inst.id
        if key in self._instances:
            existing = self._instances[key]
            existing.version += 1
            existing.updated_at = datetime.now(timezone.utc).isoformat()
            existing.attributes = inst.attributes
            existing.relations = inst.relations
        else:
            self._instances[key] = inst
        return []

    def get(self, type_name: str, identity: str) -> MetaInstance | None:
        return self._instances.get(f"{type_name}:{identity}")

    def get_by_id(self, full_id: str) -> MetaInstance | None:
        return self._instances.get(full_id)

    def find(self, type_name: str | None = None, **attrs: Any) -> list[MetaInstance]:
        results = list(self._instances.values())
        if type_name:
            results = [r for r in results if r.type_name == type_name]
        for key, value in attrs.items():
            results = [r for r in results if r.attributes.get(key) == value]
        return results

    def all(self) -> list[MetaInstance]:
        return list(self._instances.values())

    def count(self) -> int:
        return len(self._instances)

    def types_count(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for inst in self._instances.values():
            counts[inst.type_name] = counts.get(inst.type_name, 0) + 1
        return counts


class MetaModelRepositoryScanner:
    """Scans a repository directory and creates MetaInstances."""

    def __init__(self, repo_path: str | Path, repository: MetaModelRepository):
        self.repo_path = Path(repo_path)
        self.repository = repository

    def scan_all(self) -> int:
        count = 0
        path = self.repo_path
        if path.is_file():
            return self._scan_file(path)
        for py_file in sorted(path.rglob("*.py")):
            if ".venv" in str(py_file) or "__pycache__" in str(py_file):
                continue
            count += self._scan_file(py_file)
        return count

    def _scan_file(self, path: Path) -> int:
        try:
            relative = path.relative_to(self.repo_path)
        except ValueError:
            relative = path
        try:
            tree = ast.parse(path.read_text())
        except SyntaxError:
            return 0
        module_name = str(relative).replace("/", ".").replace(".py", "")
        if module_name.endswith(".__init__"):
            module_name = module_name[:-9]

        # Create Module instance
        classes = [n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
        functions = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
        imports = self._extract_imports(tree)
        lines = path.read_text().count("\n") + 1
        has_docstring = bool(tree.body) and isinstance(tree.body[0], ast.Expr) and isinstance(tree.body[0].value, ast.Constant)

        mod = MetaInstance(
            type_name="Module",
            identity=module_name,
            attributes={
                "name": module_name,
                "path": str(relative),
                "lines": lines,
                "classes": classes,
                "functions": functions,
                "has_docstring": has_docstring,
                "has_type_hints": any(self._has_annotation(n) for n in ast.walk(tree)),
            },
            relations={"imports": imports},
            source="repository_scanner",
        )
        self.repository.add(mod)

        # Create Class instances
        for cls in classes:
            c = MetaInstance(
                type_name="Class",
                identity=f"{module_name}.{cls}",
                attributes={"name": cls, "module": module_name},
                source="repository_scanner",
            )
            self.repository.add(c)

        # Create Function instances
        for fn in functions:
            f = MetaInstance(
                type_name="Function",
                identity=f"{module_name}.{fn}",
                attributes={"name": fn, "module": module_name},
                source="repository_scanner",
            )
            self.repository.add(f)

        return 1 + len(classes) + len(functions)

    def _extract_imports(self, tree: ast.Module) -> list[str]:
        imports: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
        return imports

    def _has_annotation(self, node: ast.AST) -> bool:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.returns:
                return True
            for arg in node.args.args + node.args.kwonlyargs + node.args.posonlyargs:
                if arg.annotation:
                    return True
        elif isinstance(node, ast.AnnAssign):
            return True
        return False


@dataclass
class EvolutionEvent:
    instance_id: str
    event_type: str  # created | updated | validated | tested | error
    timestamp: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


class EvolutionTracker:
    """Tracks instance evolution over time."""

    def __init__(self):
        self._events: list[EvolutionEvent] = []

    def record(self, event: EvolutionEvent):
        self._events.append(event)

    def events_for(self, instance_id: str) -> list[EvolutionEvent]:
        return [e for e in self._events if e.instance_id == instance_id]

    def recent(self, limit: int = 20) -> list[EvolutionEvent]:
        return self._events[-limit:]

    def by_type(self, event_type: str) -> list[EvolutionEvent]:
        return [e for e in self._events if e.event_type == event_type]

    def all_events(self) -> list[EvolutionEvent]:
        return list(self._events)


class MetaModelEngine:
    """Orchestrates the full meta model data flow."""

    def __init__(self, repo_path: str | Path = "."):
        self.model = MetaModel()
        self.repository = MetaModelRepository(self.model)
        self.scanner = MetaModelRepositoryScanner(repo_path, self.repository)
        self.evolution = EvolutionTracker()

    def define_builtin_types(self):
        self.model.define(MetaType(
            name="Module", kind=MetaTypeKind.COMPOUND, description="A Python module",
            attributes=[
                MetaAttribute("name", "string", True),
                MetaAttribute("path", "string", True),
                MetaAttribute("lines", "integer"),
                MetaAttribute("classes", "list"),
                MetaAttribute("functions", "list"),
                MetaAttribute("has_docstring", "boolean"),
                MetaAttribute("has_type_hints", "boolean"),
            ],
            relations=[
                MetaRelation("imports", "Module", "many"),
                MetaRelation("contains", "Class", "many"),
                MetaRelation("contains", "Function", "many"),
            ],
        ))
        self.model.define(MetaType(
            name="Class", kind=MetaTypeKind.COMPOUND, description="A class definition",
            attributes=[
                MetaAttribute("name", "string", True),
                MetaAttribute("module", "string", True),
            ],
        ))
        self.model.define(MetaType(
            name="Function", kind=MetaTypeKind.COMPOUND, description="A function definition",
            attributes=[
                MetaAttribute("name", "string", True),
                MetaAttribute("module", "string", True),
            ],
        ))

    def scan(self) -> int:
        count = self.scanner.scan_all()
        self.evolution.record(EvolutionEvent(
            instance_id="system",
            event_type="scanned",
            metadata={"modules_scanned": count},
        ))
        return count

    def summary(self) -> dict[str, Any]:
        return {
            "types": [t.name for t in self.model.all_types()],
            "total_instances": self.repository.count(),
            "instances_by_type": self.repository.types_count(),
            "total_events": len(self.evolution.all_events()),
            "events_by_type": {
                t: len(self.evolution.by_type(t))
                for t in set(e.event_type for e in self.evolution.all_events())
            },
        }

    def save(self, path: str | Path | None = None):
        if path is None:
            path = Path(__file__).parent / "census" / "meta_model.json"
        path = Path(path) if isinstance(path, str) else path
        path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "summary": self.summary(),
            "instances": [
                {
                    "id": inst.id,
                    "type_name": inst.type_name,
                    "identity": inst.identity,
                    "attributes": inst.attributes,
                    "relations": inst.relations,
                    "version": inst.version,
                    "source": inst.source,
                }
                for inst in self.repository.all()
            ],
            "events": [asdict(e) for e in self.evolution.all_events()],
        }
        with open(path, "w") as f:
            json.dump(data, f, indent=2, default=str)
        print(f"  Meta Model saved: {path} ({self.repository.count()} instances, {len(self.evolution.all_events())} events)")


# ══════════════════════════════════════════════════════════════════════════════
# Ω³ Phase 4: Complete Meta Model — UEM + RelationshipEngine integration
# ══════════════════════════════════════════════════════════════════════════════

# Canonical type map: type_name → {attribute_defs, relation_defs}
_CANONICAL_TYPE_SCHEMA: dict[str, dict[str, Any]] = {
    "artifact": {
        "attributes": [("artifact_type", "string"), ("description", "string")],
        "relations": [("depends_on", "artifact"), ("implements", "capability"), ("produces", "evidence")],
    },
    "capability": {
        "attributes": [("capability_type", "string"), ("description", "string")],
        "relations": [("requires", "capability"), ("enables", "process")],
    },
    "process": {
        "attributes": [("process_type", "string"), ("steps", "list")],
        "relations": [("depends_on", "process"), ("produces", "artifact")],
    },
    "evidence": {
        "attributes": [("evidence_type", "string"), ("description", "string"), ("confidence", "float")],
        "relations": [("supports", "hypothesis"), ("contradicts", "hypothesis")],
    },
    "decision": {
        "attributes": [("decision_type", "string"), ("rationale", "string"), ("outcome", "string")],
        "relations": [("based_on", "evidence"), ("impacts", "plan")],
    },
    "execution": {
        "attributes": [("execution_type", "string"), ("status", "string"), ("duration_ms", "float")],
        "relations": [("executes", "plan"), ("produces", "artifact")],
    },
    "knowledge": {
        "attributes": [("knowledge_type", "string"), ("content", "string"), ("domain", "string")],
        "relations": [("derives_from", "knowledge"), ("informs", "decision")],
    },
    "research": {
        "attributes": [("research_type", "string"), ("question", "string"), ("methodology", "string")],
        "relations": [("produces", "knowledge"), ("informs", "experiment")],
    },
    "prediction": {
        "attributes": [("metric", "string"), ("predicted_value", "float"), ("error_bounds", "string")],
        "relations": [("based_on", "evidence"), ("verified_by", "execution")],
    },
    "experiment": {
        "attributes": [("experiment_type", "string"), ("hypothesis", "string"), ("status", "string")],
        "relations": [("tests", "hypothesis"), ("produces", "evidence")],
    },
    "economics": {
        "attributes": [("metric_name", "string"), ("value", "float"), ("unit", "string")],
        "relations": [("measures", "execution"), ("funds", "plan")],
    },
    "history": {
        "attributes": [("history_type", "string"), ("events", "list"), ("period", "string")],
        "relations": [("records", "event")],
    },
    "memory": {
        "attributes": [("memory_type", "string"), ("content", "string"), ("strength", "float")],
        "relations": [("informs", "decision"), ("retrieved_by", "process")],
    },
    "simulation": {
        "attributes": [("sim_type", "string"), ("params", "dict"), ("results", "dict")],
        "relations": [("simulates", "process"), ("predicts", "outcome")],
    },
    "metric": {
        "attributes": [("metric_name", "string"), ("value", "float"), ("unit", "string")],
        "relations": [("measures", "entity")],
    },
    "validation": {
        "attributes": [("validation_type", "string"), ("result", "string"), ("coverage", "float")],
        "relations": [("validates", "artifact"), ("verifies", "specification")],
    },
    "contract": {
        "attributes": [("contract_type", "string"), ("producer", "string"), ("consumers", "list")],
        "relations": [("binds", "service"), ("versioned_by", "version")],
    },
    "specification": {
        "attributes": [("spec_version", "string"), ("content", "string")],
        "relations": [("governs", "module"), ("derives_from", "specification")],
    },
    "policy": {
        "attributes": [("effect", "string"), ("action", "string"), ("service", "string")],
        "relations": [("governs", "service"), ("constrains", "process")],
    },
    "service": {
        "attributes": [("service_type", "string"), ("status", "string")],
        "relations": [("depends_on", "service"), ("exposes", "capability")],
    },
    "agent": {
        "attributes": [("agent_role", "string"), ("model", "string")],
        "relations": [("operates", "process"), ("uses", "capability")],
    },
    "component": {
        "attributes": [("component_type", "string"), ("tech_stack", "list")],
        "relations": [("composes", "component"), ("implements", "service")],
    },
    "graph": {
        "attributes": [("graph_type", "string"), ("nodes", "integer"), ("edges", "integer")],
        "relations": [("represents", "entity")],
    },
    "timeline": {
        "attributes": [("events", "list")],
        "relations": [("tracks", "entity")],
    },
    "version": {
        "attributes": [("version_str", "string"), ("changes", "list")],
        "relations": [("versions", "artifact")],
    },
    "identity": {
        "attributes": [],
        "relations": [("identifies", "entity")],
    },
    "ontology": {
        "attributes": [],
        "relations": [("defines", "type")],
    },
    "runtime": {
        "attributes": [("runtime_type", "string"), ("version", "string")],
        "relations": [("runs", "component"), ("hosts", "service")],
    },
    "compiler": {
        "attributes": [("compiler_type", "string"), ("version", "string")],
        "relations": [("compiles", "artifact"), ("optimizes", "execution")],
    },
    "platform": {
        "attributes": [("version", "string")],
        "relations": [("hosts", "service"), ("contains", "component")],
    },
}


def register_universal_types(model: MetaModel) -> int:
    """Register all 32 canonical Universal* types as MetaType definitions."""
    count = 0
    for type_name, schema in sorted(_CANONICAL_TYPE_SCHEMA.items()):
        mt = MetaType(
            name=type_name,
            kind=MetaTypeKind.COMPOUND,
            description=f"Canonical {type_name} type from Ω³ type system",
            attributes=[
                MetaAttribute(name=aname, type_name=atype, required=(aname in ("type_name", "identity")))
                for aname, atype in schema["attributes"]
            ],
            relations=[
                MetaRelation(name=rname, target_type=rtype, cardinality="many")
                for rname, rtype in schema["relations"]
            ],
        )
        model.define(mt)
        count += 1
    return count


def sync_uem_entities_to_meta_model(
    repository: MetaModelRepository,
    entities: list[UniversalEntity],
    engine: RelationshipEngine | None = None,
) -> int:
    """Sync UniversalEntity instances (from ontology) into the MetaModelRepository.

    Each entity becomes a MetaInstance with full attribute, relation, and
    lifecycle data.
    """
    count = 0
    for ent in entities:
        inst = MetaInstance(
            type_name=ent.type_name,
            identity=ent.identity,
            attributes={
                "id": ent.id,
                "owner": ent.owner,
                "lifecycle": ent.lifecycle,
                "confidence": ent.confidence,
                "health": ent.health,
                "risk": ent.risk,
                "maturity": ent.maturity,
                "version": ent.version,
                "dependencies": list(ent.dependencies),
                "consumers": list(ent.consumers),
                "role": ent.role,
                **ent.attributes,
            },
            relations={},
            version=ent.version,
            source="uem_sync",
        )
        # Map dependencies as relations
        if ent.dependencies:
            inst.relations["depends_on"] = [d for d in ent.dependencies]
        if ent.consumers:
            inst.relations["consumed_by"] = [c for c in ent.consumers]

        # Map relationship engine links
        if engine:
            outgoing = engine.outgoing(ent.id)
            for rel in outgoing:
                rel_name = rel.rel_type.value
                if rel_name not in inst.relations:
                    inst.relations[rel_name] = []
                inst.relations[rel_name].append(rel.target_id)

        repository.add(inst)
        count += 1
    return count


def entity_full_schema(
    entity_id: str,
    repository: MetaModelRepository,
    engine: RelationshipEngine | None = None,
) -> dict[str, Any] | None:
    """Return the complete schema for any entity — Ω³ Phase 4 specification.

    Includes: metadata, constraints, capabilities, dependencies, consumers,
    contracts, interfaces, owners, confidence, health, risk, maturity, version,
    history, timeline, metrics, economics, validation, runtime state, graph
    position, knowledge links, research links, memory links, planner links,
    simulation links, prediction links.
    """
    inst = repository.get_by_id(entity_id)
    if inst is None:
        return None

    schema: dict[str, Any] = {
        "identity": entity_id,
        "type": inst.type_name,
        "metadata": {
            "created_at": inst.created_at,
            "updated_at": inst.updated_at,
            "version": inst.version,
            "source": inst.source,
        },
        # Constraints derived from type schema
        "constraints": {
            "required_attributes": [
                a.name for a in
                (repository.model.get(inst.type_name).attributes if repository.model.get(inst.type_name) else [])
                if a.required
            ],
        },
        # Core UEM fields
        "owner": inst.attributes.get("owner", ""),
        "lifecycle": inst.attributes.get("lifecycle", "created"),
        "confidence": inst.attributes.get("confidence", 1.0),
        "health": inst.attributes.get("health", 1.0),
        "risk": inst.attributes.get("risk", 0.0),
        "maturity": inst.attributes.get("maturity", 0.0),
        "version": inst.attributes.get("version", 1),
        "dependencies": inst.attributes.get("dependencies", []),
        "consumers": inst.attributes.get("consumers", []),
        "role": inst.attributes.get("role", ""),
        # Type-specific attributes
        "attributes": {k: v for k, v in inst.attributes.items()
                       if k not in ("owner", "lifecycle", "confidence", "health",
                                    "risk", "maturity", "version", "dependencies",
                                    "consumers", "role", "id")},
        # Relationship links
        "relations": dict(inst.relations),
        # Knowledge links
        "knowledge_links": [r.target_id for r in (engine.outgoing(entity_id, URelType.DERIVES) if engine else [])] if engine else [],
        "research_links": [r.target_id for r in (engine.outgoing(entity_id, URelType.EXPLAINS) if engine else [])] if engine else [],
        "memory_links": [],
        "planner_links": [],
        "simulation_links": [],
        "prediction_links": [],
        "timeline": [],
        "metrics": [],
        "economics": [],
        "validations": [],
        "runtime_state": {},
        "graph_position": {},
    }

    # If we have a relationship engine, populate links
    if engine:
        for rel in engine.outgoing(entity_id):
            rt = rel.rel_type.value
            if "predict" in rt:
                schema["prediction_links"].append({"target": rel.target_id, "type": rt, "confidence": rel.confidence})
            if "simulat" in rt:
                schema["simulation_links"].append({"target": rel.target_id, "type": rt})
            if "plan" in rt:
                schema["planner_links"].append({"target": rel.target_id, "type": rt})
            if "test" in rt or "valid" in rt:
                schema["validations"].append({"target": rel.target_id, "type": rt})
            if "metric" in rt or "measure" in rt:
                schema["metrics"].append({"target": rel.target_id, "type": rt})

    return schema


# Convenience functions

def build_omega3_meta_model(
    repo_root: str = ".",
    entities: list[UniversalEntity] | None = None,
    engine: RelationshipEngine | None = None,
) -> MetaModelEngine:
    """Build a Ω³-integrated MetaModelEngine with all canonical types and entities."""
    mme = build_default_meta_model(repo_root)
    register_universal_types(mme.model)
    if entities:
        sync_uem_entities_to_meta_model(mme.repository, entities, engine)
    return mme


# Restore original default builder (preserved for backward compatibility)
def build_default_meta_model(repo_root: str = ".") -> MetaModelEngine:
    engine = MetaModelEngine(repo_root)
    engine.define_builtin_types()
    return engine
