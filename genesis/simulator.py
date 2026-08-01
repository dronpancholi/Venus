"""
GENESIS-VIII Program 3: Universal Repository Simulator.

Predict architecture changes, framework migration, dependency upgrades,
language migration, API evolution, service decomposition, performance,
complexity, cost, maintainability, security, test failures, deployment
failures, resource usage — before implementation.
"""

from __future__ import annotations

import warnings
warnings.warn(
    f"{__name__} is deprecated. Use genesis.simulator_v2.SimulatorEngineV2 instead.",
    DeprecationWarning,
    stacklevel=2,
)

import math
import random
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable

from genesis.utils.identity import generate_id


class SimulationScope(Enum):
    ARCHITECTURE = "architecture"
    FRAMEWORK_MIGRATION = "framework_migration"
    DEPENDENCY_UPGRADE = "dependency_upgrade"
    LANGUAGE_MIGRATION = "language_migration"
    API_EVOLUTION = "api_evolution"
    SERVICE_DECOMPOSITION = "service_decomposition"
    PERFORMANCE = "performance"
    COMPLEXITY = "complexity"
    COST = "cost"
    MAINTAINABILITY = "maintainability"
    SECURITY = "security"
    TEST_FAILURE = "test_failure"
    DEPLOYMENT_FAILURE = "deployment_failure"
    RESOURCE_USAGE = "resource_usage"


@dataclass
class SimulationInput:
    repository_path: str = ""
    current_architecture: dict[str, Any] = field(default_factory=dict)
    proposed_changes: list[dict[str, Any]] = field(default_factory=list)
    scope: list[SimulationScope] = field(default_factory=lambda: list(SimulationScope))
    constraints: dict[str, Any] = field(default_factory=dict)
    monte_carlo_iterations: int = 1000
    time_horizon_days: int = 365


@dataclass
class SimulationResult:
    scope: SimulationScope = SimulationScope.ARCHITECTURE
    predicted_outcome: float = 0.0
    confidence_interval: tuple[float, float] = (0.0, 0.0)
    risk_factors: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class SimulationRun:
    id: str = ""
    input: SimulationInput = field(default_factory=SimulationInput)
    results: list[SimulationResult] = field(default_factory=list)
    started_at: float = 0.0
    completed_at: float = 0.0
    status: str = "pending"

    def __post_init__(self):
        if not self.id:
            self.id = generate_id("sim", 12)
        if not self.started_at:
            self.started_at = time.time()


class ArchitectureSimulator:
    """Predict architectural evolution."""

    def predict(self, current: dict[str, Any],
                changes: list[dict[str, Any]],
                horizon_days: int = 365) -> SimulationResult:
        complexity = current.get("complexity", 0.5)
        coupling = current.get("coupling", 0.5)
        module_count = current.get("module_count", 10)
        change_impact = sum(c.get("impact", 0.2) for c in changes) / max(len(changes), 1)
        time_factor = min(horizon_days / 365.0, 3.0)
        predicted = min(1.0, complexity * 0.3 + coupling * 0.3 + change_impact * 0.2 + time_factor * 0.1)
        ci_lo = max(0.0, predicted - 0.15)
        ci_hi = min(1.0, predicted + 0.15)
        return SimulationResult(
            scope=SimulationScope.ARCHITECTURE,
            predicted_outcome=predicted,
            confidence_interval=(ci_lo, ci_hi),
            risk_factors=self._risk_factors(complexity, coupling, change_impact),
            recommendations=self._recommendations(predicted, complexity, coupling),
            details={"module_count": module_count, "complexity": complexity,
                     "coupling": coupling, "change_impact": change_impact},
        )

    @staticmethod
    def _risk_factors(c: float, cp: float, ci: float) -> list[str]:
        risks = []
        if c > 0.7:
            risks.append("High base complexity")
        if cp > 0.7:
            risks.append("High coupling between modules")
        if ci > 0.5:
            risks.append("Large change impact surface")
        return risks

    @staticmethod
    def _recommendations(pred: float, c: float, cp: float) -> list[str]:
        recs = []
        if pred > 0.6:
            recs.append("Consider incremental refactoring before major changes")
        if c > 0.6:
            recs.append("Reduce module complexity through decomposition")
        if cp > 0.6:
            recs.append("Introduce interface abstractions to reduce coupling")
        return recs


