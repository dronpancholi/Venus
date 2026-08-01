"""
VRIP Phase 6 — Capability Intelligence

Build a capability model for every registered capability.
Determines purpose, inputs, outputs, deps, spec coverage, tests, consumers.
"""

from __future__ import annotations

from typing import Any

from genesis.capability.registry import capability_registry
from .kgraph import KnowledgeGraph


class CapabilityIntelligence:
    """Phase 6: Analyze every registered capability."""

    def __init__(self, kg: KnowledgeGraph):
        self.kg = kg

    def run(self) -> list[dict[str, Any]]:
        results = []
        for cap in capability_registry.all():
            info = self._analyze(cap)
            results.append(info)
            self.kg.add_node(
                "capability", f"cap:{cap.name}",
                label=cap.name,
                description=cap.description,
                version=cap.version,
                dependencies=cap.dependencies,
                interfaces=len(cap.interfaces),
                validation_rules=len(cap.validation_rules),
            )
        return results

    def _analyze(self, cap) -> dict[str, Any]:
        name = cap.name
        deps = cap.dependencies
        consumers = []
        for other in capability_registry.all():
            if name in other.dependencies:
                consumers.append(other.name)

        # Find files related to this capability
        related_files = [
            n.label for n in self.kg.find_nodes(kind="file")
            if name in n.label or name in n.attrs.get("subsystem", "")
        ]

        # Check spec coverage (simplified)
        specs = self.kg.find_nodes(kind="normative")
        covering_specs = [
            s for s in specs
            if name.replace("_", " ") in s.label.lower()
        ]

        return {
            "name": name,
            "description": cap.description,
            "version": cap.version,
            "dependencies": deps,
            "consumers": consumers,
            "related_files": related_files,
            "spec_references": len(covering_specs),
            "has_interfaces": len(cap.interfaces) > 0,
            "has_validation": len(cap.validation_rules) > 0,
        }
