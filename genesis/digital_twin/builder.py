"""
Digital Twin Builder — orchestrates all extractors to reconstruct
the entire repository as a single DigitalTwin with 14-d metadata.

Usage:
    builder = DigitalTwinBuilder("/path/to/repo")
    twin = builder.build()
    print(twin.summary())
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

from genesis.digital_twin.extractors import (
    ArchitectureExtractor,
    ContractsExtractor,
    DependenciesExtractor,
    EventsExtractor,
    EvolutionExtractor,
    PersistenceExtractor,
    SemanticsExtractor,
    SpecsExtractor,
    SyntaxExtractor,
    TestsExtractor,
)
from genesis.digital_twin.model import DigitalTwin


class DigitalTwinBuilder:
    """Build a complete repository Digital Twin by running all extractors."""

    def __init__(self, root: str | Path, twin: DigitalTwin | None = None):
        self.root = Path(root).resolve()
        self.timings: dict[str, float] = {}
        self._twin = twin

    def build(self) -> DigitalTwin:
        twin = self._twin if self._twin is not None else DigitalTwin()
        twin.metadata["root"] = str(self.root)
        twin.built_at = time.time()

        extractors = [
            ("syntax", SyntaxExtractor(self.root)),
            ("semantics", SemanticsExtractor(self.root)),
            ("contracts", ContractsExtractor(self.root)),
            ("dependencies", DependenciesExtractor(self.root)),
            ("persistence", PersistenceExtractor(self.root)),
            ("events", EventsExtractor(self.root)),
            ("architecture", ArchitectureExtractor(self.root)),
            ("specs", SpecsExtractor(self.root)),
            ("tests", TestsExtractor(self.root)),
            ("evolution", EvolutionExtractor(self.root)),
        ]

        for name, extractor in extractors:
            t0 = time.time()
            try:
                extractor.run(twin)
            except Exception as e:
                print(f"  [Twin] {name} extractor failed: {e}")
            self.timings[name] = time.time() - t0

        # — cross-ref specs to implementations —
        specs_ext = SpecsExtractor(self.root)
        try:
            specs_ext.link_nodes_to_specs(twin)
        except Exception:
            pass

        # — compute cross-refs between all dimensions —
        self._compute_cross_refs(twin)
        twin.metadata["extractor_timings"] = self.timings
        return twin

    def _compute_cross_refs(self, twin: DigitalTwin):
        for node in twin.nodes:
            # syntax <-> semantics
            if node.docstring and node.source_text:
                node.add_cross_ref("syntax_semantics", node.id)
            # contracts <-> tests
            if node.base_classes and node.test_count > 0:
                node.add_cross_ref("contracts_tests", node.id)
            # persistence <-> events
            if node.persistence_kind and node.event_emissions:
                node.add_cross_ref("persistence_events", node.id)
            # architecture <-> specs
            if node.layer is not None and node.spec_refs:
                node.add_cross_ref("architecture_specs", node.id)
            # dependencies <-> evolution
            if node.depends_on and node.change_frequency > 0:
                node.add_cross_ref("dependencies_evolution", node.id)
            # runtime <-> persistence
            if node.service_name and node.persistence_kind:
                node.add_cross_ref("runtime_persistence", node.id)
