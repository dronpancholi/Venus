"""Tests for Platform Lifecycle Manager (Mission 175)."""

import time
from unittest.mock import MagicMock

from genesis.lifecycle import (
    PlatformLifecycle,
    LifecycleState,
    SubsystemLifecycle,
    LifecycleTransition,
)


class TestPlatformLifecycle:
    def test_initial_state(self):
        pl = PlatformLifecycle()
        assert pl._state == LifecycleState.UNINITIALIZED
        assert pl.summary["subsystems"] == 0

    def test_register_subsystem(self):
        pl = PlatformLifecycle()
        sl = pl.register("test_system", {"version": "1.0"})
        assert sl.name == "test_system"
        assert sl.state == LifecycleState.UNINITIALIZED
        assert sl.metadata["version"] == "1.0"
        assert pl.get("test_system") is sl

    def test_boot_transitions(self):
        pl = PlatformLifecycle()
        pl.register("sys_a")
        pl.register("sys_b")
        results = pl.boot()

        assert pl._state == LifecycleState.READY
        assert len(pl._transitions) == 3  # init → starting → ready
        assert pl._started_at > 0

    def test_pause_resume(self):
        pl = PlatformLifecycle()
        pl.register("sys_a")
        pl.boot()

        pause_results = pl.pause()
        assert pl._state == LifecycleState.PAUSED

        resume_results = pl.resume()
        assert pl._state == LifecycleState.READY

    def test_stop(self):
        pl = PlatformLifecycle()
        pl.register("sys_a")
        pl.boot()
        stop_results = pl.stop()
        assert pl._state == LifecycleState.STOPPED

    def test_shutdown(self):
        pl = PlatformLifecycle()
        pl.register("sys_a")
        pl.boot()
        pl.shutdown()
        assert pl._state == LifecycleState.SHUTDOWN
        assert pl.get("sys_a").state == LifecycleState.SHUTDOWN

    def test_restart(self):
        pl = PlatformLifecycle()
        pl.register("sys_a")
        pl.boot()
        pl.restart()
        assert pl._state == LifecycleState.READY or pl._state == LifecycleState.STARTING

    def test_recover(self):
        pl = PlatformLifecycle()
        sl = pl.register("sys_a")
        sl.state = LifecycleState.FAILED
        sl.error = "something broke"
        pl._state = LifecycleState.FAILED
        pl.recover()
        assert pl._state == LifecycleState.READY

    def test_upgrade(self):
        pl = PlatformLifecycle()
        pl.register("sys_a")
        pl.boot()
        pl.upgrade()
        assert pl._state == LifecycleState.READY

    def test_transition_hooks(self):
        pl = PlatformLifecycle()
        calls = []
        pl.on_transition(LifecycleState.STARTING, lambda sl: calls.append(sl.name))
        pl.register("sys_a")
        pl.boot()
        assert len(calls) > 0

    def test_kernel_integration(self):
        kernel = MagicMock()
        pl = PlatformLifecycle(kernel=kernel)
        pl.register("sys_a")
        pl.boot()
        assert kernel.emit.called

    def test_subsystem_summary(self):
        pl = PlatformLifecycle()
        pl.register("sys_a")
        pl.register("sys_b")
        s = pl.summary
        assert s["subsystems"] == 2
        assert "by_state" in s

    def test_subsystem_uptime(self):
        sl = SubsystemLifecycle(name="test", state=LifecycleState.READY, started_at=time.time() - 10)
        assert sl.uptime >= 9.9
        sl.state = LifecycleState.SHUTDOWN
        assert sl.uptime == 0.0

    def test_transition_record(self):
        t = LifecycleTransition(
            from_state=LifecycleState.UNINITIALIZED,
            to_state=LifecycleState.INIT,
            duration_ms=5.0,
        )
        assert t.from_state == LifecycleState.UNINITIALIZED
        assert t.to_state == LifecycleState.INIT
        assert t.timestamp > 0
