"""
Engineering Proof Engine (Mission 25) — Formally justify every decision.

Every proof contains:
- Premises: axioms or established facts
- Evidence: measurements, references, citations
- Logical derivation: step-by-step reasoning
- Counterexamples: cases where the proof fails
- Rejected alternatives: options considered but dismissed
- Confidence: 0.0–1.0
- Validity range: scope where the proof holds
- Proof status: proven, plausible, rejected, unproven
"""

from __future__ import annotations

import time
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from threading import RLock
from typing import Any

from genesis.utils.identity import generate_id


class ProofStatus(Enum):
    UNPROVEN = "unproven"
    PROVEN = "proven"
    PLAUSIBLE = "plausible"
    REJECTED = "rejected"
    SUPERSEDED = "superseded"


class ProofDomain(Enum):
    DUPLICATE_ELIMINATION = "duplicate_elimination"
    DEPENDENCY_REDUCTION = "dependency_reduction"
    OWNERSHIP_TRANSFER = "ownership_transfer"
    MIGRATION_SAFETY = "migration_safety"
    API_COMPATIBILITY = "api_compatibility"
    SERVICE_COMPATIBILITY = "service_compatibility"
    GRAPH_COMPATIBILITY = "graph_compatibility"
    RUNTIME_CORRECTNESS = "runtime_correctness"
    KNOWLEDGE_CONSISTENCY = "knowledge_consistency"
    GOVERNANCE_CONSISTENCY = "governance_consistency"
    ARCHITECTURAL_INTEGRITY = "architectural_integrity"


@dataclass
class Premise:
    statement: str = ""
    evidence: str = ""
    accepted: bool = True


@dataclass
class ProofStep:
    step: int = 0
    statement: str = ""
    reasoning: str = ""
    derived_from: list[int] = field(default_factory=list)


@dataclass
class RejectedAlternative:
    name: str = ""
    reason: str = ""
    evaluated_at: float = 0.0

    def __post_init__(self):
        if not self.evaluated_at:
            self.evaluated_at = time.time()


@dataclass
class Proof:
    id: str = ""
    domain: ProofDomain = ProofDomain.ARCHITECTURAL_INTEGRITY
    title: str = ""
    status: ProofStatus = ProofStatus.UNPROVEN
    premises: list[Premise] = field(default_factory=list)
    derivation: list[ProofStep] = field(default_factory=list)
    conclusion: str = ""
    counterexamples: list[str] = field(default_factory=list)
    rejected_alternatives: list[RejectedAlternative] = field(default_factory=list)
    confidence: float = 0.0
    validity_range: str = ""
    created_at: float = 0.0
    updated_at: float = 0.0
    superseded_by: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.id:
            self.id = generate_id("proof", 14)
        now = time.time()
        if not self.created_at:
            self.created_at = now
        if not self.updated_at:
            self.updated_at = now


class ProofEngine:
    """Formal proof engine for engineering decisions."""

    def __init__(self):
        self._proofs: dict[str, Proof] = {}
        self._lock = RLock()

    def create_proof(self, domain: ProofDomain, title: str) -> Proof:
        proof = Proof(domain=domain, title=title)
        with self._lock:
            self._proofs[proof.id] = proof
        return proof

    def add_premise(self, proof_id: str, statement: str, evidence: str = "") -> bool:
        with self._lock:
            proof = self._proofs.get(proof_id)
            if not proof:
                return False
            proof.premises.append(Premise(statement=statement, evidence=evidence))
            proof.updated_at = time.time()
            return True

    def add_derivation_step(self, proof_id: str, statement: str,
                            reasoning: str, derived_from: list[int] | None = None) -> bool:
        with self._lock:
            proof = self._proofs.get(proof_id)
            if not proof:
                return False
            step = ProofStep(
                step=len(proof.derivation) + 1,
                statement=statement,
                reasoning=reasoning,
                derived_from=derived_from or [],
            )
            proof.derivation.append(step)
            proof.updated_at = time.time()
            return True

    def set_conclusion(self, proof_id: str, conclusion: str,
                       status: ProofStatus = ProofStatus.PROVEN,
                       confidence: float = 0.9, validity_range: str = "") -> bool:
        with self._lock:
            proof = self._proofs.get(proof_id)
            if not proof:
                return False
            proof.conclusion = conclusion
            proof.status = status
            proof.confidence = confidence
            proof.validity_range = validity_range or proof.validity_range
            proof.updated_at = time.time()
            return True

    def add_counterexample(self, proof_id: str, example: str) -> bool:
        with self._lock:
            proof = self._proofs.get(proof_id)
            if not proof:
                return False
            proof.counterexamples.append(example)
            proof.updated_at = time.time()
            return True

    def add_rejected_alternative(self, proof_id: str, name: str, reason: str) -> bool:
        with self._lock:
            proof = self._proofs.get(proof_id)
            if not proof:
                return False
            proof.rejected_alternatives.append(RejectedAlternative(name=name, reason=reason))
            proof.updated_at = time.time()
            return True

    def get_proof(self, proof_id: str) -> Proof | None:
        return self._proofs.get(proof_id)

    def get_by_domain(self, domain: ProofDomain) -> list[Proof]:
        return [p for p in self._proofs.values() if p.domain == domain]

    def get_by_status(self, status: ProofStatus) -> list[Proof]:
        return [p for p in self._proofs.values() if p.status == status]

    def supersede(self, old_id: str, new_id: str) -> bool:
        with self._lock:
            old = self._proofs.get(old_id)
            new_p = self._proofs.get(new_id)
            if not old or not new_p:
                return False
            old.status = ProofStatus.SUPERSEDED
            old.superseded_by = new_id
            old.updated_at = time.time()
            return True

    def verify(self, proof_id: str) -> dict[str, Any]:
        proof = self._proofs.get(proof_id)
        if not proof:
            return {"exists": False}
        all_premises_accepted = all(p.accepted for p in proof.premises)
        has_derivation = len(proof.derivation) > 0
        has_conclusion = bool(proof.conclusion)
        return {
            "exists": True,
            "status": proof.status.value,
            "all_premises_accepted": all_premises_accepted,
            "has_derivation": has_derivation,
            "has_conclusion": has_conclusion,
            "premises_count": len(proof.premises),
            "derivation_steps": len(proof.derivation),
            "counterexamples": len(proof.counterexamples),
            "rejected_alternatives": len(proof.rejected_alternatives),
            "confidence": proof.confidence,
        }

    def summary(self) -> dict[str, Any]:
        with self._lock:
            by_status: dict[str, int] = defaultdict(int)
            by_domain: dict[str, int] = defaultdict(int)
            for p in self._proofs.values():
                by_status[p.status.value] += 1
                by_domain[p.domain.value] += 1
            return {
                "total_proofs": len(self._proofs),
                "by_status": dict(by_status),
                "by_domain": dict(by_domain),
                "avg_confidence": sum(p.confidence for p in self._proofs.values()) / max(1, len(self._proofs)),
            }
