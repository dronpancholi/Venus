"""
Tests for GENESIS-IX Phase 1: Platform Refactor — Service-Oriented Platform.
"""

import pytest
from genesis.platform_v2 import (
    ServiceRegistry, ServiceDefinition, ServiceCategory, ServiceState,
    LifecycleManager, EventRouter, MetricsManager, TelemetryManager,
    ConfigurationManager, StateManager, ResourceScheduler, RecoveryManager,
    PlatformV2, MetricPoint, HealthStatus,
)


class TestServiceDefinition:
    def test_create_minimal(self):
        sd = ServiceDefinition(name="test_svc")
        assert sd.id
        assert sd.name == "test_svc"
        assert sd.category == ServiceCategory.PLATFORM
        assert sd.version == "1.0.0"

    def test_create_with_category(self):
        sd = ServiceDefinition(name="brain", category=ServiceCategory.COGNITIVE)
        assert sd.category == ServiceCategory.COGNITIVE


class TestServiceRegistry:
    def setup_method(self):
        self.reg = ServiceRegistry()

    def test_register(self):
        sd = self.reg.register(ServiceDefinition(name="svc1"))
        assert self.reg.get(sd.id) is sd
        assert self.reg.count == 1
        assert self.reg.state_of(sd.id) == ServiceState.CREATED

    def test_register_instance(self):
        sd = self.reg.register(ServiceDefinition(name="svc1"))
        obj = {"key": "val"}
        self.reg.register_instance(sd.id, obj)
        assert self.reg.get_instance(sd.id) is obj

    def test_get_nonexistent(self):
        assert self.reg.get("nonexistent") is None
        assert self.reg.get_instance("nonexistent") is None

    def test_find_by_category(self):
        self.reg.register(ServiceDefinition(name="storage", category=ServiceCategory.STORAGE))
        self.reg.register(ServiceDefinition(name="brain", category=ServiceCategory.COGNITIVE))
        results = self.reg.find(category=ServiceCategory.STORAGE)
        assert len(results) == 1
        assert results[0].name == "storage"

    def test_find_by_state(self):
        sd = self.reg.register(ServiceDefinition(name="svc1"))
        self.reg.set_state(sd.id, ServiceState.RUNNING)
        results = self.reg.find(state=ServiceState.RUNNING)
        assert len(results) == 1

    def test_find_by_provides(self):
        sd = ServiceDefinition(name="api", provides=["http", "rest"])
        self.reg.register(sd)
        results = self.reg.find(provides="rest")
        assert len(results) == 1

    def test_state_management(self):
        sd = self.reg.register(ServiceDefinition(name="svc1"))
        assert self.reg.state_of(sd.id) == ServiceState.CREATED
        self.reg.set_state(sd.id, ServiceState.RUNNING)
        assert self.reg.state_of(sd.id) == ServiceState.RUNNING

    def test_health_defaults(self):
        sd = self.reg.register(ServiceDefinition(name="svc1"))
        h = self.reg.health_of(sd.id)
        assert h.healthy is True
        assert h.failure_count == 0

    def test_record_metric(self):
        mp = MetricPoint(name="cpu", value=0.5, service_id="svc1")
        self.reg.record_metric(mp)
        assert "cpu" in self.reg._metrics

    def test_dependency_graph(self):
        a = ServiceDefinition(id="svc:a", name="a", dependencies=["svc:b"])
        b = ServiceDefinition(id="svc:b", name="b")
        self.reg.register(a)
        self.reg.register(b)
        dg = self.reg.dependency_graph()
        assert "svc:a" in dg
        assert dg["svc:a"] == ["svc:b"]


