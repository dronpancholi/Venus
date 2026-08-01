"""
Tests for GENESIS-VIII Program 7: Universal Engineering Operating System.
"""

import pytest
from genesis.engineering_os import (
    Service, ServiceStatus, ServiceRole, ServiceManifest,
    ServiceRegistry, ServiceScheduler, TelemetryCollector,
    CheckpointManager, EngineeringOS,
)


class TestServiceRegistry:
    def test_register(self):
        reg = ServiceRegistry()
        svc = reg.register(ServiceManifest(name="brain", role=ServiceRole.COGNITIVE))
        assert svc.name == "brain"
        assert reg.get(svc.id) is not None

    def test_find(self):
        reg = ServiceRegistry()
        reg.register(ServiceManifest(name="s1", role=ServiceRole.CORE))
        reg.register(ServiceManifest(name="s2", role=ServiceRole.MEMORY))
        results = reg.find(role=ServiceRole.MEMORY)
        assert len(results) == 1

    def test_dependency_graph(self):
        reg = ServiceRegistry()
        reg.register(ServiceManifest(name="a", dependencies=["b"]))
        reg.register(ServiceManifest(name="b", dependencies=[]))
        dg = reg.dependency_graph()
        assert len(dg) == 2


class TestServiceScheduler:
    def test_compute_start_order(self):
        reg = ServiceRegistry()
        s1 = reg.register(ServiceManifest(name="core", role=ServiceRole.CORE))
        s2 = reg.register(ServiceManifest(name="memory", role=ServiceRole.MEMORY,
                                           dependencies=[s1.id]))
        s3 = reg.register(ServiceManifest(name="brain", role=ServiceRole.COGNITIVE,
                                           dependencies=[s2.id]))
        sched = ServiceScheduler(reg)
        order = sched.compute_start_order()
        assert order.index(s1.id) < order.index(s2.id) < order.index(s3.id)

    def test_start_all(self):
        reg = ServiceRegistry()
        reg.register(ServiceManifest(name="core"))
        sched = ServiceScheduler(reg)
        started = sched.start_all()
        assert len(started) == 1
        assert started[0].status == ServiceStatus.RUNNING

    def test_health_check(self):
        reg = ServiceRegistry()
        reg.register(ServiceManifest(name="core"))
        sched = ServiceScheduler(reg)
        sched.start_all()
        health = sched.health_check()
        assert health["healthy"] >= 1


class TestTelemetryCollector:
    def test_record(self):
        tc = TelemetryCollector()
        tc.record("cpu", 0.5)
        tc.record("cpu", 0.6)
        s = tc.summary()
        assert s["cpu"]["count"] == 2
        assert s["cpu"]["avg"] == 0.55

    def test_register_collector(self):
        tc = TelemetryCollector()
        tc.register_collector("test", lambda: {"value": 42})
        results = tc.collect_all()
        assert results["test"]["value"] == 42


class TestCheckpointManager:
    def test_save_and_restore(self):
        cm = CheckpointManager()
        cpid = cm.save("test", {"key": "value"})
        state = cm.restore(cpid)
        assert state["key"] == "value"

    def test_list_checkpoints(self):
        cm = CheckpointManager()
        cm.save("a", {})
        cm.save("b", {})
        assert len(cm.list_checkpoints()) == 2


class TestEngineeringOS:
    def test_boot(self):
        os = EngineeringOS()
        os.register_service(ServiceManifest(name="core"))
        count = os.boot()
        assert count >= 1
        assert os._booted

    def test_shutdown(self):
        os = EngineeringOS()
        os.register_service(ServiceManifest(name="core"))
        os.boot()
        os.shutdown()
        assert not os._booted

    def test_health(self):
        os = EngineeringOS()
        os.register_service(ServiceManifest(name="core"))
        os.boot()
        h = os.health()
        assert h["healthy"] >= 1

    def test_system_graph(self):
        os = EngineeringOS()
        os.register_service(ServiceManifest(name="core"))
        sg = os.system_graph()
        assert "services" in sg
        assert "dependency_graph" in sg

    def test_summary(self):
        os = EngineeringOS()
        os.register_service(ServiceManifest(name="core"))
        os.boot()
        s = os.summary()
        assert s["booted"] is True
        assert s["services"]["total"] == 1
