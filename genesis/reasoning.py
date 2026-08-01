"""
Ω³ Phase 6: Repository Reasoning Engine.

Combines the Complete Type System, RelationshipEngine, Meta Model,
and CanonicalRegistry into a queryable reasoning system.

Supports:
  - Duplicate detection across the codebase
  - Dependency tracing (what depends on X?)
  - Impact analysis (what does X affect?)
  - Canonicalization status queries
  - Risk/health/maturity scoring at scale
  - Relationship pathfinding with semantic filtering
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from genesis.ontology import (
    UniversalEntity, URelType, RelationshipEngine, CanonicalRegistry,
)
from genesis.meta_model import (
    MetaModelEngine, MetaModelRepository, entity_full_schema,
)


@dataclass
class ReasoningQuery:
    """A structured query against repository knowledge."""
    query_type: str = ""
    entity_type: str = ""
    entity_id: str = ""
    rel_type: str = ""
    target_type: str = ""
    filters: dict[str, Any] = field(default_factory=dict)
    max_depth: int = 5
    limit: int = 100


@dataclass
class ReasoningResult:
    query: str = ""
    found: int = 0
    results: list[dict[str, Any]] = field(default_factory=list)
    evidence: list[str] = field(default_factory=list)
    confidence: float = 1.0
    duration_ms: float = 0.0


class ReasoningEngine:
    """Combines ontology + relationships + meta model into a reasoning system.

    Accepts structured queries and returns results with evidence.
    """

    def __init__(
        self,
        relationship_engine: RelationshipEngine | None = None,
        meta_model: MetaModelEngine | None = None,
        canonical_registry: CanonicalRegistry | None = None,
    ):
        self.engine = relationship_engine or RelationshipEngine()
        self.meta_model = meta_model
        self.canonical_registry = canonical_registry

    # ── Query execution ──

    def query(self, q: ReasoningQuery) -> ReasoningResult:
        import time
        t0 = time.time()

        handlers = {
            "find_duplicates": self._find_duplicates,
            "trace_dependencies": self._trace_dependencies,
            "find_consumers": self._find_consumers,
            "canonicalization_status": self._canonicalization_status,
            "entity_schema": self._entity_schema,
            "relationship_path": self._relationship_path,
            "high_risk": self._high_risk,
            "neighbors_by_type": self._neighbors_by_type,
            "orphans": self._orphans,
            "type_inventory": self._type_inventory,
        }
        handler = handlers.get(q.query_type)
        if handler is None:
            return ReasoningResult(query=q.query_type, found=0,
                                   confidence=0.0, results=[{"error": f"Unknown query type: {q.query_type}"}],
                                   duration_ms=(time.time() - t0) * 1000)
        result = handler(q)
        result.duration_ms = (time.time() - t0) * 1000
        return result

    # ── Query handlers ──

    def _find_duplicates(self, q: ReasoningQuery) -> ReasoningResult:
        """Find duplicate entities or abstractions across the codebase."""
        entries = []
        if q.entity_type and self.canonical_registry:
            entry = self.canonical_registry.get(q.entity_type.lower())
            if entry:
                entries.append(entry)
        else:
            entries = self.canonical_registry._entries.values() if self.canonical_registry else []

        results = []
        for entry in entries:
            legacy_count = len(entry.legacy_alternatives)
            if legacy_count > 0:
                results.append({
                    "type_name": entry.type_name,
                    "canonical_factory": entry.canonical_factory,
                    "status": entry.status.value,
                    "location": entry.location,
                    "legacy_alternatives": entry.legacy_alternatives,
                    "duplicate_count": legacy_count + 1,
                    "notes": entry.notes,
                })

        return ReasoningResult(
            query=f"find_duplicates:{q.entity_type or 'all'}",
            found=len(results),
            results=results,
            evidence=[f"CanonicalRegistry reports {len(results)} duplicated abstractions"],
            confidence=0.95,
        )

    def _trace_dependencies(self, q: ReasoningQuery) -> ReasoningResult:
        """Find everything that a given entity depends on."""
        results = []
        for rel in self.engine.outgoing(q.entity_id):
            if not q.rel_type or rel.rel_type.value == q.rel_type:
                results.append({
                    "source": rel.source_id,
                    "target": rel.target_id,
                    "relation": rel.rel_type.value,
                    "confidence": rel.confidence,
                    "weight": rel.weight,
                })

        return ReasoningResult(
            query=f"trace_dependencies:{q.entity_id}",
            found=len(results),
            results=results,
            evidence=[f"RelationshipEngine found {len(results)} outgoing dependencies"],
            confidence=0.9,
        )

    def _find_consumers(self, q: ReasoningQuery) -> ReasoningResult:
        """Find everything that depends on a given entity."""
        results = []
        for rel in self.engine.incoming(q.entity_id):
            if not q.rel_type or rel.rel_type.value == q.rel_type:
                results.append({
                    "source": rel.source_id,
                    "target": rel.target_id,
                    "relation": rel.rel_type.value,
                    "confidence": rel.confidence,
                })

        return ReasoningResult(
            query=f"find_consumers:{q.entity_id}",
            found=len(results),
            results=results,
            evidence=[f"RelationshipEngine found {len(results)} incoming consumers"],
            confidence=0.9,
        )

    def _canonicalization_status(self, q: ReasoningQuery) -> ReasoningResult:
        """Check the canonicalization status of a specific type or all types."""
        if not self.canonical_registry:
            return ReasoningResult(query="canonicalization_status",
                                   found=0, confidence=0.0,
                                   results=[{"error": "No canonical registry available"}])

        if q.entity_type:
            entry = self.canonical_registry.get(q.entity_type.lower())
            if not entry:
                return ReasoningResult(query=f"canonicalization_status:{q.entity_type}",
                                       found=0, confidence=0.5,
                                       results=[{"error": f"Unknown type: {q.entity_type}"}])
            results = [{
                "type_name": entry.type_name,
                "status": entry.status.value,
                "canonical_factory": entry.canonical_factory,
                "location": entry.location,
                "legacy_alternatives": entry.legacy_alternatives,
                "has_adapter": self.canonical_registry.adapter(entry.type_name) is not None,
            }]
        else:
            results = []
            for tname, entry in sorted(self.canonical_registry._entries.items()):
                results.append({
                    "type_name": entry.type_name,
                    "status": entry.status.value,
                    "canonical_factory": entry.canonical_factory,
                    "legacy_count": len(entry.legacy_alternatives),
                    "has_adapter": self.canonical_registry.adapter(entry.type_name) is not None,
                })

        return ReasoningResult(
            query=f"canonicalization_status:{q.entity_type or 'all'}",
            found=len(results),
            results=results,
            evidence=["CanonicalRegistry snapshot"],
            confidence=1.0,
        )

    def _entity_schema(self, q: ReasoningQuery) -> ReasoningResult:
        """Get the full meta model schema for a specific entity."""
        if not self.meta_model:
            return ReasoningResult(query="entity_schema", found=0,
                                   confidence=0.0,
                                   results=[{"error": "No meta model available"}])

        schema = entity_full_schema(q.entity_id, self.meta_model.repository, self.engine)
        if schema is None:
            return ReasoningResult(query=f"entity_schema:{q.entity_id}",
                                   found=0, confidence=0.5,
                                   results=[{"error": f"Entity not found: {q.entity_id}"}])
        return ReasoningResult(
            query=f"entity_schema:{q.entity_id}",
            found=1,
            results=[schema],
            evidence=[f"MetaModelEngine full schema for {q.entity_id}"],
            confidence=1.0,
        )

    def _relationship_path(self, q: ReasoningQuery) -> ReasoningResult:
        """Find paths between two entities."""
        if not q.target_type:
            return ReasoningResult(query="relationship_path", found=0,
                                   confidence=0.0,
                                   results=[{"error": "target_type required for path finding"}])
        paths = self.engine.path(q.entity_id, q.target_type, max_depth=q.max_depth)
        results = []
        for i, path in enumerate(paths):
            results.append({
                "path_index": i,
                "steps": [
                    {
                        "from": rel.source_id,
                        "to": rel.target_id,
                        "via": rel.rel_type.value,
                    }
                    for rel in path
                ],
                "length": len(path),
            })
        return ReasoningResult(
            query=f"relationship_path:{q.entity_id}->{q.target_type}",
            found=len(results),
            results=results,
            evidence=[f"RelationshipEngine found {len(results)} paths"],
            confidence=0.95,
        )

    def _high_risk(self, q: ReasoningQuery) -> ReasoningResult:
        """Find entities with risk above a threshold (default 0.7)."""
        threshold = q.filters.get("risk_threshold", 0.7)
        limit = q.limit
        results = []

        # Scan all entities in the relationship engine
        for eid in sorted(set(self.engine._outgoing.keys()) | set(self.engine._incoming.keys())):
            # Get schema if meta model available
            risk = 0.0
            name = eid
            if self.meta_model:
                schema = entity_full_schema(eid, self.meta_model.repository, self.engine)
                if schema:
                    risk = schema.get("risk", 0.0)
                    name = eid
            if risk >= threshold:
                results.append({"entity_id": eid, "risk": risk})
            if len(results) >= limit:
                break

        return ReasoningResult(
            query=f"high_risk:>{threshold}",
            found=len(results),
            results=results,
            evidence=[f"Risk threshold {threshold}"],
            confidence=0.85,
        )

    def _neighbors_by_type(self, q: ReasoningQuery) -> ReasoningResult:
        """Find neighbors of an entity, optionally filtered by relationship type."""
        rel_filter = URelType(q.rel_type) if q.rel_type else None
        neighbor_ids = self.engine.neighbors(q.entity_id, rel_filter)
        results = [{"entity_id": nid} for nid in neighbor_ids[:q.limit]]

        return ReasoningResult(
            query=f"neighbors_by_type:{q.entity_id}",
            found=len(results),
            results=results,
            evidence=[f"RelationshipEngine neighbors (type={q.rel_type or 'any'})"],
            confidence=0.9,
        )

    def _orphans(self, q: ReasoningQuery) -> ReasoningResult:
        """Find entities with no incoming or outgoing relationships."""
        threshold = q.filters.get("min_relations", 0)
        results = []
        all_ids = set(self.engine._outgoing.keys()) | set(self.engine._incoming.keys())
        for eid in sorted(all_ids):
            total = len(self.engine.outgoing(eid)) + len(self.engine.incoming(eid))
            if total <= threshold:
                results.append({"entity_id": eid, "total_relations": total})
            if len(results) >= q.limit:
                break

        return ReasoningResult(
            query=f"orphans:<={threshold} relations",
            found=len(results),
            results=results,
            evidence=[f"RelationshipEngine orphan detection"],
            confidence=0.9,
        )

    def _type_inventory(self, q: ReasoningQuery) -> ReasoningResult:
        """List all entities of a given type from the relationship engine."""
        type_prefix = f"{q.entity_type}:" if q.entity_type else ""
        all_ids = set(self.engine._outgoing.keys()) | set(self.engine._incoming.keys())
        matched = sorted([eid for eid in all_ids if eid.startswith(type_prefix)])
        results = [{"entity_id": eid} for eid in matched[:q.limit]]

        return ReasoningResult(
            query=f"type_inventory:{q.entity_type or 'all'}",
            found=len(results),
            results=results,
            evidence=[f"RelationshipEngine type inventory"],
            confidence=1.0,
        )

    # ── Convenience methods ──

    def summary(self) -> dict[str, Any]:
        """Return overall reasoning engine status."""
        return {
            "total_entities": len(set(self.engine._outgoing.keys()) | set(self.engine._incoming.keys())),
            "total_relationships": self.engine.count(),
            "query_types_supported": [
                "find_duplicates", "trace_dependencies", "find_consumers",
                "canonicalization_status", "entity_schema", "relationship_path",
                "high_risk", "neighbors_by_type", "orphans", "type_inventory",
            ],
            "meta_model_available": self.meta_model is not None,
            "canonical_registry_available": self.canonical_registry is not None,
            "relationship_engine_available": self.engine is not None,
        }


def build_reasoning_engine(
    eng: RelationshipEngine | None = None,
    mme: MetaModelEngine | None = None,
    cr: CanonicalRegistry | None = None,
) -> ReasoningEngine:
    return ReasoningEngine(
        relationship_engine=eng or RelationshipEngine(),
        meta_model=mme,
        canonical_registry=cr,
    )