class MigrationSimulator:
    """Simulate framework, language, and dependency migrations."""

    def simulate_migration(self, current: str, target: str,
                           module_count: int, dependency_count: int,
                           horizon_days: int = 180) -> SimulationResult:
        breaking_changes = max(1, int(module_count * 0.15))
        effort = module_count * 0.1 + dependency_count * 0.05
        risk = (breaking_changes / max(module_count, 1)) * 0.5 + (horizon_days / 180.0) * 0.3
        predicted = min(1.0, risk + effort * 0.2)
        return SimulationResult(
            scope=SimulationScope.FRAMEWORK_MIGRATION,
            predicted_outcome=predicted,
            confidence_interval=(max(0.0, predicted - 0.2), min(1.0, predicted + 0.1)),
            risk_factors=[f"{breaking_changes} estimated breaking changes",
                          f"{dependency_count} affected dependencies"],
            recommendations=["Run in isolated branch first",
                             "Automate breaking change detection",
                             "Incremental migration with feature flags"],
            details={"current": current, "target": target,
                     "module_count": module_count,
                     "breaking_changes": breaking_changes,
                     "estimated_effort_days": round(effort * 10, 1)},
        )


class PerformanceSimulator:
    """Predict performance impact of changes."""

    def predict_performance(self, current_latency_ms: float,
                            change_complexity: float,
                            concurrency: int = 10) -> SimulationResult:
        predicted = current_latency_ms * (1.0 + change_complexity * 0.3)
        overhead = change_complexity * concurrency * 0.01
        return SimulationResult(
            scope=SimulationScope.PERFORMANCE,
            predicted_outcome=predicted + overhead,
            confidence_interval=(predicted * 0.9, predicted * 1.2),
            risk_factors=(["Potential N+1 query pattern"] if change_complexity > 0.5 else []),
            recommendations=["Profile after change", "Add performance regression tests"],
            details={"current_latency_ms": current_latency_ms,
                     "change_complexity": change_complexity,
                     "concurrency": concurrency},
        )


class TestFailureSimulator:
    """Simulate test outcomes for proposed changes."""

    def simulate(self, total_tests: int, affected_modules: int,
                 change_risk: float) -> SimulationResult:
        failure_rate = change_risk * (affected_modules / max(total_tests * 0.1, 1))
        predicted_failures = int(total_tests * min(failure_rate, 0.5))
        return SimulationResult(
            scope=SimulationScope.TEST_FAILURE,
            predicted_outcome=predicted_failures / max(total_tests, 1),
            confidence_interval=(max(0.0, failure_rate - 0.1),
                                 min(1.0, failure_rate + 0.15)),
            risk_factors=[f"{predicted_failures}/{total_tests} tests may fail"],
            recommendations=["Run affected test suites first",
                             "Add integration tests for changed paths"],
            details={"total_tests": total_tests,
                     "predicted_failures": predicted_failures,
                     "change_risk": change_risk},
        )


class CostSimulator:
    """Simulate costs of engineering changes."""

    def simulate(self, engineer_hours: float, hourly_rate: float = 150.0,
                 infrastructure_cost: float = 0.0,
                 risk_premium: float = 0.2) -> SimulationResult:
        base = engineer_hours * hourly_rate + infrastructure_cost
        total = base * (1.0 + risk_premium)
        return SimulationResult(
            scope=SimulationScope.COST,
            predicted_outcome=total,
            confidence_interval=(base * 0.8, base * 1.5),
            risk_factors=[f"Risk premium: {risk_premium * 100:.0f}%"],
            recommendations=["Budget 20% contingency",
                             "Phase work to spread cost"],
            details={"engineer_hours": engineer_hours,
                     "hourly_rate": hourly_rate,
                     "base_cost": base},
        )


class MaintainabilitySimulator:
    """Predict maintainability evolution."""

    def simulate(self, current_index: float, tech_debt_ratio: float,
                 change_frequency: float, horizon_days: int = 365) -> SimulationResult:
        decay = tech_debt_ratio * 0.3 + change_frequency * 0.2
        predicted = max(0.0, current_index - decay * (horizon_days / 365.0))
        return SimulationResult(
            scope=SimulationScope.MAINTAINABILITY,
            predicted_outcome=predicted,
            confidence_interval=(max(0.0, predicted - 0.1),
                                 min(1.0, predicted + 0.1)),
            risk_factors=(["Tech debt > 50%" if tech_debt_ratio > 0.5 else ""]),
            recommendations=["Schedule regular refactoring sprints",
                             "Automate code quality checks"],
            details={"current_index": current_index,
                     "tech_debt_ratio": tech_debt_ratio,
                     "change_frequency": change_frequency},
        )


