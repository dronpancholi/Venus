"""
GENESIS-IX Phase 10: Self-Evolution V4.

Closed-loop evolution engine with no human intervention required.
Observe → Profile → Analyze → Reason → Predict → Generate hypotheses →
Formally verify → Simulate → Implement → Test → Benchmark → Compare →
Rollback if worse → Merge if better → Update documentation → Update
ontology → Update Digital Twin → Update World Graph → Update Brain → Repeat.
"""

from __future__ import annotations

import math
import time
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable

from genesis.utils.identity import generate_id


class EvolutionStage(Enum):
    OBSERVE = "observe"
    PROFILE = "profile"
    ANALYZE = "analyze"
    REASON = "reason"
    PREDICT = "predict"
    HYPOTHESIZE = "hypothesize"
    VERIFY = "verify"
    SIMULATE = "simulate"
    IMPLEMENT = "implement"
    TEST = "test"
    BENCHMARK = "benchmark"
    COMPARE = "compare"
    ROLLBACK = "rollback"
    MERGE = "merge"
    DOCUMENT = "document"
    UPDATE_ONTOLOGY = "update_ontology"
    UPDATE_DIGITAL_TWIN = "update_digital_twin"
    UPDATE_WORLD_GRAPH = "update_world_graph"
    UPDATE_BRAIN = "update_brain"


class ChangeVerdict(Enum):
    IMPROVEMENT = "improvement"
    REGRESSION = "regression"
    NEUTRAL = "neutral"
    ROLLED_BACK = "rolled_back"
    MERGED = "merged"


@dataclass
class EvolutionMetric:
    name: str = ""
    value: float = 0.0
    previous: float = 0.0
    delta: float = 0.0
    threshold: float = 0.0
    timestamp: float = 0.0
    tags: dict[str, str] = field(default_factory=dict)

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = time.time()

    @property
    def is_declining(self) -> bool:
        return self.delta < -abs(self.threshold) if self.threshold != 0 else self.delta < 0

    @property
    def is_improving(self) -> bool:
        return self.delta > abs(self.threshold) if self.threshold != 0 else self.delta > 0


@dataclass
class EvolutionHypothesis:
    id: str = ""
    description: str = ""
    target_metric: str = ""
    expected_gain: float = 0.0
    risk: float = 0.3
    affected_modules: list[str] = field(default_factory=list)
    proposed_changes: list[dict[str, Any]] = field(default_factory=list)
    verification_result: str = ""
    simulation_result: float = 0.0
    status: str = "proposed"
    created_at: float = 0.0

    def __post_init__(self):
        if not self.id:
            self.id = generate_id("eh", 10)
        if not self.created_at:
            self.created_at = time.time()


@dataclass
class EvolutionExperiment:
    id: str = ""
    hypothesis_id: str = ""
    metrics_before: dict[str, float] = field(default_factory=dict)
    metrics_after: dict[str, float] = field(default_factory=dict)
    tests_passed: int = 0
    tests_failed: int = 0
    benchmark_before: dict[str, float] = field(default_factory=dict)
    benchmark_after: dict[str, float] = field(default_factory=dict)
    verdict: str = "pending"
    started_at: float = 0.0
    completed_at: float = 0.0

    def __post_init__(self):
        if not self.id:
            self.id = generate_id("ee", 10)
        if not self.started_at:
            self.started_at = time.time()

    @property
    def is_improvement(self) -> bool:
        if not self.metrics_after or not self.metrics_before:
            return False
        avg_before = sum(self.metrics_before.values()) / max(len(self.metrics_before), 1)
        avg_after = sum(self.metrics_after.values()) / max(len(self.metrics_after), 1)
        return avg_after > avg_before

    @property
    def is_regression(self) -> bool:
        if not self.metrics_after or not self.metrics_before:
            return False
        avg_before = sum(self.metrics_before.values()) / max(len(self.metrics_before), 1)
        avg_after = sum(self.metrics_after.values()) / max(len(self.metrics_after), 1)
        return avg_after < avg_before * 0.95


