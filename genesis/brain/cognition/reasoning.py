"""
Reasoning Engine — causal, counterfactual, and Bayesian reasoning over the Brain.

Enables:
- Causal inference over entity relationships (X causes Y)
- Counterfactual reasoning (what if X were different?)
- Bayesian belief updates (P(H|E) from evidence)
- Probabilistic inference over belief networks

Integrates with: BeliefSystem (updates beliefs from reasoning),
GoalHierarchy (justifies goal priority), DigitalTwin (codebase causality),
WorldModel (ecosystem causal chains).
"""

from __future__ import annotations

import math
import random
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable

from genesis.utils.identity import generate_id


class ReasoningMode(Enum):
    DEDUCTIVE = "deductive"       # Rule-based: A→B, A ∴ B
    INDUCTIVE = "inductive"       # Pattern-based: A₁..Aₙ→B
    ABDUCTIVE = "abductive"       # Inference to best explanation: B, A→B ∴ A
    ANALOGICAL = "analogical"     # Similarity-based transfer


@dataclass
class CausalLink:
    source_id: str
    target_id: str
    strength: float = 0.5         # How likely cause produces effect (0-1)
    direction: str = "forward"     # forward (A→B) or inverse (B→A)
    evidence_count: int = 1
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Inference:
    id: str = ""
    premise: str = ""
    conclusion: str = ""
    confidence: float = 0.0
    mode: ReasoningMode = ReasoningMode.DEDUCTIVE
    source_ids: list[str] = field(default_factory=list)
    created_at: float = 0.0

    def __post_init__(self):
        if not self.id:
            self.id = generate_id("inference", 12)
        if not self.created_at:
            self.created_at = time.time()

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "premise": self.premise,
            "conclusion": self.conclusion,
            "confidence": self.confidence,
            "mode": self.mode.value,
            "source_ids": self.source_ids,
        }


