"""
Engineering Simulation Engine (Mission 24) — Predict before implementing.

Simulates engineering changes and produces impact assessments:
- Affected modules, services, APIs, reports, tests
- Expected failures, confidence, rollback cost
- Architectural, performance, and technical debt impact
"""

from __future__ import annotations

import time
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from threading import RLock
from typing import Any, Callable

from genesis.utils.identity import generate_id


class SimulationType(Enum):
    SERVICE_REMOVAL = "service_removal"
    RESPONSIBILITY_MOVE = "responsibility_move"
    MODULE_MERGE = "module_merge"
    API_RENAME = "api_rename"
    DEPENDENCY_CHANGE = "dependency_change"
    GRAPH_CHANGE = "graph_change"
    BOOT_CHANGE = "boot_change"
    RUNTIME_FAILURE = "runtime_failure"
    SERVICE_FAILURE = "service_failure"
    PLUGIN_FAILURE = "plugin_failure"
    KNOWLEDGE_CORRUPTION = "knowledge_corruption"
    MEMORY_LOSS = "memory_loss"
    GOVERNANCE_FAILURE = "governance_failure"


class SimulationStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class Confidence(Enum):
    HIGH = 0.9
    MEDIUM = 0.6
    LOW = 0.3
    SPECULATIVE = 0.1


@dataclass
class SimulatedImpact:
    affected_modules: list[str] = field(default_factory=list)
    affected_services: list[str] = field(default_factory=list)
    affected_apis: list[str] = field(default_factory=list)
    affected_reports: list[str] = field(default_factory=list)
    affected_tests: list[str] = field(default_factory=list)
    expected_failures: list[str] = field(default_factory=list)
    confidence: float = 0.5
    rollback_cost: str = "low"
    estimated_effort_hours: float = 1.0
    architectural_impact: str = "none"
    performance_impact: str = "none"
    technical_debt_impact: str = "none"


@dataclass
class SimulationResult:
    id: str = ""
    sim_type: SimulationType = SimulationType.SERVICE_REMOVAL
    target: str = ""
    status: SimulationStatus = SimulationStatus.PENDING
    impact: SimulatedImpact = field(default_factory=SimulatedImpact)
    description: str = ""
    started_at: float = 0.0
    completed_at: float = 0.0
    errors: list[str] = field(default_factory=list)


class SimulationEngine:
    """Simulates engineering changes and assesses impact."""

    def __init__(self):
        self._history: list[SimulationResult] = []
        self._lock = RLock()
        self._models: dict[str, Callable] = {}
        self._register_default_models()

    def _register_default_models(self):
        self.register_model(SimulationType.SERVICE_REMOVAL, self._simulate_service_removal)
        self.register_model(SimulationType.RESPONSIBILITY_MOVE, self._simulate_responsibility_move)
        self.register_model(SimulationType.DEPENDENCY_CHANGE, self._simulate_dependency_change)

    def register_model(self, sim_type: SimulationType, model_fn: Callable):
        self._models[sim_type.value] = model_fn

    def simulate(self, sim_type: SimulationType, target: str,
                 context: dict[str, Any] | None = None) -> SimulationResult:
        result = SimulationResult(
            sim_type=sim_type, target=target,
            status=SimulationStatus.RUNNING, started_at=time.time(),
        )
        try:
            model = self._models.get(sim_type.value)
            if model:
                impact = model(target, context or {})
                result.impact = impact
                result.status = SimulationStatus.COMPLETED
            else:
                result.status = SimulationStatus.FAILED
                result.errors.append(f"No model registered for {sim_type.value}")
        except Exception as e:
            result.status = SimulationStatus.FAILED
            result.errors.append(str(e))
        result.completed_at = time.time()

        with self._lock:
            self._history.append(result)
        return result

    def simulate_many(self, simulations: list[tuple[SimulationType, str, dict]]) -> list[SimulationResult]:
        return [self.simulate(st, tg, ctx) for st, tg, ctx in simulations]

    def history(self, limit: int = 20) -> list[SimulationResult]:
        with self._lock:
            return list(self._history[-limit:])

    def _simulate_service_removal(self, target: str, ctx: dict) -> SimulatedImpact:
        deps = ctx.get("dependents", [])
        impact = SimulatedImpact(
            affected_modules=[target] + deps,
            affected_services=[target],
            affected_apis=[f"{target}.*"],
            affected_reports=[f"Reports about {target}"],
            affected_tests=[f"tests for {target}"],
            expected_failures=[f"{d} depends on {target}" for d in deps],
            confidence=0.8 if deps else 0.95,
            rollback_cost="high" if len(deps) > 3 else "medium",
            estimated_effort_hours=len(deps) * 2.0 + 4.0,
            architectural_impact="major" if len(deps) > 5 else "moderate",
        )
        return impact

    def _simulate_responsibility_move(self, target: str, ctx: dict) -> SimulatedImpact:
        impact = SimulatedImpact(
            affected_modules=[target, ctx.get("target_module", "unknown")],
            affected_services=[target],
            affected_apis=[f"{target}.*", f"{ctx.get('target_module', '?')}.*"],
            affected_tests=[],
            confidence=0.7,
            rollback_cost="medium",
            estimated_effort_hours=8.0,
            architectural_impact="moderate" if target else "minor",
        )
        return impact

    def _simulate_dependency_change(self, target: str, ctx: dict) -> SimulatedImpact:
        consumers = ctx.get("consumers", [])
        impact = SimulatedImpact(
            affected_modules=[target] + consumers,
            affected_services=consumers,
            expected_failures=[f"{c} may break from {target} API change" for c in consumers],
            confidence=0.6 if consumers else 0.9,
            rollback_cost="medium" if consumers else "low",
            estimated_effort_hours=len(consumers) * 1.0,
            architectural_impact="moderate" if consumers else "minor",
        )
        return impact

    def summary(self) -> dict[str, Any]:
        with self._lock:
            completed = sum(1 for r in self._history if r.status == SimulationStatus.COMPLETED)
            failed = sum(1 for r in self._history if r.status == SimulationStatus.FAILED)
            return {
                "total_simulations": len(self._history),
                "completed": completed,
                "failed": failed,
                "models_registered": len(self._models),
                "avg_confidence": sum(r.impact.confidence for r in self._history if r.status == SimulationStatus.COMPLETED) / max(1, completed),
            }
