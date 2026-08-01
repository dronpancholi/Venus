"""
Prediction Engine — Stage 12 of the OMEGA loop.

Predicts architecture drift, future coupling, bottlenecks, 
and instability from DigitalTwin state and evolution history.

Every prediction carries a confidence interval.
"""

from __future__ import annotations

import math
from collections import Counter, defaultdict
from typing import Any

from genesis.digital_twin.model import DigitalTwin


class Prediction:
    """A prediction about future architecture state."""

    def __init__(
        self,
        kind: str,
        statement: str,
        confidence: float,
        confidence_interval: tuple[float, float],
        horizon: str,
        evidence: list[str],
        affected_ids: list[str] | None = None,
    ):
        self.kind = kind
        self.statement = statement
        self.confidence = confidence
        self.confidence_interval = confidence_interval
        self.horizon = horizon
        self.evidence = evidence
        self.affected_ids = affected_ids or []

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": self.kind,
            "statement": self.statement,
            "confidence": self.confidence,
            "ci": self.confidence_interval,
            "horizon": self.horizon,
            "evidence": self.evidence[:3],
        }


class PredictionEngine:
    """Predict future architecture properties from current state."""

    def __init__(self, twin: DigitalTwin):
        self.twin = twin

    def predict_all(self) -> list[Prediction]:
        predictions: list[Prediction] = []
        predictions.extend(self._predict_coupling_growth())
        predictions.extend(self._predict_spec_drift())
        predictions.extend(self._predict_hub_instability())
        predictions.extend(self._predict_layer_erosion())
        predictions.extend(self._predict_complexity_growth())
        predictions.extend(self._predict_test_debt())
        predictions.extend(self._predict_duplication_spread())
        return predictions

    def _predict_coupling_growth(self) -> list[Prediction]:
        """Predict how coupling will grow based on current hub trajectory."""
        predictions = []
        dep_counts: Counter = Counter()
        for edge in self.twin.find_edges("imports"):
            dep_counts[edge[1]] += 1

        for node_id, count in dep_counts.most_common(3):
            if count >= 5:
                node = self.twin.get_node(node_id)
                label = node.label if node else node_id
                growth_rate = count * 0.15
                projected = count + growth_rate
                predictions.append(Prediction(
                    kind="coupling_growth",
                    statement=f"'{label}' coupling predicted to grow from {count} to "
                             f"{projected:.0f} dependents ({(growth_rate / count * 100):.0f}% increase)",
                    confidence=0.5,
                    confidence_interval=(projected * 0.8, projected * 1.2),
                    horizon="next evolution cycle",
                    evidence=[f"Current: {count} dependents", f"Growth rate: {growth_rate:.1f}"],
                    affected_ids=[node_id],
                ))
        return predictions

    def _predict_spec_drift(self) -> list[Prediction]:
        """Predict how far spec coverage will drift without intervention."""
        specs = self.twin.find_nodes(kind="normative")
        if not specs:
            return []

        linked = sum(1 for s in specs if any(
            e[0] == s.id for e in self.twin.find_edges("implements")
        ))
        total = len(specs)
        pct = linked / total * 100 if total > 0 else 0

        if pct < 50:
            unlinked = total - linked
            drift_rate = unlinked * 0.1
            projected = unlinked + drift_rate
            predictions = [Prediction(
                kind="spec_drift",
                statement=f"Spec coverage at {pct:.0f}% — predicted to drift to "
                         f"{linked}/{total - projected:.0f} linked without intervention",
                confidence=0.6,
                confidence_interval=(pct - 5, pct + 5),
                horizon="next 3 evolution cycles",
                evidence=[
                    f"Current: {linked}/{total} linked",
                    f"Drift rate: {drift_rate:.1f} per cycle",
                ],
                affected_ids=[s.id for s in specs if not any(
                    e[0] == s.id for e in self.twin.find_edges("implements")
                )][:5],
            )]
            return predictions
        return []

    def _predict_hub_instability(self) -> list[Prediction]:
        """Predict which hubs are most likely to become instability points."""
        predictions = []
        for edge in self.twin.find_edges("imports"):
            dep_counts: Counter = Counter()
            dep_counts[edge[1]] += 1

        in_degree_counts: Counter = Counter()
        for s, t, _ in self.twin.find_edges("imports"):
            in_degree_counts[t] += 1

        for node_id, count in in_degree_counts.most_common(5):
            if count >= 5:
                node = self.twin.get_node(node_id)
                label = node.label if node else node_id.split("/")[-1]
                instability_index = count / (count + len(node.depends_on if node else []))
                if instability_index > 0.7:
                    predictions.append(Prediction(
                        kind="hub_instability",
                        statement=f"'{label}' has instability index {instability_index:.2f} "
                                 f"(highly unstable — change here propagates to {count} dependents)",
                        confidence=0.7,
                        confidence_interval=(instability_index - 0.1, instability_index + 0.1),
                        horizon="current",
                        evidence=[
                            f"Afferent couplings: {count}",
                            f"Efferent couplings: {len(node.depends_on if node else [])}",
                        ],
                        affected_ids=[node_id],
                    ))
        return predictions

    def _predict_layer_erosion(self) -> list[Prediction]:
        """Predict whether layering will erode further."""
        violations = []
        for edge in self.twin.find_edges("imports"):
            s, t, _ = edge
            sn = self.twin.get_node(s)
            tn = self.twin.get_node(t)
            if sn and tn and sn.layer is not None and tn.layer is not None:
                if "/tests/" not in s and sn.layer < tn.layer:
                    violations.append((s, t))

        if violations:
            predictions = [Prediction(
                kind="layer_erosion",
                statement=f"Layer violations predicted to grow: {len(violations)} current violations "
                         f"tend to invite more as developers follow established patterns",
                confidence=0.4,
                confidence_interval=(len(violations), len(violations) * 1.5),
                horizon="next 3 cycles",
                evidence=[
                    f"Current: {len(violations)} violations",
                    "Violations normalize deviance from layering rules",
                ],
                affected_ids=[v[0] for v in violations[:5]],
            )]
            return predictions
        return []

    def _predict_complexity_growth(self) -> list[Prediction]:
        """Predict complexity growth based on node/edge trends."""
        node_count = self.twin.node_count
        edge_count = self.twin.edge_count
        if node_count == 0:
            return []

        density = edge_count / node_count
        # — assume linear growth —
        projected_density = density * 1.1

        predictions = [Prediction(
            kind="complexity_growth",
            statement=f"Graph complexity (edges/node) predicted to grow from "
                     f"{density:.2f} to {projected_density:.2f}",
            confidence=0.5,
            confidence_interval=(density * 1.05, density * 1.2),
            horizon="next cycle",
            evidence=[
                f"Current nodes: {node_count}",
                f"Current edges: {edge_count}",
                f"Current density: {density:.2f}",
            ],
        )]
        return predictions

    def _predict_test_debt(self) -> list[Prediction]:
        """Predict test debt accumulation."""
        classes = self.twin.find_nodes(kind="class")
        untested = [c for c in classes if c.test_count == 0]
        if not classes:
            return []
        pct = len(untested) / len(classes) * 100

        if pct > 50:
            predictions = [Prediction(
                kind="test_debt",
                statement=f"Test debt at {pct:.0f}% — predicted to reach "
                         f"{min(pct * 1.2, 100):.0f}% without intervention",
                confidence=0.7,
                confidence_interval=(pct, min(pct * 1.3, 100)),
                horizon="next 3 cycles",
                evidence=[
                    f"Untested: {len(untested)}/{len(classes)} classes",
                    "Test debt compounds as new code lacks test coverage",
                ],
                affected_ids=[c.id for c in untested[:5]],
            )]
            return predictions
        return []

    def _predict_duplication_spread(self) -> list[Prediction]:
        """Predict duplication growth."""
        name_counts = Counter(n.label for n in self.twin.find_nodes(kind="class"))
        dups = {name: count for name, count in name_counts.items() if count > 1}
        if not dups:
            return []

        dup_rate = len(dups) / max(len(name_counts), 1) * 100
        predictions = [Prediction(
            kind="duplication_spread",
            statement=f"Duplication at {dup_rate:.0f}% — {len(dups)} names duplicated "
                     f"across {sum(dups.values())} nodes. Predicted to grow "
                     f"without canonicalization intervention.",
            confidence=0.5,
            confidence_interval=(dup_rate * 0.9, dup_rate * 1.2),
            horizon="next 3 cycles",
            evidence=[
                f"Duplicated names: {len(dups)}",
                f"Total instances: {sum(dups.values())}",
            ],
            affected_ids=[n.id for n in self.twin.find_nodes(kind="class")
                         if name_counts.get(n.label, 0) > 1][:5],
        )]
        return predictions
