"""Evolution bottleneck detection — finds modules that resist change."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from genesis.digital_twin.model import DigitalTwin


class EvolutionAnalyzer:
    """Detect evolution bottlenecks: volatile hubs, unstable deps, knowledge silos."""

    def run(self, twin: DigitalTwin) -> list[dict[str, Any]]:
        findings: list[dict[str, Any]] = []

        findings.extend(self._check_volatile_hubs(twin))
        findings.extend(self._check_knowledge_silos(twin))
        findings.extend(self._check_high_churn(twin))

        return findings

    def _check_volatile_hubs(self, twin: DigitalTwin) -> list[dict[str, Any]]:
        findings = []
        for node in twin.nodes:
            if node.kind != "file":
                continue
            if node.change_frequency > 20 and len(node.depended_by) > 5:
                findings.append({
                    "kind": "volatile_hub",
                    "priority": "P1",
                    "title": f"Volatile hub: '{node.label}'",
                    "description": (
                        f"Changed {node.change_frequency}x, depended by {len(node.depended_by)} modules"
                    ),
                    "effort": "Multiple sessions",
                    "leverage": "High (stabilizes evolution)",
                    "risk": "High",
                })
        return findings

    def _check_knowledge_silos(self, twin: DigitalTwin) -> list[dict[str, Any]]:
        findings = []
        for node in twin.nodes:
            if node.kind != "file":
                continue
            if node.depends_on and not node.depended_by:
                continue
            if node.change_frequency == 0 and len(node.depended_by) > 3:
                findings.append({
                    "kind": "knowledge_silo",
                    "priority": "P2",
                    "title": f"Knowledge silo: '{node.label}'",
                    "description": (
                        f"{len(node.depended_by)} dependents but never modified — "
                        f"single point of failure"
                    ),
                    "effort": "1 session",
                    "leverage": "Medium (distributes knowledge)",
                    "risk": "Medium",
                })
        return findings

    def _check_high_churn(self, twin: DigitalTwin) -> list[dict[str, Any]]:
        findings = []
        for node in twin.find_nodes(kind="file"):
            if node.change_frequency > 50:
                findings.append({
                    "kind": "high_churn",
                    "priority": "P3",
                    "title": f"High churn: '{node.label}'"
                    f" ({node.change_frequency} changes)",
                    "description": "Module changes frequently — may indicate instability",
                    "effort": "1 session",
                    "leverage": "Medium (identifies instability)",
                    "risk": "Low",
                })
        return findings
