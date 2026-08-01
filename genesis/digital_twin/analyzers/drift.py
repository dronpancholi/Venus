"""Specification drift detection — finds mismatches between spec and implementation."""

from __future__ import annotations

from typing import Any

from genesis.digital_twin.model import DigitalTwin


class DriftAnalyzer:
    """Detect specification drift: unimplemented specs, untraced implementations."""

    def run(self, twin: DigitalTwin) -> list[dict[str, Any]]:
        findings: list[dict[str, Any]] = []

        findings.extend(self._check_unlinked_specs(twin))
        findings.extend(self._check_untraced_classes(twin))
        findings.extend(self._check_adr_coverage(twin))

        return findings

    def _check_unlinked_specs(self, twin: DigitalTwin) -> list[dict[str, Any]]:
        findings = []
        for node in twin.find_nodes(kind="normative"):
            edges = twin.edges_from(node.id)
            impl_edges = [e for e in edges if len(e) >= 2 and "implements" in e]
            if not impl_edges:
                findings.append({
                    "kind": "drift",
                    "priority": "P1",
                    "title": f"Unimplemented spec: {node.label[:60]}",
                    "description": f"Normative requirement with no implementation link",
                    "effort": "1 session",
                    "leverage": "High (restores traceability)",
                    "risk": "Low",
                })
        return findings

    def _check_untraced_classes(self, twin: DigitalTwin) -> list[dict[str, Any]]:
        findings = []
        for node in twin.find_nodes(kind="class"):
            if not node.spec_refs and node.role:
                findings.append({
                    "kind": "untraced",
                    "priority": "P2",
                    "title": f"Untraced {node.role}: '{node.label}'",
                    "description": f"No spec reference in {node.file_path}",
                    "effort": "Partial session",
                    "leverage": "Medium (improves traceability)",
                    "risk": "Low",
                })
        return findings

    def _check_adr_coverage(self, twin: DigitalTwin) -> list[dict[str, Any]]:
        findings = []
        adr_count = len(twin.find_nodes(kind="adr"))
        if adr_count == 0:
            findings.append({
                "kind": "documentation",
                "priority": "P2",
                "title": "No ADRs detected",
                "description": "Architecture decisions not documented",
                "effort": "Multiple sessions",
                "leverage": "High (preserves knowledge)",
                "risk": "Low",
            })
        return findings
