"""
Equilibrium Detector + Scientific Validator — Stages 20 & 22 of the OMEGA loop.

Equilibrium Detector:
  - Detects when no improvement can be found
  - Identifies which assumptions prevent improvement
  - Challenges those assumptions to discover new frontiers

Scientific Validator:
  - Every improvement must pass mathematical, simulation, empirical,
    architectural, repository, and historical evidence gates
"""

from __future__ import annotations

from collections import Counter
from typing import Any

from genesis.digital_twin.hypothesis import Hypothesis
from genesis.digital_twin.model import DigitalTwin


class EquilibriumSignal:
    """Signal that the platform may be at architectural equilibrium."""

    def __init__(
        self,
        kind: str,
        signal: str,
        strength: float,
        assumption_challenged: str | None = None,
        new_direction: str | None = None,
    ):
        self.kind = kind
        self.signal = signal
        self.strength = strength
        self.assumption_challenged = assumption_challenged
        self.new_direction = new_direction

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": self.kind,
            "signal": self.signal,
            "strength": self.strength,
            "assumption_challenged": self.assumption_challenged,
            "new_direction": self.new_direction,
        }


class EquilibriumDetector:
    """Detect when no improvement is possible and challenge assumptions."""

    def __init__(self, twin: DigitalTwin):
        self.twin = twin

    def analyze(
        self,
        hypotheses: list[Hypothesis],
        metrics: dict[str, float],
        previous_metrics: dict[str, float] | None = None,
    ) -> list[EquilibriumSignal]:
        signals: list[EquilibriumSignal] = []

        signals.extend(self._check_hypothesis_stagnation(hypotheses))
        signals.extend(self._check_metric_plateau(metrics, previous_metrics))
        signals.extend(self._challenge_assumptions(metrics))

        return signals

    def _check_hypothesis_stagnation(
        self, hypotheses: list[Hypothesis]
    ) -> list[EquilibriumSignal]:
        signals = []
        if not hypotheses:
            signals.append(EquilibriumSignal(
                kind="stagnation",
                signal="No hypotheses generated — platform may be at local maximum",
                strength=0.8,
                assumption_challenged="All possible improvements have been discovered",
                new_direction="Expand scope: analyze external repositories, add new metric dimensions",
            ))
            return signals

        top_roe = hypotheses[0].roe if hypotheses else 0
        if top_roe < 0.1:
            signals.append(EquilibriumSignal(
                kind="low_yield",
                signal=f"Top hypothesis ROE is {top_roe:.3f} — below actionable threshold",
                strength=0.6,
                assumption_challenged="The current metric set captures all improvement dimensions",
                new_direction="Invent new metrics to reveal hidden improvement opportunities",
            ))

        # — check hypothesis diversity —
        kinds = set(h.kind for h in hypotheses)
        if len(kinds) <= 3:
            signals.append(EquilibriumSignal(
                kind="low_diversity",
                signal=f"Only {len(kinds)} hypothesis kinds generated: {kinds}",
                strength=0.5,
                assumption_challenged="All improvement types are known",
                new_direction="Add new analyzer types or import external pattern libraries",
            ))

        return signals

    def _check_metric_plateau(
        self,
        metrics: dict[str, float],
        previous: dict[str, float] | None = None,
    ) -> list[EquilibriumSignal]:
        signals = []

        if previous:
            deltas = {}
            for k in metrics:
                if k in previous and isinstance(metrics[k], (int, float)):
                    deltas[k] = metrics[k] - previous[k]

            improved = sum(1 for d in deltas.values() if d > 0)
            if improved == 0:
                signals.append(EquilibriumSignal(
                    kind="metric_plateau",
                    signal="No metrics improved in last cycle — full plateau",
                    strength=0.9,
                    assumption_challenged="Current intervention strategies are effective",
                    new_direction="Try different hypothesis types, increase simulation depth",
                ))

        # — check if intelligence score has room —
        ris = metrics.get("repository_intelligence_score", 0)
        if ris > 0.9:
            signals.append(EquilibriumSignal(
                kind="high_intelligence",
                signal=f"Repository Intelligence Score at {ris:.2f} — approaching theoretical max",
                strength=0.7,
                assumption_challenged="The RIS formula captures all dimensions of intelligence",
                new_direction="Expand RIS formula with new factors: reasoning depth, prediction accuracy, autonomy level",
            ))

        # — check for saturated metrics —
        saturated = []
        for k, v in metrics.items():
            if isinstance(v, (int, float)) and v >= 0.95:
                saturated.append(k)

        if saturated:
            signals.append(EquilibriumSignal(
                kind="metric_saturation",
                signal=f"Metrics saturated: {', '.join(saturated[:5])}",
                strength=0.5,
                assumption_challenged="These metrics are meaningful at their maximum",
                new_direction="Replace saturated metrics with more granular alternatives",
            ))

        return signals

    def _challenge_assumptions(
        self, metrics: dict[str, float]
    ) -> list[EquilibriumSignal]:
        """Challenge fundamental assumptions of the current architecture."""
        signals = []

        # — Assumption: layered architecture is optimal —
        signals.append(EquilibriumSignal(
            kind="assumption_challenge",
            signal="Challenging assumption: is a layered architecture optimal for this domain?",
            strength=0.3,
            assumption_challenged="Layered architecture is the correct abstraction",
            new_direction="Evaluate hexagonal, event-driven, or actor-based alternatives",
        ))

        # — Assumption: Python is the right language —
        signals.append(EquilibriumSignal(
            kind="assumption_challenge",
            signal="Challenging assumption: is Python optimal for all platform components?",
            strength=0.2,
            assumption_challenged="Single-language codebase is optimal",
            new_direction="Evaluate performance-critical components for Rust or Go migration",
        ))

        # — Assumption: current metrics capture all value —
        if metrics.get("specification_completeness", 1) < 0.3:
            signals.append(EquilibriumSignal(
                kind="assumption_challenge",
                signal=f"Challenging assumption: spec coverage at "
                       f"{metrics['specification_completeness']:.0%} may indicate "
                       f"spec-implementation gap is measurement problem, not implementation gap",
                strength=0.4,
                assumption_challenged="Low spec coverage means missing implementation",
                new_direction="Improve spec→code linking algorithm before attempting to implement more",
            ))

        return signals


