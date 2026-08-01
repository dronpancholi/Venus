"""
Self-Analysis — the DigitalTwin analyzes its own implementation.

Detects:
  - Missing extractor dimensions
  - Low-coverage extractors  
  - Gaps in the twin's own metadata
  - Extractor implementation weaknesses
"""

from __future__ import annotations

from typing import Any

from genesis.digital_twin.model import DigitalTwin


TWIN_REQUIRED_DIMENSIONS = {
    "syntax": "source_text",
    "semantics": "purpose",
    "ownership": "layer",
    "contracts": "interfaces",
    "dependencies": "imports",
    "lifecycle": "change_frequency",
    "persistence": "persistence_kind",
    "runtime": "service_name",
    "role": "role",
    "specs": "spec_refs",
    "tests": "test_count",
    "evolution": "version_history",
}

TWIN_DIR = "genesis/digital_twin"
EXTRACTORS_DIR = f"{TWIN_DIR}/extractors"
ANALYZERS_DIR = f"{TWIN_DIR}/analyzers"


class SelfAnalyzer:
    """Analyze the DigitalTwin's own implementation for gaps."""

    def __init__(self, twin: DigitalTwin):
        self.twin = twin

    def analyze(self) -> list[dict[str, Any]]:
        findings: list[dict[str, Any]] = []

        findings.extend(self._missing_dimensions())
        findings.extend(self._low_coverage_extractors())
        findings.extend(self._missing_self_tests())
        findings.extend(self._twin_coverage_gaps())

        return findings

    def _missing_dimensions(self) -> list[dict[str, Any]]:
        """Check which metadata dimensions are missing from twin nodes."""
        findings = []
        for dim_name, field_name in TWIN_REQUIRED_DIMENSIONS.items():
            nodes_with = 0
            total = 0
            for node in self.twin.find_nodes(kind="class"):
                total += 1
                if getattr(node, field_name, None):
                    if isinstance(getattr(node, field_name), (list, tuple)):
                        if len(getattr(node, field_name)) > 0:
                            nodes_with += 1
                    else:
                        nodes_with += 1

            if total > 0:
                coverage = nodes_with / total
                if coverage < 0.5:
                    findings.append({
                        "kind": "low_dimension_coverage",
                        "priority": "P2",
                        "title": f"Low coverage: '{dim_name}' ({coverage:.0%})",
                        "description": f"Dimension '{dim_name}' (field '{field_name}') "
                                     f"populated on only {coverage:.0%} of class nodes.",
                        "effort": "1 session",
                        "leverage": "Medium",
                        "risk": "Low",
                        "coverage": coverage,
                        "dimension": dim_name,
                    })
        return findings

    def _low_coverage_extractors(self) -> list[dict[str, Any]]:
        """Check which extractors have low coverage of their target dimension."""
        findings = []
        extractor_names = [
            "SyntaxExtractor", "SemanticsExtractor", "ContractsExtractor",
            "DependenciesExtractor", "PersistenceExtractor", "EventsExtractor",
            "ArchitectureExtractor", "SpecsExtractor", "TestsExtractor",
            "EvolutionExtractor",
        ]

        for name in extractor_names:
            nodes = self.twin.find_nodes(kind="class", label=name)
            if not nodes:
                findings.append({
                    "kind": "missing_extractor",
                    "priority": "P1",
                    "title": f"Missing extractor: {name}",
                    "description": f"Extractor class '{name}' not found in DigitalTwin. "
                                   f"It may not be loading or may not exist.",
                    "effort": "1 session",
                    "leverage": "High",
                    "risk": "Low",
                })

        return findings

    def _missing_self_tests(self) -> list[dict[str, Any]]:
        """Check whether DigitalTwin code has adequate tests."""
        findings = []
        twin_nodes = [n for n in self.twin.nodes if TWIN_DIR in (n.file_path or "")]
        untested = [n for n in twin_nodes if n.kind == "class" and n.test_count == 0]

        if untested:
            findings.append({
                "kind": "untested_twin_code",
                "priority": "P2",
                "title": f"Untested DigitalTwin code: {len(untested)} classes",
                "description": f"{len(untested)} classes in the DigitalTwin have no tests. "
                               f"Classes: {', '.join(n.label for n in untested[:5])}",
                "effort": "1 session",
                "leverage": "High",
                "risk": "Low",
                "untested_classes": [n.label for n in untested],
            })

        return findings

    def _twin_coverage_gaps(self) -> list[dict[str, Any]]:
        """Analyze what fraction of the repository is captured in the twin."""
        findings = []

        all_py_files = [
            n for n in self.twin.nodes
            if n.kind == "file" and n.file_path and n.file_path.endswith(".py")
        ]
        genesis_py = [n for n in all_py_files if n.file_path.startswith("genesis/")]

        classes_in_twin = len(self.twin.find_nodes(kind="class"))
        classes_with_source = sum(
            1 for n in self.twin.find_nodes(kind="class") if n.source_text
        )
        classes_with_layer = sum(
            1 for n in self.twin.find_nodes(kind="class") if n.layer is not None
        )

        if classes_in_twin > 0:
            source_cov = classes_with_source / classes_in_twin
            layer_cov = classes_with_layer / classes_in_twin

            if source_cov < 0.8:
                findings.append({
                    "kind": "low_source_coverage",
                    "priority": "P2",
                    "title": f"Low source text coverage: {source_cov:.0%}",
                    "description": f"Only {source_cov:.0%} of class nodes have source_text populated.",
                    "effort": "Partial session",
                    "leverage": "Medium",
                    "risk": "Low",
                })

            if layer_cov < 0.8:
                findings.append({
                    "kind": "low_layer_coverage",
                    "priority": "P3",
                    "title": f"Low layer assignment coverage: {layer_cov:.0%}",
                    "description": f"Only {layer_cov:.0%} of class nodes have layer assignments.",
                    "effort": "Partial session",
                    "leverage": "Low",
                    "risk": "Low",
                })

        # — check for non-genesis file coverage —
        external_py = [n for n in all_py_files if not n.file_path.startswith("genesis/")]
        if external_py:
            findings.append({
                "kind": "external_files_in_twin",
                "priority": "P3",
                "title": f"Non-genesis files in twin: {len(external_py)}",
                "description": f"DigitalTwin contains {len(external_py)} files outside genesis/.",
                "effort": "Partial session",
                "leverage": "Low",
                "risk": "Low",
            })

        return findings
