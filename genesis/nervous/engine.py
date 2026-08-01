from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field
from typing import Any, Callable

from genesis.engineering import EngineeringObject, EngineeringObjectType, get_registry
from genesis.state import get_state


@dataclass
class Signal:
    source: str
    domain: str
    key: str
    value: Any = None
    event: str = ""
    timestamp: float = 0.0
    priority: int = 0


class EngineeringNervousSystem:
    def __init__(self, kernel=None):
        self._kernel = kernel
        self._registry = get_registry()
        self._state = get_state()
        self._listeners: dict[str, list[Callable]] = {}
        self._lock = threading.RLock()
        self._signal_history: list[Signal] = []
        self._max_history = 5000
        self._ns_obj: EngineeringObject | None = None
        self._running = False
        self._booted = False

    def boot(self):
        if self._booted:
            return
        self._booted = True
        self._ns_obj = EngineeringObject(
            object_type=EngineeringObjectType.SERVICE,
            name="EngineeringNervousSystem",
            description="Continuous engineering signal propagation — every subsystem emits state signals",
            tags=["nervous", "signals", "propagation"],
        )
        self._registry.register(self._ns_obj)
        self._state.set("nervous", "status", "booted")
        self._state.set("nervous", "signals_processed", 0)
        self._wire_subsystem_signals()
        self._running = True

    def _wire_subsystem_signals(self):
        state = self._state
        state.observe("*", self._on_state_change)

    def _on_state_change(self, domain: str, key: str, value: Any, old: Any, event: str):
        for pattern, callbacks in list(self._listeners.items()):
            signal_key = f"{domain}.{key}"
            if pattern == "*" or pattern == signal_key or signal_key.startswith(pattern.rstrip("*")):
                signal = Signal(
                    source=domain,
                    domain=domain,
                    key=key,
                    value=value,
                    event=event,
                    timestamp=time.time(),
                )
                self._signal_history.append(signal)
                if len(self._signal_history) > self._max_history:
                    self._signal_history = self._signal_history[-self._max_history:]
                self._state.set("nervous", "signals_processed",
                                self._state.get("nervous", "signals_processed", 0) + 1)
                for cb in callbacks:
                    try:
                        cb(signal)
                    except Exception:
                        pass

    def on_signal(self, pattern: str, callback: Callable[[Signal], None]):
        with self._lock:
            if pattern not in self._listeners:
                self._listeners[pattern] = []
            self._listeners[pattern].append(callback)

    def emit_signal(self, source: str, domain: str, key: str, value: Any = None, event: str = ""):
        self._state.set(domain, key, value, event or f"signal.{domain}.{key}")
        signal = Signal(
            source=source, domain=domain, key=key,
            value=value, event=event or f"signal.{domain}.{key}",
            timestamp=time.time(),
        )
        self._signal_history.append(signal)
        if len(self._signal_history) > self._max_history:
            self._signal_history = self._signal_history[-self._max_history:]
        return signal

    def signal_history(self, domain: str | None = None, limit: int = 50) -> list[Signal]:
        if domain:
            return [s for s in self._signal_history[-limit:] if s.domain == domain]
        return list(self._signal_history[-limit:])

    def stats(self) -> dict[str, Any]:
        return {
            "running": self._running,
            "signals_processed": self._state.get("nervous", "signals_processed", 0),
            "signal_history": len(self._signal_history),
            "listeners": sum(len(v) for v in self._listeners.values()),
        }
