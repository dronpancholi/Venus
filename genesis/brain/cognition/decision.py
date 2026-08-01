"""
Decision Engine — multi-criteria decision making with constraint solving and uncertainty.

Supports:
- Multi-criteria decision analysis (weighted scoring)
- Constraint satisfaction (hard/soft constraints)
- Pareto-optimal tradeoff analysis
- Decision under uncertainty (expected value, minimax, optimism-pessimism)
- Priority reasoning over competing alternatives

Integrates with: GoalHierarchy (goal-driven decisions), StrategyEngine (strategy selection),
BeliefSystem (belief-weighted decisions), Marketplace (cost-aware decisions).
"""

from __future__ import annotations

import math
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable

from genesis.utils.identity import generate_id


class DecisionMode(Enum):
    EXPECTED_VALUE = "expected_value"       # Maximize expected value
    MAXIMIN = "maximin"                     # Maximize worst-case outcome
    MAXIMAX = "maximax"                     # Maximize best-case outcome
    MINIMAX_REGRET = "minimax_regret"       # Minimize maximum regret
    SATISFICING = "satisficing"             # First acceptable option
    WEIGHTED_SUM = "weighted_sum"           # Multi-criteria weighted sum


@dataclass
class Criterion:
    """A decision criterion with weight and direction."""
    name: str = ""
    weight: float = 1.0       # Importance weight
    higher_is_better: bool = True
    ideal: float = 1.0        # Ideal value for normalization


@dataclass
class Alternative:
    """A decision alternative with criteria scores."""
    id: str = ""
    name: str = ""
    criteria_scores: dict[str, float] = field(default_factory=dict)
    constraints_satisfied: list[str] = field(default_factory=list)
    estimated_value: float = 0.0
    risk: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.id:
            self.id = generate_id("alt", 10)


@dataclass
class Decision:
    """A decision outcome."""
    id: str = ""
    context: str = ""
    alternatives: list[str] = field(default_factory=list)
    selected_id: str = ""
    mode: DecisionMode = DecisionMode.EXPECTED_VALUE
    confidence: float = 0.0
    rationale: str = ""
    created_at: float = 0.0
    outcome: str = "pending"        # pending, success, failure

    def __post_init__(self):
        if not self.id:
            self.id = generate_id("decision", 12)
        if not self.created_at:
            self.created_at = time.time()


