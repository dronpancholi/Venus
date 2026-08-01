import time

import pytest

from genesis.orchestration import ServiceDef
from genesis.service_kernel import (
    ServiceKernel, LifecycleManager, HealthManager, FailureManager,
    CapabilityPublisher, MetricsCollector, HeartbeatManager,
    ServiceState, CircuitState, RecoveryAction, RecoveryPolicy,
    CircuitBreaker, ServiceHealth, ServiceMetrics,
)


class TestLifecycleManager:
    def test_register_get_state(self):
        lm = LifecycleManager()
        lm.register("svc_a")
        assert lm.get_state("svc_a") == ServiceState.PENDING

    def test_valid_transition_pending_to_booting(self):
        lm = LifecycleManager()
        lm.register("svc_a")
        assert lm.transition("svc_a", ServiceState.BOOTING)
        assert lm.get_state("svc_a") == ServiceState.BOOTING

    def test_valid_transition_booting_to_healthy(self):
        lm = LifecycleManager()
        lm.register("svc_a")
        lm.transition("svc_a", ServiceState.BOOTING)
        assert lm.transition("svc_a", ServiceState.HEALTHY)

    def test_invalid_transition_pending_to_stopped(self):
        lm = LifecycleManager()
        lm.register("svc_a")
        assert not lm.transition("svc_a", ServiceState.STOPPED)
        assert lm.get_state("svc_a") == ServiceState.PENDING

    def test_invalid_transition_healthy_to_booting(self):
        lm = LifecycleManager()
        lm.register("svc_a")
        lm.transition("svc_a", ServiceState.BOOTING)
        lm.transition("svc_a", ServiceState.HEALTHY)
        assert not lm.transition("svc_a", ServiceState.BOOTING)

    def test_failed_to_booting_is_valid(self):
        lm = LifecycleManager()
        lm.register("svc_a")
        lm.force_set("svc_a", ServiceState.FAILED)
        assert lm.transition("svc_a", ServiceState.BOOTING)

    def test_unregister(self):
        lm = LifecycleManager()
        lm.register("svc_a")
        assert lm.unregister("svc_a")
        assert lm.get_state("svc_a") is None

    def test_force_set(self):
        lm = LifecycleManager()
        lm.register("svc_a")
        lm.force_set("svc_a", ServiceState.FAILED)
        assert lm.get_state("svc_a") == ServiceState.FAILED

    def test_all_states_and_summary(self):
        lm = LifecycleManager()
        lm.register("a")
        lm.register("b")
        lm.transition("a", ServiceState.BOOTING)
        lm.transition("a", ServiceState.HEALTHY)
        states = lm.all_states()
        assert states["a"] == ServiceState.HEALTHY
        assert states["b"] == ServiceState.PENDING
        summary = lm.summary()
        assert summary["healthy"] == 1
        assert summary["pending"] == 1


class TestHealthManager:
    def test_register_get_health(self):
        hm = HealthManager()
        hm.register("svc_a")
        health = hm.get_health("svc_a")
        assert health is not None
        assert health.healthy

    def test_record_healthy(self):
        hm = HealthManager()
        hm.register("svc_a")
        hm.record_result("svc_a", True, 5.0)
        health = hm.get_health("svc_a")
        assert health.healthy
        assert health.last_latency_ms == 5.0
        assert health.consecutive_failures == 0

    def test_record_unhealthy(self):
        hm = HealthManager()
        hm.register("svc_a")
        hm.record_result("svc_a", False, 10.0, "timeout")
        health = hm.get_health("svc_a")
        assert not health.healthy
        assert health.consecutive_failures == 1
        assert health.error == "timeout"

    def test_unhealthy_services(self):
        hm = HealthManager()
        hm.register("svc_a")
        hm.register("svc_b")
        hm.record_result("svc_a", False)
        unhealthy = hm.unhealthy_services()
        assert "svc_a" in unhealthy
        assert "svc_b" not in unhealthy

    def test_on_unhealthy_callback(self):
        hm = HealthManager()
        hm.register("svc_a")
        triggered = []
        hm.on_unhealthy(lambda sid, h: triggered.append(sid))
        hm.record_result("svc_a", False, error="fail")
        assert triggered == ["svc_a"]

    def test_check_service_with_fn(self):
        hm = HealthManager()
        instance = {"ok": True}
        hm.register("svc_a", check_fn=lambda i: i.get("ok", False), interval_ms=100.0)
        health = hm.check_service("svc_a", instance)
        assert health.healthy

    def test_check_service_with_fn_failing(self):
        hm = HealthManager()
        instance = {"ok": False}
        hm.register("svc_a", check_fn=lambda i: i.get("ok", False))
        health = hm.check_service("svc_a", instance)
        assert not health.healthy

    def test_check_service_exception(self):
        hm = HealthManager()
        hm.register("svc_a", check_fn=lambda i: (_ for _ in ()).throw(ValueError("bad")))
        health = hm.check_service("svc_a", object())
        assert not health.healthy
        assert "bad" in (health.error or "")

    def test_summary(self):
        hm = HealthManager()
        hm.register("a")
        hm.register("b")
        hm.record_result("a", False)
        s = hm.summary()
        assert s["monitored"] == 2
        assert s["unhealthy"] == 1
        assert s["healthy"] == 1


