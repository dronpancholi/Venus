"""
VRIP Phase 8 — Autonomous Gap Detection

Continuously discover highest-leverage improvements, riskiest subsystems,
most incomplete specifications, greatest duplication, largest missing capabilities.
"""

from __future__ import annotations

from typing import Any

from genesis.capability.registry import capability_registry
from .kgraph import KnowledgeGraph


class Gap:
    def __init__(self, kind: str, priority: str, title: str, description: str,
                 effort: str = "", leverage: str = "", risk: str = ""):
        self.kind = kind
        self.priority = priority
        self.title = title
        self.description = description
        self.effort = effort
        self.leverage = leverage
        self.risk = risk

    def to_dict(self) -> dict[str, str]:
        return {
            "kind": self.kind,
            "priority": self.priority,
            "title": self.title,
            "description": self.description,
            "effort": self.effort,
            "leverage": self.leverage,
            "risk": self.risk,
        }


class GapDetector:
    """Phase 8: Autonomous gap detection and prioritization."""

    def __init__(self, kg: KnowledgeGraph, metrics: dict[str, Any]):
        self.kg = kg
        self.metrics = metrics
        self.gaps: list[Gap] = []

    def run(self) -> list[dict[str, str]]:
        self.gaps = []
        self._check_spec_coverage()
        self._check_persistence_wiring()
        self._check_capability_deps()
        self._check_event_coverage()
        self._check_duplication()
        self._check_adr_coverage()
        self._sort_by_priority()
        return [g.to_dict() for g in self.gaps]

    def _check_spec_coverage(self):
        norms = self.kg.find_nodes(kind="normative")
        norms_with_impl = 0
        for norm in norms:
            neighbors = self.kg.neighbors(norm.node_id)
            if any(n.kind in ("class", "file", "test", "capability") for n in neighbors):
                norms_with_impl += 1
        uncovered = len(norms) - norms_with_impl
        if uncovered > 0:
            self.gaps.append(Gap(
                "specification", "P0" if uncovered > 5 else "P1",
                f"{uncovered} normative requirements lack implementation",
                "Specifications without implementation create architectural drift",
                effort="2 sessions", leverage="High (closes drift)", risk="Low",
            ))

    def _check_persistence_wiring(self):
        pers = self.metrics.get("persistence", {})
        wired = pers.get("wired_to_services", 0)
        total = pers.get("providers", 5)
        if wired < total:
            self.gaps.append(Gap(
                "persistence", "P0",
                f"Storage providers: {wired}/{total} wired to domain services",
                "Unwired storage providers provide no benefit",
                effort="1 session", leverage="High (enables persistence)", risk="Low",
            ))

    def _check_capability_deps(self):
        cap_nodes = self.kg.find_nodes(kind="capability")
        root_caps = [n for n in cap_nodes if not n.attrs.get("dependencies")]
        if len(root_caps) > len(cap_nodes) * 0.5:
            self.gaps.append(Gap(
                "capability", "P2",
                f"{len(root_caps)}/{len(cap_nodes)} capabilities have no dependencies",
                "Flat capability graph suggests missing dependency relationships",
                effort="Partial session", leverage="Medium (improves graph)", risk="Low",
            ))

    def _check_event_coverage(self):
        evt = self.metrics.get("event_coverage", {})
        services = evt.get("services_with_events", 0)
        total = evt.get("total_services", 8)
        if services < total:
            self.gaps.append(Gap(
                "observability", "P1",
                f"EventBus: {services}/{total} domain services wired",
                "Silent services violate VPS observability requirements",
                effort="1 session", leverage="Medium (enables observability)", risk="Low",
            ))

    def _check_duplication(self):
        classes: dict[str, list[str]] = {}
        for node in self.kg.find_nodes(kind="class"):
            name = node.label
            if name not in classes:
                classes[name] = []
            classes[name].append(node.attrs.get("module", ""))
        duplicated = {k: v for k, v in classes.items() if len(v) > 1}
        if duplicated:
            self.gaps.append(Gap(
                "duplication", "P1",
                f"{len(duplicated)} class names appear in multiple modules",
                "Potential duplicate abstractions",
                effort="1 session", leverage="Medium (reduces entropy)", risk="Medium",
            ))

    def _check_adr_coverage(self):
        adrs = self.kg.find_nodes(kind="adr")
        if len(adrs) < 5:
            self.gaps.append(Gap(
                "governance", "P2",
                f"Only {len(adrs)} ADRs recorded (target: 5+)",
                "Incomplete decision history reduces auditability",
                effort="1 session", leverage="Medium (knowledge preservation)", risk="None",
            ))

    def _sort_by_priority(self):
        order = {"P0": 0, "P1": 1, "P2": 2}
        self.gaps.sort(key=lambda g: order.get(g.priority, 99))
