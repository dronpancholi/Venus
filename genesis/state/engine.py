from __future__ import annotations

import threading
import time
from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any, Callable

from genesis.engineering import EngineeringObject, EngineeringObjectType, get_registry


@dataclass
class StateTransition:
    timestamp: float
    domain: str
    key: str
    old_value: Any = None
    new_value: Any = None
    event: str = ""


@dataclass
class StateEvent:
    event_type: str
    domain: str
    key: str
    value: Any = None
    timestamp: float = 0.0
    origin: str = ""


class EngineeringState:
    _instance: EngineeringState | None = None

    @classmethod
    def instance(cls) -> EngineeringState:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        if EngineeringState._instance is not None:
            raise RuntimeError("EngineeringState is a singleton. Use EngineeringState.instance()")
        EngineeringState._instance = self
        self._state: dict[str, dict[str, Any]] = {}
        self._transitions: list[StateTransition] = []
        self._max_transitions = 10000
        self._listeners: dict[str, list[Callable]] = {}
        self._lock = threading.RLock()
        self._state_obj: EngineeringObject | None = None
        self._kernel = None

    def set_kernel(self, kernel):
        self._kernel = kernel

    def boot(self):
        self._state_obj = EngineeringObject(
            object_type=EngineeringObjectType.SERVICE,
            name="EngineeringState",
            description="Unified canonical engineering state — all subsystems observe the same state",
            tags=["state", "canonical"],
            metadata={"domains": 0, "keys": 0, "transitions": 0},
        )
        get_registry().register(self._state_obj)

    def _ensure_domain(self, domain: str):
        if domain not in self._state:
            self._state[domain] = {}
            self._emit("state.domain.created", {"domain": domain})

    def get(self, domain: str, key: str, default: Any = None) -> Any:
        with self._lock:
            return self._state.get(domain, {}).get(key, default)

    def get_domain(self, domain: str) -> dict[str, Any]:
        with self._lock:
            return dict(self._state.get(domain, {}))

    def set(self, domain: str, key: str, value: Any, event: str = ""):
        with self._lock:
            self._ensure_domain(domain)
            old = self._state[domain].get(key)
            self._state[domain][key] = deepcopy(value)
            trans = StateTransition(
                timestamp=time.time(),
                domain=domain,
                key=key,
                old_value=old,
                new_value=value,
                event=event,
            )
            self._transitions.append(trans)
            if len(self._transitions) > self._max_transitions:
                self._transitions = self._transitions[-self._max_transitions:]
        self._notify(domain, key, value, old, event)
        self._emit(event or f"state.{domain}.{key}.changed", {
            "domain": domain, "key": key, "old": str(old)[:200] if old else None, "new": str(value)[:200],
        })

    def update_domain(self, domain: str, values: dict[str, Any], event_prefix: str = ""):
        for key, value in values.items():
            self.set(domain, key, value, event=f"{event_prefix}.{key}" if event_prefix else "")

    def observe(self, domain_pattern: str, callback: Callable[[str, str, Any, Any, str], None]):
        with self._lock:
            if domain_pattern not in self._listeners:
                self._listeners[domain_pattern] = []
            self._listeners[domain_pattern].append(callback)

    def _notify(self, domain: str, key: str, value: Any, old: Any, event: str):
        for pattern, callbacks in list(self._listeners.items()):
            if pattern == "*" or pattern == domain or domain.startswith(pattern.rstrip("*")):
                for cb in callbacks:
                    try:
                        cb(domain, key, value, old, event)
                    except Exception:
                        pass

    def _emit(self, event_type: str, payload: dict[str, Any]):
        if self._kernel:
            self._kernel.emit(event_type, payload, origin="state", tags=["state"])

    def transitions(self, domain: str | None = None, limit: int = 100) -> list[StateTransition]:
        with self._lock:
            if domain:
                return [t for t in self._transitions[-limit:] if t.domain == domain]
            return list(self._transitions[-limit:])

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            return {
                "domains": {d: dict(v) for d, v in self._state.items()},
                "total_domains": len(self._state),
                "total_keys": sum(len(v) for v in self._state.values()),
                "total_transitions": len(self._transitions),
            }

    def domains(self) -> list[str]:
        return list(self._state.keys())

    def replay(self, domain: str | None = None):
        return self.transitions(domain)

    def clear_domain(self, domain: str):
        with self._lock:
            self._state.pop(domain, None)
            self._emit("state.domain.cleared", {"domain": domain})

    def clear_all(self):
        with self._lock:
            self._state.clear()
            self._transitions.clear()
            self._emit("state.cleared", {})

    def has(self, domain: str, key: str) -> bool:
        with self._lock:
            return domain in self._state and key in self._state[domain]


def get_state() -> EngineeringState:
    return EngineeringState.instance()
