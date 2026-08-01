"""
Reflection Engine — self-criticism, pattern detection, and improvement over past decisions.

Analyses episodic memory to detect:
- Patterns of success and failure
- Repeated mistakes
- Suboptimal decisions
- Improvement opportunities

Generates reflections that update beliefs and goals.

Integrates with: EpisodicMemory (replay decisions), BeliefSystem (update from reflection),
GoalHierarchy (new goals from reflection), ReasoningEngine (patterns as rules).
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

from genesis.utils.identity import generate_id


@dataclass
class Reflection:
    """A reflection — insight derived from analyzing past experience."""
    id: str = ""
    insight: str = ""
    category: str = ""           # pattern, mistake, improvement, success
    supporting_episodes: list[str] = field(default_factory=list)
    confidence: float = 0.0
    recommendation: str = ""
    created_at: float = 0.0
    applied: bool = False

    def __post_init__(self):
        if not self.id:
            self.id = generate_id("reflect", 12)
        if not self.created_at:
            self.created_at = time.time()

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "insight": self.insight,
            "category": self.category,
            "supporting_episodes": self.supporting_episodes,
            "confidence": self.confidence,
            "recommendation": self.recommendation,
            "created_at": self.created_at,
            "applied": self.applied,
        }


class ReflectionEngine:
    """Analyzes episodic memory to derive insights and self-improvements.

    Performs:
    - Outcome analysis: what worked, what didn't
    - Pattern detection: recurring success/failure patterns
    - Mistake analysis: identifying root causes of failures
    - Improvement generation: actionable recommendations
    """

    def __init__(self):
        self._reflections: list[Reflection] = []
        self._criticism_count = 0

    @property
    def reflection_count(self) -> int:
        return len(self._reflections)

    def analyze_decisions(self, episodes: list) -> list[Reflection]:
        """Analyze a set of episodes and generate reflections."""
        reflections: list[Reflection] = []
        self._criticism_count += 1

        # 1. Outcome analysis
        outcomes: dict[str, list[str]] = {"success": [], "failure": [], "unknown": []}
        for ep in episodes:
            outcome = getattr(ep, 'outcome', 'unknown') if hasattr(ep, 'outcome') else 'unknown'
            outcomes.get(outcome, []).append(ep)

        if len(outcomes.get("failure", [])) > len(outcomes.get("success", [])):
            ref = Reflection(
                insight=f"More failures ({len(outcomes['failure'])}) than successes ({len(outcomes['success'])})",
                category="pattern",
                supporting_episodes=[getattr(e, 'id', '') for e in outcomes.get("failure", [])[:5]],
                confidence=0.6,
                recommendation="Review failure patterns and adjust approach",
            )
            reflections.append(ref)

        # 2. Pattern detection
        event_types: dict[str, int] = {}
        type_outcomes: dict[str, dict[str, int]] = {}
        for ep in episodes:
            etype = getattr(ep, 'event_type', 'unknown') if hasattr(ep, 'event_type') else 'unknown'
            outcome = getattr(ep, 'outcome', 'unknown') if hasattr(ep, 'outcome') else 'unknown'
            event_types[etype] = event_types.get(etype, 0) + 1
            type_outcomes.setdefault(etype, {"success": 0, "failure": 0, "unknown": 0})
            type_outcomes[etype][outcome] = type_outcomes[etype].get(outcome, 0) + 1

        for etype, outcomes_dict in type_outcomes.items():
            total = sum(outcomes_dict.values())
            if total >= 3:  # Needs enough samples
                fail_rate = outcomes_dict.get("failure", 0) / total
                if fail_rate > 0.6:
                    ref = Reflection(
                        insight=f"{etype} actions fail {fail_rate:.0%} of the time",
                        category="pattern",
                        supporting_episodes=[getattr(e, 'id', '') for e in episodes 
                                            if getattr(e, 'event_type', None) == etype][:3],
                        confidence=fail_rate,
                        recommendation=f"Review and improve {etype} strategy",
                    )
                    reflections.append(ref)

        # 3. Confidence change analysis
        for ep in episodes:
            bb = getattr(ep, 'beliefs_before', {}) if hasattr(ep, 'beliefs_before') else {}
            ba = getattr(ep, 'beliefs_after', {}) if hasattr(ep, 'beliefs_after') else {}
            for key in ba:
                if key in bb and abs(ba[key] - bb[key]) > 0.5:
                    ref = Reflection(
                        insight=f"Belief '{key}' changed from {bb[key]:.2f} to {ba[key]:.2f}",
                        category="pattern",
                        supporting_episodes=[getattr(ep, 'id', '')],
                        confidence=0.7,
                        recommendation=f"Investigate what caused the shift in '{key}'",
                    )
                    reflections.append(ref)

        self._reflections.extend(reflections)
        return reflections

    def self_criticize(self, decisions: list[dict]) -> list[str]:
        """Self-criticism: identify suboptimal past decisions."""
        criticisms: list[str] = []
        for decision in decisions:
            outcome = decision.get("outcome", "unknown")
            if outcome == "failure":
                # Check if alternatives were considered
                alternatives = decision.get("alternatives", [])
                if not alternatives:
                    criticisms.append(
                        f"No alternatives considered for decision: {decision.get('description', '')}"
                    )
                # Check if evidence was sufficient
                evidence = decision.get("evidence_count", 0)
                if evidence < 3:
                    criticisms.append(
                        f"Insufficient evidence ({evidence} items) for: {decision.get('description', '')}"
                    )
        return criticisms

    def generate_recommendations(self, episodes: list) -> list[dict[str, Any]]:
        """Generate actionable recommendations from analysis."""
        recommendations: list[dict[str, Any]] = []

        # Find repeated failure patterns
        failure_descriptions: dict[str, int] = {}
        for ep in episodes:
            outcome = getattr(ep, 'outcome', '') if hasattr(ep, 'outcome') else ''
            if outcome == "failure":
                desc = getattr(ep, 'description', '')[:50] if hasattr(ep, 'description') else ''
                failure_descriptions[desc] = failure_descriptions.get(desc, 0) + 1

        for desc, count in failure_descriptions.items():
            if count >= 2:
                recommendations.append({
                    "type": "avoid_pattern",
                    "pattern": desc,
                    "frequency": count,
                    "recommendation": f"Consider alternative to this recurring failure",
                })

        return recommendations

    def summary(self) -> dict[str, Any]:
        categories: dict[str, int] = {}
        for r in self._reflections:
            categories[r.category] = categories.get(r.category, 0) + 1
        return {
            "total_reflections": len(self._reflections),
            "by_category": categories,
            "criticism_cycles": self._criticism_count,
            "applied": sum(1 for r in self._reflections if r.applied),
        }
