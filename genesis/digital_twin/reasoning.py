"""
Reasoning Engine — Stage 11 of the OMEGA loop.

Goes beyond graph traversal to answer *why*, deduce causation,
induce patterns, and explain architectural intent.

Reasoning modes:
  Deductive   — apply known rules to derive new facts
  Inductive   — discover patterns and generalize into rules
  Abductive   — infer best explanation for observations
  Counterfactual — "what if" simulation on the twin
  Causal      — trace causes of architectural properties
  Explanatory — answer "why does this exist?"
"""

from __future__ import annotations

import re
from collections import Counter, defaultdict
from typing import Any

from genesis.digital_twin.model import DigitalTwin, TwinNode


class Evidence:
    """A piece of evidence supporting a conclusion."""

    def __init__(self, source: str, fact: str, confidence: float = 1.0):
        self.source = source
        self.fact = fact
        self.confidence = confidence

    def to_dict(self) -> dict[str, Any]:
        return {"source": self.source, "fact": self.fact, "confidence": self.confidence}


class Conclusion:
    """A reasoned conclusion about the architecture."""

    def __init__(
        self,
        kind: str,
        statement: str,
        confidence: float,
        evidence: list[Evidence],
        premises: list[str],
        affected_ids: list[str] | None = None,
    ):
        self.kind = kind
        self.statement = statement
        self.confidence = confidence
        self.evidence = evidence
        self.premises = premises
        self.affected_ids = affected_ids or []

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": self.kind,
            "statement": self.statement,
            "confidence": self.confidence,
            "evidence_count": len(self.evidence),
            "premises": self.premises[:3],
            "affected_ids": self.affected_ids[:5],
        }


class Rule:
    """A reasoning rule: antecedent → consequent."""

    def __init__(
        self,
        name: str,
        antecedent: str,
        consequent: str,
        confidence: float = 0.9,
        kind: str = "deductive",
    ):
        self.name = name
        self.antecedent = antecedent
        self.consequent = consequent
        self.confidence = confidence
        self.kind = kind


