"""
Belief System — probabilistic belief representation with confidence propagation.

Beliefs are statements with associated confidence probabilities. Evidence
supports or contradicts beliefs. Confidence propagates through belief networks.
Contradiction detection flags inconsistent beliefs for resolution.

Integrates with: EngineeringBrain (entities become beliefs), Memory (belief history),
DigitalTwin (evidence from codebase analysis), WorldModel (ecosystem beliefs).
"""

from __future__ import annotations

import math
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable

from genesis.utils.identity import generate_id


class BeliefStatus(Enum):
    HYPOTHESIS = "hypothesis"       # Proposed, not yet evaluated
    PLAUSIBLE = "plausible"         # Some evidence supports
    LIKELY = "likely"               # Strong evidence supports
    CONFIRMED = "confirmed"         # Overwhelming evidence
    CONTRADICTED = "contradicted"   # Conflicting evidence
    REFUTED = "refuted"            # Evidence disproves
    UNKNOWN = "unknown"             # No evidence either way


class EvidenceKind(Enum):
    EMPIRICAL = "empirical"         # Observed data
    ANALYTICAL = "analytical"       # Derived from reasoning
    TESTIMONIAL = "testimonial"     # From trusted source
    STATISTICAL = "statistical"     # Statistical analysis
    FORMAL = "formal"              # Formal proof
    SIMULATION = "simulation"       # From simulation
    EXPERIMENT = "experiment"       # From controlled experiment
    REVIEW = "review"              # Peer review


@dataclass
class BeliefEvidence:
    id: str = ""
    kind: EvidenceKind = EvidenceKind.EMPIRICAL
    statement: str = ""
    supports: bool = True           # True = supports, False = contradicts
    weight: float = 1.0            # Strength of evidence (0-1)
    source: str = ""                # Which subsystem produced it
    confidence: float = 1.0        # Confidence in the evidence itself
    timestamp: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.id:
            self.id = generate_id("evidence", 12)
        if not self.timestamp:
            self.timestamp = time.time()

    def impact(self) -> float:
        """Compute the belief impact of this evidence (negative if contradicts)."""
        base = self.weight * self.confidence
        return base if self.supports else -base


@dataclass
class Belief:
    """A belief is a proposition with associated confidence and evidence."""
    id: str = ""
    statement: str = ""
    confidence: float = 0.0         # 0.0 (no confidence) to 1.0 (certain)
    status: BeliefStatus = BeliefStatus.UNKNOWN
    evidence: list[BeliefEvidence] = field(default_factory=list)
    parent_id: str = ""             # Belief this derives from
    child_ids: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    source_system: str = ""
    source_id: str = ""
    created_at: float = 0.0
    updated_at: float = 0.0
    decay_rate: float = 0.0         # Confidence decay per day (0 = no decay)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.id:
            self.id = generate_id("belief", 12)
        if not self.created_at:
            self.created_at = time.time()
        if not self.updated_at:
            self.updated_at = self.created_at

    def add_evidence(self, evidence: BeliefEvidence):
        self.evidence.append(evidence)
        self._recompute_confidence()
        self.updated_at = time.time()

    def _recompute_confidence(self):
        if not self.evidence:
            self.confidence = 0.0
            self.status = BeliefStatus.UNKNOWN
            return

        total_impact = 0.0
        total_weight = 0.0
        supports_count = 0
        contradicts_count = 0

        for ev in self.evidence:
            imp = ev.impact()
            total_impact += imp
            total_weight += ev.weight * ev.confidence
            if ev.supports:
                supports_count += 1
            else:
                contradicts_count += 1

        # Normalize confidence to [0, 1] using sigmoid of net impact
        self.confidence = 1.0 / (1.0 + math.exp(-total_impact))

        # Determine status
        if contradicts_count > supports_count * 2:
            self.status = BeliefStatus.REFUTED
        elif contradicts_count > 0 and supports_count > 0:
            self.status = BeliefStatus.CONTRADICTED
        elif self.confidence >= 0.95:
            self.status = BeliefStatus.CONFIRMED
        elif self.confidence >= 0.75:
            self.status = BeliefStatus.LIKELY
        elif self.confidence >= 0.4:
            self.status = BeliefStatus.PLAUSIBLE
        elif supports_count > 0:
            self.status = BeliefStatus.HYPOTHESIS
        else:
            self.status = BeliefStatus.UNKNOWN

    def decay(self, days_passed: float = 1.0):
        """Apply confidence decay over time."""
        if self.decay_rate <= 0:
            return
        decay_factor = math.exp(-self.decay_rate * days_passed)
        self.confidence *= decay_factor
        if self.confidence < 0.01:
            self.status = BeliefStatus.UNKNOWN

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "statement": self.statement,
            "confidence": self.confidence,
            "status": self.status.value,
            "evidence": [e.__dict__ for e in self.evidence],
            "parent_id": self.parent_id,
            "child_ids": self.child_ids,
            "tags": self.tags,
            "source_system": self.source_system,
            "source_id": self.source_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "decay_rate": self.decay_rate,
        }


