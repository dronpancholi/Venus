from __future__ import annotations

import threading
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable

from genesis.utils.identity import generate_id


class PolicyEffect(Enum):
    ALLOW = "allow"
    DENY = "deny"
    AUDIT = "audit"
    WARN = "warn"


@dataclass
class Policy:
    id: str = ""
    name: str = ""
    description: str = ""
    effect: PolicyEffect = PolicyEffect.DENY
    service: str = ""
    action: str = ""
    conditions: dict[str, Any] = field(default_factory=dict)
    priority: int = 0
    enabled: bool = True

    def __post_init__(self):
        if not self.id:
            self.id = generate_id("pol", 12)

    def applies_to(self, service: str, action: str) -> bool:
        if not self.enabled:
            return False
        if self.service and self.service != service:
            return False
        if self.action and self.action != action:
            return False
        return True


@dataclass
class PolicyResult:
    allowed: bool = True
    policy: Policy | None = None
    reason: str = ""
    warnings: list[str] = field(default_factory=list)


class PolicyEngine:
    """Policy enforcement engine for the fabric."""

    def __init__(self):
        self._policies: dict[str, Policy] = {}
        self._lock = threading.RLock()

    def add(self, policy: Policy):
        with self._lock:
            self._policies[policy.id] = policy

    def remove(self, policy_id: str) -> bool:
        with self._lock:
            return self._policies.pop(policy_id, None) is not None

    def evaluate(self, service: str, action: str,
                 context: dict[str, Any] | None = None) -> PolicyResult:
        with self._lock:
            applicable = sorted(
                [p for p in self._policies.values() if p.applies_to(service, action)],
                key=lambda p: -p.priority,
            )
            warnings: list[str] = []
            for policy in applicable:
                if policy.effect == PolicyEffect.DENY:
                    return PolicyResult(
                        allowed=False,
                        policy=policy,
                        reason=f"Policy '{policy.name}' denied {service}.{action}",
                    )
                elif policy.effect == PolicyEffect.WARN:
                    warnings.append(policy.name)
                elif policy.effect == PolicyEffect.AUDIT:
                    pass
            return PolicyResult(allowed=True, warnings=warnings)

    def list_policies(self) -> list[Policy]:
        return list(self._policies.values())

    def clear(self):
        with self._lock:
            self._policies.clear()

    def count(self) -> int:
        return len(self._policies)

    def summary(self) -> dict[str, Any]:
        effects: dict[str, int] = {}
        for p in self._policies.values():
            effects[p.effect.value] = effects.get(p.effect.value, 0) + 1
        return {
            "policies": len(self._policies),
            "by_effect": effects,
        }