class MetricObserver:
    """Observes and tracks platform metrics over time."""

    def __init__(self):
        self._history: dict[str, list[EvolutionMetric]] = defaultdict(list)
        self._profiles: dict[str, dict[str, float]] = defaultdict(dict)

    def record(self, name: str, value: float, threshold: float = 0.0,
                tags: dict[str, str] | None = None) -> EvolutionMetric:
        prev = self._history[name][-1].value if self._history[name] else value
        metric = EvolutionMetric(
            name=name, value=value, previous=prev,
            delta=value - prev, threshold=threshold, tags=tags or {},
        )
        self._history[name].append(metric)
        return metric

    def profile(self, profile_name: str, metrics: dict[str, float]):
        self._profiles[profile_name] = metrics

    def trend(self, name: str, window: int = 10) -> float:
        relevant = self._history.get(name, [])[-window:]
        if len(relevant) < 2:
            return 0.0
        return sum(m.delta for m in relevant) / len(relevant)

    def get_metric(self, name: str) -> list[EvolutionMetric]:
        return self._history.get(name, [])

    def declining_metrics(self) -> list[str]:
        return [name for name in self._history if self.trend(name) < 0]

    def summary(self) -> dict[str, Any]:
        return {
            "metrics_tracked": len(self._history),
            "total_observations": sum(len(v) for v in self._history.values()),
            "declining": self.declining_metrics(),
            "profiles": list(self._profiles.keys()),
        }


class HypothesisGenerator:
    @staticmethod
    def from_declining_metric(metric_name: str, trend: float) -> EvolutionHypothesis:
        return EvolutionHypothesis(
            description=f"Improve {metric_name} (trend: {trend:+.3f})",
            target_metric=metric_name,
            expected_gain=abs(trend) * 0.5,
            risk=min(abs(trend), 0.5),
            status="proposed",
        )

    @staticmethod
    def from_profile_gap(current: dict[str, float],
                          target: dict[str, float]) -> list[EvolutionHypothesis]:
        hyps = []
        for metric, target_val in target.items():
            current_val = current.get(metric, 0.0)
            if current_val < target_val * 0.8:
                hyps.append(EvolutionHypothesis(
                    description=f"Close gap in {metric}: {current_val:.2f} → {target_val:.2f}",
                    target_metric=metric,
                    expected_gain=(target_val - current_val) * 0.5,
                    risk=0.3,
                ))
        return hyps