class TestFailureManager:
    def test_register_policy_creates_breaker(self):
        fm = FailureManager()
        policy = RecoveryPolicy(max_retries=2)
        fm.register_policy("svc_a", policy)
        breaker = fm.get_breaker("svc_a")
        assert breaker is not None
        assert breaker.state == CircuitState.CLOSED
        assert fm.get_policy("svc_a") is policy

    def test_record_failure_triggers_restart_action(self):
        fm = FailureManager()
        policy = RecoveryPolicy(max_retries=3, action=RecoveryAction.RESTART)
        fm.register_policy("svc_a", policy)
        action = fm.record_failure("svc_a", "error")
        assert action == RecoveryAction.RESTART

    def test_circuit_breaker_opens_after_threshold(self):
        fm = FailureManager()
        policy = RecoveryPolicy(max_retries=10, circuit_breaker_threshold=3)
        fm.register_policy("svc_a", policy)
        for _ in range(3):
            fm.record_failure("svc_a")
        breaker = fm.get_breaker("svc_a")
        assert breaker.state == CircuitState.OPEN

    def test_circuit_breaker_returns_ignore_when_open(self):
        fm = FailureManager()
        policy = RecoveryPolicy(max_retries=10, circuit_breaker_threshold=2)
        fm.register_policy("svc_a", policy)
        fm.record_failure("svc_a")
        action = fm.record_failure("svc_a")
        assert action == RecoveryAction.IGNORE

    def test_exhaust_retries_returns_degrade(self):
        fm = FailureManager()
        policy = RecoveryPolicy(max_retries=1, circuit_breaker_threshold=10)
        fm.register_policy("svc_a", policy)
        fm.record_failure("svc_a")
        action = fm.record_failure("svc_a")
        assert action == RecoveryAction.DEGRADE

    def test_record_success_resets_breaker(self):
        fm = FailureManager()
        fm.register_policy("svc_a")
        fm.record_failure("svc_a")
        fm.record_success("svc_a")
        breaker = fm.get_breaker("svc_a")
        assert breaker.failure_count == 0
        assert breaker.state == CircuitState.CLOSED

    def test_retry_delay_exponential(self):
        fm = FailureManager()
        policy = RecoveryPolicy(retry_delay_ms=100.0, backoff_factor=2.0, max_retries=5)
        fm.register_policy("svc_a", policy)
        fm.record_failure("svc_a")
        d1 = fm.retry_delay_ms("svc_a")
        assert d1 == 100.0
        fm.record_failure("svc_a")
        d2 = fm.retry_delay_ms("svc_a")
        assert d2 == 200.0
        fm.record_failure("svc_a")
        d3 = fm.retry_delay_ms("svc_a")
        assert d3 == 400.0

    def test_reset(self):
        fm = FailureManager()
        fm.register_policy("svc_a")
        fm.record_failure("svc_a")
        fm.record_failure("svc_a")
        fm.reset("svc_a")
        breaker = fm.get_breaker("svc_a")
        assert breaker.failure_count == 0
        assert breaker.state == CircuitState.CLOSED

    def test_summary(self):
        fm = FailureManager()
        fm.register_policy("a")
        fm.register_policy("b")
        fm.record_failure("a")
        fm.record_failure("a")
        fm.record_failure("a")
        fm.record_failure("a")
        fm.record_failure("a")
        s = fm.summary()
        assert s["circuits"] == 2
        assert s["closed"] == 1
        assert s["open"] == 1