class ReasoningEngine:
    """Reason over the DigitalTwin to produce conclusions."""

    def __init__(self, twin: DigitalTwin):
        self.twin = twin
        self.conclusions: list[Conclusion] = []

    # — Public API —

    def reason_all(self) -> list[Conclusion]:
        """Run all reasoning modes."""
        self.conclusions = []
        self.conclusions.extend(self._deduce_roles())
        self.conclusions.extend(self._deduce_layer_compliance())
        self.conclusions.extend(self._deduce_spec_coverage())
        self.conclusions.extend(self._deduce_event_consistency())
        self.conclusions.extend(self._induce_duplication_patterns())
        self.conclusions.extend(self._induce_missing_abstractions())
        self.conclusions.extend(self._abduce_best_explanations())
        self.conclusions.extend(self._explain_architectural_intent())
        return self.conclusions

    def deduce(self, question: str) -> list[Conclusion]:
        """Answer a specific question using deduction."""
        q = question.lower()
        conclusions = []

        if "role" in q or "what is" in q:
            for node in self.twin.find_nodes(kind="class"):
                role = self._infer_role(node)
                if role:
                    conclusions.append(Conclusion(
                        kind="deduction",
                        statement=f"'{node.label}' has role '{role}'",
                        confidence=0.8,
                        evidence=[Evidence(node.id, f"class with name containing '{role}'")],
                        premises=["Classes with specific naming patterns have architectural roles"],
                        affected_ids=[node.id],
                    ))

        if "layer" in q or "violation" in q:
            for node in self.twin.find_nodes(kind="class"):
                if node.layer is not None:
                    imp_edges = self.twin.find_edges("imports")
                    for s, t, _ in imp_edges:
                        sn = self.twin.get_node(s)
                        tn = self.twin.get_node(t)
                        if sn and tn and sn.layer is not None and tn.layer is not None:
                            if sn.layer < tn.layer and "/tests/" not in s:
                                conclusions.append(Conclusion(
                                    kind="deduction",
                                    statement=f"'{s}' violates layering by importing '{t}'",
                                    confidence=0.9,
                                    evidence=[
                                        Evidence(s, f"layer {sn.layer}"),
                                        Evidence(t, f"layer {tn.layer}"),
                                    ],
                                    premises=["Lower layers must not import higher layers"],
                                    affected_ids=[s, t],
                                ))

        if "responsible" in q or "accountable" in q:
            for node in self.twin.find_nodes(kind="class"):
                if node.depended_by:
                    conclusions.append(Conclusion(
                        kind="deduction",
                        statement=f"'{node.label}' is depended upon by {len(node.depended_by)} modules — high responsibility",
                        confidence=0.7,
                        evidence=[Evidence(n, "depends on this") for n in node.depended_by[:5]],
                        premises=["Modules depended upon by many others carry high responsibility"],
                        affected_ids=[node.id],
                    ))

        return conclusions

    def induce(self) -> list[Conclusion]:
        """Discover patterns and generalize into rules."""
        return self._induce_duplication_patterns() + self._induce_missing_abstractions()

    def explain(self, node_id: str) -> list[Conclusion]:
        """Explain why a node exists and its architectural role."""
        node = self.twin.get_node(node_id)
        if not node:
            return [Conclusion(
                kind="explanatory",
                statement=f"Node '{node_id}' not found in DigitalTwin",
                confidence=0.0,
                evidence=[],
                premises=[],
            )]

        conclusions = []

        # — Why does this exist? —
        spec_refs = node.spec_refs[:5]
        if spec_refs:
            conclusions.append(Conclusion(
                kind="explanatory",
                statement=f"'{node.label}' exists to implement specification requirements: "
                         f"{', '.join(spec_refs[:3])}",
                confidence=0.8,
                evidence=[Evidence(ref, "spec requirement") for ref in spec_refs],
                premises=["All implementations exist to satisfy specification requirements"],
                affected_ids=[node.id],
            ))

        # — What depends on it? —
        if node.depended_by:
            conclusions.append(Conclusion(
                kind="explanatory",
                statement=f"'{node.label}' is critical: depended upon by {len(node.depended_by)} modules",
                confidence=0.7,
                evidence=[Evidence(d, "depends on this") for d in node.depended_by[:5]],
                premises=["Modules with many dependents are critical infrastructure"],
                affected_ids=[node.id] + node.depended_by[:5],
            ))

        # — What role does it play? —
        role = self._infer_role(node)
        if role:
            conclusions.append(Conclusion(
                kind="explanatory",
                statement=f"'{node.label}' serves as a '{role}' in the architecture",
                confidence=0.8,
                evidence=[
                    Evidence(node.id, f"naming pattern: '{node.label}'"),
                    Evidence(node.id, f"layer: {node.layer_name}"),
                ],
                premises=["Architectural role is inferred from naming, dependencies, and layer"],
                affected_ids=[node.id],
            ))

        if not conclusions:
            conclusions.append(Conclusion(
                kind="explanatory",
                statement=f"No strong explanation for '{node.label}' — it may be dead code or untracked",
                confidence=0.3,
                evidence=[],
                premises=["Every module should have a traceable reason for existence"],
                affected_ids=[node.id],
            ))

        return conclusions

    def counterfactual(self, action: str, target_id: str) -> list[Conclusion]:
        """What if we removed/moved/changed a node?"""
        conclusions = []
        node = self.twin.get_node(target_id)
        if not node:
            return conclusions

        if action == "remove":
            affected = []
            if node.depended_by:
                for dep in node.depended_by:
                    affected.append(dep)
            for edge in self.twin.find_edges("imports"):
                if edge[1] == target_id:
                    affected.append(edge[0])

            confidence = 0.6 if affected else 0.9
            conclusions.append(Conclusion(
                kind="counterfactual",
                statement=f"Removing '{node.label}' would affect {len(affected)} direct dependents",
                confidence=confidence,
                evidence=[Evidence(a, "would be affected") for a in set(affected)][:10],
                premises=["Removing a module breaks all its dependents"],
                affected_ids=list(set(affected)),
            ))

        elif action == "extract":
            conclusions.append(Conclusion(
                kind="counterfactual",
                statement=f"Extracting '{node.label}' into a separate module would reduce coupling",
                confidence=0.5,
                evidence=[Evidence(node.id, f"has {len(node.depends_on)} dependencies")],
                premises=["Extracting reduces coupling when a module has distinct concerns"],
                affected_ids=[node.id],
            ))

        return conclusions

    # — Internal reasoning methods —

    def _infer_role(self, node: TwinNode) -> str | None:
        if node.role:
            return node.role
        label = (node.label or "").lower()
        role_map = {
            "engine": "engine", "service": "service", "manager": "manager",
            "store": "persistence_store", "registry": "registry",
            "validator": "validator", "protocol": "protocol",
            "interface": "interface", "factory": "factory",
            "adapter": "adapter", "controller": "controller",
            "repository": "repository", "serializer": "serializer",
            "plugin": "plugin", "compiler": "compiler",
            "executor": "executor", "scheduler": "scheduler",
        }
        for kw, role in role_map.items():
            if kw in label:
                return role
        if node.protocols:
            return "protocol_implementer"
        if node.interfaces:
            return "interface_implementer"
        return None

    def _deduce_roles(self) -> list[Conclusion]:
        """Deduce architectural roles from naming + structure."""
        conclusions = []
        role_counts: Counter = Counter()
        for node in self.twin.find_nodes(kind="class"):
            role = self._infer_role(node)
            if role:
                role_counts[role] += 1

        for role, count in role_counts.most_common():
            conclusions.append(Conclusion(
                kind="deduction",
                statement=f"Detected {count} '{role}' components in the architecture",
                confidence=0.9,
                evidence=[Evidence(f"class::{role}", f"{count} instances")],
                premises=["Architectural components follow naming conventions that imply roles"],
            ))
        return conclusions

    def _deduce_layer_compliance(self) -> list[Conclusion]:
        """Deduce whether layer rules are followed."""
        violations = []
        compliant = 0
        total = 0
        for edge in self.twin.find_edges("imports"):
            s, t, _ = edge
            sn = self.twin.get_node(s)
            tn = self.twin.get_node(t)
            if sn and tn and sn.layer is not None and tn.layer is not None:
                total += 1
                if "/tests/" not in s and sn.layer < tn.layer:
                    violations.append((s, t, sn.layer, tn.layer))
                else:
                    compliant += 1

        if violations:
            conclusions = []
            for s, t, sl, tl in violations[:5]:
                conclusions.append(Conclusion(
                    kind="deduction",
                    statement=f"Layer violation: '{s}' (L{sl}) imports '{t}' (L{tl})",
                    confidence=0.95,
                    evidence=[
                        Evidence(s, f"assigned layer {sl}"),
                        Evidence(t, f"assigned layer {tl}"),
                    ],
                    premises=["A lower layer must not import from a higher layer"],
                    affected_ids=[s, t],
                ))
            pct = compliant / max(total, 1) * 100
            conclusions.append(Conclusion(
                kind="deduction",
                statement=f"Layer compliance: {pct:.0f}% ({compliant}/{total} edges)",
                confidence=0.95,
                evidence=[Evidence("layer_analysis", f"{compliant} compliant, {len(violations)} violations")],
                premises=["Layer compliance is calculated from import edges between layers"],
            ))
            return conclusions

        return [Conclusion(
            kind="deduction",
            statement="All import edges are layer-compliant",
            confidence=0.95,
            evidence=[Evidence("layer_analysis", "0 violations")],
            premises=["No lower-layer module imports from a higher layer"],
        )]

    def _deduce_spec_coverage(self) -> list[Conclusion]:
        """Deduce specification coverage and traceability gaps."""
        specs = self.twin.find_nodes(kind="normative")
        if not specs:
            return []

        linked = 0
        unlinked = []
        for s in specs:
            has_impl = False
            for edge in self.twin.find_edges("implements"):
                if edge[0] == s.id:
                    has_impl = True
                    break
            if has_impl:
                linked += 1
            else:
                unlinked.append(s)

        total = len(specs)
        pct = linked / total * 100

        conclusions = [Conclusion(
            kind="deduction",
            statement=f"Specification coverage: {pct:.0f}% ({linked}/{total} specs linked to implementation)",
            confidence=0.95,
            evidence=[
                Evidence(f"{linked} specs", "linked to implementation"),
                Evidence(f"{total - linked} specs", "unlinked"),
            ],
            premises=["Every specification should be traceable to its implementation"],
            affected_ids=[s.id for s in unlinked[:10]],
        )]

        if unlinked:
            conclusions.append(Conclusion(
                kind="deduction",
                statement=f"{len(unlinked)} specifications lack implementation links — traceability gap",
                confidence=0.9,
                evidence=[Evidence(s.id, s.label[:60]) for s in unlinked[:5]],
                premises=["Untraced specifications indicate incomplete implementation or missing links"],
                affected_ids=[s.id for s in unlinked[:10]],
            ))

        return conclusions

    def _deduce_event_consistency(self) -> list[Conclusion]:
        """Deduce whether event-driven services follow consistent patterns."""
        emitters = [n for n in self.twin.nodes if n.event_emissions]
        subscribers = [n for n in self.twin.nodes if n.event_subscriptions]

        conclusions = []
        if emitters:
            total_events = sum(len(e.event_emissions) for e in emitters)
            conclusions.append(Conclusion(
                kind="deduction",
                statement=f"{len(emitters)} components emit {total_events} event types",
                confidence=0.8,
                evidence=[Evidence(e.id, f"emits {len(e.event_emissions)} events") for e in emitters[:5]],
                premises=["Event-driven components should have observable emit patterns"],
                affected_ids=[e.id for e in emitters],
            ))

        if subscribers:
            total_subs = sum(len(s.event_subscriptions) for s in subscribers)
            conclusions.append(Conclusion(
                kind="deduction",
                statement=f"{len(subscribers)} components subscribe to {total_subs} event types",
                confidence=0.8,
                evidence=[Evidence(s.id, f"subscribes to {len(s.event_subscriptions)} events") for s in subscribers[:5]],
                premises=["Event-driven components should have observable subscribe patterns"],
                affected_ids=[s.id for s in subscribers],
            ))

        return conclusions

    def _induce_duplication_patterns(self) -> list[Conclusion]:
        """Induce patterns from duplicate class names."""
        name_counts: Counter = Counter()
        name_nodes: dict[str, list[TwinNode]] = defaultdict(list)
        for node in self.twin.find_nodes(kind="class"):
            name_counts[node.label] += 1
            name_nodes[node.label].append(node)

        conclusions = []
        for name, count in name_counts.items():
            if count > 2:
                nodes = name_nodes[name]
                conclusions.append(Conclusion(
                    kind="induction",
                    statement=f"Pattern detected: '{name}' appears in {count} modules — "
                             f"likely needs canonicalization",
                    confidence=0.7,
                    evidence=[Evidence(n.id, f"duplicate in {n.file_path}") for n in nodes[:5]],
                    premises=[
                        "Names appearing in 3+ modules indicate a shared concept",
                        "Shared concepts should be canonicalized into one definition",
                    ],
                    affected_ids=[n.id for n in nodes],
                ))

        return conclusions

    def _induce_missing_abstractions(self) -> list[Conclusion]:
        """Induce missing abstractions from repeated patterns."""
        tag_patterns: dict[str, list[str]] = defaultdict(list)
        for node in self.twin.find_nodes(kind="class"):
            for tag in node.tags:
                if tag and node.file_path:
                    tag_patterns[tag].append(node.file_path)

        conclusions = []
        for tag, paths in tag_patterns.items():
            path_counts = Counter(paths)
            for path, count in path_counts.items():
                if count >= 3:
                    conclusions.append(Conclusion(
                        kind="induction",
                        statement=f"Missing abstraction: {count} '{tag}' components in '{path}' "
                                 f"should be unified",
                        confidence=0.5,
                        evidence=[Evidence(path, f"{count} {tag} components")],
                        premises=[
                            f"Multiple {tag} components in one module suggest a missing abstraction",
                            "Canonical abstractions reduce duplication and improve cohesion",
                        ],
                        affected_ids=[path],
                    ))
        return conclusions

    def _abduce_best_explanations(self) -> list[Conclusion]:
        """Abduce best explanations for observed architectural properties."""
        conclusions = []

        # — Explain why hub modules exist —
        dep_counts: Counter = Counter()
        for edge in self.twin.find_edges("imports"):
            dep_counts[edge[1]] += 1

        for node_id, count in dep_counts.most_common(3):
            if count >= 5:
                node = self.twin.get_node(node_id)
                if node:
                    conclusions.append(Conclusion(
                        kind="abduction",
                        statement=f"Best explanation for '{node.label}' being a hub ({count} imports): "
                                 f"it provides foundational infrastructure used by many consumers",
                        confidence=0.6,
                        evidence=[
                            Evidence(node_id, f"imported by {count} modules"),
                        ],
                        premises=[
                            "Hub modules typically provide shared infrastructure",
                            "Alternative: poor decomposition forced consumers to couple directly",
                        ],
                        affected_ids=[node_id],
                    ))

        # — Explain spec coverage gaps —
        specs = self.twin.find_nodes(kind="normative")
        if specs:
            linked = 0
            for s in specs:
                for edge in self.twin.find_edges("implements"):
                    if edge[0] == s.id:
                        linked += 1
                        break
            if linked < len(specs) * 0.5:
                conclusions.append(Conclusion(
                    kind="abduction",
                    statement="Best explanation for low spec coverage: "
                             "specs are written at a higher abstraction level than implementation code, "
                             "making automated linking difficult",
                    confidence=0.5,
                    evidence=[
                        Evidence(f"{len(specs)} specs", f"{linked} linked ({linked/len(specs)*100:.0f}%)"),
                    ],
                    premises=[
                        "Spec-to-code linking is a hard NLP problem",
                        "Alternative: implementation doesn't fully satisfy specifications",
                        "Both cases indicate actionable gaps",
                    ],
                ))

        return conclusions

    def _explain_architectural_intent(self) -> list[Conclusion]:
        """Explain the architectural intent behind design decisions."""
        conclusions = []

        # — Explain layering structure —
        layers: set[int] = set()
        for n in self.twin.nodes:
            if n.layer is not None:
                layers.add(n.layer)
        if layers:
            layer_names = [f"L{l}" for l in sorted(layers)]
            conclusions.append(Conclusion(
                kind="explanatory",
                statement=f"Architecture uses {len(layers)} layers ({', '.join(layer_names)}): "
                         f"L0 (persistence) → L1 (infrastructure) → "
                         f"L2 (services) → L3 (intelligence) → L4 (platform)",
                confidence=0.9,
                evidence=[Evidence(f"L{l}", f"{len([n for n in self.twin.nodes if n.layer == l])} nodes")
                         for l in sorted(layers)],
                premises=[
                    "Layered architecture isolates concerns and controls dependency direction",
                    "Inner layers provide foundational services to outer layers",
                ],
            ))

        # — Explain role distribution —
        role_counts: Counter = Counter()
        for n in self.twin.nodes:
            if n.role:
                role_counts[n.role] += 1
        if role_counts:
            primary_role = role_counts.most_common(1)[0]
            conclusions.append(Conclusion(
                kind="explanatory",
                statement=f"Architecture is dominated by '{primary_role[0]}' components "
                         f"({primary_role[1]} instances) — consistent with "
                         f"{'a service-oriented' if primary_role[0] == 'service' else 'an engine-driven'} design",
                confidence=0.7,
                evidence=[Evidence(role, f"{count} instances") for role, count in role_counts.most_common(3)],
                premises=[
                    "Component role distribution reveals architectural style",
                    "Dominant roles indicate primary design paradigm",
                ],
            ))

        return conclusions
