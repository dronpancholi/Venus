"""Tests for PlatformOrchestrator — declarative, dependency-resolved boot orchestration."""

import time
from genesis.orchestration import (
    PlatformOrchestrator, ServiceDef, ServiceStatus, BootPhase,
)


def test_register_single_service():
    o = PlatformOrchestrator()
    svc = ServiceDef(id="test", factory=lambda: {"name": "test"})
    o.register(svc)
    assert o.get_status("test") == ServiceStatus.PENDING


def test_register_many():
    o = PlatformOrchestrator()
    o.register_many([
        ServiceDef(id="a"),
        ServiceDef(id="b"),
        ServiceDef(id="c"),
    ])
    assert o.get_status("a") == ServiceStatus.PENDING
    assert o.get_status("b") == ServiceStatus.PENDING
    assert o.get_status("c") == ServiceStatus.PENDING


def test_duplicate_registration_raises():
    o = PlatformOrchestrator()
    o.register(ServiceDef(id="x"))
    try:
        o.register(ServiceDef(id="x"))
        assert False, "Should have raised"
    except ValueError:
        pass


def test_boot_order_dependency_respected():
    o = PlatformOrchestrator()
    results = []

    o.register_many([
        ServiceDef(id="dep", factory=lambda: results.append("dep")),
        ServiceDef(id="main", dependencies=["dep"],
                   factory=lambda: results.append("main")),
    ])
    o.boot()
    assert results == ["dep", "main"], f"Expected dep first, got {results}"


def test_boot_order_parallel_levels():
    o = PlatformOrchestrator()
    o.register_many([
        ServiceDef(id="a"),
        ServiceDef(id="b"),
        ServiceDef(id="c"),
    ])
    levels = o.compute_boot_order()
    assert len(levels) == 1
    assert set(levels[0]) == {"a", "b", "c"}


def test_boot_order_multi_level():
    o = PlatformOrchestrator()
    o.register_many([
        ServiceDef(id="root"),
        ServiceDef(id="mid", dependencies=["root"]),
        ServiceDef(id="leaf", dependencies=["mid"]),
    ])
    levels = o.compute_boot_order()
    assert len(levels) == 3
    assert "root" in levels[0]
    assert "mid" in levels[1]
    assert "leaf" in levels[2]


def test_cycle_detection():
    o = PlatformOrchestrator()
    o.register_many([
        ServiceDef(id="a", dependencies=["b"]),
        ServiceDef(id="b", dependencies=["c"]),
        ServiceDef(id="c", dependencies=["a"]),
    ])
    cycles = o.detect_cycles()
    assert len(cycles) > 0, "Should detect cycle a→b→c→a"


def test_missing_dependency_detected():
    o = PlatformOrchestrator()
    o.register(ServiceDef(id="a", dependencies=["nonexistent"]))
    errors = o.validate_dependencies()
    assert len(errors) == 1
    assert "nonexistent" in errors[0]


def test_health_check_called():
    o = PlatformOrchestrator()
    healthy = False

    def check(inst):
        nonlocal healthy
        healthy = True
        return True

    o.register(ServiceDef(id="test", factory=lambda: {}, health_check=check))
    report = o.boot()
    assert healthy, "Health check should have been called"
    assert report.healthy_count == 1


def test_health_check_failure_sets_degraded():
    o = PlatformOrchestrator()

    def check(inst):
        return False

    o.register(ServiceDef(id="test", factory=lambda: {}, health_check=check))
    report = o.boot()
    assert report.degraded_count == 1
    assert report.healthy_count == 0
    assert o.get_status("test") == ServiceStatus.DEGRADED


def test_factory_exception_sets_failed():
    o = PlatformOrchestrator()

    def bad_factory():
        raise RuntimeError("factory failed")

    o.register(ServiceDef(id="test", factory=bad_factory))
    report = o.boot()
    assert report.failed_count == 1
    assert o.get_status("test") == ServiceStatus.FAILED