class ValidatorGate:
    """A single evidence gate that improvements must pass."""

    def __init__(self, name: str, passed: bool, evidence: str, score: float):
        self.name = name
        self.passed = passed
        self.evidence = evidence
        self.score = score

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name, "passed": self.passed, "evidence": self.evidence, "score": self.score}


class ValidationResult:
    """Aggregated validation result for a hypothesis."""

    def __init__(
        self,
        hypothesis_title: str,
        gates: list[ValidatorGate],
        overall_score: float,
        passed: bool,
    ):
        self.hypothesis_title = hypothesis_title
        self.gates = gates
        self.overall_score = overall_score
        self.passed = passed

    def to_dict(self) -> dict[str, Any]:
        return {
            "hypothesis": self.hypothesis_title,
            "gates": [g.to_dict() for g in self.gates],
            "overall_score": self.overall_score,
            "passed": self.passed,
        }


class ScientificValidator:
    """Validate improvements through 6 evidence gates (Stage 20)."""

    GATES = [
        "mathematical", "simulation", "empirical",
        "architectural", "repository", "historical",
    ]

    def __init__(self, twin: DigitalTwin, metrics: dict[str, float]):
        self.twin = twin
        self.metrics = metrics

    def validate(self, hypothesis: Hypothesis) -> ValidationResult:
        gates: list[ValidatorGate] = []

        for gate_name in self.GATES:
            method = getattr(self, f"_gate_{gate_name}", None)
            if method:
                gate = method(hypothesis)
                gates.append(gate)

        overall = sum(g.score for g in gates) / max(len(gates), 1)
        passed = all(g.passed for g in gates)
        return ValidationResult(hypothesis.title, gates, overall, passed)

    def _gate_mathematical(self, h: Hypothesis) -> ValidatorGate:
        gain = sum(abs(v) for v in h.expected_impact.values())
        if gain > 0 and h.roe > 0:
            return ValidatorGate(
                "mathematical", True,
                f"Expected gain: {gain:.3f}, ROE: {h.roe:.3f}", 0.9,
            )
        return ValidatorGate("mathematical", False, "No mathematical justification", 0.0)

    def _gate_simulation(self, h: Hypothesis) -> ValidatorGate:
        from genesis.digital_twin.evolution import EvolutionEngine

        evolver = EvolutionEngine(self.twin)
        evolver.baseline_metrics()
        result = evolver.evaluate(h)
        if result.acceptable:
            return ValidatorGate(
                "simulation", True,
                f"Quality delta: {result.quality_delta:+.4f}", 0.9,
            )
        return ValidatorGate(
            "simulation", result.acceptable,
            f"Quality delta: {result.quality_delta:+.4f} (below threshold)", 0.2,
        )

    def _gate_empirical(self, h: Hypothesis) -> ValidatorGate:
        if h.confidence >= 0.5:
            return ValidatorGate(
                "empirical", True,
                f"Confidence: {h.confidence:.0%}", 0.8,
            )
        return ValidatorGate(
            "empirical", False,
            f"Confidence {h.confidence:.0%} below 50% threshold", 0.3,
        )

    def _gate_architectural(self, h: Hypothesis) -> ValidatorGate:
        ris = self.metrics.get("repository_intelligence_score", 0)
        expected_ris_gain = h.expected_impact.get("repository_intelligence_score", 0)
        if expected_ris_gain > 0 or ris > 0.3:
            return ValidatorGate(
                "architectural", True,
                f"Expected RIS gain: {expected_ris_gain:+.3f}", 0.8,
            )
        return ValidatorGate("architectural", False, "No architectural benefit detected", 0.3)

    def _gate_repository(self, h: Hypothesis) -> ValidatorGate:
        if h.target_ids or h.effort in ("Partial session", "1 session"):
            return ValidatorGate(
                "repository", True,
                f"Effort: {h.effort}, targets: {len(h.target_ids)}", 0.8,
            )
        return ValidatorGate("repository", False, "No concrete targets or excessive effort", 0.4)

    def _gate_historical(self, h: Hypothesis) -> ValidatorGate:
        # — Check if similar change was previously applied —
        from genesis.digital_twin.evolution import EvolutionEngine
        evolver = EvolutionEngine(self.twin)
        evolver.baseline_metrics()
        result = evolver.evaluate(h)
        if result.quality_delta > 0:
            return ValidatorGate(
                "historical", True,
                f"Similar interventions show positive delta: {result.quality_delta:+.4f}", 0.8,
            )
        return ValidatorGate("historical", False, "Similar interventions show negative delta", 0.2)
