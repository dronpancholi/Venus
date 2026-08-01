"""
UCOS: CapabilityNegotiator — Negotiates capability provisioning between consumers and providers.
"""

from __future__ import annotations

import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any

from genesis.ucos.capability import Capability, CapabilityState
from genesis.utils.identity import generate_id


@dataclass
class ProvisioningAgreement:
    id: str = ""
    consumer_id: str = ""
    provider_id: str = ""
    capability_id: str = ""
    terms: dict[str, Any] = field(default_factory=dict)
    constraints: list[str] = field(default_factory=list)
    status: str = "proposed"
    created_at: float = 0.0
    accepted_at: float = 0.0
    expires_at: float = 0.0

    def __post_init__(self):
        now = time.time()
        if not self.id:
            self.id = generate_id("agree", 10)
        if not self.created_at:
            self.created_at = now


class CapabilityNegotiator:
    """Negotiates capability provisioning between consumers and providers."""

    def __init__(self, registry):
        self._registry = registry
        self._agreements: dict[str, ProvisioningAgreement] = {}
        self._negotiation_log: list[dict[str, Any]] = []

    def propose(self, consumer_id: str, capability_id: str,
                requirements: dict[str, Any] | None = None) -> ProvisioningAgreement | None:
        cap = self._registry.get(capability_id)
        consumer = self._registry.get(consumer_id)
        if not cap or not consumer:
            return None
        if cap.state != CapabilityState.READY and cap.state != CapabilityState.RUNNING:
            return None
        providers = cap.definition.providers if cap.definition.providers else [cap.id]
        if not providers:
            return None
        agreement = ProvisioningAgreement(
            consumer_id=consumer_id,
            provider_id=providers[0],
            capability_id=capability_id,
            terms={
                "requirements": requirements or {},
                "guarantees": cap.definition.execution_policy.get("guarantees", {}),
            },
            status="proposed",
        )
        self._agreements[agreement.id] = agreement
        self._negotiation_log.append({
            "action": "propose",
            "agreement_id": agreement.id,
            "consumer": consumer_id,
            "capability": capability_id,
            "timestamp": time.time(),
        })
        return agreement

    def accept(self, agreement_id: str) -> bool:
        agreement = self._agreements.get(agreement_id)
        if not agreement or agreement.status != "proposed":
            return False
        agreement.status = "accepted"
        agreement.accepted_at = time.time()
        self._registry.register_consumer(agreement.capability_id, agreement.consumer_id)
        self._negotiation_log.append({
            "action": "accept",
            "agreement_id": agreement_id,
            "timestamp": time.time(),
        })
        return True

    def reject(self, agreement_id: str, reason: str = "") -> bool:
        agreement = self._agreements.get(agreement_id)
        if not agreement:
            return False
        agreement.status = f"rejected: {reason}" if reason else "rejected"
        self._negotiation_log.append({
            "action": "reject",
            "agreement_id": agreement_id,
            "reason": reason,
            "timestamp": time.time(),
        })
        return True

    def revoke(self, agreement_id: str) -> bool:
        agreement = self._agreements.get(agreement_id)
        if not agreement:
            return False
        agreement.status = "revoked"
        self._negotiation_log.append({
            "action": "revoke",
            "agreement_id": agreement_id,
            "timestamp": time.time(),
        })
        return True

    def find_providers(self, capability_id: str) -> list[Capability]:
        cap = self._registry.get(capability_id)
        if not cap:
            return []
        candidate_ids = cap.definition.providers if cap.definition.providers else [cap.id]
        providers = []
        for pid in candidate_ids:
            p = self._registry.get(pid)
            if p and p.state in (CapabilityState.READY, CapabilityState.RUNNING):
                providers.append(p)
        return providers

    def active_agreements(self) -> list[ProvisioningAgreement]:
        return [a for a in self._agreements.values() if a.status == "accepted"]

    def agreements_for_consumer(self, consumer_id: str) -> list[ProvisioningAgreement]:
        return [a for a in self._agreements.values() if a.consumer_id == consumer_id]
