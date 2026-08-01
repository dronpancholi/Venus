"""
Universal Kernel: SecurityManager — Authentication, authorization, audit, encryption.
"""

from __future__ import annotations

import hashlib
import time
from collections import defaultdict
from typing import Any

from genesis.utils.identity import generate_id


class SecurityManager:
    """Manages security policies, access control, and audit logging."""

    def __init__(self):
        self._roles: dict[str, set[str]] = defaultdict(set)
        self._policies: dict[str, list[dict[str, Any]]] = defaultdict(list)
        self._tokens: dict[str, dict[str, Any]] = {}
        self._audit_log: list[dict[str, Any]] = []

    def create_role(self, role: str, permissions: list[str] | None = None):
        self._roles[role] = set(permissions or [])

    def assign_role(self, identity: str, role: str):
        self._roles[identity].add(role)

    def remove_role(self, identity: str, role: str):
        self._roles[identity].discard(role)

    def add_permission(self, role: str, permission: str):
        self._roles[role].add(permission)

    def has_permission(self, identity: str, permission: str) -> bool:
        if identity in self._roles and permission in self._roles[identity]:
            return True
        for role in self._roles.get(identity, set()):
            if role in self._roles and permission in self._roles[role]:
                return True
        return False

    def roles_of(self, identity: str) -> list[str]:
        return list(self._roles.get(identity, set()))

    def add_policy(self, resource: str, action: str, effect: str = "allow",
                    conditions: dict[str, Any] | None = None):
        self._policies[resource].append({
            "action": action,
            "effect": effect,
            "conditions": conditions or {},
            "created_at": time.time(),
        })

    def check_policy(self, identity: str, resource: str, action: str,
                     context: dict[str, Any] | None = None) -> bool:
        for policy in self._policies.get(resource, []):
            if policy["action"] != action and policy["action"] != "*":
                continue
            if policy["effect"] == "allow":
                ctx = context or {}
                conditions_met = all(
                    ctx.get(k) == v for k, v in policy["conditions"].items()
                ) if policy["conditions"] else True
                if conditions_met:
                    self._audit_log.append({
                        "identity": identity,
                        "resource": resource,
                        "action": action,
                        "effect": "allow",
                        "timestamp": time.time(),
                    })
                    return True
        self._audit_log.append({
            "identity": identity,
            "resource": resource,
            "action": action,
            "effect": "deny",
            "timestamp": time.time(),
        })
        return False

    def issue_token(self, identity: str, ttl_seconds: float = 3600.0) -> str:
        token = hashlib.sha256(f"{identity}:{time.time()}:{generate_id('tok', 8)}".encode()).hexdigest()
        self._tokens[token] = {
            "identity": identity,
            "issued_at": time.time(),
            "expires_at": time.time() + ttl_seconds,
        }
        return token

    def validate_token(self, token: str) -> str | None:
        info = self._tokens.get(token)
        if not info:
            return None
        if time.time() > info["expires_at"]:
            self._tokens.pop(token, None)
            return None
        return info["identity"]

    def revoke_token(self, token: str) -> bool:
        return self._tokens.pop(token, None) is not None

    def revoke_all_for(self, identity: str) -> int:
        count = 0
        for token, info in list(self._tokens.items()):
            if info["identity"] == identity:
                self._tokens.pop(token, None)
                count += 1
        return count

    def audit_log(self, since: float = 0.0, limit: int = 100) -> list[dict[str, Any]]:
        return [e for e in self._audit_log if e["timestamp"] >= since][-limit:]

    def summary(self) -> dict[str, Any]:
        return {
            "roles": len([k for k in self._roles if k not in self._roles or not any(
                r in self._roles for r in self._roles[k])]),
            "policies": sum(len(v) for v in self._policies.values()),
            "active_tokens": len(self._tokens),
            "audit_entries": len(self._audit_log),
        }
