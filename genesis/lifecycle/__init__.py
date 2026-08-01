"""
Platform Lifecycle Manager — unified lifecycle for all Genesis subsystems.

Not a new engine. A thin coordinator that wraps existing lifecycle methods
(boot, shutdown, etc.) and adds pause/resume/recover/upgrade/restart.

Every lifecycle-aware subsystem participates:
  init → start → ready ↔ pause ↔ resume
                    ↓
                stop → shutdown → recover → restart
                    ↓
               upgrade → restart
"""

from __future__ import annotations

import signal
import sys
import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable


class LifecycleState(Enum):
    UNINITIALIZED = "uninitialized"
    INIT = "init"
    STARTING = "starting"
    READY = "ready"
    PAUSING = "pausing"
    PAUSED = "paused"
    RESUMING = "resuming"
    STOPPING = "stopping"
    STOPPED = "stopped"
    SHUTTING_DOWN = "shutting_down"
    SHUTDOWN = "shutdown"
    RECOVERING = "recovering"
    UPGRADING = "upgrading"
    RESTARTING = "restarting"
    FAILED = "failed"


@dataclass
class SubsystemLifecycle:
    name: str
    state: LifecycleState = LifecycleState.UNINITIALIZED
    started_at: float = 0.0
    stopped_at: float = 0.0
    error: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def uptime(self) -> float:
        if self.started_at and self.state in (LifecycleState.READY, LifecycleState.PAUSED):
            return time.time() - self.started_at
        return 0.0


@dataclass
class LifecycleTransition:
    from_state: LifecycleState
    to_state: LifecycleState
    timestamp: float = 0.0
    duration_ms: float = 0.0

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = time.time()


