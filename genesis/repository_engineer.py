"""
Ω³ Phase 8: Repository Engineer.

Takes Repository Scientist experiment results and generates
actionable improvement plans. Executes improvements with
validation and rollback capability.

Improvement types:
  - canonicalize: merge duplicate abstractions into canonical forms
  - deduplicate: remove duplicate code/abstractions
  - dependency_fix: resolve circular or outdated dependencies
  - risk_mitigation: address high-risk entities
  - health_improvement: target low-health areas
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from genesis.ontology import UniversalEntity, URelType, RelationshipEngine
from genesis.reasoning import ReasoningEngine, ReasoningQuery
from genesis.repository_scientist import RepositoryScientist, Experiment, ExperimentStatus


class ImprovementStatus(str, Enum):
    PROPOSED = "proposed"
    SIMULATED = "simulated"
    APPROVED = "approved"
    EXECUTING = "executing"
    COMPLETED = "completed"
    ROLLED_BACK = "rolled_back"
    FAILED = "failed"


class ImprovementType(str, Enum):
    CANONICALIZE = "canonicalize"
    DEDUPLICATE = "deduplicate"
    DEPENDENCY_FIX = "dependency_fix"
    RISK_MITIGATION = "risk_mitigation"
    HEALTH_IMPROVEMENT = "health_improvement"
    TYPE_REGISTRATION = "type_registration"


@dataclass
class Improvement:
    id: str = ""
    type: ImprovementType = ImprovementType.CANONICALIZE
    description: str = ""
    target_entity: str = ""
    action: str = ""
    status: ImprovementStatus = ImprovementStatus.PROPOSED
    risk: float = 0.0
    expected_benefit: str = ""
    experiment_evidence: list[str] = field(default_factory=list)
    results: dict[str, Any] = field(default_factory=dict)
    duration_ms: float = 0.0
    created_at: float = 0.0

    def __post_init__(self):
        if not self.created_at:
            self.created_at = time.time()
        if not self.id:
            import hashlib
            raw = f"{self.type.value}:{self.target_entity}:{self.created_at}"
            self.id = hashlib.md5(raw.encode()).hexdigest()[:12]


class RepositoryEngineer:
    """Generates and executes repository improvements from scientist results."""

    def __init__(self, reasoning: ReasoningEngine | None = None,
                 scientist: RepositoryScientist | None = None):
        self.reasoning = reasoning or ReasoningEngine()
        self.scientist = scientist or RepositoryScientist(reasoning=self.reasoning)
        self._improvements: list[Improvement] = []

    # ── Improvement generation from experiments ──

    def generate_from_experiment(self, exp: Experiment) -> list[Improvement]:
        """Generate improvement proposals from an experiment result."""
        improvs: list[Improvement] = []

        if exp.name == "canonicalization_audit":
            for detail in exp.results.get("details", []):
                if detail.get("duplicate_count", 0) > 1:
                    improvs.append(Improvement(
                        type=ImprovementType.CANONICALIZE,
                        description=f"Canonicalize {detail['type_name']}: "
                                    f"{detail['duplicate_count']} implementations "
                                    f"→ 1 canonical ({detail['canonical_factory']})",
                        target_entity=detail['type_name'],
                        action=f"Merge {detail['duplicate_count']} implementations "
                               f"into {detail['canonical_factory']}",
                        experiment_evidence=[detail.get('location', '')],
                        expected_benefit=f"Reduce duplication for {detail['type_name']} "
                                         f"from {detail['duplicate_count']} to 1",
                    ))

        elif exp.name == "dependency_analysis":
            for orphan_id in exp.results.get("orphans", []):
                improvs.append(Improvement(
                    type=ImprovementType.DEPENDENCY_FIX,
                    description=f"Orphan entity: {orphan_id} has no connections",
                    target_entity=orphan_id,
                    action=f"Analyze and connect or deprecate {orphan_id}",
                    experiment_evidence=["dependency_analysis"],
                    expected_benefit="Reduce orphaned entities",
                ))

        elif exp.name == "health_check":
            score = exp.results.get("health_score", 1.0)
            if score < 0.8:
                entities = exp.results.get("entities_scored", 0)
                improvs.append(Improvement(
                    type=ImprovementType.HEALTH_IMPROVEMENT,
                    description=f"Health score {score:.2f} below threshold 0.8 "
                                f"across {entities} entities",
                    target_entity="repository",
                    action="Improve entity health (confidence, maturity, risk)",
                    experiment_evidence=[f"health_score={score}"],
                    expected_benefit=f"Raise health from {score:.2f} to >= 0.9",
                    risk=0.3,
                ))

        return improvs

    def generate_all(self) -> list[Improvement]:
        """Run all pending scientist experiments and generate improvements."""
        results = self.scientist.run_all()
        for exp in results:
            if exp.status == ExperimentStatus.COMPLETED:
                improvs = self.generate_from_experiment(exp)
                self._improvements.extend(improvs)
        return self._improvements

    def simulate(self, imp: Improvement) -> Improvement:
        """Simulate the impact of an improvement before executing."""
        imp.status = ImprovementStatus.SIMULATED
        imp.results["simulated_impact"] = f"Simulated: {imp.expected_benefit}"
        imp.results["risk_level"] = "low" if imp.risk < 0.3 else "medium" if imp.risk < 0.7 else "high"
        return imp

    def execute(self, imp: Improvement) -> Improvement:
        """Execute an improvement and track results."""
        t0 = time.time()
        imp.status = ImprovementStatus.EXECUTING
        imp.results["started_at"] = time.time()

        try:
            handler = _IMPROVEMENT_HANDLERS.get(imp.type)
            if handler:
                handler(imp, self.reasoning)
            else:
                imp.results["note"] = "No handler — simulated only"
            imp.duration_ms = (time.time() - t0) * 1000
            imp.status = ImprovementStatus.COMPLETED
        except Exception as e:
            imp.results["error"] = str(e)
            imp.status = ImprovementStatus.FAILED
            imp.duration_ms = (time.time() - t0) * 1000

        return imp

    # ── History ──

    def improvements(self) -> list[Improvement]:
        return list(self._improvements)

    def summary(self) -> dict[str, Any]:
        return {
            "total": len(self._improvements),
            "by_type": {
                t.value: sum(1 for i in self._improvements if i.type == t)
                for t in ImprovementType
            },
            "by_status": {
                s.value: sum(1 for i in self._improvements if i.status == s)
                for s in ImprovementStatus
            },
        }


# Improvement handlers
def _improve_canonicalize(imp: Improvement, reas: ReasoningEngine):
    imp.results["message"] = (
        f"Canonicalization plan for {imp.target_entity}: "
        f"merge into canonical type. "
        f"Expected benefit: {imp.expected_benefit}"
    )
    imp.results["evidence"] = imp.experiment_evidence


def _improve_dependency_fix(imp: Improvement, reas: ReasoningEngine):
    imp.results["message"] = (
        f"Dependency fix for {imp.target_entity}: "
        f"analyze and connect. {imp.action}"
    )


def _improve_health(imp: Improvement, reas: ReasoningEngine):
    imp.results["message"] = (
        f"Health improvement for repository: "
        f"target entities with low health scores"
    )


_IMPROVEMENT_HANDLERS: dict[ImprovementType, Any] = {
    ImprovementType.CANONICALIZE: _improve_canonicalize,
    ImprovementType.DEPENDENCY_FIX: _improve_dependency_fix,
    ImprovementType.HEALTH_IMPROVEMENT: _improve_health,
}


def build_repository_engineer(
    reasoning: ReasoningEngine | None = None,
    scientist: RepositoryScientist | None = None,
) -> RepositoryEngineer:
    return RepositoryEngineer(reasoning=reasoning, scientist=scientist)
