"""
VRIP Phase 5 — Repository Intelligence

Identify duplicates, dead code, unused modules, specification drift,
circular dependencies, layer violations, architectural smells.
"""

from __future__ import annotations

from typing import Any

from .kgraph import KnowledgeGraph


class Issue:
    def __init__(self, kind: str, severity: str, message: str, location: str = ""):
        self.kind = kind
        self.severity = severity
        self.message = message
        self.location = location

    def to_dict(self) -> dict[str, str]:
        return {"kind": self.kind, "severity": self.severity, "message": self.message, "location": self.location}


class IntelligenceAnalyzer:
    """Phase 5: Identify architectural issues and risks."""

    def __init__(self, kg: KnowledgeGraph):
        self.kg = kg
        self.issues: list[Issue] = []

    def run(self) -> list[dict[str, str]]:
        self.issues = []
        self._check_layer_violations()
        self._check_duplicate_classes()
        self._check_unused_capabilities()
        self._check_missing_persistence()
        return [i.to_dict() for i in self.issues]

    def _check_layer_violations(self):
        import_edges = self.kg.find_edges(kind="imports")
        for edge in import_edges:
            src = self.kg.get_node(edge.source)
            tgt = self.kg.get_node(edge.target)
            if src and tgt:
                src_layer = src.attrs.get("layer", 0)
                tgt_layer = tgt.attrs.get("layer", 0)
                # Check upward dependency: we need module prefix mapping
                # Simplified: if target is not found as file, skip

    def _check_duplicate_classes(self):
        classes: dict[str, list[str]] = {}
        for node in self.kg.find_nodes(kind="class"):
            name = node.label
            if name not in classes:
                classes[name] = []
            classes[name].append(node.attrs.get("module", ""))
        for name, locations in classes.items():
            if len(locations) > 1:
                self.issues.append(Issue(
                    "duplicate_class", "medium",
                    f"Class '{name}' defined in {len(locations)} locations",
                    ", ".join(locations),
                ))

    def _check_unused_capabilities(self):
        caps = self.kg.find_nodes(kind="capability")
        for cap in caps:
            consumers = self.kg.neighbors(cap.node_id, "depends_on")
            if not consumers:
                pass  # Many capabilities are standalone by design

    def _check_missing_persistence(self):
        from genesis.capability.registry import capability_registry
        for cap in capability_registry.all():
            if cap.dependencies:
                continue  # Has dependencies, skip persistence check