class TestCapabilityPublisher:
    def test_publish_and_find_by_service(self):
        cp = CapabilityPublisher()
        cp.publish("svc_a", "compiler", interfaces=[{"method": "POST", "path": "/compile"}])
        caps = cp.find_by_service("svc_a")
        assert len(caps) == 1
        assert caps[0]["capability_name"] == "compiler"

    def test_find_by_interface(self):
        cp = CapabilityPublisher()
        cp.publish("svc_a", "compiler", interfaces=[{"method": "POST", "path": "/compile"}])
        cp.publish("svc_b", "validator", interfaces=[{"method": "POST", "path": "/validate"}])
        results = cp.find_by_interface("POST", "/compile")
        assert len(results) == 1
        assert results[0]["service_id"] == "svc_a"

    def test_unpublish(self):
        cp = CapabilityPublisher()
        cp.publish("svc_a", "compiler")
        assert cp.unpublish("svc_a", "compiler")
        assert len(cp.find_by_service("svc_a")) == 0

    def test_unpublish_all(self):
        cp = CapabilityPublisher()
        cp.publish("svc_a", "compiler")
        cp.publish("svc_a", "validator")
        assert cp.unpublish_all("svc_a")
        assert len(cp.find_by_service("svc_a")) == 0

    def test_all_published(self):
        cp = CapabilityPublisher()
        cp.publish("svc_a", "compiler")
        cp.publish("svc_b", "validator")
        assert len(cp.all_published()) == 2

    def test_summary(self):
        cp = CapabilityPublisher()
        cp.publish("svc_a", "compiler")
        cp.publish("svc_a", "validator")
        cp.publish("svc_b", "graph")
        s = cp.summary()
        assert s["services_publishing"] == 2
        assert s["total_capabilities"] == 3


class TestMetricsCollector:
    def test_register_and_get(self):
        mc = MetricsCollector()
        mc.register("svc_a")
        m = mc.get_metrics("svc_a")
        assert m is not None
        assert m.service_id == "svc_a"

    def test_record_start_updates_uptime(self):
        mc = MetricsCollector()
        mc.register("svc_a")
        mc.record_start("svc_a")
        m = mc.get_metrics("svc_a")
        assert m.started_at > 0
        assert m.uptime_seconds > 0

    def test_record_health_check(self):
        mc = MetricsCollector()
        mc.register("svc_a")
        mc.record_health_check("svc_a", True, 5.0)
        mc.record_health_check("svc_a", False, 10.0)
        m = mc.get_metrics("svc_a")
        assert m.health_check_count == 2
        assert m.health_check_failures == 1
        assert m.avg_health_latency_ms == 7.5

    def test_record_failure_and_recovery(self):
        mc = MetricsCollector()
        mc.register("svc_a")
        mc.record_failure("svc_a")
        mc.record_recovery("svc_a")
        m = mc.get_metrics("svc_a")
        assert m.failure_count == 1
        assert m.recovery_count == 1

    def test_record_restart(self):
        mc = MetricsCollector()
        mc.register("svc_a")
        mc.record_restart("svc_a")
        m = mc.get_metrics("svc_a")
        assert m.restarts == 1

    def test_summary(self):
        mc = MetricsCollector()
        mc.register("a")
        mc.register("b")
        mc.record_health_check("a", True, 1.0)
        mc.record_failure("b")
        s = mc.summary()
        assert s["services"] == 2
        assert s["total_health_checks"] == 1
        assert s["total_failures"] == 1


class TestHeartbeatManager:
    def test_record_and_is_alive(self):
        hbm = HeartbeatManager()
        hbm.record("svc_a")
        assert hbm.is_alive("svc_a", timeout_ms=60000.0)

    def test_is_alive_returns_false_for_unknown(self):
        hbm = HeartbeatManager()
        assert not hbm.is_alive("unknown")

    def test_get_stale_services(self):
        hbm = HeartbeatManager()
        hbm.record("svc_a")
        time.sleep(0.01)
        stale = hbm.get_stale_services(timeout_ms=1.0)
        assert "svc_a" in stale

    def test_on_stale_callback(self):
        hbm = HeartbeatManager()
        hbm.record("svc_a")
        triggered = []
        hbm.on_stale(lambda sid: triggered.append(sid))
        time.sleep(0.01)
        hbm.check_for_stale(timeout_ms=1.0)
        assert "svc_a" in triggered

    def test_last_heartbeat(self):
        hbm = HeartbeatManager()
        before = time.time()
        hbm.record("svc_a")
        after = time.time()
        ts = hbm.last_heartbeat("svc_a")
        assert ts is not None
        assert before <= ts <= after

    def test_all_heartbeats(self):
        hbm = HeartbeatManager()
        hbm.record("a")
        hbm.record("b")
        assert len(hbm.all_heartbeats()) == 2

    def test_summary(self):
        hbm = HeartbeatManager()
        hbm.record("a")
        hbm.record("b")
        s = hbm.summary()
        assert s["active"] == 2


