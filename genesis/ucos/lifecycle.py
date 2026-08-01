"""
UCOS: CapabilityLifecycleManager — State machine for capability lifecycle.
"""

from __future__ import annotations

import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any

from genesis.ucos.capability import Capability, CapabilityState


CAPABILITY_STATE_TRANSITIONS: dict[CapabilityState, set[CapabilityState]] = {
    CapabilityState.DORMANT: {CapabilityState.REGISTERED},
    CapabilityState.REGISTERED: {CapabilityState.VERIFIED, CapabilityState.DORMANT, CapabilityState.OBSOLETE},
    CapabilityState.VERIFIED: {CapabilityState.READY, CapabilityState.REGISTERED, CapabilityState.FAILED},
    CapabilityState.READY: {CapabilityState.RUNNING, CapabilityState.STOPPED, CapabilityState.DEGRADED},
    CapabilityState.RUNNING: {CapabilityState.DEGRADED, CapabilityState.STOPPED, CapabilityState.FAILED, CapabilityState.READY},
    CapabilityState.DEGRADED: {CapabilityState.RUNNING, CapabilityState.STOPPED, CapabilityState.FAILED, CapabilityState.READY},
    CapabilityState.FAILED: {CapabilityState.READY, CapabilityState.STOPPED, CapabilityState.DORMANT},
    CapabilityState.STOPPED: {CapabilityState.READY, CapabilityState.DORMANT, CapabilityState.OBSOLETE},
    CapabilityState.OBSOLETE: set(),
}


@dataclass
class LifecycleEvent:
    capability_id: str = ""
    from_state: str = ""
    to_state: str = ""
    timestamp: float = 0.0
    reason: str = ""
    actor: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = time.time()


class CapabilityLifecycleManager:
    """Manages state transitions with validation and event logging."""

    def __init__(self, registry):
        self._registry = registry
        self._history: dict[str, list[LifecycleEvent]] = defaultdict(list)
        self._hooks: dict[str, list[callable]] = defaultdict(list)

    def can_transition(self, capability_id: str, target: CapabilityState) -> bool:
        cap = self._registry.get(capability_id)
        if not cap:
            return False
        allowed = CAPABILITY_STATE_TRANSITIONS.get(cap.state, set())
        return target in allowed

    def transition(self, capability_id: str, target: CapabilityState,
                   reason: str = "", actor: str = "") -> bool:
        cap = self._registry.get(capability_id)
        if not cap:
            return False
        if not self.can_transition(capability_id, target):
            return False
        from_state = cap.state
        cap.state = target
        cap.definition.touch()
        evt = LifecycleEvent(
            capability_id=capability_id,
            from_state=from_state.value,
            to_state=target.value,
            reason=reason,
            actor=actor,
        )
        self._history[capability_id].append(evt)
        for hook in self._hooks.get(target.value, []):
            try:
                hook(cap, evt)
            except Exception:
                pass
        return True

    def on_transition(self, state: str, hook: callable):
        self._hooks[state].append(hook)

    def verify(self, capability_id: str) -> bool:
        return self.transition(capability_id, CapabilityState.VERIFIED,
                               reason="verification completed")

    def ready(self, capability_id: str) -> bool:
        return self.transition(capability_id, CapabilityState.READY,
                               reason="all dependencies ready")

    def start(self, capability_id: str) -> bool:
        return self.transition(capability_id, CapabilityState.RUNNING,
                               reason="execution started")

    def stop(self, capability_id: str) -> bool:
        return self.transition(capability_id, CapabilityState.STOPPED,
                               reason="execution stopped")

    def fail(self, capability_id: str, reason: str = "") -> bool:
        return self.transition(capability_id, CapabilityState.FAILED,
                               reason=reason or "execution failed")

    def degrade(self, capability_id: str, reason: str = "") -> bool:
        return self.transition(capability_id, CapabilityState.DEGRADED,
                               reason=reason or "degraded")

    def recover(self, capability_id: str) -> bool:
        cap = self._registry.get(capability_id)
        if not cap:
            return False
        if cap.state in (CapabilityState.FAILED, CapabilityState.DEGRADED):
            return self.transition(capability_id, CapabilityState.READY,
                                   reason="recovery")
        return False

    def get_history(self, capability_id: str) -> list[LifecycleEvent]:
        return list(self._history.get(capability_id, []))

    def recent_events(self, n: int = 100) -> list[LifecycleEvent]:
        all_events = []
        for events in self._history.values():
            all_events.extend(events)
        all_events.sort(key=lambda e: e.timestamp, reverse=True)
        return all_events[:n]

    def failed_capabilities(self) -> list[Capability]:
        return [c for c in self._registry.all if c.state == CapabilityState.FAILED]

    def running_capabilities(self) -> list[Capability]:
        return [c for c in self._registry.all if c.state == CapabilityState.RUNNING]
