"""Tests for UCOS CapabilityRuntime."""

import pytest
from genesis.ucos.capability import CapabilityDefinition, CapabilityState
from genesis.ucos.registry import CapabilityRegistry
from genesis.ucos.runtime import CapabilityRuntime


@pytest.fixture
def runtime():
    reg = CapabilityRegistry()
    reg.register(CapabilityDefinition(id="run_a", name="Runnable"),
                  implementation=lambda: 42)
    reg.set_state("run_a", CapabilityState.READY)
    r = CapabilityRuntime(reg)
    return reg, r


def test_execute(runtime):
    reg, r = runtime
    ctx = r.execute("run_a")
    assert ctx.capability_id == "run_a"
    assert ctx.success
    assert ctx.duration_ms >= 0
    assert ctx.outputs == {"result": 42}


def test_execute_missing(runtime):
    reg, r = runtime
    ctx = r.execute("missing")
    assert not ctx.success
    assert "not found" in ctx.error.lower()


def test_execute_plan(runtime):
    reg, r = runtime
    reg.register(CapabilityDefinition(id="run_b", name="Runnable2"),
                  implementation=lambda: "ok")
    reg.set_state("run_b", CapabilityState.READY)
    results = r.execute_plan(["run_a", "run_b"])
    assert len(results) == 2
    assert all(ctx.success for ctx in results)


def test_failed_executions(runtime):
    reg, r = runtime
    r.execute("run_a")
    r.execute("missing")
    failed = r.failed_executions()
    assert len(failed) == 1


def test_success_rate(runtime):
    reg, r = runtime
    r.execute("run_a")
    r.execute("run_a")
    r.execute("missing")
    assert r.success_rate() == 2.0 / 3.0


def test_avg_duration_ms(runtime):
    reg, r = runtime
    r.execute("run_a")
    r.execute("run_a")
    assert r.avg_duration_ms() >= 0


def test_recent(runtime):
    reg, r = runtime
    r.execute("run_a")
    r.execute("missing")
    recent = r.recent(n=1)
    assert len(recent) == 1


def test_summary(runtime):
    reg, r = runtime
    r.execute("run_a")
    summary = r.summary()
    assert summary["total_executions"] >= 1
    assert "success_rate" in summary


def test_context_tracking(runtime):
    reg, r = runtime
    ctx = r.execute("run_a")
    retrieved = r.get_context(ctx.id)
    assert retrieved is not None
    assert retrieved.id == ctx.id


def test_execution_count(runtime):
    reg, r = runtime
    r.execute("run_a")
    r.execute("run_a")
    cap = reg.get("run_a")
    assert cap.execution_count == 2


def test_middleware(runtime):
    reg, r = runtime
    calls = []
    def mw(phase, cap, ctx):
        calls.append((phase, cap.id))
    r.use(mw)
    r.execute("run_a")
    assert len(calls) >= 1