class TestLifecycleManager:
    def setup_method(self):
        self.reg = ServiceRegistry()
        self.lm = LifecycleManager(self.reg)

    def test_compute_boot_order(self):
        a = self.reg.register(ServiceDefinition(id="svc:a", name="a", dependencies=["svc:b"]))
        b = self.reg.register(ServiceDefinition(id="svc:b", name="b"))
        order = self.lm.compute_boot_order()
        assert order.index("svc:b") < order.index("svc:a")

    def test_initialize_all(self):
        a = self.reg.register(ServiceDefinition(id="svc:a", name="a", dependencies=["svc:b"]))
        b = self.reg.register(ServiceDefinition(id="svc:b", name="b"))
        initialized = self.lm.initialize_all()
        assert len(initialized) == 2
        assert self.reg.state_of("svc:a") == ServiceState.READY
        assert self.reg.state_of("svc:b") == ServiceState.READY

    def test_start_all(self):
        self.reg.register(ServiceDefinition(name="svc1"))
        self.lm.initialize_all()
        started = self.lm.start_all()
        assert len(started) == 1
        assert self.reg.state_of(started[0]) == ServiceState.RUNNING

    def test_stop_all(self):
        self.reg.register(ServiceDefinition(name="svc1"))
        self.lm.initialize_all()
        self.lm.start_all()
        self.lm.stop_all()
        assert self.reg.state_of(self.reg.services[0].id) == ServiceState.STOPPED

    def test_health_check_all(self):
        self.reg.register(ServiceDefinition(name="svc1"))
        results = self.lm.health_check_all()
        assert len(results) == 1

    def test_health_check_with_callback(self):
        def health_check():
            return False
        self.reg.register(ServiceDefinition(name="svc1", health_check=health_check))
        results = self.lm.health_check_all()
        assert results[self.reg.services[0].id] is False

    def test_health_check_failure_threshold(self):
        self.reg.register(ServiceDefinition(name="svc1"))
        for _ in range(5):
            self.lm.health_check_all()
        h = self.reg.health_of(self.reg.services[0].id)
        assert h.failure_count == 5 or h.healthy is False


class TestEventRouter:
    def setup_method(self):
        self.er = EventRouter()

    def test_publish_subscribe(self):
        received = []
        def handler(event):
            received.append(event)
        self.er.subscribe("test.event", handler)
        self.er.publish("test.event", {"msg": "hello"})
        assert len(received) == 1
        assert received[0]["data"]["msg"] == "hello"

    def test_multiple_handlers(self):
        count = [0]
        def h1(e):
            count[0] += 1
        def h2(e):
            count[0] += 1
        self.er.subscribe("test.event", h1)
        self.er.subscribe("test.event", h2)
        self.er.publish("test.event")
        assert count[0] == 2

    def test_handler_exception_safe(self):
        def broken(e):
            raise ValueError("oops")
        self.er.subscribe("test.event", broken)
        self.er.publish("test.event")

    def test_recent(self):
        for i in range(5):
            self.er.publish(f"event.{i}")
        assert len(self.er.recent(3)) == 3


class TestMetricsManager:
    def setup_method(self):
        self.mm = MetricsManager()

    def test_record(self):
        self.mm.record("cpu", 0.5, service_id="svc1")
        points = self.mm.get_metric("cpu")
        assert len(points) == 1
        assert points[0].value == 0.5

    def test_increment(self):
        self.mm.increment("requests")
        self.mm.increment("requests", 5)
        s = self.mm.summary()
        assert s["counters"]["requests"] == 6

    def test_gauge(self):
        self.mm.set_gauge("temperature", 36.5)
        s = self.mm.summary()
        assert s["gauges"]["temperature"] == 36.5

    def test_summary(self):
        self.mm.record("latency", 100)
        self.mm.record("latency", 200)
        self.mm.record("latency", 300)
        s = self.mm.summary()
        assert s["latency"]["min"] == 100
        assert s["latency"]["max"] == 300
        assert s["latency"]["avg"] == 200
        assert s["latency"]["count"] == 3

    def test_empty_summary(self):
        s = self.mm.summary()
        assert s["counters"] == {}
        assert s["gauges"] == {}


class TestTelemetryManager:
    def setup_method(self):
        self.tm = TelemetryManager()

    def test_start_end_trace(self):
        tid = self.tm.start_trace("test_trace")
        assert tid
        self.tm.end_trace(tid, "ok")
        r = self.tm.report()
        assert r["traces"] == 1

    def test_start_end_span(self):
        tid = self.tm.start_trace("trace1")
        sid = self.tm.start_span(tid, "span1")
        self.tm.end_span(sid)
        r = self.tm.report()
        assert r["completed_spans"] == 1

    def test_active_spans(self):
        tid = self.tm.start_trace("trace1")
        self.tm.start_span(tid, "active_span")
        r = self.tm.report()
        assert r["active_spans"] == 1