class BeliefSystem:
    """Manages a network of beliefs with confidence propagation.

    Supports:
    - Belief creation with evidence tracking
    - Confidence propagation through belief networks
    - Contradiction detection and resolution
    - Evidence-weighted belief updates
    - Temporal decay of old beliefs
    """

    def __init__(self):
        self._beliefs: dict[str, Belief] = {}
        self._index_by_source: dict[str, dict[str, str]] = {}
        self._contradictions: list[tuple[str, str]] = []  # (belief_id_1, belief_id_2)

    @property
    def belief_count(self) -> int:
        return len(self._beliefs)

    def believe(self, statement: str, confidence: float = 0.5,
                source_system: str = "", source_id: str = "",
                tags: list[str] | None = None,
                evidence: BeliefEvidence | None = None) -> Belief:
        """Create or update a belief."""
        existing = None
        if source_system and source_id:
            mapping = self._index_by_source.get(source_system, {})
            existing_id = mapping.get(source_id)
            if existing_id:
                existing = self._beliefs.get(existing_id)

        if existing:
            if evidence:
                existing.add_evidence(evidence)
            if confidence != 0.5:
                existing.confidence = confidence
            existing.updated_at = time.time()
            return existing

        belief = Belief(
            statement=statement,
            confidence=confidence,
            source_system=source_system,
            source_id=source_id,
            tags=tags or [],
        )
        if evidence:
            belief.add_evidence(evidence)
        else:
            belief.status = self._status_from_confidence(confidence)
        self._beliefs[belief.id] = belief
        if source_system and source_id:
            self._index_by_source.setdefault(source_system, {})[source_id] = belief.id
        return belief

    def get(self, belief_id: str) -> Belief | None:
        return self._beliefs.get(belief_id)

    def find(self, statement_contains: str = "", status: BeliefStatus | None = None,
             tag: str = "", source_system: str = "") -> list[Belief]:
        results = list(self._beliefs.values())
        if statement_contains:
            results = [b for b in results if statement_contains.lower() in b.statement.lower()]
        if status:
            results = [b for b in results if b.status == status]
        if tag:
            results = [b for b in results if tag in b.tags]
        if source_system:
            mapping = self._index_by_source.get(source_system, {})
            ids = set(mapping.values())
            results = [b for b in results if b.id in ids]
        return results

    def relate(self, parent_id: str, child_id: str):
        """Create a parent-child relationship between beliefs."""
        parent = self._beliefs.get(parent_id)
        child = self._beliefs.get(child_id)
        if parent and child:
            if child_id not in parent.child_ids:
                parent.child_ids.append(child_id)
            child.parent_id = parent_id
            self._propagate_confidence(child)

    @staticmethod
    def _status_from_confidence(confidence: float) -> BeliefStatus:
        if confidence >= 0.95:
            return BeliefStatus.CONFIRMED
        elif confidence >= 0.75:
            return BeliefStatus.LIKELY
        elif confidence >= 0.4:
            return BeliefStatus.PLAUSIBLE
        elif confidence > 0:
            return BeliefStatus.HYPOTHESIS
        return BeliefStatus.UNKNOWN

    def _propagate_confidence(self, belief: Belief):
        """Propagate confidence from a belief to its children."""
        if belief.parent_id:
            parent = self._beliefs.get(belief.parent_id)
            if parent:
                parent.confidence = max(parent.confidence, belief.confidence * 0.8)
                parent.updated_at = time.time()

    def detect_contradictions(self) -> list[tuple[str, str, float]]:
        """Find beliefs that contradict each other (same statement, different conclusions)."""
        contradictions: list[tuple[str, str, float]] = []
        beliefs = list(self._beliefs.values())
        for i in range(len(beliefs)):
            for j in range(i + 1, len(beliefs)):
                b1, b2 = beliefs[i], beliefs[j]
                if b1.statement.lower() == b2.statement.lower():
                    if (b1.confidence >= 0.7 and b2.confidence >= 0.7 and
                            abs(b1.confidence - b2.confidence) >= 0.3):
                        contradictions.append((b1.id, b2.id, abs(b1.confidence - b2.confidence)))
                        if (b1.id, b2.id) not in self._contradictions:
                            self._contradictions.append((b1.id, b2.id))
        return contradictions

    def resolve_contradiction(self, belief_id_1: str, belief_id_2: str,
                              resolver: Callable[[Belief, Belief], Belief]):
        """Resolve a contradiction using a custom resolver function."""
        b1 = self._beliefs.get(belief_id_1)
        b2 = self._beliefs.get(belief_id_2)
        if b1 and b2:
            resolved = resolver(b1, b2)
            self._beliefs[resolved.id] = resolved
            # Mark originals as resolved (remove from contradictions)
            self._contradictions = [(a, b) for a, b in self._contradictions
                                    if not ({a, b} == {belief_id_1, belief_id_2})]
            return resolved
        return None

    def decay_all(self, days_passed: float = 1.0):
        """Apply decay to all beliefs."""
        for belief in self._beliefs.values():
            belief.decay(days_passed)

    def prune(self, min_confidence: float = 0.01, max_age_days: float = 365.0):
        """Remove beliefs below confidence threshold or older than max_age."""
        now = time.time()
        max_age_seconds = max_age_days * 86400
        to_remove = [
            bid for bid, b in self._beliefs.items()
            if b.confidence < min_confidence or (now - b.created_at) > max_age_seconds
        ]
        for bid in to_remove:
            del self._beliefs[bid]
            for system, mapping in self._index_by_source.items():
                to_del = [sid for sid, bid2 in mapping.items() if bid2 == bid]
                for sid in to_del:
                    del mapping[sid]
        return len(to_remove)

    def summary(self) -> dict[str, Any]:
        status_counts: dict[str, int] = {}
        for b in self._beliefs.values():
            status_counts[b.status.value] = status_counts.get(b.status.value, 0) + 1
        return {
            "total_beliefs": len(self._beliefs),
            "by_status": status_counts,
            "contradictions": len(self._contradictions),
            "average_confidence": sum(b.confidence for b in self._beliefs.values()) / max(len(self._beliefs), 1),
        }
