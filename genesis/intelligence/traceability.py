"""
VRIP Phase 3 — Traceability Matrix

Every normative statement maps to implementation, tests, verification, ADR, subsystem.
Missing items become architectural gaps.
Auto-links requirements to implementing code via heuristic keyword matching.
"""

from __future__ import annotations

import re
from typing import Any

from .kgraph import KnowledgeGraph


# Keyword-to-kind mappings for auto-linking normative requirements
_NORMATIVE_KEYWORDS: dict[str, str] = {
    # Storage providers
    "artifact_store": "genesis.persistence.ArtifactStore",
    "artifact store": "genesis.persistence.ArtifactStore",
    "knowledge_store": "genesis.persistence.KnowledgeStore",
    "knowledge store": "genesis.persistence.KnowledgeStore",
    "history_store": "genesis.persistence.HistoryStore",
    "history store": "genesis.persistence.HistoryStore",
    "metadata_store": "genesis.persistence.MetadataStore",
    "metadata store": "genesis.persistence.MetadataStore",
    "checkpoint_store": "genesis.persistence.CheckpointStore",
    "checkpoint store": "genesis.persistence.CheckpointStore",
    # Domain services
    "compiler": "genesis.compiler.compiler.Compiler",
    "compilation": "genesis.compiler.compiler.Compiler",
    "knowledge graph": "genesis.graph.engine.KnowledgeGraphEngine",
    "execution": "genesis.runtime.executor.ExecutionEngine",
    "executor": "genesis.runtime.executor.ExecutionEngine",
    "metadata": "genesis.core.metadata.MetadataEngine",
    "metadata engine": "genesis.core.metadata.MetadataEngine",
    "diagnostics": "genesis.diagnostics.diagnostics.Diagnostics",
    "indexer": "genesis.indexer.indexer.RepositoryIndexer",
    "plugin": "genesis.plugin.manager.PluginManager",
    "capability": "genesis.capability.registry.CapabilityRegistry",
    "capability registry": "genesis.capability.registry.CapabilityRegistry",
    # Infrastructure
    "event": "genesis.events.bus.EventBus",
    "eventbus": "genesis.events.bus.EventBus",
    "event bus": "genesis.events.bus.EventBus",
    "di": "genesis.di.container.ServiceProvider",
    "dependency injection": "genesis.di.container.ServiceProvider",
    "validation": "genesis.validation.engine.ValidationEngine",
    "validator": "genesis.validation.engine.ValidationEngine",
    # Lifecycle
    "platform": "genesis.platform.VenusPlatform",
    "lifecycle": "genesis.platform.VenusPlatform",
    "shutdown": "genesis.di.container.ServiceProvider",
    "bootstrap": "genesis.di.bootstrap",
    # Architecture
    "layer": "genesis.tests.test_architecture.ArchitectureAnalysis",
    "architecture": "genesis.tests.test_architecture.ArchitectureAnalysis",
    "uir": "genesis.core.uir",
    "universal intermediate": "genesis.core.uir",
    # Intelligence
    "vrip": "genesis.intelligence.engine.RepositoryIntelligence",
    "intelligence": "genesis.intelligence.engine.RepositoryIntelligence",
    "knowledge graph node": "genesis.intelligence.kgraph",
    # Core objects
    "audit": "genesis.core.base.AuditEntry",
    "entity": "genesis.core.base.Entity",
    "artifact": "genesis.core.base.Artifact",
    "observation": "genesis.runtime.executor.ExecutionEngine",
}


class TraceabilityMatrix:
    """Phase 3: Map normative requirements to implementation artifacts."""

    def __init__(self, kg: KnowledgeGraph):
        self.kg = kg
        self._impl_cache: dict[str, str | None] = {}

    def _resolve_impl(self, module_path: str) -> str | None:
        """Resolve a module path to a knowledge graph node id."""
        if module_path in self._impl_cache:
            return self._impl_cache[module_path]
        parts = module_path.split(".")
        candidates = self.kg.find_nodes(kind="class") + self.kg.find_nodes(kind="file")
        for node in candidates:
            if node.label == parts[-1] or node.node_id.endswith(parts[-1]):
                self._impl_cache[module_path] = node.node_id
                return node.node_id
        # Try as module
        for node in self.kg.find_nodes(kind="file"):
            if parts[-1] in node.label:
                self._impl_cache[module_path] = node.node_id
                return node.node_id
        self._impl_cache[module_path] = None
        return None

    def _auto_link(self, norm: Any) -> bool:
        """Heuristically link a normative requirement to implementing nodes."""
        label_lower = norm.label.lower()
        desc = norm.attrs.get("description", "").lower()
        text = f"{label_lower} {desc}"

        for keyword, impl_path in _NORMATIVE_KEYWORDS.items():
            if keyword in text:
                impl_id = self._resolve_impl(impl_path)
                if impl_id is not None:
                    existing = self.kg.find_edges(kind="implements", source=norm.node_id, target=impl_id)
                    if not existing:
                        self.kg.add_edge(norm.node_id, impl_id, "implements")
                        return True
        return False

    def run(self) -> dict[str, Any]:
        norms = self.kg.find_nodes(kind="normative")
        adrs = self.kg.find_nodes(kind="adr")
        caps = self.kg.find_nodes(kind="capability")
        tests = self.kg.find_nodes(kind="test")
        files = self.kg.find_nodes(kind="file")
        classes = self.kg.find_nodes(kind="class")

        auto_linked = 0
        covered_norms = 0
        uncovered_norms = []
        for norm in norms:
            # Always attempt auto-link regardless of existing coverage
            if self._auto_link(norm):
                auto_linked += 1
            neighbors = self.kg.neighbors(norm.node_id)
            has_impl = any(n.kind in ("class", "file", "test", "capability") for n in neighbors)
            if has_impl:
                covered_norms += 1
            else:
                uncovered_norms.append(norm)

        return {
            "total_norms": len(norms),
            "covered_norms": covered_norms,
            "uncovered_norms": len(uncovered_norms),
            "auto_linked": auto_linked,
            "total_adrs": len(adrs),
            "total_capabilities": len(caps),
            "total_tests": len(tests),
            "total_files": len(files),
            "total_classes": len(classes),
            "traceability_pct": round(covered_norms / max(len(norms), 1) * 100, 1),
        }