class TestConfigurationManager:
    def setup_method(self):
        self.cm = ConfigurationManager()

    def test_set_and_get(self):
        self.cm.set("svc1", "host", "localhost")
        assert self.cm.get("svc1", "host") == "localhost"

    def test_get_default(self):
        assert self.cm.get("svc1", "nonexistent", "default_val") == "default_val"

    def test_defaults(self):
        self.cm.set_defaults("svc1", {"port": 8080})
        assert self.cm.get("svc1", "port") == 8080

    def test_override_default(self):
        self.cm.set_defaults("svc1", {"host": "default"})
        self.cm.set("svc1", "host", "explicit")
        assert self.cm.get("svc1", "host") == "explicit"

    def test_all_for(self):
        self.cm.set_defaults("svc1", {"host": "default", "port": 80})
        self.cm.set("svc1", "port", 8080)
        cfg = self.cm.all_for("svc1")
        assert cfg["host"] == "default"
        assert cfg["port"] == 8080


class TestStateManager:
    def setup_method(self):
        self.sm = StateManager()

    def test_set_and_get(self):
        self.sm.set_state("svc1", "status", "running")
        assert self.sm.get_state("svc1", "status") == "running"

    def test_get_default(self):
        assert self.sm.get_state("svc1", "missing", "default") == "default"

    def test_snapshot_and_restore(self):
        self.sm.set_state("svc1", "key", "value")
        sid = self.sm.snapshot()
        self.sm.set_state("svc1", "other", "changed")
        self.sm.restore(sid)
        assert self.sm.get_state("svc1", "key") == "value"

    def test_restore_nonexistent(self):
        assert self.sm.restore("nonexistent") is False


class TestResourceScheduler:
    def setup_method(self):
        self.rs = ResourceScheduler()

    def test_register_and_allocate(self):
        self.rs.register_resource("cpu", 100.0)
        assert self.rs.allocate("cpu", "svc1", 30.0) is True

    def test_allocate_insufficient(self):
        self.rs.register_resource("cpu", 10.0)
        assert self.rs.allocate("cpu", "svc1", 20.0) is False

    def test_allocate_unregistered(self):
        assert self.rs.allocate("unknown", "svc1", 10.0) is False

    def test_release(self):
        self.rs.register_resource("cpu", 100.0)
        self.rs.allocate("cpu", "svc1", 30.0)
        self.rs.release("cpu", "svc1")
        util = self.rs.utilization()
        assert util["cpu"] == 0.0

    def test_utilization(self):
        self.rs.register_resource("cpu", 100.0)
        self.rs.register_resource("mem", 512.0)
        self.rs.allocate("cpu", "svc1", 25.0)
        util = self.rs.utilization()
        assert util["cpu"] == 0.25
        assert util["mem"] == 0.0


class TestRecoveryManager:
    def setup_method(self):
        self.reg = ServiceRegistry()
        self.lm = LifecycleManager(self.reg)
        self.rm = RecoveryManager(self.reg, self.lm)

    def test_recover_nonexistent(self):
        assert self.rm.recover_service("nonexistent") is False

    def test_recover_service(self):
        sd = self.reg.register(ServiceDefinition(name="svc1"))
        self.reg.set_state(sd.id, ServiceState.FAILED)
        assert self.rm.recover_service(sd.id) is True
        assert self.reg.state_of(sd.id) == ServiceState.RUNNING

    def test_recover_all_degraded(self):
        sd1 = self.reg.register(ServiceDefinition(name="svc1"))
        sd2 = self.reg.register(ServiceDefinition(name="svc2"))
        self.reg.set_state(sd1.id, ServiceState.FAILED)
        self.reg.set_state(sd2.id, ServiceState.DEGRADED)
        recovered = self.rm.recover_all_degraded()
        assert len(recovered) == 2


class TestPlatformV2:
    def setup_method(self):
        self.platform = PlatformV2()

    def test_register_service(self):
        svc = self.platform.register_service("my_svc", ServiceCategory.COGNITIVE)
        assert svc.id
        assert svc.category == ServiceCategory.COGNITIVE
        assert self.platform.registry.count == 1

    def test_boot(self):
        self.platform.register_service("svc1")
        count = self.platform.boot()
        assert count >= 1

    def test_shutdown(self):
        self.platform.register_service("svc1")
        self.platform.boot()
        self.platform.shutdown()

    def test_health(self):
        self.platform.register_service("svc1")
        self.platform.boot()
        h = self.platform.health()
        assert len(h) == 1

    def test_summary(self):
        self.platform.register_service("svc1", ServiceCategory.COGNITIVE)
        self.platform.boot()
        s = self.platform.summary()
        assert s["services"]["total"] == 1
        assert s["services"]["by_category"]["cognitive"] == 1
        assert "telemetry" in s
        assert "resources" in s
        assert "metrics" in s
