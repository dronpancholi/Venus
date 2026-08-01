"""
GENESIS Ω Phase 6: Engineering Economics.

Track and optimize engineering economics across the platform.
Compute investment scores and rank improvement opportunities by expected return.
"""

from __future__ import annotations

import json
import time
from collections import defaultdict
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from math import exp
from typing import Any

from genesis.utils.identity import generate_id


@dataclass
class EconomicMetric:
    name: str
    value: float
    unit: str = ""
    tags: dict[str, str] = field(default_factory=dict)
    timestamp: float = 0.0

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = time.time()


@dataclass
class InvestmentScore:
    opportunity_id: str
    name: str
    category: str
    expected_return: float
    implementation_cost: float
    risk: float
    confidence: float
    score: float
    factors: dict[str, float] = field(default_factory=dict)


class EconomicsEngine:
    """Engineering economics engine — tracks costs, computes ROI, ranks opportunities."""

    def __init__(self):
        self._metrics: list[EconomicMetric] = []
        self._scores: list[InvestmentScore] = []

    def record(self, name: str, value: float, unit: str = "", tags: dict[str, str] | None = None):
        self._metrics.append(EconomicMetric(
            name=name, value=value, unit=unit, tags=tags or {},
        ))

    def metrics(self, name: str | None = None, since: float = 0) -> list[EconomicMetric]:
        results = [m for m in self._metrics if m.timestamp >= since]
        if name:
            results = [m for m in results if m.name == name]
        return results

    def latest_value(self, name: str) -> float | None:
        matching = [m for m in self._metrics if m.name == name]
        if not matching:
            return None
        return max(matching, key=lambda m: m.timestamp).value

    def average(self, name: str, window: int = 10) -> float | None:
        matching = [m.value for m in self._metrics if m.name == name]
        if not matching:
            return None
        recent = matching[-window:]
        return sum(recent) / len(recent)

    # ── Specific metric computations ──

    def engineering_cost(self, agent_seconds: float, compute_units: float,
                         storage_gb: float) -> float:
        cost = agent_seconds * 0.01 + compute_units * 0.05 + storage_gb * 0.10
        self.record("engineering_cost", cost, "credits", {
            "agent_seconds": str(round(agent_seconds, 2)),
            "compute_units": str(round(compute_units, 2)),
            "storage_gb": str(round(storage_gb, 2)),
        })
        return cost

    def maintenance_cost(self, complexity: float, coupling: float,
                         test_coverage: float) -> float:
        if test_coverage <= 0:
            return 1.0
        cost = (complexity * coupling) / test_coverage
        self.record("maintenance_cost", round(cost, 4), "index", {
            "complexity": str(round(complexity, 2)),
            "coupling": str(round(coupling, 2)),
            "test_coverage": str(round(test_coverage, 2)),
        })
        return cost

    def technical_debt(self, maturity: float, risk: float, lines: int) -> float:
        debt = (1.0 - maturity) * risk * (lines / 1000.0)
        self.record("technical_debt", round(debt, 4), "kcredits", {
            "maturity": str(round(maturity, 2)),
            "risk": str(round(risk, 2)),
            "lines": str(lines),
        })
        return debt

    def research_roi(self, confidence_gain: float, knowledge_created: float,
                     cost: float) -> float:
        if cost <= 0:
            return 0.0
        roi = (confidence_gain * knowledge_created) / cost
        self.record("research_roi", round(roi, 4), "ratio")
        return roi

    def memory_roi(self, recall_accuracy: float, storage_cost: float) -> float:
        if storage_cost <= 0:
            return 0.0
        roi = recall_accuracy / storage_cost
        self.record("memory_roi", round(roi, 4), "ratio")
        return roi

    def agent_productivity(self, tasks_completed: int, value: float,
                           agent_seconds: float) -> float:
        if agent_seconds <= 0:
            return 0.0
        prod = (tasks_completed * value) / agent_seconds
        self.record("agent_productivity", round(prod, 4), "value_per_second")
        return prod

    def repository_value(self, test_coverage: float, doc_coverage: float,
                         maturity: float) -> float:
        val = (test_coverage + doc_coverage + maturity) / 3.0
        self.record("repository_value", round(val, 4), "score")
        return val

    def knowledge_growth(self, new_entities: int, total_entities: int) -> float:
        if total_entities <= 0:
            return 0.0
        growth = new_entities / total_entities
        self.record("knowledge_growth", round(growth, 4), "fraction")
        return growth

    def test_value(self, bugs_caught: int, severity: float,
                   execution_time: float) -> float:
        if execution_time <= 0:
            return 0.0
        val = (bugs_caught * severity) / execution_time
        self.record("test_value", round(val, 4), "value_per_second")
        return val

    def performance_value(self, latency_improvement: float,
                          throughput_improvement: float) -> float:
        val = (latency_improvement + throughput_improvement) / 2.0
        self.record("performance_value", round(val, 4), "score")
        return val

    def prediction_accuracy(self, correct: int, total: int) -> float:
        if total <= 0:
            return 0.0
        acc = correct / total
        self.record("prediction_accuracy", round(acc, 4), "fraction")
        return acc

    def optimization_gain(self, before_cost: float, after_cost: float) -> float:
        if before_cost <= 0:
            return 0.0
        gain = (before_cost - after_cost) / before_cost
        self.record("optimization_gain", round(gain, 4), "fraction")
        return gain

    # ── Investment scoring ──

    def score_opportunity(self, opportunity_id: str, name: str, category: str,
                          expected_return: float, implementation_cost: float,
                          risk: float, confidence: float,
                          factors: dict[str, float] | None = None) -> InvestmentScore:
        if implementation_cost <= 0:
            score = 0.0
        else:
            risk_penalty = 1.0 - risk
            score = (expected_return * confidence * risk_penalty) / implementation_cost

        inv = InvestmentScore(
            opportunity_id=opportunity_id,
            name=name,
            category=category,
            expected_return=expected_return,
            implementation_cost=implementation_cost,
            risk=risk,
            confidence=confidence,
            score=round(score, 4),
            factors=factors or {},
        )
        self._scores.append(inv)
        return inv

    def ranked_opportunities(self, min_score: float = 0.0,
                             category: str | None = None) -> list[InvestmentScore]:
        results = list(self._scores)
        if category:
            results = [s for s in results if s.category == category]
        results.sort(key=lambda s: s.score, reverse=True)
        if min_score > 0:
            results = [s for s in results if s.score >= min_score]
        return results

    def best_opportunity(self) -> InvestmentScore | None:
        ranked = self.ranked_opportunities()
        return ranked[0] if ranked else None

    # ── Summary ──

    def summary(self) -> dict[str, Any]:
        metric_names = set(m.name for m in self._metrics)
        return {
            "total_metrics": len(self._metrics),
            "total_opportunities": len(self._scores),
            "metrics": {
                name: {
                    "count": len([m for m in self._metrics if m.name == name]),
                    "latest": self.latest_value(name),
                    "average": self.average(name),
                }
                for name in sorted(metric_names)
            },
            "top_opportunities": [
                {"name": s.name, "score": s.score, "category": s.category}
                for s in self.ranked_opportunities()[:5]
            ],
        }

    def save(self, path: str):
        data = {
            "metrics": [asdict(m) for m in self._metrics],
            "scores": [asdict(s) for s in self._scores],
            "summary": self.summary(),
        }
        with open(path, "w") as f:
            json.dump(data, f, indent=2, default=str)
