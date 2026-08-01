from __future__ import annotations

import threading
import time
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable


class PolicyEffect(Enum):
    ALLOW = "allow"
    DENY = "deny"
    WARN = "warn"
    AUDIT = "audit"


class PolicyMatch(Enum):
    EXACT = "exact"
    PREFIX = "prefix"
    PATTERN = "pattern"


@dataclass
class Policy:
    id: str = ""
    resource: str = ""
    action: str = ""
    effect: PolicyEffect = PolicyEffect.ALLOW
    conditions: dict[str, Any] = field(default_factory=dict)
    priority: int = 0
    description: str = ""
    enabled: bool = True


@dataclass
class AuditEntry:
    id: str = ""
    timestamp: float = 0.0
    source: str = ""
    action: str = ""
    resource: str = ""
    identity: str = ""
    result: str = ""
    detail: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class CircuitBreakerState:
    name: str = ""
    state: str = "closed"
    failure_count: int = 0
    threshold: int = 5
    recovery_timeout: float = 30.0
    last_failure: float = 0.0
    half_open_attempts: int = 0


@dataclass
class Lock:
    name: str = ""
    acquired: bool = False
    owner: str = ""
    acquired_at: float = 0.0
    ttl: float = 0.0
    reentrant: bool = False


class PolicyEngine:
    def __init__(self):
        self._policies: list[Policy] = []
        self._lock = threading.RLock()

    def add(self, policy: Policy):
        with self._lock:
            self._policies.append(policy)
            self._policies.sort(key=lambda p: -p.priority)

    def remove(self, policy_id: str) -> bool:
        with self._lock:
            before = len(self._policies)
            self._policies = [p for p in self._policies if p.id != policy_id]
            return len(self._policies) < before

    def evaluate(self, resource: str, action: str,
                 context: dict[str, Any] | None = None) -> tuple[PolicyEffect, Policy | None]:
        ctx = context or {}
        with self._lock:
            for policy in self._policies:
                if not policy.enabled:
                    continue
                if not self._match_resource(policy.resource, resource):
                    continue
                if policy.action != "*" and policy.action != action:
                    continue
                if self._check_conditions(policy.conditions, ctx):
                    return policy.effect, policy
        return PolicyEffect.DENY, None

    def check(self, resource: str, action: str,
              context: dict[str, Any] | None = None) -> bool:
        effect, _ = self.evaluate(resource, action, context)
        return effect == PolicyEffect.ALLOW

    def all_policies(self) -> list[Policy]:
        return list(self._policies)

    def clear(self):
        with self._lock:
            self._policies.clear()

    @staticmethod
    def _match_resource(pattern: str, resource: str) -> bool:
        if pattern == resource:
            return True
        if pattern.endswith("*"):
            return resource.startswith(pattern[:-1])
        return False

    @staticmethod
    def _check_conditions(conditions: dict[str, Any], context: dict[str, Any]) -> bool:
        for k, v in conditions.items():
            if context.get(k) != v:
                return False
        return True


class AuditTrail:
    def __init__(self, max_entries: int = 10000):
        self._entries: list[AuditEntry] = []
        self._lock = threading.RLock()
        self._max_entries = max_entries

    def record(self, source: str, action: str, resource: str,
               identity: str = "", result: str = "allowed",
               detail: str = "", metadata: dict[str, Any] | None = None) -> AuditEntry:
        entry = AuditEntry(
            timestamp=time.time(),
            source=source, action=action, resource=resource,
            identity=identity, result=result, detail=detail,
            metadata=metadata or {},
        )
        with self._lock:
            self._entries.append(entry)
            if len(self._entries) > self._max_entries:
                self._entries.pop(0)
        return entry

    def query(self, source: str | None = None, action: str | None = None,
              resource: str | None = None, identity: str | None = None,
              result: str | None = None,
              since: float = 0.0, limit: int = 100) -> list[AuditEntry]:
        with self._lock:
            results = list(self._entries)
        if source:
            results = [e for e in results if e.source == source]
        if action:
            results = [e for e in results if e.action == action]
        if resource:
            results = [e for e in results if e.resource == resource]
        if identity:
            results = [e for e in results if e.identity == identity]
        if result:
            results = [e for e in results if e.result == result]
        if since > 0:
            results = [e for e in results if e.timestamp >= since]
        results.sort(key=lambda e: -e.timestamp)
        return results[:limit]

    def recent(self, n: int = 20) -> list[AuditEntry]:
        with self._lock:
            return list(self._entries[-n:])

    def count(self) -> int:
        with self._lock:
            return len(self._entries)