class PlatformLifecycle:
    """Unified platform lifecycle coordinator.

    Wraps FabricKernel, Platform, app_platform, watchers, etc.
    Does NOT duplicate boot logic — delegates to existing lifecycle methods.
    """

    def __init__(self, kernel: Any = None):
        self._kernel = kernel
        self._state = LifecycleState.UNINITIALIZED
        self._subsystems: dict[str, SubsystemLifecycle] = {}
        self._transitions: list[LifecycleTransition] = []
        self._hooks: dict[LifecycleState, list[Callable]] = {}
        self._lock = threading.RLock()
        self._started_at: float = 0.0
        self._signal_handlers: list[int] = []

    # ── subsystem registration ──────────────────────────────────────

    def register(self, name: str, metadata: dict[str, Any] | None = None) -> SubsystemLifecycle:
        with self._lock:
            sl = SubsystemLifecycle(name=name, state=LifecycleState.UNINITIALIZED, metadata=metadata or {})
            self._subsystems[name] = sl
            return sl

    def get(self, name: str) -> SubsystemLifecycle | None:
        return self._subsystems.get(name)

    @property
    def subsystems(self) -> dict[str, SubsystemLifecycle]:
        return dict(self._subsystems)

    @property
    def summary(self) -> dict[str, Any]:
        by_state: dict[str, int] = {}
        for s in self._subsystems.values():
            by_state[s.state.value] = by_state.get(s.state.value, 0) + 1
        return {
            "platform_state": self._state.value,
            "subsystems": len(self._subsystems),
            "by_state": by_state,
            "transitions": len(self._transitions),
            "uptime_seconds": time.time() - self._started_at if self._started_at else 0.0,
        }

    def on_transition(self, state: LifecycleState, handler: Callable):
        self._hooks.setdefault(state, []).append(handler)

    # ── lifecycle transitions ───────────────────────────────────────

    def _transition(self, target: LifecycleState) -> list[str]:
        results: list[str] = []
        for name, sl in list(self._subsystems.items()):
            try:
                self._transition_subsystem(name, target)
                results.append(f"{name}: OK")
            except Exception as e:
                sl.state = LifecycleState.FAILED
                sl.error = str(e)
                results.append(f"{name}: FAILED ({e})")
        return results

    def _transition_subsystem(self, name: str, target: LifecycleState):
        sl = self._subsystems.get(name)
        if not sl:
            return
        handlers = self._hooks.get(target, [])
        for h in handlers:
            h(sl)
        if target == LifecycleState.INIT:
            if hasattr(sl, '_init'):
                sl._init()
        elif target == LifecycleState.STARTING:
            if hasattr(sl, '_start'):
                sl._start()
        elif target == LifecycleState.STOPPING:
            if hasattr(sl, '_stop'):
                sl._stop()
        elif target == LifecycleState.SHUTTING_DOWN:
            if hasattr(sl, '_shutdown'):
                sl._shutdown()
        sl.state = target

    def _record(self, from_state: LifecycleState, to_state: LifecycleState):
        t = LifecycleTransition(from_state=from_state, to_state=to_state)
        self._transitions.append(t)
        self._state = to_state
        if self._kernel:
            try:
                self._kernel.emit(
                    f"lifecycle.{to_state.value}",
                    {"from": from_state.value, "to": to_state.value, "uptime": time.time() - self._started_at},
                    origin="lifecycle",
                    tags=["lifecycle", to_state.value],
                )
            except Exception:
                pass

    # ── public lifecycle API ─────────────────────────────────────────

    def boot(self):
        """Initialize and start all registered subsystems."""
        self._started_at = time.time()
        self._record(LifecycleState.UNINITIALIZED, LifecycleState.INIT)
        results = self._transition(LifecycleState.INIT)
        self._record(LifecycleState.INIT, LifecycleState.STARTING)
        results += self._transition(LifecycleState.STARTING)
        self._record(LifecycleState.STARTING, LifecycleState.READY)
        self._install_signal_handlers()
        return results

    def pause(self):
        self._record(LifecycleState.READY, LifecycleState.PAUSING)
        results = self._transition(LifecycleState.PAUSING)
        for sl in self._subsystems.values():
            if sl.state == LifecycleState.READY:
                sl.state = LifecycleState.PAUSED
        self._record(LifecycleState.PAUSING, LifecycleState.PAUSED)
        return results

    def resume(self):
        self._record(LifecycleState.PAUSED, LifecycleState.RESUMING)
        results = self._transition(LifecycleState.RESUMING)
        for sl in self._subsystems.values():
            if sl.state == LifecycleState.PAUSED:
                sl.state = LifecycleState.READY
        self._record(LifecycleState.RESUMING, LifecycleState.READY)
        return results

    def stop(self):
        self._record(LifecycleState.READY if self._state == LifecycleState.READY else self._state,
                      LifecycleState.STOPPING)
        results = self._transition(LifecycleState.STOPPING)
        for sl in self._subsystems.values():
            if sl.state in (LifecycleState.READY, LifecycleState.PAUSED):
                sl.state = LifecycleState.STOPPED
        self._record(LifecycleState.STOPPING, LifecycleState.STOPPED)
        return results

    def shutdown(self):
        self._record(self._state, LifecycleState.SHUTTING_DOWN)
        results = self._transition(LifecycleState.SHUTTING_DOWN)
        for sl in self._subsystems.values():
            sl.state = LifecycleState.SHUTDOWN
        self._record(LifecycleState.SHUTTING_DOWN, LifecycleState.SHUTDOWN)

    def recover(self):
        self._record(LifecycleState.FAILED if self._state == LifecycleState.FAILED else self._state,
                      LifecycleState.RECOVERING)
        results = self._transition(LifecycleState.RECOVERING)
        for sl in self._subsystems.values():
            if sl.error:
                sl.error = ""
                sl.state = LifecycleState.STARTING
        self.boot()
        return results

    def upgrade(self):
        self._record(self._state, LifecycleState.UPGRADING)
        results = self._transition(LifecycleState.UPGRADING)
        self._record(LifecycleState.UPGRADING, LifecycleState.READY)
        return results

    def restart(self):
        self.shutdown()
        self._record(LifecycleState.SHUTDOWN, LifecycleState.RESTARTING)
        for sl in self._subsystems.values():
            sl.state = LifecycleState.UNINITIALIZED
            sl.error = ""
        self._started_at = 0.0
        self.boot()

    # ── signal handling ─────────────────────────────────────────────

    def _install_signal_handlers(self):
        for sig in (signal.SIGINT, signal.SIGTERM):
            try:
                handler = signal.signal(sig, self._handle_signal)
                self._signal_handlers.append(sig)
            except (ValueError, RuntimeError):
                pass

    def _handle_signal(self, signum: int, frame):
        sig_name = signal.Signals(signum).name if hasattr(signal, 'Signals') else str(signum)
        print(f"\nReceived {sig_name}. Shutting down...", file=sys.stderr)
        self.shutdown()
        sys.exit(0)


# Convenience factory — wraps a FabricKernel into lifecycle
def lifecycle_for_kernel(kernel) -> PlatformLifecycle:
    pl = PlatformLifecycle(kernel=kernel)
    pl.register("kernel", {"version": getattr(kernel, 'version', 'unknown')})

    lazy_subsystems = [
        "agent_runtime", "task_graph", "execution_engine", "task_executor",
        "state_engine", "nervous_system", "health_engine", "observability",
        "observatory", "explorer", "planner", "multi_project",
        "live_architecture", "visual_reasoning", "command_center",
        "knowledge_organizer", "memory_v2", "context_engine",
        "insight_engine", "decision_intelligence", "proactive_copilot",
        "ai", "automation", "workflow_engine", "playbooks", "agentos",
        "app_platform", "sdk",
    ]
    for name in lazy_subsystems:
        pl.register(name)

    pl.on_transition(LifecycleState.STARTING, lambda sl: _boot_subsystem(kernel, sl))
    return pl


def _boot_subsystem(kernel, sl: SubsystemLifecycle):
    try:
        prop = getattr(kernel, sl.name, None)
        if prop and hasattr(prop, 'boot'):
            prop.boot()
            sl.started_at = time.time()
            sl.state = LifecycleState.READY
    except Exception as e:
        sl.state = LifecycleState.FAILED
        sl.error = str(e)
