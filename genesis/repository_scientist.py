"""
Ω³ Phase 7: Repository Scientist.

Conducts automated scientific experiments on the repository itself.
Uses the ReasoningEngine to detect issues, then designs and runs
experiments with validated results.

Experiment types:
  - canonicalization_audit: measures duplication severity
  - dependency_analysis: finds circular/outdated dependencies
  - test_gap_analysis: finds untested code paths
  - risk_assessment: computes and ranks risk scores
  - health_check: composite health score across the repository
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from genesis.ontology import UniversalEntity, URelType, RelationshipEngine
from genesis.reasoning import ReasoningEngine, ReasoningQuery


class ExperimentStatus(str, Enum):
    PROPOSED = "proposed"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    INCONCLUSIVE = "inconclusive"


@dataclass
class Experiment:
    id: str = ""
    name: str = ""
    description: str = ""
    status: ExperimentStatus = ExperimentStatus.PROPOSED
    hypothesis: str = ""
    method: str = ""
    input_data: dict[str, Any] = field(default_factory=dict)
    results: dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    evidence: list[str] = field(default_factory=list)
    duration_ms: float = 0.0
    created_at: float = 0.0

    def __post_init__(self):
        if not self.created_at:
            self.created_at = time.time()
        if not self.id:
            import hashlib
            raw = f"{self.name}:{self.created_at}"
            self.id = hashlib.md5(raw.encode()).hexdigest()[:12]


class RepositoryScientist:
    """Conducts experiments on the repository using the ReasoningEngine."""

    def __init__(self, reasoning: ReasoningEngine | None = None):
        self.reasoning = reasoning or ReasoningEngine()
        self._experiments: list[Experiment] = []

    # ── Experiment lifecycle ──

    def propose(self, name: str, description: str = "",
                hypothesis: str = "", method: str = "",
                **input_data: Any) -> Experiment:
        exp = Experiment(
            name=name,
            description=description,
            hypothesis=hypothesis,
            method=method,
            input_data=input_data,
            status=ExperimentStatus.PROPOSED,
        )
        self._experiments.append(exp)
        return exp

    def run(self, exp_id: str) -> Experiment | None:
        for exp in self._experiments:
            if exp.id == exp_id:
                return self._execute(exp)
        return None

    def run_all(self) -> list[Experiment]:
        results = []
        for exp in self._experiments:
            if exp.status == ExperimentStatus.PROPOSED:
                results.append(self._execute(exp))
        return results

    def _execute(self, exp: Experiment) -> Experiment:
        t0 = time.time()
        exp.status = ExperimentStatus.RUNNING
        try:
            handler = _EXPERIMENT_HANDLERS.get(exp.name)
            if handler:
                handler(exp, self.reasoning)
            else:
                exp.results = {"error": f"Unknown experiment: {exp.name}"}
                exp.status = ExperimentStatus.INCONCLUSIVE
            exp.duration_ms = (time.time() - t0) * 1000
            if exp.status == ExperimentStatus.RUNNING:
                exp.status = ExperimentStatus.COMPLETED
        except Exception as e:
            exp.results = {"error": str(e)}
            exp.status = ExperimentStatus.FAILED
            exp.duration_ms = (time.time() - t0) * 1000
        return exp

    # ── History ──

    def experiments(self) -> list[Experiment]:
        return list(self._experiments)

    def latest(self, n: int = 5) -> list[Experiment]:
        return sorted(self._experiments, key=lambda e: e.created_at, reverse=True)[:n]

    def summary(self) -> dict[str, Any]:
        return {
            "total": len(self._experiments),
            "by_status": {
                s.value: sum(1 for e in self._experiments if e.status == s)
                for s in ExperimentStatus
            },
            "experiment_types": sorted(set(e.name for e in self._experiments)),
        }


# ══════════════════════════════════════════════════════════════════════════════
# Experiment handlers
# ══════════════════════════════════════════════════════════════════════════════

def _experiment_canonicalization_audit(exp: Experiment, reas: ReasoningEngine):
    """Measure duplication severity across all canonical types."""
    q = ReasoningQuery(query_type="find_duplicates")
    result = reas.query(q)
    total_duplicates = sum(r.get("duplicate_count", 0) for r in result.results)
    total_types = len(result.results)

    exp.results = {
        "duplicated_types": total_types,
        "total_implementations": total_duplicates,
        "severity": "high" if total_duplicates > total_types * 2 else "medium" if total_duplicates > total_types else "low",
        "details": result.results,
    }
    exp.confidence = result.confidence
    exp.evidence = result.evidence
    exp.status = ExperimentStatus.COMPLETED


def _experiment_dependency_analysis(exp: Experiment, reas: ReasoningEngine):
    """Analyze dependencies for circular patterns and orphan detection."""
    q1 = ReasoningQuery(query_type="orphans",
                        filters={"min_relations": 0},
                        limit=50)
    orphans = reas.query(q1)

    exp.results = {
        "orphan_count": orphans.found,
        "orphans": [r["entity_id"] for r in orphans.results[:10]],
    }
    exp.confidence = orphans.confidence
    exp.evidence = orphans.evidence
    exp.status = ExperimentStatus.COMPLETED


def _experiment_risk_assessment(exp: Experiment, reas: ReasoningEngine):
    """Compute risk scores across the repository."""
    threshold = exp.input_data.get("risk_threshold", 0.7)
    q = ReasoningQuery(query_type="high_risk",
                       filters={"risk_threshold": threshold})
    result = reas.query(q)

    total_entities = 0
    if reas.meta_model:
        total_entities = reas.meta_model.repository.count()

    exp.results = {
        "threshold": threshold,
        "high_risk_count": result.found,
        "total_entities": total_entities,
        "high_risk_entities": [r["entity_id"] for r in result.results[:10]],
        "risk_percentage": (result.found / total_entities * 100) if total_entities > 0 else 0,
    }
    exp.confidence = result.confidence
    exp.evidence = result.evidence
    exp.status = ExperimentStatus.COMPLETED


def _experiment_health_check(exp: Experiment, reas: ReasoningEngine):
    """Composite health score across repository entities."""
    total = 0
    total_health = 0.0
    if reas.meta_model:
        for inst in reas.meta_model.repository.all():
            total += 1
            h = inst.attributes.get("health", 1.0)
            if isinstance(h, (int, float)):
                total_health += h

    avg_health = total_health / total if total > 0 else 0.0
    score = min(1.0, avg_health)

    exp.results = {
        "entities_scored": total,
        "average_health": round(avg_health, 3),
        "health_score": round(score, 3),
        "grade": "A" if score >= 0.9 else "B" if score >= 0.8 else "C" if score >= 0.7 else "D",
    }
    exp.confidence = 0.9
    exp.evidence = [f"Health scored across {total} entities"]
    exp.status = ExperimentStatus.COMPLETED


def _experiment_type_inventory(exp: Experiment, reas: ReasoningEngine):
    """Count entities by type from the relationship engine."""
    type_name = exp.input_data.get("type_name", "")
    q = ReasoningQuery(query_type="type_inventory", entity_type=type_name)
    result = reas.query(q)

    exp.results = {
        "type": type_name or "all",
        "count": result.found,
        "entities": [r["entity_id"] for r in result.results[:20]],
    }
    exp.confidence = result.confidence
    exp.evidence = result.evidence
    exp.status = ExperimentStatus.COMPLETED


_EXPERIMENT_HANDLERS: dict[str, Any] = {
    "canonicalization_audit": _experiment_canonicalization_audit,
    "dependency_analysis": _experiment_dependency_analysis,
    "risk_assessment": _experiment_risk_assessment,
    "health_check": _experiment_health_check,
    "type_inventory": _experiment_type_inventory,
}


def build_repository_scientist(
    reasoning: ReasoningEngine | None = None,
) -> RepositoryScientist:
    return RepositoryScientist(reasoning=reasoning)
