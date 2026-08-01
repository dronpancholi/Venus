"""
Engineering Experiment Platform (Program H) — hypothesis testing as experiments.

Every hypothesis becomes an experiment:
  1. Design experiment
  2. Select repositories
  3. Run simulation
  4. Collect metrics
  5. Compare outcomes
  6. Accept or reject hypothesis
  7. Publish evidence
"""

from __future__ import annotations

import random
import time
from dataclasses import dataclass, field
from typing import Any

from genesis.laboratory.genome.model import SoftwareGenome, FitnessScore


@dataclass
class ExperimentDesign:
    """Design of an engineering experiment."""
    hypothesis_id: str = ""
    hypothesis: str = ""
    prediction: str = ""
    control_repos: list[str] = field(default_factory=list)
    treatment_repos: list[str] = field(default_factory=list)
    metrics: list[str] = field(default_factory=list)
    min_sample_size: int = 2
    significance_level: float = 0.05


@dataclass
class ExperimentResult:
    """Result of running an experiment."""
    experiment_id: str = ""
    hypothesis: str = ""
    accepted: bool = False
    p_value: float = 1.0
    effect_size: float = 0.0
    control_metrics: dict[str, float] = field(default_factory=dict)
    treatment_metrics: dict[str, float] = field(default_factory=dict)
    evidence: list[str] = field(default_factory=list)
    timestamp: float = 0.0
    duration: float = 0.0


@dataclass
class ExperimentHistory:
    """History of all experiments run."""
    experiments: list[ExperimentResult] = field(default_factory=list)

    @property
    def acceptance_rate(self) -> float:
        if not self.experiments:
            return 0.0
        return sum(1 for e in self.experiments if e.accepted) / len(self.experiments)

    def summary(self) -> dict[str, Any]:
        return {
            "total": len(self.experiments),
            "accepted": sum(1 for e in self.experiments if e.accepted),
            "rejected": sum(1 for e in self.experiments if not e.accepted),
            "acceptance_rate": self.acceptance_rate,
            "avg_effect_size": (
                sum(e.effect_size for e in self.experiments) / len(self.experiments)
                if self.experiments else 0.0
            ),
        }


class ExperimentPlatform:
    """Execute engineering experiments."""

    def __init__(self):
        self.history = ExperimentHistory()

    def design_experiment(self, hypothesis_id: str, hypothesis: str,
                           prediction: str) -> ExperimentDesign:
        return ExperimentDesign(
            hypothesis_id=hypothesis_id,
            hypothesis=hypothesis,
            prediction=prediction,
        )

    def run(self, design: ExperimentDesign,
            genomes: dict[str, SoftwareGenome]) -> ExperimentResult:
        """Run an experiment comparing control vs treatment groups."""
        start = time.time()

        control_genomes = [genomes[r] for r in design.control_repos if r in genomes]
        treatment_genomes = [genomes[r] for r in design.treatment_repos if r in genomes]

        # Collect metrics
        control_metrics = self._aggregate_fitness(control_genomes)
        treatment_metrics = self._aggregate_fitness(treatment_genomes)

        # Compute effect size
        effect_size = self._compute_effect_size(control_metrics, treatment_metrics)

        # Simulate p-value (Monte Carlo permutation test approximation)
        p_value = self._estimate_p_value(control_genomes, treatment_genomes, 500)

        accepted = p_value < design.significance_level and abs(effect_size) > 0.05

        result = ExperimentResult(
            experiment_id=f"exp_{len(self.history.experiments) + 1}",
            hypothesis=design.hypothesis,
            accepted=accepted,
            p_value=round(p_value, 4),
            effect_size=round(effect_size, 4),
            control_metrics=control_metrics,
            treatment_metrics=treatment_metrics,
            evidence=[
                f"Control: {len(control_genomes)} genomes, "
                f"Treatment: {len(treatment_genomes)} genomes",
                f"Effect size: {effect_size:.4f}",
                f"P-value: {p_value:.4f}",
                f"Decision: {'ACCEPT' if accepted else 'REJECT'} {design.hypothesis}",
            ],
            timestamp=time.time(),
            duration=round(time.time() - start, 3),
        )

        self.history.experiments.append(result)
        return result

    def _aggregate_fitness(self, genomes: list[SoftwareGenome]) -> dict[str, float]:
        if not genomes:
            return {"overall": 0.0, "maintainability": 0.0, "quality": 0.0}

        metrics: dict[str, float] = {}
        keys = ["overall", "maintainability", "test_coverage",
                "coupling", "complexity", "maturity"]

        for key in keys:
            values = [getattr(g.fitness, key, 0.0) for g in genomes]
            metrics[key] = round(sum(values) / len(values), 4)

        return metrics

    def _compute_effect_size(self, control: dict[str, float],
                               treatment: dict[str, float]) -> float:
        """Cohen's d approximation."""
        diffs = []
        for key in control:
            if key in treatment:
                diffs.append(treatment[key] - control[key])
        return sum(diffs) / len(diffs) if diffs else 0.0

    def _estimate_p_value(self, control: list, treatment: list,
                           permutations: int = 500) -> float:
        """Approximate p-value via random permutation."""
        if not control or not treatment:
            return 1.0

        all_values = (
            [g.fitness.overall for g in control] +
            [g.fitness.overall for g in treatment]
        )
        n = len(control)
        observed_diff = abs(
            sum(all_values[:n]) / n - sum(all_values[n:]) / max(len(all_values[n:]), 1)
        )

        extreme = 0
        combined = list(all_values)
        for _ in range(permutations):
            random.shuffle(combined)
            perm_diff = abs(
                sum(combined[:n]) / n -
                sum(combined[n:]) / max(len(combined[n:]), 1)
            )
            if perm_diff >= observed_diff:
                extreme += 1

        return (extreme + 1) / (permutations + 1)