class TestServiceKernel:
    def test_register(self):
        sk = ServiceKernel()
        svc = ServiceDef(id="svc_a", factory=lambda: {})
        sk.register(svc)
        assert sk.lifecycle.get_state("svc_a") == ServiceState.PENDING
        status = sk.get_status("svc_a")
        assert status["lifecycle"] == ServiceState.PENDING

    def test_boot_sets_lifecycle_healthy(self):
        sk = ServiceKernel()
        svc = ServiceDef(id="svc_a", factory=lambda: {})
        sk.register(svc)
        report = sk.boot()
        assert report.healthy_count == 1
        assert sk.lifecycle.get_state("svc_a") == ServiceState.HEALTHY

    def test_boot_sets_failed_on_exception(self):
        sk = ServiceKernel()
        svc = ServiceDef(id="svc_a", factory=lambda: (_ for _ in ()).throw(RuntimeError("fail")))
        sk.register(svc)
        report = sk.boot()
        assert report.failed_count == 1
        assert sk.lifecycle.get_state("svc_a") == ServiceState.FAILED

    def test_all_status(self):
        sk = ServiceKernel()
        sk.register(ServiceDef(id="a", factory=lambda: {}))
        sk.register(ServiceDef(id="b", factory=lambda: {}))
        sk.boot()
        statuses = sk.all_status()
        assert "a" in statuses
        assert "b" in statuses

    def test_summary(self):
        sk = ServiceKernel()
        sk.register(ServiceDef(id="a", factory=lambda: {}))
        sk.boot()
        s = sk.summary()
        assert s["services"]["registered"] == 1
        assert s["services"]["booted"] == 1
        assert s["running"]

    def test_restart_failed_service(self):
        sk = ServiceKernel()
        factory_calls = []
        svc = ServiceDef(id="svc_a", factory=lambda: factory_calls.append(1) or {})
        sk.register(svc)
        sk.boot()
        sk.lifecycle.force_set("svc_a", ServiceState.FAILED)
        assert sk.restart_service("svc_a")
        assert len(factory_calls) == 2
        assert sk.lifecycle.get_state("svc_a") == ServiceState.HEALTHY

    def test_restart_healthy_service_returns_false(self):
        sk = ServiceKernel()
        svc = ServiceDef(id="svc_a", factory=lambda: {})
        sk.register(svc)
        sk.boot()
        assert not sk.restart_service("svc_a")

    def test_heartbeat_integration(self):
        sk = ServiceKernel()
        sk.register(ServiceDef(id="svc_a", factory=lambda: {}))
        sk.boot()
        sk.record_heartbeat("svc_a")
        assert sk.heartbeat.is_alive("svc_a")

    def test_capability_publish_integration(self):
        cp = CapabilityPublisher()
        cp.publish("svc_a", "compiler", interfaces=[{"method": "POST", "path": "/compile"}])
        caps = cp.find_by_service("svc_a")
        assert len(caps) == 1
        results = cp.find_by_interface("POST", "/compile")
        assert len(results) == 1

    def test_event_handlers(self):
        sk = ServiceKernel()
        events = []
        sk.on("kernel.booted", lambda d: events.append(d))
        sk.register(ServiceDef(id="a", factory=lambda: {}))
        sk.boot()
        assert len(events) == 1
        assert events[0]["healthy"] == 1

    def test_shutdown(self):
        sk = ServiceKernel()
        sk.register(ServiceDef(id="a", factory=lambda: {}))
        sk.boot()
        sk.shutdown()
        assert not sk._running
        s = sk.summary()
        assert not s["running"]
