from __future__ import annotations

import threading
import time

import pytest

from genesis.governance import (
    AuditTrail,
    CircuitBreakerRegistry,
    ConcurrencyControl,
    Governance,
    Policy,
    PolicyEffect,
    PolicyEngine,
)


class TestPolicyEngine:
    def test_add_and_evaluate_allow(self):
        g = PolicyEngine()
        g.add(Policy(id="p1", resource="doc:*", action="read", effect=PolicyEffect.ALLOW))
        effect, policy = g.evaluate("doc:report", "read")
        assert effect == PolicyEffect.ALLOW
        assert policy.id == "p1"

    def test_add_and_evaluate_deny(self):
        g = PolicyEngine()
        g.add(Policy(id="p1", resource="doc:secret", action="read", effect=PolicyEffect.DENY))
        effect, _ = g.evaluate("doc:secret", "read")
        assert effect == PolicyEffect.DENY

    def test_default_deny(self):
        g = PolicyEngine()
        effect, _ = g.evaluate("unknown:resource", "delete")
        assert effect == PolicyEffect.DENY

    def test_star_action_wildcard(self):
        g = PolicyEngine()
        g.add(Policy(id="p1", resource="doc:*", action="*", effect=PolicyEffect.ALLOW))
        assert g.check("doc:foo", "delete")
        assert g.check("doc:bar", "write")

    def test_prefix_resource_matching(self):
        g = PolicyEngine()
        g.add(Policy(id="p1", resource="storage:*", action="read", effect=PolicyEffect.ALLOW))
        assert g.check("storage:users", "read")
        assert not g.check("storage:users", "write")

    def test_exact_resource_matching(self):
        g = PolicyEngine()
        g.add(Policy(id="p1", resource="exact:one", action="get", effect=PolicyEffect.ALLOW))
        assert g.check("exact:one", "get")
        assert not g.check("exact:two", "get")

    def test_conditions(self):
        g = PolicyEngine()
        g.add(Policy(
            id="p1", resource="api:*", action="write",
            effect=PolicyEffect.ALLOW,
            conditions={"role": "admin"},
        ))
        assert g.check("api:data", "write", {"role": "admin"})
        assert not g.check("api:data", "write", {"role": "user"})

    def test_priority_ordering(self):
        g = PolicyEngine()
        g.add(Policy(id="deny_all", resource="*", action="*", effect=PolicyEffect.DENY, priority=100))
        g.add(Policy(id="allow_read", resource="doc:*", action="read", effect=PolicyEffect.ALLOW, priority=50))
        effect, policy = g.evaluate("doc:report", "read")
        assert effect == PolicyEffect.DENY
        assert policy.id == "deny_all"

    def test_priority_ordering_reverse(self):
        g = PolicyEngine()
        g.add(Policy(id="allow_read", resource="doc:*", action="read", effect=PolicyEffect.ALLOW, priority=50))
        g.add(Policy(id="deny_all", resource="*", action="*", effect=PolicyEffect.DENY, priority=100))
        effect, policy = g.evaluate("doc:report", "read")
        assert effect == PolicyEffect.DENY
        assert policy.id == "deny_all"

    def test_remove_policy(self):
        g = PolicyEngine()
        g.add(Policy(id="p1", resource="doc:*", action="read", effect=PolicyEffect.ALLOW))
        assert g.remove("p1")
        assert not g.check("doc:foo", "read")

    def test_remove_nonexistent(self):
        g = PolicyEngine()
        assert not g.remove("nonexistent")

    def test_disabled_policy(self):
        g = PolicyEngine()
        g.add(Policy(id="p1", resource="*", action="*", effect=PolicyEffect.ALLOW, enabled=False))
        assert not g.check("anything", "anything")

    def test_warn_effect(self):
        g = PolicyEngine()
        g.add(Policy(id="p1", resource="*", action="*", effect=PolicyEffect.WARN))
        effect, _ = g.evaluate("foo", "bar")
        assert effect == PolicyEffect.WARN

    def test_audit_effect(self):
        g = PolicyEngine()
        g.add(Policy(id="p1", resource="*", action="*", effect=PolicyEffect.AUDIT))
        effect, _ = g.evaluate("foo", "bar")
        assert effect == PolicyEffect.AUDIT

    def test_all_policies(self):
        g = PolicyEngine()
        g.add(Policy(id="p1"))
        g.add(Policy(id="p2"))
        assert len(g.all_policies()) == 2

    def test_clear(self):
        g = PolicyEngine()
        g.add(Policy(id="p1"))
        g.clear()
        assert len(g.all_policies()) == 0

    def test_check_convenience(self):
        g = PolicyEngine()
        g.add(Policy(id="p1", resource="*", action="*", effect=PolicyEffect.ALLOW))
        assert g.check("x", "y")

    def test_condition_mismatch_all_keys(self):
        g = PolicyEngine()
        g.add(Policy(id="p1", resource="*", action="*", effect=PolicyEffect.ALLOW, conditions={"a": "1", "b": "2"}))
        assert not g.check("x", "y", {"a": "1"})

    def test_thread_safe_add(self):
        g = PolicyEngine()
        results: list[bool] = []

        def adder():
            g.add(Policy(id=f"p{threading.get_ident()}", resource="*", action="*", effect=PolicyEffect.ALLOW))
            results.append(True)

        threads = [threading.Thread(target=adder) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        assert len(results) == 10
        assert len(g.all_policies()) == 10


class TestAuditTrail:
    def test_record(self):
        a = AuditTrail()
        entry = a.record("test", "read", "doc:1", identity="alice")
        assert entry.source == "test"
        assert entry.action == "read"
        assert entry.resource == "doc:1"
        assert entry.identity == "alice"
        assert entry.result == "allowed"

    def test_count(self):
        a = AuditTrail()
        assert a.count() == 0
        a.record("src", "act", "res")
        assert a.count() == 1

    def test_recent_empty(self):
        a = AuditTrail()
        assert a.recent() == []

    def test_recent(self):
        a = AuditTrail()
        for i in range(5):
            a.record("src", "act", f"res:{i}")
        recent = a.recent(3)
        assert len(recent) == 3

    def test_query_by_source(self):
        a = AuditTrail()
        a.record("s1", "read", "doc:1")
        a.record("s2", "write", "doc:2")
        results = a.query(source="s1")
        assert len(results) == 1
        assert results[0].source == "s1"

    def test_query_by_action(self):
        a = AuditTrail()
        a.record("src", "read", "doc:1")
        a.record("src", "write", "doc:2")
        results = a.query(action="read")
        assert len(results) == 1
        assert results[0].action == "read"

    def test_query_by_resource(self):
        a = AuditTrail()
        a.record("src", "read", "doc:1")
        a.record("src", "write", "doc:2")
        results = a.query(resource="doc:1")
        assert len(results) == 1
        assert results[0].resource == "doc:1"

    def test_query_by_identity(self):
        a = AuditTrail()
        a.record("src", "read", "doc:1", identity="alice")
        a.record("src", "write", "doc:2", identity="bob")
        results = a.query(identity="alice")
        assert len(results) == 1
        assert results[0].identity == "alice"

    def test_query_by_result(self):
        a = AuditTrail()
        a.record("src", "read", "doc:1", result="allowed")
        a.record("src", "write", "doc:2", result="denied")
        results = a.query(result="denied")
        assert len(results) == 1

    def test_query_since(self):
        a = AuditTrail()
        a.record("src", "read", "doc:1")
        time.sleep(0.01)
        cutoff = time.time()
        time.sleep(0.01)
        a.record("src", "write", "doc:2")
        results = a.query(since=cutoff)
        assert len(results) == 1
        assert results[0].action == "write"

    def test_query_limit(self):
        a = AuditTrail()
        for i in range(10):
            a.record("src", "act", f"res:{i}")
        results = a.query(limit=3)
        assert len(results) == 3

    def test_max_entries(self):
        a = AuditTrail(max_entries=5)
        for i in range(10):
            a.record("src", "act", f"res:{i}")
        assert a.count() == 5

    def test_metadata(self):
        a = AuditTrail()
        entry = a.record("src", "act", "res", metadata={"key": "val"})
        assert entry.metadata["key"] == "val"

    def test_multiple_filters(self):
        a = AuditTrail()
        a.record("src", "read", "doc:1", identity="alice", result="allowed")
        a.record("src", "write", "doc:1", identity="bob", result="denied")
        a.record("src", "read", "doc:2", identity="alice", result="denied")
        results = a.query(source="src", action="read", identity="alice")
        assert len(results) == 2

    def test_empty_query(self):
        a = AuditTrail()
        results = a.query()
        assert results == []


class TestConcurrencyControl:
    def test_acquire_lock(self):
        cc = ConcurrencyControl()
        assert cc.acquire_lock("lock:1", owner="alice")

    def test_acquire_lock_twice(self):
        cc = ConcurrencyControl()
        assert cc.acquire_lock("lock:1", owner="alice")
        assert not cc.acquire_lock("lock:1", owner="bob")

    def test_release_lock(self):
        cc = ConcurrencyControl()
        assert cc.acquire_lock("lock:1", owner="alice")
        assert cc.release_lock("lock:1", owner="alice")
        assert cc.acquire_lock("lock:1", owner="bob")

    def test_release_wrong_owner(self):
        cc = ConcurrencyControl()
        cc.acquire_lock("lock:1", owner="alice")
        assert not cc.release_lock("lock:1", owner="bob")

    def test_is_locked(self):
        cc = ConcurrencyControl()
        assert not cc.is_locked("lock:1")
        cc.acquire_lock("lock:1", owner="alice")
        assert cc.is_locked("lock:1")

    def test_lock_ttl_expiry(self):
        cc = ConcurrencyControl()
        cc.acquire_lock("lock:1", owner="alice", ttl=0.01)
        time.sleep(0.02)
        assert cc.acquire_lock("lock:1", owner="bob")

    def test_lock_ttl_not_expired(self):
        cc = ConcurrencyControl()
        cc.acquire_lock("lock:1", owner="alice", ttl=100.0)
        assert not cc.acquire_lock("lock:1", owner="bob")

    def test_lock_timeout(self):
        cc = ConcurrencyControl()
        cc.acquire_lock("lock:1", owner="alice")
        assert not cc.acquire_lock("lock:1", owner="bob", timeout_ms=10)

    def test_is_locked_after_ttl_expiry(self):
        cc = ConcurrencyControl()
        cc.acquire_lock("lock:1", owner="alice", ttl=0.01)
        time.sleep(0.02)
        assert not cc.is_locked("lock:1")

    def test_create_and_acquire_semaphore(self):
        cc = ConcurrencyControl()
        cc.create_semaphore("sem:1", 2)
        assert cc.acquire_semaphore("sem:1")
        assert cc.acquire_semaphore("sem:1")
        assert not cc.acquire_semaphore("sem:1")

    def test_release_semaphore(self):
        cc = ConcurrencyControl()
        cc.create_semaphore("sem:1", 1)
        assert cc.acquire_semaphore("sem:1")
        assert cc.release_semaphore("sem:1")
        assert cc.acquire_semaphore("sem:1")

    def test_semaphore_nonexistent(self):
        cc = ConcurrencyControl()
        assert not cc.acquire_semaphore("nonexistent")
        assert not cc.release_semaphore("nonexistent")

    def test_rate_limit_allowed(self):
        cc = ConcurrencyControl()
        assert cc.check_rate_limit("user:1", 5, 1000)

    def test_rate_limit_exceeded(self):
        cc = ConcurrencyControl()
        for _ in range(5):
            assert cc.check_rate_limit("user:1", 5, 10000)
        assert not cc.check_rate_limit("user:1", 5, 10000)

    def test_rate_limit_window_reset(self):
        cc = ConcurrencyControl()
        for _ in range(5):
            assert cc.check_rate_limit("user:1", 5, 100)
        time.sleep(0.15)
        assert cc.check_rate_limit("user:1", 5, 100)

    def test_locks_summary(self):
        cc = ConcurrencyControl()
        assert cc.locks_summary()["active_locks"] == 0
        cc.acquire_lock("lock:1", owner="alice")
        assert cc.locks_summary()["active_locks"] == 1

    def test_concurrent_lock_contention(self):
        cc = ConcurrencyControl()
        acquired: list[bool] = []

        def contending():
            result = cc.acquire_lock("contended", owner=str(threading.get_ident()), timeout_ms=200)
            acquired.append(result)

        cc.acquire_lock("contended", owner="primary")
        threads = [threading.Thread(target=contending) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        assert sum(acquired) == 0
        cc.release_lock("contended", owner="primary")
        result2 = cc.acquire_lock("contended", owner="secondary")
        assert result2


class TestCircuitBreakerRegistry:
    def test_register(self):
        cb = CircuitBreakerRegistry()
        cb.register("svc:1")
        assert cb.get_state("svc:1") == "closed"

    def test_is_allowed_closed(self):
        cb = CircuitBreakerRegistry()
        cb.register("svc:1")
        assert cb.is_allowed("svc:1")

    def test_opens_after_threshold(self):
        cb = CircuitBreakerRegistry()
        cb.register("svc:1", threshold=3)
        for _ in range(3):
            cb.record_failure("svc:1")
        assert cb.get_state("svc:1") == "open"
        assert not cb.is_allowed("svc:1")

    def test_stays_closed_below_threshold(self):
        cb = CircuitBreakerRegistry()
        cb.register("svc:1", threshold=5)
        for _ in range(4):
            cb.record_failure("svc:1")
        assert cb.get_state("svc:1") == "closed"
        assert cb.is_allowed("svc:1")

    def test_reset_success(self):
        cb = CircuitBreakerRegistry()
        cb.register("svc:1", threshold=2)
        cb.record_failure("svc:1")
        cb.record_success("svc:1")
        cb.record_failure("svc:1")
        assert cb.get_state("svc:1") == "closed"

    def test_half_open_to_closed(self):
        cb = CircuitBreakerRegistry()
        cb.register("svc:1", threshold=2, recovery_timeout=0.01)
        for _ in range(2):
            cb.record_failure("svc:1")
        assert cb.get_state("svc:1") == "open"
        time.sleep(0.02)
        assert cb.is_allowed("svc:1")
        assert cb.get_state("svc:1") == "half_open"
        cb.record_success("svc:1")
        cb.record_success("svc:1")
        assert cb.get_state("svc:1") == "closed"

    def test_half_open_to_open_on_failure(self):
        cb = CircuitBreakerRegistry()
        cb.register("svc:1", threshold=2, recovery_timeout=0.01)
        for _ in range(2):
            cb.record_failure("svc:1")
        time.sleep(0.02)
        assert cb.is_allowed("svc:1")
        cb.record_failure("svc:1")
        assert cb.get_state("svc:1") == "open"

    def test_get_state_nonexistent(self):
        cb = CircuitBreakerRegistry()
        assert cb.get_state("nonexistent") is None

    def test_is_allowed_nonexistent(self):
        cb = CircuitBreakerRegistry()
        assert cb.is_allowed("nonexistent")

    def test_reset(self):
        cb = CircuitBreakerRegistry()
        cb.register("svc:1", threshold=2)
        cb.record_failure("svc:1")
        cb.record_failure("svc:1")
        assert cb.get_state("svc:1") == "open"
        cb.reset("svc:1")
        assert cb.get_state("svc:1") == "closed"
        assert cb.is_allowed("svc:1")

    def test_summary(self):
        cb = CircuitBreakerRegistry()
        assert cb.summary()["total"] == 0
        cb.register("svc:1")
        assert cb.summary()["total"] == 1
        assert cb.summary()["by_state"]["closed"] == 1


class TestGovernance:
    def test_create(self):
        g = Governance()
        assert g.policies is not None
        assert g.audit is not None
        assert g.concurrency is not None
        assert g.circuit_breakers is not None

    def test_authorize_allowed(self):
        g = Governance()
        g.policies.add(Policy(id="p1", resource="doc:*", action="read", effect=PolicyEffect.ALLOW))
        assert g.authorize("doc:1", "read", source="test", identity="alice")

    def test_authorize_denied(self):
        g = Governance()
        assert not g.authorize("doc:1", "delete", source="test", identity="alice")

    def test_authorize_audits(self):
        g = Governance()
        g.authorize("doc:1", "read", source="test", identity="alice")
        assert g.audit.count() == 1

    def test_summary(self):
        g = Governance()
        s = g.summary()
        assert "policies" in s
        assert "audit_entries" in s
        assert "concurrency" in s
        assert "circuit_breakers" in s

    def test_full_workflow(self):
        g = Governance()
        g.policies.add(Policy(id="p1", resource="api:*", action="read", effect=PolicyEffect.ALLOW))
        assert g.authorize("api:users", "read", source="web", identity="alice")
        g.policies.add(Policy(id="p2", resource="api:admin", action="*", effect=PolicyEffect.DENY, priority=100))
        assert not g.authorize("api:admin", "read", source="web", identity="alice")
        g.concurrency.acquire_lock("lock:1", owner="alice")
        assert g.concurrency.is_locked("lock:1")
        g.circuit_breakers.register("svc:1", threshold=3)
        for _ in range(3):
            g.circuit_breakers.record_failure("svc:1")
        assert not g.circuit_breakers.is_allowed("svc:1")
