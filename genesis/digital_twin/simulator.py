"""
Evolution Simulator — simulate architectural changes before applying them.

Simulates:
  - Import graph changes
  - New module additions
  - Dependency changes
  - Metric impact

Auto-rolls back if quality decreases.
"""

from __future__ import annotations

import copy
from typing import Any

from genesis.digital_twin.metrics import RepositoryMetrics
from genesis.digital_twin.model import DigitalTwin, TwinNode


class EvolutionSimulator:
    """Simulate changes on a Digital Twin and evaluate quality impact."""

    def __init__(self, twin: DigitalTwin):
        self.original = twin
        self.baseline: dict[str, float] = {}
        self.simulated: DigitalTwin | None = None
        self.candidates: list[dict[str, Any]] = []

    def baseline_metrics(self) -> dict[str, float]:
        self.baseline = RepositoryMetrics().compute(self.original)
        return self.baseline

    def simulate_add_module(
        self, module_path: str, depends_on: list[str] | None = None
    ) -> dict[str, Any]:
        twin = copy.deepcopy(self.original)
        node = TwinNode(
            id=module_path,
            kind="file",
            label=module_path.split("/")[-1],
            file_path=module_path,
            module=module_path.replace("/", ".").replace(".py", ""),
        )
        twin.add_node(node)
        for dep in (depends_on or []):
            twin.add_edge(module_path, dep, "imports")
        return self._evaluate(twin, f"Add module {module_path}")

    def simulate_remove_module(self, module_path: str) -> dict[str, Any]:
        twin = copy.deepcopy(self.original)
        node = twin.get_node(module_path)
        if node:
            del twin._nodes[module_path]
        return self._evaluate(twin, f"Remove module {module_path}")

    def simulate_add_dependency(
        self, source: str, target: str
    ) -> dict[str, Any]:
        twin = copy.deepcopy(self.original)
        twin.add_edge(source, target, "imports")
        return self._evaluate(twin, f"Add dependency {source} -> {target}")

    def simulate_remove_dependency(
        self, source: str, target: str
    ) -> dict[str, Any]:
        twin = copy.deepcopy(self.original)
        edges = twin._edges_by_kind.get("imports", [])
        twin._edges_by_kind["imports"] = [
            e for e in edges if not (e[0] == source and e[1] == target)
        ]
        return self._evaluate(twin, f"Remove dependency {source} -> {target}")

    def _evaluate(self, twin: DigitalTwin, label: str) -> dict[str, Any]:
        if not self.baseline:
            self.baseline_metrics()

        metrics = RepositoryMetrics().compute(twin)
        delta = {}
        for k in self.baseline:
            bv = self.baseline[k]
            mv = metrics.get(k, 0)
            if isinstance(bv, (int, float)) and isinstance(mv, (int, float)):
                delta[k] = round(mv - bv, 4)

        quality_change = sum(delta.values())
        acceptable = quality_change >= -0.05

        result = {
            "simulation": label,
            "acceptable": acceptable,
            "quality_change": round(quality_change, 4),
            "delta": delta,
            "metrics_after": metrics,
        }
        self.candidates.append(result)
        return result

    def best_candidate(self) -> dict[str, Any] | None:
        valid = [c for c in self.candidates if c.get("acceptable")]
        if not valid:
            return None
        return max(valid, key=lambda c: c.get("quality_change", 0))

    def auto_rollback(self, result: dict[str, Any]) -> bool:
        if not result.get("acceptable", False):
            return True
        return False
