"""
Evolution Engine — Phase 6-7 of the ULTRA EVOLUTION LOOP.

Takes ranked hypotheses → simulates each on twin copy → evaluates quality delta →
applies only improvements that increase architectural intelligence.

Pipeline:
  Hypothesis Engine → EvolutionEngine.evaluate() → EvolutionEngine.evolve()
"""

from __future__ import annotations

import copy
from typing import Any

from genesis.digital_twin.hypothesis import Hypothesis
from genesis.digital_twin.metrics import RepositoryMetrics
from genesis.digital_twin.model import DigitalTwin


class SimulatedChange:
    """Result of simulating a hypothesis on the DigitalTwin."""

    def __init__(
        self,
        hypothesis: Hypothesis,
        quality_delta: float,
        metric_deltas: dict[str, float],
        acceptable: bool,
        twin_snapshot: DigitalTwin | None = None,
    ):
        self.hypothesis = hypothesis
        self.quality_delta = quality_delta
        self.metric_deltas = metric_deltas
        self.acceptable = acceptable
        self.twin_snapshot = twin_snapshot

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.hypothesis.title,
            "kind": self.hypothesis.kind,
            "quality_delta": self.quality_delta,
            "metric_deltas": self.metric_deltas,
            "acceptable": self.acceptable,
            "roe": self.hypothesis.roe,
            "confidence": self.hypothesis.confidence,
            "risk": self.hypothesis.risk,
        }


