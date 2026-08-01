"""
Hypothesis Engine — Phase 5 of the ULTRA EVOLUTION LOOP.

Generates concrete architectural hypotheses from DigitalTwin gaps + metrics.
Each hypothesis carries expected impact, risk, confidence, ROI, and mathematical justification.
"""

from __future__ import annotations

import re
from collections import Counter, defaultdict
from typing import Any

from genesis.digital_twin.model import DigitalTwin, TwinNode


class Hypothesis:
    """An actionable architectural improvement hypothesis."""

    def __init__(
        self,
        kind: str,
        title: str,
        description: str,
        target_ids: list[str],
        expected_impact: dict[str, float],
        risk: float,
        confidence: float,
        justification: str,
        implementation_steps: list[str],
        effort: str = "1 session",
    ):
        self.kind = kind
        self.title = title
        self.description = description
        self.target_ids = target_ids
        self.expected_impact = expected_impact
        self.risk = risk
        self.confidence = confidence
        self.justification = justification
        self.implementation_steps = implementation_steps
        self.effort = effort

    @property
    def roe(self) -> float:
        """Return on Engineering = expected_gain / (risk * effort_factor)."""
        gain = sum(abs(v) for v in self.expected_impact.values())
        effort_factor = {"Partial session": 0.3, "1 session": 0.5, "Multiple sessions": 1.0}
        ef = effort_factor.get(self.effort, 0.5)
        risk_penalty = 1.0 + self.risk
        return round(gain * self.confidence / (ef * risk_penalty), 4)

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": self.kind,
            "title": self.title,
            "description": self.description,
            "target_ids": self.target_ids,
            "expected_impact": self.expected_impact,
            "risk": self.risk,
            "confidence": self.confidence,
            "roe": self.roe,
            "justification": self.justification,
            "implementation_steps": self.implementation_steps,
            "effort": self.effort,
        }