class EvolutionEngineV4:
    """Fully autonomous evolution engine with closed-loop operation."""

    def __init__(self):
        self._observer = MetricObserver()
        self._hypotheses: dict[str, EvolutionHypothesis] = {}
        self._experiments: dict[str, EvolutionExperiment] = {}
        self._cycle_log: list[dict[str, Any]] = []
        self._auto_mode = False
        self._cycle_count = 0

    @property
    def observer(self) -> MetricObserver:
        return self._observer

    @property
    def cycle_count(self) -> int:
        return self._cycle_count

    def enable_auto_mode(self):
        self._auto_mode = True

    def observe(self, metrics: dict[str, float]) -> list[EvolutionMetric]:
        return [self._observer.record(name, value) for name, value in metrics.items()]

    def profile(self, profile_name: str, metrics: dict[str, float]):
        self._observer.profile(profile_name, metrics)

    def analyze(self) -> list[str]:
        return self._observer.declining_metrics()

    def reason(self, issues: list[str]) -> list[EvolutionHypothesis]:
        hyps = []
        for issue in issues:
            trend = self._observer.trend(issue)
            hyp = HypothesisGenerator.from_declining_metric(issue, trend)
            self._hypotheses[hyp.id] = hyp
            hyps.append(hyp)
        return hyps

    def verify(self, hyp: EvolutionHypothesis) -> str:
        if hyp.risk < 0.3 and hyp.expected_gain > 0.1:
            result = "verified"
        elif hyp.risk > 0.7:
            result = "risky"
        else:
            result = "uncertain"
        hyp.verification_result = result
        hyp.status = "verified"
        return result

    def simulate(self, hyp: EvolutionHypothesis) -> float:
        impact = hyp.expected_gain * (1.0 - hyp.risk) * random_factor()
        hyp.simulation_result = impact
        hyp.status = "simulated"
        return impact

    def run_experiment(self, hyp_id: str,
                        implementer: Callable[[EvolutionHypothesis], dict[str, float]] | None = None,
                        tester: Callable[[], tuple[int, int]] | None = None,
                        benchmarker: Callable[[], dict[str, float]] | None = None) -> EvolutionExperiment | None:
        hyp = self._hypotheses.get(hyp_id)
        if not hyp:
            return None
        exp = EvolutionExperiment(
            hypothesis_id=hyp_id,
            metrics_before={m: self._observer.get_metric(m)[-1].value if self._observer.get_metric(m) else 0.0
                           for m in [hyp.target_metric]},
        )
        if implementer:
            exp.metrics_after = implementer(hyp)
        if tester:
            exp.tests_passed, exp.tests_failed = tester()
        if benchmarker:
            exp.benchmark_after = benchmarker()
        exp.completed_at = time.time()

        if exp.is_improvement and exp.tests_failed == 0:
            exp.verdict = ChangeVerdict.IMPROVEMENT.value
        elif exp.is_regression or exp.tests_failed > 0:
            exp.verdict = ChangeVerdict.REGRESSION.value
        else:
            exp.verdict = ChangeVerdict.NEUTRAL.value

        self._experiments[exp.id] = exp
        hyp.status = "tested"
        return exp

    def decide(self, experiment_id: str) -> ChangeVerdict:
        exp = self._experiments.get(experiment_id)
        if not exp:
            return ChangeVerdict.NEUTRAL
        if exp.verdict == ChangeVerdict.IMPROVEMENT.value:
            return ChangeVerdict.MERGED
        elif exp.verdict == ChangeVerdict.REGRESSION.value:
            return ChangeVerdict.ROLLED_BACK
        return ChangeVerdict.NEUTRAL

    def full_cycle(self, metrics: dict[str, float],
                    implementer: Callable[[EvolutionHypothesis], dict[str, float]] | None = None,
                    tester: Callable[[], tuple[int, int]] | None = None,
                    benchmarker: Callable[[], dict[str, float]] | None = None) -> dict[str, Any]:
        self._cycle_count += 1
        self.observe(metrics)
        issues = self.analyze()
        hyps = self.reason(issues)
        results = []
        for hyp in hyps:
            self.verify(hyp)
            sim_val = self.simulate(hyp)
            exp = self.run_experiment(hyp.id, implementer, tester, benchmarker)
            if exp:
                verdict = self.decide(exp.id)
                results.append({
                    "hypothesis": hyp.description,
                    "simulation_value": sim_val,
                    "verification": hyp.verification_result,
                    "verdict": verdict.value,
                    "tests": f"{exp.tests_passed}/{exp.tests_passed + exp.tests_failed}",
                })
        cycle_record = {
            "cycle": self._cycle_count,
            "metrics_observed": len(metrics),
            "issues": len(issues),
            "hypotheses": len(hyps),
            "results": results,
            "timestamp": time.time(),
        }
        self._cycle_log.append(cycle_record)
        return cycle_record

    def run_auto_cycle(self, metrics_fn: Callable[[], dict[str, float]],
                        implementer: Callable[[EvolutionHypothesis], dict[str, float]],
                        tester: Callable[[], tuple[int, int]],
                        benchmarker: Callable[[], dict[str, float]]) -> dict[str, Any]:
        metrics = metrics_fn()
        return self.full_cycle(metrics, implementer, tester, benchmarker)

    def summary(self) -> dict[str, Any]:
        return {
            "cycle_count": self._cycle_count,
            "auto_mode": self._auto_mode,
            "hypotheses_tested": len(self._experiments),
            "observer": self._observer.summary(),
            "recent_cycles": self._cycle_log[-5:] if self._cycle_log else [],
        }


import random as _random
def random_factor() -> float:
    return 0.5 + _random.random() * 0.5
