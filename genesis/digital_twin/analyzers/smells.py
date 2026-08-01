"""Architectural smell detection — derives automatically from Digital Twin."""

from __future__ import annotations

from collections import Counter
from typing import Any

from genesis.digital_twin.model import DigitalTwin


class SmellAnalyzer:
    """Detect architectural smells: duplication, god classes, circular deps, etc."""

    def run(self, twin: DigitalTwin) -> list[dict[str, Any]]:
        findings: list[dict[str, Any]] = []

        findings.extend(self._check_name_duplication(twin))
        findings.extend(self._check_god_classes(twin))
        findings.extend(self._check_circular_edges(twin))
        findings.extend(self._check_layer_violations(twin))
        findings.extend(self._check_orphaned_nodes(twin))
        findings.extend(self._check_unverified_contracts(twin))

        return findings

    def _check_name_duplication(self, twin: DigitalTwin) -> list[dict[str, Any]]:
        findings = []
        name_counts: Counter = Counter()
        name_modules: dict[str, list[str]] = {}

        for node in twin.find_nodes(kind="class"):
            name_counts[node.label] += 1
            name_modules.setdefault(node.label, []).append(node.module or "")

        for name, count in name_counts.items():
            if count > 1:
                findings.append({
                    "kind": "duplication",
                    "priority": "P1",
                    "title": f"'{name}' appears in {count} modules",
                    "description": f"Modules: {name_modules[name]}",
                    "effort": "1 session",
                    "leverage": "Medium (reduces entropy)",
                    "risk": "Medium",
                })
        return findings

    def _check_god_classes(self, twin: DigitalTwin) -> list[dict[str, Any]]:
        findings = []
        for node in twin.nodes:
            if node.kind != "class":
                continue
            children = twin.find_nodes(kind="method")
            method_count = sum(1 for m in children if node.id in m.id)
            if method_count > 20:
                findings.append({
                    "kind": "god_class",
                    "priority": "P2",
                    "title": f"'{node.label}' has {method_count} methods",
                    "description": f"Large class in {node.file_path}",
                    "effort": "Partial session",
                    "leverage": "Medium (improves cohesion)",
                    "risk": "Low",
                })
        return findings

    def _check_circular_edges(self, twin: DigitalTwin) -> list[dict[str, Any]]:
        findings = []
        import_edges = twin.find_edges("imports")
        edge_set = {(s, t) for s, t, _ in import_edges}
        for s, t in edge_set:
            if (t, s) in edge_set and s < t:
                findings.append({
                    "kind": "circular_dependency",
                    "priority": "P1",
                    "title": f"Circular import: {s} <-> {t}",
                    "description": "Two modules import each other",
                    "effort": "Partial session",
                    "leverage": "High (eliminates cycle)",
                    "risk": "Low",
                })
        return findings

    def _check_layer_violations(self, twin: DigitalTwin) -> list[dict[str, Any]]:
        findings = []
        for edge in twin.find_edges("imports"):
            s, t, _ = edge
            sn = twin.get_node(s)
            tn = twin.get_node(t)
            if not sn or not tn or sn.layer is None or tn.layer is None:
                continue
            if "/tests/" in s or "/tests/" in t:
                continue
            if sn.layer < tn.layer:
                    findings.append({
                        "kind": "layer_violation",
                        "priority": "P0",
                        "title": f"Layer violation: {s} (L{sn.layer}) imports {t} (L{tn.layer})",
                        "description": f"Lower layer {sn.layer_name} imports from higher layer {tn.layer_name}",
                        "effort": "1 session",
                        "leverage": "High (restores layering)",
                        "risk": "Medium",
                    })
        return findings

    def _check_orphaned_nodes(self, twin: DigitalTwin) -> list[dict[str, Any]]:
        findings = []
        for node in twin.find_nodes(kind="class"):
            incoming = twin.find_edges("imports")
            outgoing_edges = twin.edges_from(node.id)
            has_outgoing = bool(outgoing_edges)
            has_incoming = any(t == node.id for _, t, _ in incoming)
            if not has_incoming and not has_outgoing:
                findings.append({
                    "kind": "orphan",
                    "priority": "P3",
                    "title": f"Orphan class: '{node.label}'",
                    "description": f"No incoming or outgoing import edges — possibly dead code",
                    "effort": "Partial session",
                    "leverage": "Low (cleanup)",
                    "risk": "Low",
                })
        return findings

    def _check_unverified_contracts(self, twin: DigitalTwin) -> list[dict[str, Any]]:
        findings = []
        for node in twin.nodes:
            if not node.protocols and not node.interfaces:
                continue
            if node.test_count == 0:
                findings.append({
                    "kind": "unverified_contract",
                    "priority": "P2",
                    "title": f"Unverified contract: '{node.label}'",
                    "description": f"Protocol/interface with no tests in {node.file_path}",
                    "effort": "Partial session",
                    "leverage": "Medium (improves verification)",
                    "risk": "Low",
                })
        return findings