class EvolutionEngine:
    """Simulate and apply architectural improvements."""

    def __init__(self, twin: DigitalTwin):
        self.original = twin
        self.baseline: dict[str, float] = {}
        self.changes: list[SimulatedChange] = []
        self.applied: list[SimulatedChange] = []

    def baseline_metrics(self) -> dict[str, float]:
        self.baseline = RepositoryMetrics().compute(self.original)
        return self.baseline

    def evaluate(self, hypothesis: Hypothesis) -> SimulatedChange:
        """Simulate a hypothesis on the twin and compute quality impact."""
        if not self.baseline:
            self.baseline_metrics()

        twin = copy.deepcopy(self.original)
        self._apply_hypothesis(twin, hypothesis)
        metrics = RepositoryMetrics().compute(twin)

        deltas: dict[str, float] = {}
        quality_delta = 0.0
        for k in self.baseline:
            bv = self.baseline.get(k, 0)
            mv = metrics.get(k, 0)
            if isinstance(bv, (int, float)) and isinstance(mv, (int, float)):
                delta = mv - bv
                deltas[k] = round(delta, 4)
                quality_delta += delta

        acceptable = quality_delta >= -0.01 or hypothesis.confidence > 0.8
        change = SimulatedChange(
            hypothesis=hypothesis,
            quality_delta=round(quality_delta, 4),
            metric_deltas=deltas,
            acceptable=acceptable,
        )
        self.changes.append(change)
        return change

    def evolve(self, hypotheses: list[Hypothesis], max_changes: int = 5) -> list[SimulatedChange]:
        """Evaluate hypotheses in ROE order, apply acceptable ones."""
        if not self.baseline:
            self.baseline_metrics()

        sorted_h = sorted(hypotheses, key=lambda h: h.roe, reverse=True)
        applied: list[SimulatedChange] = []

        for h in sorted_h[:max_changes * 2]:
            if len(applied) >= max_changes:
                break
            change = self.evaluate(h)
            if change.acceptable:
                applied.append(change)
                self.applied.append(change)

        return applied

    def generate_evolution_report(self) -> str:
        """Generate a text report of all applied changes."""
        lines = [
            "=" * 60,
            "EVOLUTION REPORT",
            "=" * 60,
            "",
        ]

        if not self.applied:
            lines.append("No changes applied.")
            lines.append("=" * 60)
            return "\n".join(lines)

        lines.append(f"Changes applied: {len(self.applied)}")
        lines.append("")

        total_delta = 0.0
        for i, change in enumerate(self.applied, 1):
            lines.append(f"#{i}: {change.hypothesis.title}")
            lines.append(f"    Kind: {change.hypothesis.kind}")
            lines.append(f"    Quality delta: {change.quality_delta:+.4f}")
            lines.append(f"    Confidence: {change.hypothesis.confidence:.0%}")
            lines.append(f"    ROE: {change.hypothesis.roe:.3f}")
            lines.append(f"    Effort: {change.hypothesis.effort}")
            lines.append(f"    Justification: {change.hypothesis.justification[:100]}")
            lines.append(f"    Steps:")
            for step in change.hypothesis.implementation_steps:
                lines.append(f"      - {step}")
            lines.append("")
            total_delta += change.quality_delta

        lines.append(f"Total quality improvement: {total_delta:+.4f}")
        lines.append("=" * 60)
        return "\n".join(lines)

    def _apply_hypothesis(self, twin: DigitalTwin, hypothesis: Hypothesis):
        """Apply a hypothesis to a twin copy for simulation."""
        kind = hypothesis.kind
        target_ids = hypothesis.target_ids

        if kind == "merge_duplicates" and len(target_ids) >= 2:
            primary = target_ids[0]
            for dup_id in target_ids[1:]:
                dup_node = twin.get_node(dup_id)
                if dup_node:
                    del twin._nodes[dup_id]
                    del twin._indexes.get("kind", {}).get(dup_node.kind, [])[:]

        elif kind == "fix_layer_violation" and len(target_ids) >= 2:
            source_id, target_id = target_ids[:2]
            twin.add_edge(source_id, target_id, "abstraction_introduced")

        elif kind == "split_hub":
            for tid in target_ids:
                node = twin.get_node(tid)
                if node:
                    for edge in twin.find_edges("imports"):
                        if edge[1] == tid:
                            twin.add_edge(edge[0], f"{tid}_sub", "imports")

        elif kind == "link_specs":
            for finding_title in target_ids:
                spec_nodes = twin.find_nodes(kind="normative")
                for s in spec_nodes:
                    if s.label and finding_title[:20].lower() in s.label.lower():
                        class_nodes = twin.find_nodes(kind="class")
                        for c in class_nodes:
                            twin.add_edge(c.id, s.id, "implements")
                            if s.id not in c.spec_refs:
                                c.spec_refs.append(s.id)

        elif kind == "add_tests":
            for tid in target_ids:
                node = twin.get_node(tid)
                if node:
                    node.test_count = max(node.test_count, 1)
                    twin.add_node(node)

        elif kind == "improve_spec_coverage":
            spec_nodes = twin.find_nodes(kind="normative")
            class_nodes = twin.find_nodes(kind="class")
            for spec in spec_nodes:
                has_impl = any(
                    e[0] != spec.id and "implements" in e
                    for e in twin.find_edges("implements")
                )
                if not has_impl:
                    for c in class_nodes[:5]:
                        twin.add_edge(c.id, spec.id, "implements")

        elif kind == "improve_contract_coverage":
            for node in twin.find_nodes(kind="class"):
                if node.protocols or node.interfaces:
                    node.test_count = max(node.test_count, 3)
                    twin.add_node(node)

        elif kind == "wire_capability_graph":
            for node in twin.find_nodes(kind="class"):
                if "capability" in (node.label or "").lower():
                    for other in twin.find_nodes(kind="class"):
                        if other.id != node.id and "capability" in (other.label or "").lower():
                            twin.add_edge(node.id, other.id, "depends_on")

        elif kind == "add_extractor_tests":
            for tid in target_ids:
                node = twin.get_node(tid)
                if node:
                    node.test_count = max(node.test_count, 5)
                    twin.add_node(node)

        elif kind == "split_overlap":
            for node in twin.nodes:
                if any(tid in node.id for tid in target_ids):
                    node.tags.append("refactored")
                    twin.add_node(node)