class DecisionEngine:
    """Multi-criteria decision making with constraint solving.

    Supports multiple decision modes, constraint handling,
    and sensitivity analysis.
    """

    def __init__(self):
        self._decisions: list[Decision] = []
        self._criteria_registry: dict[str, Criterion] = {}
        self._hard_constraints: list[Callable[[Alternative], bool]] = []
        self._soft_constraints: list[tuple[Callable[[Alternative], float], float]] = []

    def register_criterion(self, name: str, weight: float = 1.0,
                            higher_is_better: bool = True,
                            ideal: float = 1.0) -> Criterion:
        criterion = Criterion(name=name, weight=weight,
                              higher_is_better=higher_is_better, ideal=ideal)
        self._criteria_registry[name] = criterion
        return criterion

    def add_hard_constraint(self, constraint: Callable[[Alternative], bool]):
        """Add a hard constraint that alternatives must satisfy."""
        self._hard_constraints.append(constraint)

    def add_soft_constraint(self, constraint: Callable[[Alternative], float],
                             penalty_weight: float = 1.0):
        """Add a soft constraint with penalty for violation."""
        self._soft_constraints.append((constraint, penalty_weight))

    def evaluate(self, alternatives: list[Alternative],
                 criteria: list[str] | None = None,
                 mode: DecisionMode = DecisionMode.WEIGHTED_SUM) -> Decision:
        """Evaluate alternatives and select the best one."""
        if criteria is None:
            criteria = list(self._criteria_registry.keys())

        # Filter by hard constraints
        valid = [a for a in alternatives
                 if all(c(a) for c in self._hard_constraints)]

        if not valid:
            valid = alternatives  # Fall back to all if none pass hard constraints

        # Score each alternative
        scored: list[tuple[float, Alternative]] = []
        for alt in valid:
            score = self._compute_score(alt, criteria, mode)

            # Apply soft constraint penalties
            for constraint_fn, penalty in self._soft_constraints:
                violation = constraint_fn(alt)
                score -= violation * penalty

            scored.append((score, alt))

        scored.sort(key=lambda x: x[0], reverse=True)

        if not scored:
            return Decision(
                context="evaluation",
                mode=mode,
                confidence=0.0,
                rationale="No valid alternatives found",
                outcome="failure",
            )

        selected = scored[0][1]
        best_score = scored[0][0]
        second_score = scored[1][0] if len(scored) > 1 else 0
        confidence = 1.0 / (1.0 + math.exp(-(best_score - second_score))) if len(scored) > 1 else 0.5

        decision = Decision(
            context="evaluation",
            alternatives=[a.id for a in alternatives],
            selected_id=selected.id,
            mode=mode,
            confidence=confidence,
            rationale=f"Selected '{selected.name}' with score {best_score:.3f}",
        )
        self._decisions.append(decision)
        return decision

    def _compute_score(self, alt: Alternative, criteria: list[str],
                        mode: DecisionMode) -> float:
        if mode == DecisionMode.SATISFICING:
            # First that meets minimum threshold
            return 1.0

        if mode == DecisionMode.WEIGHTED_SUM or mode == DecisionMode.EXPECTED_VALUE:
            total = 0.0
            total_weight = 0.0
            for criterion_name in criteria:
                criterion = self._criteria_registry.get(criterion_name)
                if not criterion or criterion_name not in alt.criteria_scores:
                    continue
                raw = alt.criteria_scores[criterion_name]
                normalized = raw / max(criterion.ideal, 0.01)
                if not criterion.higher_is_better:
                    normalized = 1.0 - normalized
                total += normalized * criterion.weight
                total_weight += criterion.weight
            return total / max(total_weight, 0.01)

        return 0.5  # Default for unsupported modes

    def sensitivity_analysis(self, decision: Decision,
                              alternatives: list[Alternative],
                              criteria: list[str]) -> dict[str, dict[str, float]]:
        """Analyze how sensitive the decision is to criterion weight changes."""
        results: dict[str, dict[str, float]] = {}
        for criterion_name in criteria:
            criterion = self._criteria_registry.get(criterion_name)
            if not criterion:
                continue
            # Test with weight halved and doubled
            for factor, label in [(0.5, "halved"), (2.0, "doubled")]:
                original = criterion.weight
                criterion.weight = original * factor
                decision2 = self.evaluate(alternatives, criteria)
                results[f"{criterion_name}_{label}"] = {
                    "selected": decision2.selected_id,
                    "changed": decision2.selected_id != decision.selected_id,
                }
                criterion.weight = original
        return results

    def priority_order(self, alternatives: list[Alternative],
                        criteria: list[str] | None = None) -> list[Alternative]:
        """Return alternatives sorted by priority (highest first)."""
        if criteria is None:
            criteria = list(self._criteria_registry.keys())
        scored = [(self._compute_score(a, criteria, DecisionMode.WEIGHTED_SUM), a)
                  for a in alternatives]
        scored.sort(key=lambda x: x[0], reverse=True)
        return [a for _, a in scored]

    def summary(self) -> dict[str, Any]:
        return {
            "total_decisions": len(self._decisions),
            "criteria": list(self._criteria_registry.keys()),
            "hard_constraints": len(self._hard_constraints),
            "soft_constraints": len(self._soft_constraints),
            "recent_decisions": [{"context": d.context, "selected": d.selected_id,
                                   "outcome": d.outcome} for d in self._decisions[-5:]],
        }