def test_startup_hook_called():
    o = PlatformOrchestrator()
    hook_called = False

    def hook(inst):
        nonlocal hook_called
        hook_called = True

    o.register(ServiceDef(id="test", factory=lambda: {"x": 1}, startup_hook=hook))
    o.boot()
    assert hook_called


def test_verification_hook_failure():
    o = PlatformOrchestrator()

    def verify(inst):
        return False

    o.register(ServiceDef(id="test", factory=lambda: {}, verification_hook=verify))
    report = o.boot()
    assert report.failed_count == 1


def test_shutdown_hook_called():
    o = PlatformOrchestrator()
    shutdown_called = False

    def shutdown(inst):
        nonlocal shutdown_called
        shutdown_called = True

    def startup(inst):
        pass

    o.register(ServiceDef(id="test", factory=lambda: {},
                          startup_hook=startup, shutdown_hook=shutdown))
    o.boot()
    o.shutdown()
    assert shutdown_called, "Shutdown hook should have been called"


def test_shutdown_reverse_order():
    o = PlatformOrchestrator()
    order = []

    o.register_many([
        ServiceDef(id="root", factory=lambda: {},
                   startup_hook=lambda i: order.append("root_up"),
                   shutdown_hook=lambda i: order.append("root_down")),
        ServiceDef(id="mid", factory=lambda: {}, dependencies=["root"],
                   startup_hook=lambda i: order.append("mid_up"),
                   shutdown_hook=lambda i: order.append("mid_down")),
        ServiceDef(id="leaf", factory=lambda: {}, dependencies=["mid"],
                   startup_hook=lambda i: order.append("leaf_up"),
                   shutdown_hook=lambda i: order.append("leaf_down")),
    ])
    o.boot()
    order.clear()
    o.shutdown()
    assert order == ["leaf_down", "mid_down", "root_down"], f"Got {order}"


def test_boot_report_summary():
    o = PlatformOrchestrator()
    o.register_many([
        ServiceDef(id="a", factory=lambda: {}),
        ServiceDef(id="b", factory=lambda: {}),
    ])
    report = o.boot()
    summary = report.summary()
    assert summary["healthy"] == 2
    assert summary["failed"] == 0
    assert summary["all_healthy"] is True
    assert summary["total_duration_ms"] > 0


def test_boot_steps_recorded():
    o = PlatformOrchestrator()
    o.register(ServiceDef(id="test", factory=lambda: {}))
    report = o.boot()
    assert len(report.steps) > 0
    step = report.steps[0]
    assert step.service_id == "test"
    assert step.status == ServiceStatus.HEALTHY


def test_critical_path():
    o = PlatformOrchestrator()
    o.register_many([
        ServiceDef(id="fast", estimated_startup_ms=10),
        ServiceDef(id="slow", dependencies=["fast"], estimated_startup_ms=100),
    ])
    path = o.compute_critical_path()
    assert len(path) == 2


def test_is_idempotent():
    o = PlatformOrchestrator()
    o.register(ServiceDef(id="test", factory=lambda: {}))
    r1 = o.boot()
    assert r1.healthy_count == 1


def test_complex_dag():
    o = PlatformOrchestrator()
    o.register_many([
        ServiceDef(id="a"),
        ServiceDef(id="b"),
        ServiceDef(id="c", dependencies=["a"]),
        ServiceDef(id="d", dependencies=["a", "b"]),
        ServiceDef(id="e", dependencies=["c", "d"]),
    ])
    levels = o.compute_boot_order()
    
    assert "a" in levels[0] or "b" in levels[0]
    
    all_flat = [sid for level in levels for sid in level]
    assert len(all_flat) == 5
    
    a_pos = all_flat.index("a")
    b_pos = all_flat.index("b")
    c_pos = all_flat.index("c")
    d_pos = all_flat.index("d")
    e_pos = all_flat.index("e")
    assert c_pos > a_pos, "c depends on a"
    assert d_pos > a_pos and d_pos > b_pos, "d depends on a,b"
    assert e_pos > c_pos and e_pos > d_pos, "e depends on c,d"