class SecuritySimulator:
    """Simulate security impact of changes."""

    def simulate(self, exposed_apis: int, auth_coverage: float,
                 dependency_vulnerabilities: int,
                 change_scope: str = "major") -> SimulationResult:
        risk = (exposed_apis * 0.1) * (1.0 - auth_coverage) + dependency_vulnerabilities * 0.05
        if change_scope == "major":
            risk *= 1.5
        predicted = min(1.0, risk)
        return SimulationResult(
            scope=SimulationScope.SECURITY,
            predicted_outcome=predicted,
            confidence_interval=(max(0.0, predicted - 0.1),
                                 min(1.0, predicted + 0.15)),
            risk_factors=[f"{dependency_vulnerabilities} vulnerable deps",
                          f"{1.0 - auth_coverage:.0%} APIs unprotected"],
            recommendations=["Run security audit before deployment",
                             "Update vulnerable dependencies",
                             "Add authentication to exposed APIs"],
            details={"exposed_apis": exposed_apis,
                     "auth_coverage": auth_coverage,
                     "dependency_vulnerabilities": dependency_vulnerabilities},
        )


class SimulatorEngine:
    """Unified simulation engine combining all simulators."""

    def __init__(self):
        self._arch = ArchitectureSimulator()
        self._migration = MigrationSimulator()
        self._perf = PerformanceSimulator()
        self._test = TestFailureSimulator()
        self._cost = CostSimulator()
        self._maintain = MaintainabilitySimulator()
        self._security = SecuritySimulator()
        self._runs: dict[str, SimulationRun] = {}

    def simulate(self, sim_input: SimulationInput) -> SimulationRun:
        run = SimulationRun(input=sim_input, status="running", started_at=time.time())
        scopes = sim_input.scope or list(SimulationScope)
        for scope in scopes:
            result = self._simulate_scope(scope, sim_input)
            if result:
                run.results.append(result)
        run.status = "completed"
        run.completed_at = time.time()
        self._runs[run.id] = run
        return run

    def _simulate_scope(self, scope: SimulationScope,
                         inp: SimulationInput) -> SimulationResult | None:
        if scope == SimulationScope.ARCHITECTURE:
            return self._arch.predict(inp.current_architecture,
                                      inp.proposed_changes, inp.time_horizon_days)
        elif scope == SimulationScope.FRAMEWORK_MIGRATION:
            return self._migration.simulate_migration(
                inp.current_architecture.get("framework", "unknown"),
                inp.proposed_changes[0].get("target", "unknown") if inp.proposed_changes else "new",
                inp.current_architecture.get("module_count", 10),
                inp.current_architecture.get("dependency_count", 50),
                inp.time_horizon_days,
            )
        elif scope == SimulationScope.PERFORMANCE:
            return self._perf.predict_performance(
                inp.current_architecture.get("latency_ms", 100.0),
                sum(c.get("impact", 0.2) for c in inp.proposed_changes) / max(len(inp.proposed_changes), 1),
            )
        elif scope == SimulationScope.TEST_FAILURE:
            return self._test.simulate(
                inp.current_architecture.get("test_count", 100),
                len(inp.proposed_changes),
                sum(c.get("impact", 0.2) for c in inp.proposed_changes) / max(len(inp.proposed_changes), 1),
            )
        elif scope == SimulationScope.COST:
            return self._cost.simulate(
                inp.current_architecture.get("estimated_hours", 100.0),
            )
        elif scope == SimulationScope.MAINTAINABILITY:
            return self._maintain.simulate(
                inp.current_architecture.get("maintainability_index", 0.7),
                inp.current_architecture.get("tech_debt_ratio", 0.3),
                len(inp.proposed_changes) / max(inp.time_horizon_days, 1),
                inp.time_horizon_days,
            )
        elif scope == SimulationScope.SECURITY:
            return self._security.simulate(
                inp.current_architecture.get("exposed_apis", 5),
                inp.current_architecture.get("auth_coverage", 0.8),
                inp.current_architecture.get("vulnerable_deps", 0),
            )
        return None

    def get_run(self, run_id: str) -> SimulationRun | None:
        return self._runs.get(run_id)

    def all_runs(self) -> list[SimulationRun]:
        return list(self._runs.values())

    def summary(self) -> dict[str, Any]:
        return {
            "total_runs": len(self._runs),
            "avg_results_per_run": sum(len(r.results) for r in self._runs.values()) / max(len(self._runs), 1),
            "scopes_available": [s.value for s in SimulationScope],
        }