class ReasoningEngine:
    """Multi-modal reasoning over beliefs, entities, and causal graphs.

    Supports causal inference, counterfactual reasoning, Bayesian updates,
    and deductive/inductive/abductive/analogical inference.
    """

    def __init__(self):
        self._causal_links: dict[str, CausalLink] = {}
        self._inferences: list[Inference] = []
        self._rules: list[tuple[str, str, float]] = []  # (antecedent, consequent, confidence)

    @property
    def inference_count(self) -> int:
        return len(self._inferences)

    @property
    def causal_link_count(self) -> int:
        return len(self._causal_links)

    # ——— Causal Reasoning ———

    def add_causal_link(self, source_id: str, target_id: str,
                         strength: float = 0.5, direction: str = "forward",
                         **metadata) -> CausalLink:
        key = f"{source_id}→{target_id}"
        existing = self._causal_links.get(key)
        if existing:
            existing.evidence_count += 1
            existing.strength = (existing.strength + strength) / 2
            existing.metadata.update(metadata)
            return existing
        link = CausalLink(
            source_id=source_id, target_id=target_id,
            strength=strength, direction=direction,
            metadata=metadata,
        )
        self._causal_links[key] = link
        return link

    def infer_causes(self, target_id: str, min_strength: float = 0.1) -> list[CausalLink]:
        """Find all causal links pointing to a target."""
        return [l for l in self._causal_links.values()
                if l.target_id == target_id and l.strength >= min_strength]

    def infer_effects(self, source_id: str, min_strength: float = 0.1) -> list[CausalLink]:
        """Find all causal links originating from a source."""
        return [l for l in self._causal_links.values()
                if l.source_id == source_id and l.strength >= min_strength]

    def causal_chain(self, start_id: str, max_depth: int = 5) -> list[list[CausalLink]]:
        """Trace causal chains forward from a starting entity."""
        chains: list[list[CausalLink]] = []

        def _trace(current_id: str, path: list[CausalLink], depth: int):
            if depth > max_depth:
                return
            effects = self.infer_effects(current_id)
            if not effects:
                if path:
                    chains.append(list(path))
                return
            for effect in effects:
                path.append(effect)
                _trace(effect.target_id, path, depth + 1)
                path.pop()

        _trace(start_id, [], 0)
        return chains

    # ——— Counterfactual Reasoning ———

    def counterfactual(self, belief_fn: Callable[[str], float],
                       what_if: str, new_value: float) -> dict[str, float]:
        """What-if analysis: change a variable and observe effects.

        Args:
            belief_fn: Function that returns confidence for a given entity ID
            what_if: Entity ID to change
            new_value: New confidence/value for the entity

        Returns:
            Dict mapping affected entity IDs → their new inferred confidence
        """
        effects: dict[str, float] = {}
        effects[what_if] = new_value

        # Propagate through causal links
        queue = [(what_if, 1.0)]
        visited = {what_if}
        while queue:
            current, decay = queue.pop(0)
            links = self.infer_effects(current)
            for link in links:
                if link.target_id not in visited:
                    visited.add(link.target_id)
                    propagated = new_value * link.strength * decay
                    effects[link.target_id] = propagated
                    queue.append((link.target_id, decay * 0.5))

        return effects

    # ——— Bayesian Reasoning ———

    def bayesian_update(self, prior: float, likelihood: float,
                        evidence_prob: float) -> float:
        """P(H|E) = P(E|H) * P(H) / P(E)

        Args:
            prior: P(H) — prior probability of hypothesis
            likelihood: P(E|H) — probability of evidence given hypothesis
            evidence_prob: P(E) — probability of evidence

        Returns:
            P(H|E) — posterior probability
        """
        if evidence_prob == 0:
            return prior
        return (likelihood * prior) / evidence_prob

    def bayesian_network(self, priors: dict[str, float],
                          conditional: dict[str, dict[str, float]]) -> dict[str, float]:
        """Simple Bayesian network inference.

        Args:
            priors: Dict mapping node_id → prior probability
            conditional: Dict mapping node_id → {parent_value: conditional_prob}

        Returns:
            Dict mapping node_id → posterior probability
        """
        posteriors = dict(priors)
        for node_id, conds in conditional.items():
            if node_id in priors:
                continue  # Root node, keep prior
            # Compute posterior from parents
            posterior = 0.0
            for parent_val, cond_prob in conds.items():
                parent_prob = posteriors.get(parent_val, 0.5)
                posterior += parent_prob * cond_prob
            posteriors[node_id] = min(1.0, posterior)
        return posteriors

    # ——— Rule-Based Reasoning ———

    def add_rule(self, antecedent: str, consequent: str, confidence: float = 1.0):
        """Add a deductive rule: if antecedent then consequent."""
        self._rules.append((antecedent, consequent, confidence))

    def deduce(self, facts: dict[str, float],
               min_confidence: float = 0.1) -> list[Inference]:
        """Apply rules to facts to derive new conclusions."""
        inferences: list[Inference] = []
        for antecedent, consequent, rule_conf in self._rules:
            # Check if antecedent matches any fact
            for fact_name, fact_conf in facts.items():
                if antecedent.lower() in fact_name.lower() or fact_name.lower() in antecedent.lower():
                    confidence = fact_conf * rule_conf
                    if confidence >= min_confidence:
                        inference = Inference(
                            premise=f"{antecedent} (confidence: {fact_conf})",
                            conclusion=consequent,
                            confidence=confidence,
                            mode=ReasoningMode.DEDUCTIVE,
                            source_ids=[fact_name],
                        )
                        inferences.append(inference)
                        self._inferences.append(inference)
        return inferences

    def analogical_transfer(self, source_entity: dict[str, Any],
                             target_entity: dict[str, Any],
                             similarity_fn: Callable[[dict, dict], float]) -> list[str]:
        """Transfer attributes from source to target based on similarity."""
        similarity = similarity_fn(source_entity, target_entity)
        if similarity < 0.3:
            return []
        transferred: list[str] = []
        for key, value in source_entity.items():
            if key not in target_entity or target_entity[key] is None:
                transferred.append(key)
        return transferred

    def summary(self) -> dict[str, Any]:
        return {
            "total_inferences": len(self._inferences),
            "causal_links": len(self._causal_links),
            "rules": len(self._rules),
            "by_mode": {mode.value: len([i for i in self._inferences if i.mode == mode])
                        for mode in ReasoningMode},
        }
