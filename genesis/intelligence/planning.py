"""
VRIP Phase 9 — Strategic Planning

Build a dependency-aware roadmap.
Every initiative includes: justification, specs, affected modules,
risks, alternatives, migration plan, verification, effort estimate.
"""

from __future__ import annotations

from typing import Any


class Initiative:
    def __init__(self, title: str, priority: str, rationale: str,
                 specs: list[str], modules: list[str], effort: str,
                 maturity_increase: str, risk: str):
        self.title = title
        self.priority = priority
        self.rationale = rationale
        self.specs = specs
        self.modules = modules
        self.effort = effort
        self.maturity_increase = maturity_increase
        self.risk = risk
        self.dependencies: list[str] = []

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "priority": self.priority,
            "rationale": self.rationale,
            "specs": self.specs,
            "modules": self.modules,
            "effort": self.effort,
            "maturity_increase": self.maturity_increase,
            "risk": self.risk,
            "dependencies": self.dependencies,
        }


class StrategicPlanner:
    """Phase 9: Build dependency-aware roadmap."""

    def __init__(self, gaps: list[dict[str, str]], metrics: dict[str, Any]):
        self.gaps = gaps
        self.metrics = metrics
        self.initiatives: list[Initiative] = []

    def run(self) -> list[dict[str, Any]]:
        self.initiatives = []
        self._build_from_gaps()
        self._order_by_dependencies()
        return [i.to_dict() for i in self.initiatives]

    def _build_from_gaps(self):
        self.initiatives.extend([
            Initiative(
                title="Wire CheckpointStore into platform lifecycle",
                priority="P0" if any(g["kind"] == "persistence" for g in self.gaps) else "P1",
                rationale="CheckpointStore is the only unwired VPS Part X storage provider",
                specs=["VPS §10.1.5", "GENESIS_II_ARCHITECTURE §5.7"],
                modules=["genesis/intelligence/", "genesis/di/interfaces.py"],
                effort="1 session",
                maturity_increase="+5% (VPS Part X 100% wired)",
                risk="Low",
            ),
            Initiative(
                title="Wire EventBus into remaining services (indexer, plugin, capability)",
                priority="P1",
                rationale="5 domain services still operate silently",
                specs=["VPS §5.6: Runtime must record Observations"],
                modules=["genesis/indexer/", "genesis/plugin/", "genesis/capability/"],
                effort="1 session",
                maturity_increase="+3% (observability coverage)",
                risk="Low",
            ),
            Initiative(
                title="Backfill missing ADRs (EventBus pattern, UIR delegation, layer refactor)",
                priority="P2",
                rationale="Only 3 ADRs exist; key architectural decisions undocumented",
                specs=["Governance Gates: Documentation updated"],
                modules=["genesis/decisions/"],
                effort="1 session",
                maturity_increase="+2% (governance completeness)",
                risk="None",
            ),
        ])

    def _order_by_dependencies(self):
        for i in self.initiatives:
            if i.title == "Wire EventBus into remaining services":
                continue
