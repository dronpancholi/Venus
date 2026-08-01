"""Hidden coupling detection — finds implicit and transitive dependencies."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from genesis.digital_twin.model import DigitalTwin


class CouplingAnalyzer:
    """Detect hidden coupling: transitive deps, hub modules, overlap."""

    def run(self, twin: DigitalTwin) -> list[dict[str, Any]]:
        findings: list[dict[str, Any]] = []

        findings.extend(self._check_hub_modules(twin))
        findings.extend(self._check_transitive_coupling(twin))
        findings.extend(self._check_conceptual_overlap(twin))

        return findings

    def _check_hub_modules(self, twin: DigitalTwin) -> list[dict[str, Any]]:
        findings = []
        dep_count: dict[str, int] = defaultdict(int)
        for edge in twin.find_edges("imports"):
            _, t, _ = edge
            dep_count[t] += 1

        for node_id, count in sorted(dep_count.items(), key=lambda x: -x[1])[:5]:
            if count >= 5:
                node = twin.get_node(node_id)
                findings.append({
                    "kind": "hub_module",
                    "priority": "P2",
                    "title": f"Hub: '{node_id}' imported by {count} modules",
                    "description": f"Central dependency bottleneck",
                    "effort": "1 session",
                    "leverage": "High (reduces coupling)",
                    "risk": "Medium",
                })
        return findings

    def _check_transitive_coupling(self, twin: DigitalTwin) -> list[dict[str, Any]]:
        findings = []
        import_edges = twin.find_edges("imports")
        direct = {(s, t) for s, t, _ in import_edges}

        for node in twin.nodes:
            if node.kind != "file":
                continue
            node_deps = {t for s, t in direct if s == node.id}
            if len(node_deps) < 3:
                continue
            for dep in node_deps:
                dep_deps = {t for s, t in direct if s == dep}
                transitive = dep_deps - node_deps - {node.id}
                for td in transitive:
                    tn = twin.get_node(td)
                    if tn and tn.layer is not None and node.layer is not None:
                        if tn.layer < node.layer:
                            findings.append({
                                "kind": "transitive_coupling",
                                "priority": "P2",
                                "title": f"Transitive: {node.label} -> {dep} -> {tn.label}",
                                "description": f"Hidden dependency via intermediate module",
                                "effort": "Partial session",
                                "leverage": "Medium (clarifies deps)",
                                "risk": "Low",
                            })
                            break
        return findings

    def _check_conceptual_overlap(self, twin: DigitalTwin) -> list[dict[str, Any]]:
        findings = []
        tag_modules: dict[str, list[str]] = defaultdict(list)
        for node in twin.find_nodes(kind="class"):
            for tag in node.tags:
                if tag:
                    tag_modules[tag].append(node.file_path or node.module or "")

        for tag, mods in tag_modules.items():
            if len(mods) > 3 and len(set(mods)) < len(mods):
                dups = [m for m in set(mods) if mods.count(m) > 1]
                for d in dups[:3]:
                    findings.append({
                        "kind": "conceptual_overlap",
                        "priority": "P3",
                        "title": f"Overlapping {tag} in {d}",
                        "description": f"Multiple {tag} classes in same module — consider splitting",
                        "effort": "Partial session",
                        "leverage": "Low (improves cohesion)",
                        "risk": "Low",
                    })
        return findings
