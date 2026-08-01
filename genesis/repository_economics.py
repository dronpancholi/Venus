"""
Ω³ Phase 9: Repository Economics.

Ties the EconomicsEngine into the scientist/engineer pipeline.
Every experiment and improvement gets a cost/benefit analysis.

Metrics computed:
  - experiment_roi: cost/benefit of running an experiment
  - improvement_value: expected value of executing an improvement
  - duplication_tax: ongoing cost of maintaining duplicate abstractions
  - health_debt: cost of low-health entities
  - dependency_cost: maintenance cost per dependency
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

from genesis.ontology import RelationshipEngine
from genesis.reasoning import ReasoningEngine, ReasoningQuery
from genesis.repository_scientist import Experiment, ExperimentStatus, RepositoryScientist
from genesis.repository_engineer import Improvement, ImprovementStatus, ImprovementType, RepositoryEngineer


@dataclass
class CostBenefit:
    entity_id: str = ""
    entity_type: str = ""
    current_cost: float = 0.0
    expected_benefit: float = 0.0
    roi: float = 0.0
    payback_period: str = ""
    confidence: float = 0.0
    breakdown: dict[str, float] = field(default_factory=dict)


class RepositoryEconomics:
    """Economic analysis for repository experiments and improvements."""

    def __init__(self, reasoning: ReasoningEngine | None = None):
        self.reasoning = reasoning or ReasoningEngine()
        self._analyses: list[CostBenefit] = []

    def analyze_experiment(self, exp: Experiment) -> CostBenefit:
        cost = self._compute_experiment_cost(exp)
        benefit = self._compute_experiment_benefit(exp)
        roi = (benefit - cost) / max(cost, 0.01)
        cb = CostBenefit(
            entity_id=exp.id,
            entity_type="experiment",
            current_cost=round(cost, 3),
            expected_benefit=round(benefit, 3),
            roi=round(roi, 3),
            payback_period="immediate" if roi > 1 else "short" if roi > 0.5 else "long",
            confidence=exp.confidence,
            breakdown={
                "execution_cost": round(cost * 0.6, 3),
                "analysis_cost": round(cost * 0.4, 3),
                "direct_benefit": round(benefit * 0.7, 3),
                "knowledge_benefit": round(benefit * 0.3, 3),
            },
        )
        self._analyses.append(cb)
        return cb

    def analyze_improvement(self, imp: Improvement) -> CostBenefit:
        cost = self._compute_improvement_cost(imp)
        benefit = self._compute_improvement_benefit(imp)
        roi = (benefit - cost) / max(cost, 0.01)
        cb = CostBenefit(
            entity_id=imp.id,
            entity_type=imp.type.value,
            current_cost=round(cost, 3),
            expected_benefit=round(benefit, 3),
            roi=round(roi, 3),
            payback_period="immediate" if roi > 2 else "short" if roi > 1 else "medium" if roi > 0.5 else "long",
            confidence=1.0 - imp.risk,
            breakdown={
                "implementation_cost": round(cost * 0.5, 3),
                "validation_cost": round(cost * 0.3, 3),
                "migration_cost": round(cost * 0.2, 3),
                "maintenance_savings": round(benefit * 0.5, 3),
                "complexity_reduction": round(benefit * 0.3, 3),
                "risk_reduction": round(benefit * 0.2, 3),
            },
        )
        self._analyses.append(cb)
        return cb

    def analyze_duplication_tax(self) -> CostBenefit:
        """Compute the ongoing cost of maintaining duplicate abstractions."""
        q = ReasoningQuery(query_type="find_duplicates")
        result = self.reasoning.query(q)
        total_dupes = sum(r.get("duplicate_count", 1) - 1 for r in result.results)
        cost = total_dupes * 5.0  # 5 cost units per duplicate
        benefit = cost * 0.8  # 80% recoverable
        roi = (benefit - cost) / max(cost, 0.01)
        cb = CostBenefit(
            entity_id="repository",
            entity_type="duplication_tax",
            current_cost=round(cost, 3),
            expected_benefit=round(benefit, 3),
            roi=round(roi, 3),
            payback_period="immediate" if abs(roi) > 1 else "short",
            confidence=0.85,
            breakdown={"per_duplicate_cost": 5.0, "total_duplicates": total_dupes},
        )
        self._analyses.append(cb)
        return cb

    def _compute_experiment_cost(self, exp: Experiment) -> float:
        base = len(exp.input_data) * 2.0
        if exp.status in (ExperimentStatus.COMPLETED, ExperimentStatus.FAILED):
            base += exp.duration_ms / 1000 * 0.5
        return max(base, 1.0)

    def _compute_experiment_benefit(self, exp: Experiment) -> float:
        result_count = len(exp.results) * 3.0
        evidence_count = len(exp.evidence) * 2.0
        return max(result_count + evidence_count, 1.0)

    def _compute_improvement_cost(self, imp: Improvement) -> float:
        base = imp.risk * 20.0 + 5.0
        return max(base, 1.0)

    def _compute_improvement_benefit(self, imp: Improvement) -> float:
        if imp.type == ImprovementType.CANONICALIZE:
            return 30.0
        elif imp.type == ImprovementType.DEPENDENCY_FIX:
            return 15.0
        elif imp.type == ImprovementType.HEALTH_IMPROVEMENT:
            return 20.0
        return 10.0

    def analyses(self) -> list[CostBenefit]:
        return list(self._analyses)

    def summary(self) -> dict[str, Any]:
        total_cost = sum(a.current_cost for a in self._analyses)
        total_benefit = sum(a.expected_benefit for a in self._analyses)
        avg_roi = (sum(a.roi for a in self._analyses) / len(self._analyses)) if self._analyses else 0.0
        return {
            "total_analyses": len(self._analyses),
            "total_cost": round(total_cost, 3),
            "total_benefit": round(total_benefit, 3),
            "net_value": round(total_benefit - total_cost, 3),
            "average_roi": round(avg_roi, 3),
            "by_type": {
                t: sum(1 for a in self._analyses if a.entity_type == t)
                for t in set(a.entity_type for a in self._analyses)
            },
        }


def build_repository_economics(
    reasoning: ReasoningEngine | None = None,
) -> RepositoryEconomics:
    return RepositoryEconomics(reasoning=reasoning)
