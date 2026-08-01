"""
Initiative Discovery — generate every possible improvement, rank by value.

For each initiative computes:
  architectural_value, strategic_value, impact, risk, migration_cost,
  verification_cost, leverage, intelligence_gain, maturity_increase, ROE
"""

from __future__ import annotations

from typing import Any

from genesis.digital_twin.analyzers import (
    CouplingAnalyzer,
    DriftAnalyzer,
    EvolutionAnalyzer,
    SmellAnalyzer,
)
from genesis.digital_twin.metrics import RepositoryMetrics
from genesis.digital_twin.model import DigitalTwin


class Initiative:
    """A ranked improvement candidate for the repository."""

    def __init__(
        self,
        title: str,
        kind: str,
        priority: str,
        findings: list[dict[str, Any]] | None = None,
    ):
        self.title = title
        self.kind = kind
        self.priority = priority
        self.findings = findings or []

    def compute_value(
        self, metrics: dict[str, Any] | None = None
    ) -> dict[str, float]:
        metrics = metrics or {}
        priority_values = {"P0": 1.0, "P1": 0.8, "P2": 0.5, "P3": 0.2}
        base = priority_values.get(self.priority, 0.3)

        architectural_value = base * 0.4 + len(self.findings) * 0.1
        strategic_value = base * 0.3 + (1 - metrics.get("repository_intelligence_score", 0)) * 0.3
        impact = base * 0.5 + (1 - metrics.get("maintainability_index", 0)) * 0.3
        risk = 1.0 - base
        migration_cost = 0.5 if self.kind in ("duplication", "orphan") else 0.7
        verification_cost = 0.3 if self.kind in ("layer_violation", "circular_dependency") else 0.5
        leverage = base * 0.6 + (1 - metrics.get("architectural_entropy", 1) / 5) * 0.3
        intelligence_gain = (1 - metrics.get("repository_intelligence_score", 0)) * base
        maturity_increase = (1 - metrics.get("specification_completeness", 0)) * base * 0.5

        roe = (architectural_value * 0.3 + strategic_value * 0.2 + intelligence_gain * 0.3) / max(
            migration_cost + verification_cost, 0.01
        )

        return {
            "architectural_value": round(architectural_value, 4),
            "strategic_value": round(strategic_value, 4),
            "impact": round(impact, 4),
            "risk": round(risk, 4),
            "migration_cost": round(migration_cost, 4),
            "verification_cost": round(verification_cost, 4),
            "leverage": round(leverage, 4),
            "intelligence_gain": round(intelligence_gain, 4),
            "maturity_increase": round(maturity_increase, 4),
            "return_on_engineering": round(roe, 4),
        }


class InitiativeDiscovery:
    """Discover and rank all possible improvements."""

    def __init__(self, twin: DigitalTwin):
        self.twin = twin
        self.metrics = RepositoryMetrics().compute(twin)

    def discover_all(self) -> list[dict[str, Any]]:
        initiatives: list[dict[str, Any]] = []

        # — from analyzers —
        analyzers = [
            ("architectural_smell", SmellAnalyzer().run(self.twin)),
            ("spec_drift", DriftAnalyzer().run(self.twin)),
            ("hidden_coupling", CouplingAnalyzer().run(self.twin)),
            ("evolution_bottleneck", EvolutionAnalyzer().run(self.twin)),
        ]

        for kind, findings in analyzers:
            grouped = self._group_by_priority(findings)
            for priority, group in grouped.items():
                inc = Initiative(
                    title=f"{priority} {kind.replace('_', ' ').title()}",
                    kind=kind,
                    priority=priority,
                    findings=group,
                )
                value = inc.compute_value(self.metrics)
                initiatives.append({
                    "title": inc.title,
                    "kind": inc.kind,
                    "priority": inc.priority,
                    "finding_count": len(group),
                    "findings": inc.findings[:5],
                    **value,
                })

        # — strategic initiatives from metrics —
        initiatives.extend(self._strategic_initiatives())

        return sorted(
            initiatives,
            key=lambda i: i.get("return_on_engineering", 0),
            reverse=True,
        )

    def _group_by_priority(
        self, findings: list[dict[str, Any]]
    ) -> dict[str, list[dict[str, Any]]]:
        groups: dict[str, list[dict[str, Any]]] = {}
        for f in findings:
            p = f.get("priority", "P3")
            groups.setdefault(p, []).append(f)
        return groups

    def _strategic_initiatives(self) -> list[dict[str, Any]]:
        m = self.metrics
        initiatives = []

        if m.get("specification_completeness", 1) < 0.5:
            inc = Initiative("Improve Specification Coverage", "specification", "P1")
            v = inc.compute_value(m)
            initiatives.append({
                "title": inc.title,
                "kind": inc.kind,
                "priority": inc.priority,
                "finding_count": 1,
                "findings": [{"title": "Spec coverage below 50%", "priority": "P1"}],
                **v,
            })

        if m.get("contract_coverage", 1) < 0.5:
            inc = Initiative("Improve Contract Test Coverage", "verification", "P2")
            v = inc.compute_value(m)
            initiatives.append({
                "title": inc.title,
                "kind": inc.kind,
                "priority": inc.priority,
                "finding_count": 1,
                "findings": [{"title": "Contract test coverage below 50%", "priority": "P2"}],
                **v,
            })

        if m.get("subsystem_cohesion", 1) < 0.3:
            inc = Initiative("Improve Subsystem Cohesion", "architecture", "P2")
            v = inc.compute_value(m)
            initiatives.append({
                "title": inc.title,
                "kind": inc.kind,
                "priority": inc.priority,
                "finding_count": 1,
                "findings": [{"title": "Low subsystem cohesion", "priority": "P2"}],
                **v,
            })

        if m.get("capability_maturity", 0) < 0.3:
            inc = Initiative("Wire Capability Graph Dependencies", "capability", "P2")
            v = inc.compute_value(m)
            initiatives.append({
                "title": inc.title,
                "kind": inc.kind,
                "priority": inc.priority,
                "finding_count": 1,
                "findings": [{"title": "Flat capability graph", "priority": "P2"}],
                **v,
            })

        return initiatives