class HypothesisEngine:
    """Generate architectural hypotheses from DigitalTwin analysis."""

    def __init__(self, twin: DigitalTwin):
        self.twin = twin

    def generate(self, findings: list[dict[str, Any]], metrics: dict[str, Any]) -> list[Hypothesis]:
        hypotheses: list[Hypothesis] = []

        hypotheses.extend(self._from_duplications(findings))
        hypotheses.extend(self._from_layer_violations(findings))
        hypotheses.extend(self._from_hubs(findings))
        hypotheses.extend(self._from_unimplemented_specs(findings))
        hypotheses.extend(self._from_unverified_contracts(findings))
        hypotheses.extend(self._from_metric_gaps(metrics))
        hypotheses.extend(self._from_extractor_gaps())
        hypotheses.extend(self._from_conceptual_overlap(findings))

        return sorted(hypotheses, key=lambda h: h.roe, reverse=True)

    def _from_duplications(self, findings: list[dict]) -> list[Hypothesis]:
        hyps = []
        for f in findings:
            if f.get("kind") != "duplication":
                continue
            # — find duplicate class nodes —
            title = f.get("title", "")
            name_match = re.match(r"'(\w+)'", title)
            if not name_match:
                continue
            name = name_match.group(1)
            nodes = [n for n in self.twin.find_nodes(kind="class") if n.label == name]
            if len(nodes) < 2:
                continue

            modules = [n.module or n.file_path for n in nodes]
            primary = nodes[0]
            merge_count = len(nodes) - 1

            hyps.append(Hypothesis(
                kind="merge_duplicates",
                title=f"Merge '{name}' into canonical definition",
                description=f"'{name}' appears in {len(nodes)} modules: {modules}. "
                            f"Merge into a single canonical definition.",
                target_ids=[n.id for n in nodes],
                expected_impact={
                    "repository_intelligence_score": 0.03 * merge_count,
                    "semantic_duplication_index": -0.01 * merge_count,
                    "maintainability_index": 0.01 * merge_count,
                },
                risk=0.3,
                confidence=0.7,
                justification=f"Removing {merge_count} duplicate definitions of '{name}' reduces "
                             f"semantic entropy by eliminating ambiguous references. "
                             f"Duplication index decreases by ~{0.01 * merge_count:.3f}.",
                implementation_steps=[
                    f"Extract '{name}' from {[m for m in modules[1:]]} into shared module",
                    f"Update all imports to reference canonical definition",
                    f"Remove duplicate class definitions",
                    f"Verify compilation and tests pass",
                ],
                effort="1 session",
            ))
        return hyps

    def _from_layer_violations(self, findings: list[dict]) -> list[Hypothesis]:
        hyps = []
        for f in findings:
            if f.get("kind") != "layer_violation":
                continue
            title = f.get("title", "")
            parts = title.split(" imports ")
            if len(parts) != 2:
                continue
            source = parts[0].split("(")[0].strip()
            target = parts[1].split("(")[0].strip()

            hyps.append(Hypothesis(
                kind="fix_layer_violation",
                title=f"Fix layer violation: {source} -> {target}",
                description=f"Module {source} imports from higher-layer {target}. "
                            f"Introduce abstraction or restructure dependencies.",
                target_ids=[source, target],
                expected_impact={
                    "architectural_stability": 0.05,
                    "maintainability_index": 0.02,
                },
                risk=0.5,
                confidence=0.6,
                justification="Layer violations increase coupling and reduce maintainability. "
                             "Each violation adds ~0.05 to architectural entropy. "
                             "Fixing restores layering invariant and improves stability.",
                implementation_steps=[
                    f"Analyze what {source} needs from {target}",
                    f"Extract required interface into lower-layer abstraction",
                    f"Update {source} to depend on abstraction instead of {target}",
                    f"Verify no circular dependencies introduced",
                ],
                effort="1 session",
            ))
        return hyps

    def _from_hubs(self, findings: list[dict]) -> list[Hypothesis]:
        hyps = []
        for f in findings:
            if f.get("kind") != "hub_module":
                continue
            title = f.get("title", "")
            name_match = re.search(r"'([^']+)'", title)
            if not name_match:
                continue
            hub = name_match.group(1)
            count_match = re.search(r"(\d+) modules?", title)
            dep_count = int(count_match.group(1)) if count_match else 0

            hyps.append(Hypothesis(
                kind="split_hub",
                title=f"Split hub module: {hub}",
                description=f"{hub} is imported by {dep_count} modules. "
                            f"Split into focused sub-modules to reduce coupling.",
                target_ids=[hub],
                expected_impact={
                    "subsystem_cohesion": 0.03,
                    "maintainability_index": 0.02,
                },
                risk=0.6,
                confidence=0.5,
                justification=f"Hub modules create coupling bottlenecks. "
                             f"With {dep_count} dependents, any change propagates widely. "
                             f"Splitting reduces dependency centrality by distributing interfaces.",
                implementation_steps=[
                    f"Analyze {hub}'s public interface",
                    f"Group functions/classes by concern",
                    f"Extract into separate modules",
                    f"Update imports across all {dep_count} dependents",
                ],
                effort="Multiple sessions",
            ))
        return hyps

    def _from_unimplemented_specs(self, findings: list[dict]) -> list[Hypothesis]:
        hyps = []
        unlinked = [f for f in findings if f.get("kind") == "drift" and "Unimplemented" in f.get("title", "")]
        if not unlinked:
            return hyps

        # — group by topic —
        topic_map: dict[str, list[dict]] = defaultdict(list)
        for f in unlinked:
            desc = f.get("title", "")
            for topic in ["compiler", "store", "event", "execution", "capability",
                          "security", "validation", "knowledge", "scheduler",
                          "observability", "identity", "certification", "plugin"]:
                if topic in desc.lower():
                    topic_map[topic].append(f)
                    break
            else:
                topic_map["other"].append(f)

        for topic, group in topic_map.items():
            count = len(group)
            hyps.append(Hypothesis(
                kind="link_specs",
                title=f"Link {count} {topic} specs to implementations",
                description=f"{count} unimplemented normative requirements in '{topic}' domain. "
                            f"Link to existing code or implement missing functionality.",
                target_ids=[f.get("title", "")[:40] for f in group[:5]],
                expected_impact={
                    "specification_completeness": 0.1 * min(count / 10, 1.0),
                    "repository_intelligence_score": 0.02 * min(count / 20, 1.0),
                },
                risk=0.2,
                confidence=0.8,
                justification=f"Increasing spec coverage by {count} links improves "
                             f"traceability and verification. Each link enables automated "
                             f"compliance checking and drift detection.",
                implementation_steps=[
                    f"Analyze each {topic} spec for implementation keywords",
                    f"Search codebase for matching classes/functions",
                    f"Add spec-ref annotations to implementations",
                    f"Verify traceability matrix completeness",
                ],
                effort="Multiple sessions" if count > 20 else "1 session",
            ))
        return hyps

    def _from_unverified_contracts(self, findings: list[dict]) -> list[Hypothesis]:
        hyps = []
        unverified = [f for f in findings if f.get("kind") == "unverified_contract"]
        if not unverified:
            return hyps

        for f in unverified:
            title = f.get("title", "")
            name_match = re.match(r"Unverified contract: '([^']+)'", title)
            if not name_match:
                continue
            name = name_match.group(1)
            node = next((n for n in self.twin.find_nodes(kind="class") if n.label == name), None)
            if not node:
                continue

            hyps.append(Hypothesis(
                kind="add_tests",
                title=f"Add contract tests for '{name}'",
                description=f"'{name}' defines a protocol/interface with no tests. "
                            f"Add contract tests to verify implementations.",
                target_ids=[node.id],
                expected_impact={
                    "contract_coverage": 0.01,
                    "maintainability_index": 0.005,
                },
                risk=0.1,
                confidence=0.9,
                justification=f"Untested contracts are the #1 source of regression bugs. "
                             f"Adding contract tests for {name} improves verification surface.",
                implementation_steps=[
                    f"Analyze {name}'s interface methods",
                    f"Create test stub with mock implementations",
                    f"Verify each method handles expected/edge cases",
                    f"Run tests to confirm contract compliance",
                ],
                effort="Partial session",
            ))
        return hyps

    def _from_metric_gaps(self, metrics: dict[str, Any]) -> list[Hypothesis]:
        hyps = []

        spec_cov = metrics.get("specification_completeness", 0)
        if spec_cov < 0.5:
            hyps.append(Hypothesis(
                kind="improve_spec_coverage",
                title="Improve overall specification coverage",
                description=f"Spec coverage is {spec_cov:.0%}. Target: 100%. "
                            f"Systematically link all normative requirements.",
                target_ids=[],
                expected_impact={
                    "specification_completeness": 0.5 - spec_cov,
                    "repository_intelligence_score": 0.05,
                },
                risk=0.2,
                confidence=0.7,
                justification=f"Spec completeness is the strongest predictor of platform "
                             f"maturity. Current {spec_cov:.0%} leaves {1-spec_cov:.0%} of "
                             f"requirements untraceable — each represents a verification gap.",
                implementation_steps=[
                    "Run traceability matrix to identify all unlinked specs",
                    "For each, search codebase for implementation patterns",
                    "Document spec-code mapping in spec_ref annotations",
                    "Verify all 150 normative requirements are linked",
                ],
                effort="Multiple sessions",
            ))

        contract_cov = metrics.get("contract_coverage", 0)
        if contract_cov < 0.5:
            hyps.append(Hypothesis(
                kind="improve_contract_coverage",
                title="Improve contract test coverage",
                description=f"Contract test coverage is {contract_cov:.0%}. "
                            f"Add tests for all protocols and interfaces.",
                target_ids=[],
                expected_impact={
                    "contract_coverage": 0.5 - contract_cov,
                    "maintainability_index": 0.05,
                },
                risk=0.1,
                confidence=0.8,
                justification=f"Contracts without tests are liabilities. "
                             f"Every untested interface accumulates verification debt.",
                implementation_steps=[
                    "Identify all protocols and interfaces without tests",
                    "Prioritize by dependency centrality",
                    "Generate test skeletons for each",
                    "Run and verify contract compliance",
                ],
                effort="Multiple sessions",
            ))

        cap_maturity = metrics.get("capability_maturity", 0)
        if cap_maturity < 0.5:
            hyps.append(Hypothesis(
                kind="wire_capability_graph",
                title="Wire capability dependency graph",
                description=f"Capability maturity is {cap_maturity:.0%}. "
                            f"Add dependency relationships between capabilities.",
                target_ids=[],
                expected_impact={
                    "capability_maturity": 0.5 - cap_maturity,
                    "repository_intelligence_score": 0.03,
                },
                risk=0.3,
                confidence=0.6,
                justification="Flat capability graphs prevent dependency resolution, "
                             "activation ordering, and impact analysis. Without edges, "
                             "the platform cannot determine which capabilities are affected "
                             "by a change.",
                implementation_steps=[
                    "Analyze import graph between capability modules",
                    "Add explicit dependency declarations",
                    "Verify acyclic property of capability graph",
                    "Update discovery/resolution to use graph",
                ],
                effort="Multiple sessions",
            ))

        return hyps

    def _from_extractor_gaps(self) -> list[Hypothesis]:
        """Find gaps in the DigitalTwin extractors by analyzing the extractor code itself."""
        hyps = []
        extractor_nodes = [
            n for n in self.twin.nodes
            if "digital_twin/extractors" in (n.file_path or "")
        ]

        # — check which extractors lack full coverage —
        missing_aspects = []
        if not any("persistence" in (n.file_path or "") for n in extractor_nodes):
            missing_aspects.append("persistence")
        if not any("evolution" in (n.file_path or "") for n in extractor_nodes):
            missing_aspects.append("evolution")

        # — check for extractor self-test coverage —
        extractors_tested = []
        for n in extractor_nodes:
            if n.kind == "class" and n.test_count == 0:
                extractors_tested.append(n.label)

        if extractors_tested:
            hyps.append(Hypothesis(
                kind="add_extractor_tests",
                title=f"Add tests for extractors: {', '.join(extractors_tested[:3])}",
                description=f"{len(extractors_tested)} extractor classes lack tests. "
                            f"Add unit tests for each extractor.",
                target_ids=[n.id for n in extractor_nodes if n.kind == "class" and n.test_count == 0],
                expected_impact={
                    "maintainability_index": 0.02,
                    "contract_coverage": 0.02,
                },
                risk=0.1,
                confidence=0.9,
                justification=f"Extractors are the foundation of the DigitalTwin. "
                             f"Untested extractors produce unreliable twin data. "
                             f"Each test increases confidence in repository intelligence.",
                implementation_steps=[
                    f"Create test file for each untested extractor",
                    f"Test with sample AST/code patterns",
                    f"Verify extracted metadata is correct",
                    f"Run full test suite",
                ],
                effort="1 session",
            ))

        return hyps

    def _from_conceptual_overlap(self, findings: list[dict]) -> list[Hypothesis]:
        hyps = []
        for f in findings:
            if f.get("kind") != "conceptual_overlap":
                continue
            title = f.get("title", "")
            tag_match = re.search(r"Overlapping (\w+) in", title)
            if not tag_match:
                continue
            tag = tag_match.group(1)

            hyps.append(Hypothesis(
                kind="split_overlap",
                title=f"Resolve overlapping {tag} concerns",
                description=f"Multiple {tag}-related classes in same module. "
                            f"Consider splitting into focused sub-modules.",
                target_ids=[f.get("title", "")],
                expected_impact={
                    "subsystem_cohesion": 0.02,
                    "architectural_entropy": 0.01,
                },
                risk=0.3,
                confidence=0.5,
                justification=f"Overlapping concerns within a module reduce cohesion "
                             f"and increase cognitive load. Separation improves "
                             f"discoverability and single-responsibility adherence.",
                implementation_steps=[
                    f"Analyze shared vs distinct functionality",
                    f"Extract distinct concerns into separate modules",
                    f"Update cross-references",
                ],
                effort="1 session",
            ))
        return hyps
