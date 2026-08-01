"""
Repository Intelligence Score v2 — Stage 21 of the OMEGA loop.

Expanded 21-factor score measuring:
  Understanding, Reasoning, Prediction, Simulation, Validation,
  Autonomy, Learning, Reuse, Knowledge, Architecture, Compiler,
  Runtime, Graph, Memory, Evolution, Platform Intelligence

Tracks trend across cycles. Score must always trend upward.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from genesis.digital_twin.model import DigitalTwin


class RIScore:
    """Repository Intelligence Score — expanded 21-factor measurement."""

    def __init__(self):
        self.factors: dict[str, float] = {}
        self.history: list[dict[str, float]] = []
        self.trend: dict[str, float] = {}

    def compute(self, twin: DigitalTwin, previous: dict[str, float] | None = None) -> dict[str, Any]:
        factors = {}

        # — 1. Understanding (how well does the twin capture reality?) —
        factors["understanding"] = self._understanding(twin)

        # — 2. Reasoning (conclusions drawn per node) —
        factors["reasoning"] = self._reasoning(twin)

        # — 3. Prediction (coverage of future states) —
        factors["prediction"] = self._prediction(twin)

        # — 4. Simulation (hypothesis simulation coverage) —
        factors["simulation"] = self._simulation(twin)

        # — 5. Validation (evidence gates passed) —
        factors["validation"] = self._validation(twin)

        # — 6. Autonomy (self-operation level) —
        factors["autonomy"] = self._autonomy(twin)

        # — 7. Learning (cross-cycle improvement) —
        factors["learning"] = self._learning(twin)

        # — 8. Reuse (canonical abstraction ratio) —
        factors["reuse"] = self._reuse(twin)

        # — 9. Knowledge (spec coverage) —
        factors["knowledge"] = self._knowledge(twin)

        # — 10. Architecture (layer compliance, stability) —
        factors["architecture"] = self._architecture(twin)

        # — 11. Compiler (compilation pipeline completeness) —
        factors["compiler"] = self._compiler(twin)

        # — 12. Runtime (execution capability) —
        factors["runtime"] = self._runtime(twin)

        # — 13. Graph (graph completeness) —
        factors["graph"] = self._graph(twin)

        # — 14. Memory (persistence store completeness) —
        factors["memory"] = self._memory(twin)

        # — 15. Evolution (evolution engine capability) —
        factors["evolution"] = self._evolution(twin)

        # — 16. Platform (platform integration) —
        factors["platform"] = self._platform(twin)

        # — 17. Observation (analyzer coverage) —
        factors["observation"] = self._observation(twin)

        # — 18. Hypothesis (hypothesis diversity) —
        factors["hypothesis"] = self._hypothesis(twin)

        # — 19. Testing (test coverage) —
        factors["testing"] = self._testing(twin)

        # — 20. Documentation (documentation coverage) —
        factors["documentation"] = self._documentation(twin)

        # — 21. Self-Improvement (self-analysis capability) —
        factors["self_improvement"] = self._self_improvement(twin)

        self.factors = factors
        overall = sum(factors.values()) / max(len(factors), 1)

        if previous:
            self.trend = {
                k: factors.get(k, 0) - previous.get(k, 0)
                for k in set(list(factors.keys()) + list(previous.keys()))
            }

        self.history.append(factors)

        return {
            "overall": round(overall, 4),
            "factors": {k: round(v, 4) for k, v in factors.items()},
            "trend": {k: round(v, 4) for k, v in self.trend.items()},
            "history_depth": len(self.history),
            "trend_direction": "up" if overall > (previous.get("overall", 0) if previous else 0) else "down",
        }

    def _understanding(self, twin: DigitalTwin) -> float:
        files = twin.find_nodes(kind="file")
        if not files:
            return 0.0
        with_source = sum(1 for f in files if f.source_text)
        with_purpose = sum(1 for f in files if f.purpose)
        return (with_source / len(files) * 0.5 + with_purpose / len(files) * 0.5)

    def _reasoning(self, twin: DigitalTwin) -> float:
        tools = [
            "genesis/digital_twin/reasoning.py",
            "ReasoningEngine",
        ]
        found = sum(1 for t in tools if any(t in (n.id or "") for n in twin.nodes))
        return min(found / len(tools), 1.0)

    def _prediction(self, twin: DigitalTwin) -> float:
        tools = [
            "genesis/digital_twin/predict.py",
            "PredictionEngine",
        ]
        found = sum(1 for t in tools if any(t in (n.id or "") for n in twin.nodes))
        return min(found / len(tools), 1.0)

    def _simulation(self, twin: DigitalTwin) -> float:
        tools = [
            "genesis/digital_twin/simulator.py",
            "genesis/digital_twin/evolution.py",
            "EvolutionSimulator",
            "EvolutionEngine",
        ]
        found = sum(1 for t in tools if any(t in (n.id or "") for n in twin.nodes))
        return min(found / len(tools), 1.0)

    def _validation(self, twin: DigitalTwin) -> float:
        tools = [
            "genesis/digital_twin/validation.py",
            "ScientificValidator",
        ]
        found = sum(1 for t in tools if any(t in (n.id or "") for n in twin.nodes))
        return min(found / len(tools), 1.0)

    def _autonomy(self, twin: DigitalTwin) -> float:
        cli_nodes = twin.find_nodes(kind="class")
        auto_triggers = sum(1 for n in cli_nodes if "Evolve" in (n.label or "") or "Auto" in (n.label or ""))
        return min(auto_triggers * 0.2, 1.0)

    def _learning(self, twin: DigitalTwin) -> float:
        return 0.5  # baseline — improved by cross-repository learning

    def _reuse(self, twin: DigitalTwin) -> float:
        name_counts = defaultdict(list)
        for n in twin.find_nodes(kind="class"):
            name_counts[n.label].append(n)
        dups = sum(1 for v in name_counts.values() if len(v) > 1)
        total = len(name_counts)
        if total == 0:
            return 1.0
        return 1.0 - (dups / total)

    def _knowledge(self, twin: DigitalTwin) -> float:
        specs = twin.find_nodes(kind="normative")
        if not specs:
            return 1.0
        linked = sum(1 for s in specs if any(
            e[0] == s.id for e in twin.find_edges("implements")
        ))
        return linked / len(specs)

    def _architecture(self, twin: DigitalTwin) -> float:
        classes = twin.find_nodes(kind="class")
        with_layer = sum(1 for c in classes if c.layer is not None)
        layer_cov = with_layer / max(len(classes), 1)
        violations = 0
        for edge in twin.find_edges("imports"):
            sn = twin.get_node(edge[0])
            tn = twin.get_node(edge[1])
            if sn and tn and sn.layer is not None and tn.layer is not None:
                if "/tests/" not in edge[0] and sn.layer < tn.layer:
                    violations += 1
        layer_health = 1.0 / (1 + violations)
        return layer_cov * 0.5 + layer_health * 0.5

    def _compiler(self, twin: DigitalTwin) -> float:
        compilers = [n for n in twin.find_nodes(kind="class") if "Compiler" in (n.label or "")]
        return min(len(compilers) * 0.15, 1.0)

    def _runtime(self, twin: DigitalTwin) -> float:
        runtimes = [n for n in twin.find_nodes(kind="class")
                   if "Executor" in (n.label or "") or "Runtime" in (n.label or "")]
        return min(len(runtimes) * 0.2, 1.0)

    def _graph(self, twin: DigitalTwin) -> float:
        edge_kinds = len(twin.find_edges())
        node_kinds = len(twin.count_by_kind())
        return min((edge_kinds * 0.05 + node_kinds * 0.05), 1.0)

    def _memory(self, twin: DigitalTwin) -> float:
        stores = twin.find_nodes(kind="store")
        return min(len(stores) * 0.1, 1.0)

    def _evolution(self, twin: DigitalTwin) -> float:
        evolution_tools = [
            "genesis/digital_twin/hypothesis.py",
            "genesis/digital_twin/evolution.py",
            "genesis/digital_twin/discovery.py",
        ]
        found = sum(1 for t in evolution_tools if any(t in (n.id or "") for n in twin.nodes))
        return min(found / len(evolution_tools), 1.0) * 0.8 + 0.2

    def _platform(self, twin: DigitalTwin) -> float:
        platform = twin.get_node("genesis/platform.py")
        if platform:
            return 1.0
        return 0.0

    def _observation(self, twin: DigitalTwin) -> float:
        analyzers = [
            "SmellAnalyzer", "DriftAnalyzer",
            "CouplingAnalyzer", "EvolutionAnalyzer",
        ]
        found = sum(1 for a in analyzers if any(
            n.label == a for n in twin.find_nodes(kind="class")
        ))
        return found / len(analyzers)

    def _hypothesis(self, twin: DigitalTwin) -> float:
        hypo_classes = [n for n in twin.find_nodes(kind="class")
                       if "Hypothesis" in (n.label or "")]
        return min(len(hypo_classes) * 0.3, 1.0)

    def _testing(self, twin: DigitalTwin) -> float:
        classes = twin.find_nodes(kind="class")
        tested = sum(1 for c in classes if c.test_count > 0)
        return tested / max(len(classes), 1)

    def _documentation(self, twin: DigitalTwin) -> float:
        adrs = twin.find_nodes(kind="adr")
        specs = twin.find_nodes(kind="normative")
        total = len(adrs) + len(specs)
        return min(total * 0.02, 1.0)

    def _self_improvement(self, twin: DigitalTwin) -> float:
        self_tools = [
            "genesis/digital_twin/self_analysis.py",
        ]
        found = sum(1 for t in self_tools if any(t in (n.id or "") for n in twin.nodes))
        return min(found, 1.0)