class ConcurrencyControl:
    def __init__(self):
        self._locks: dict[str, Lock] = {}
        self._semaphores: dict[str, tuple[int, int]] = {}
        self._rate_limiters: dict[str, list[float]] = defaultdict(list)
        self._lock = threading.RLock()

    def acquire_lock(self, name: str, owner: str = "",
                     timeout_ms: float = 0.0, ttl: float = 0.0) -> bool:
        deadline = time.time() + timeout_ms / 1000 if timeout_ms > 0 else time.time()
        first = True
        while True:
            with self._lock:
                existing = self._locks.get(name)
                if existing is None:
                    self._locks[name] = Lock(
                        name=name, acquired=True, owner=owner,
                        acquired_at=time.time(), ttl=ttl,
                    )
                    return True
                if existing.ttl > 0 and time.time() - existing.acquired_at > existing.ttl:
                    self._locks.pop(name, None)
                    self._locks[name] = Lock(
                        name=name, acquired=True, owner=owner,
                        acquired_at=time.time(), ttl=ttl,
                    )
                    return True
            if first and timeout_ms == 0:
                return False
            first = False
            if time.time() >= deadline:
                return False
            time.sleep(0.01)

    def release_lock(self, name: str, owner: str = "") -> bool:
        with self._lock:
            lock = self._locks.get(name)
            if lock is None:
                return False
            if owner and lock.owner != owner:
                return False
            self._locks.pop(name, None)
            return True

    def is_locked(self, name: str) -> bool:
        with self._lock:
            lock = self._locks.get(name)
            if lock is None:
                return False
            if lock.ttl > 0 and time.time() - lock.acquired_at > lock.ttl:
                self._locks.pop(name, None)
                return False
            return True

    def create_semaphore(self, name: str, max_count: int):
        with self._lock:
            self._semaphores[name] = [max_count, max_count]

    def acquire_semaphore(self, name: str) -> bool:
        with self._lock:
            sem = self._semaphores.get(name)
            if sem is None:
                return False
            if sem[1] <= 0:
                return False
            sem[1] -= 1
            return True

    def release_semaphore(self, name: str) -> bool:
        with self._lock:
            sem = self._semaphores.get(name)
            if sem is None:
                return False
            sem[1] = min(sem[0], sem[1] + 1)
            return True

    def check_rate_limit(self, key: str, max_calls: int, window_ms: float) -> bool:
        now = time.time()
        window = window_ms / 1000.0
        with self._lock:
            calls = self._rate_limiters[key]
            cutoff = now - window
            calls[:] = [t for t in calls if t > cutoff]
            if len(calls) >= max_calls:
                return False
            calls.append(now)
            return True

    def locks_summary(self) -> dict[str, Any]:
        with self._lock:
            return {
                "active_locks": len(self._locks),
                "active_semaphores": len(self._semaphores),
                "rate_limiters": len(self._rate_limiters),
            }


class CircuitBreakerRegistry:
    def __init__(self):
        self._breakers: dict[str, CircuitBreakerState] = {}
        self._lock = threading.RLock()

    def register(self, name: str, threshold: int = 5, recovery_timeout: float = 30.0):
        with self._lock:
            self._breakers[name] = CircuitBreakerState(
                name=name, threshold=threshold, recovery_timeout=recovery_timeout,
            )

    def record_success(self, name: str):
        with self._lock:
            cb = self._breakers.get(name)
            if cb is None:
                return
            if cb.state == "half_open":
                cb.half_open_attempts += 1
                if cb.half_open_attempts >= 2:
                    cb.state = "closed"
                    cb.failure_count = 0
                    cb.half_open_attempts = 0
            elif cb.state == "closed":
                cb.failure_count = 0

    def record_failure(self, name: str):
        with self._lock:
            cb = self._breakers.get(name)
            if cb is None:
                return
            cb.failure_count += 1
            cb.last_failure = time.time()
            if cb.state == "closed" and cb.failure_count >= cb.threshold:
                cb.state = "open"
            elif cb.state == "half_open":
                cb.state = "open"
                cb.half_open_attempts = 0

    def is_allowed(self, name: str) -> bool:
        with self._lock:
            cb = self._breakers.get(name)
            if cb is None:
                return True
            if cb.state == "closed":
                return True
            if cb.state == "open":
                if time.time() - cb.last_failure >= cb.recovery_timeout:
                    cb.state = "half_open"
                    return True
                return False
            if cb.state == "half_open":
                return True
            return True

    def get_state(self, name: str) -> str | None:
        with self._lock:
            cb = self._breakers.get(name)
            return cb.state if cb else None

    def reset(self, name: str):
        with self._lock:
            cb = self._breakers.get(name)
            if cb:
                cb.state = "closed"
                cb.failure_count = 0
                cb.half_open_attempts = 0

    def summary(self) -> dict[str, Any]:
        with self._lock:
            states: dict[str, int] = defaultdict(int)
            for cb in self._breakers.values():
                states[cb.state] += 1
            return {
                "total": len(self._breakers),
                "by_state": dict(states),
            }


class Governance:
    def __init__(self):
        self.policies = PolicyEngine()
        self.audit = AuditTrail()
        self.concurrency = ConcurrencyControl()
        self.circuit_breakers = CircuitBreakerRegistry()

    def authorize(self, resource: str, action: str,
                  context: dict[str, Any] | None = None,
                  source: str = "", identity: str = "") -> bool:
        effect, policy = self.policies.evaluate(resource, action, context)
        allowed = effect == PolicyEffect.ALLOW
        self.audit.record(
            source=source or "governance",
            action=action,
            resource=resource,
            identity=identity,
            result="allowed" if allowed else "denied",
            detail=f"Effect: {effect.value}" + (f", policy: {policy.id}" if policy else ""),
            metadata={"context": context or {}},
        )
        return allowed

    def summary(self) -> dict[str, Any]:
        return {
            "policies": len(self.policies.all_policies()),
            "audit_entries": self.audit.count(),
            "concurrency": self.concurrency.locks_summary(),
            "circuit_breakers": self.circuit_breakers.summary(),
        }
