from __future__ import annotations

import time
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable

from genesis.capability.registry import CapabilityDefinition, CapabilityRegistry, capability_registry
from genesis.events.bus import EventBus
from genesis.utils.identity import generate_id


class CapabilityState(Enum):
    REGISTERED = "registered"
    ACTIVE = "active"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"
    DEPRECATED = "deprecated"


@dataclass
class ServiceCapability:
    id: str = ""
    service_id: str = ""
    capability_name: str = ""
    version: str = "1.0.0"
    description: str = ""
    interfaces: list[dict[str, Any]] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    state: CapabilityState = CapabilityState.REGISTERED
    registered_at: float = 0.0
    health_check: Callable[[], bool] | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.id:
            self.id = generate_id("cap", 12)
        if not self.registered_at:
            self.registered_at = time.time()


@dataclass
class ResolutionResult:
    capability_name: str
    resolved: bool
    service_id: str | None = None
    state: CapabilityState | None = None
    error: str | None = None
    dependency_chain: list[str] = field(default_factory=list)


class EngineCapabilityRegistry:
    def __init__(self, registry: CapabilityRegistry | None = None,
                 event_bus: EventBus | None = None):
        self._inner = registry or capability_registry
        self._bus = event_bus
        self._capabilities: dict[str, ServiceCapability] = {}
        self._by_name: dict[str, list[str]] = defaultdict(list)
        self._by_service: dict[str, list[str]] = defaultdict(list)
        self._events: list[dict[str, Any]] = []
        self._on_register: list[Callable] = []
        self._on_unregister: list[Callable] = []
        self._on_state_change: list[Callable] = []

    def on_register(self, callback: Callable):
        self._on_register.append(callback)

    def on_unregister(self, callback: Callable):
        self._on_unregister.append(callback)

    def on_state_change(self, callback: Callable):
        self._on_state_change.append(callback)

    def _emit(self, event_type: str, data: dict[str, Any]):
        record = {"type": event_type, "data": data, "timestamp": time.time()}
        self._events.append(record)
        if self._bus:
            self._bus.emit(f"capability.{event_type}", data)

    def register(self, svc_cap: ServiceCapability):
        if svc_cap.capability_name in self._by_name:
            existing = self._capabilities.get(self._by_name[svc_cap.capability_name][0])
            if existing and existing.state != CapabilityState.DEPRECATED:
                pass
        self._capabilities[svc_cap.id] = svc_cap
        self._by_name[svc_cap.capability_name].append(svc_cap.id)
        self._by_service[svc_cap.service_id].append(svc_cap.id)
        inner_def = CapabilityDefinition(
            name=svc_cap.capability_name,
            description=svc_cap.description,
            version=svc_cap.version,
            owner=svc_cap.service_id,
        )
        self._inner.register(inner_def)
        self._emit("registered", {
            "id": svc_cap.id,
            "capability_name": svc_cap.capability_name,
            "service_id": svc_cap.service_id,
            "version": svc_cap.version,
        })
        for cb in self._on_register:
            try:
                cb(svc_cap)
            except Exception:
                pass

    def unregister(self, capability_id: str) -> bool:
        cap = self._capabilities.pop(capability_id, None)
        if cap is None:
            return False
        name_list = self._by_name.get(cap.capability_name, [])
        if capability_id in name_list:
            name_list.remove(capability_id)
        svc_list = self._by_service.get(cap.service_id, [])
        if capability_id in svc_list:
            svc_list.remove(capability_id)
        self._emit("unregistered", {
            "id": capability_id,
            "capability_name": cap.capability_name,
            "service_id": cap.service_id,
        })
        for cb in self._on_unregister:
            try:
                cb(cap)
            except Exception:
                pass
        return True

    def set_state(self, capability_id: str, state: CapabilityState):
        cap = self._capabilities.get(capability_id)
        if cap is None:
            return
        old = cap.state
        cap.state = state
        self._emit("state_changed", {
            "id": capability_id,
            "capability_name": cap.capability_name,
            "old_state": old.value,
            "new_state": state.value,
        })
        for cb in self._on_state_change:
            try:
                cb(cap, old, state)
            except Exception:
                pass

    def get(self, capability_name: str) -> ServiceCapability | None:
        ids = self._by_name.get(capability_name, [])
        if not ids:
            return None
        active = [cid for cid in ids
                  if self._capabilities[cid].state in (CapabilityState.ACTIVE, CapabilityState.REGISTERED)]
        return self._capabilities.get(active[0]) if active else self._capabilities.get(ids[0])

    def get_by_id(self, capability_id: str) -> ServiceCapability | None:
        return self._capabilities.get(capability_id)

    def find_by_service(self, service_id: str) -> list[ServiceCapability]:
        return [self._capabilities[cid] for cid in self._by_service.get(service_id, [])
                if cid in self._capabilities]

    def find_by_interface(self, method: str, path: str) -> list[ServiceCapability]:
        results = []
        for cap in self._capabilities.values():
            for iface in cap.interfaces:
                if iface.get("method") == method and iface.get("path") == path:
                    if cap.state in (CapabilityState.ACTIVE, CapabilityState.REGISTERED):
                        results.append(cap)
        return results

    def find_healthy(self, capability_name: str) -> ServiceCapability | None:
        ids = self._by_name.get(capability_name, [])
        for cid in ids:
            cap = self._capabilities[cid]
            if cap.state == CapabilityState.ACTIVE:
                if cap.health_check is None:
                    return cap
                try:
                    if cap.health_check():
                        return cap
                except Exception:
                    continue
        for cid in ids:
            cap = self._capabilities[cid]
            if cap.state == CapabilityState.REGISTERED:
                return cap
        return None

    def resolve(self, capability_name: str, chain: list[str] | None = None) -> ResolutionResult:
        chain = chain or []
        if capability_name in chain:
            return ResolutionResult(
                capability_name=capability_name,
                resolved=False,
                error=f"Circular dependency: {capability_name}",
                dependency_chain=chain + [capability_name],
            )
        cap = self.get(capability_name)
        if cap is None:
            inner = self._inner.get(capability_name)
            if inner:
                return ResolutionResult(
                    capability_name=capability_name,
                    resolved=True,
                    state=CapabilityState.REGISTERED,
                    dependency_chain=chain + [capability_name],
                )
            return ResolutionResult(
                capability_name=capability_name,
                resolved=False,
                error=f"Capability not found: {capability_name}",
                dependency_chain=chain + [capability_name],
            )
        current_chain = chain + [capability_name]
        full_chain = list(current_chain)
        for dep in cap.dependencies:
            result = self.resolve(dep, current_chain)
            if not result.resolved:
                return result
            for c in result.dependency_chain:
                if c not in full_chain:
                    full_chain.append(c)
        return ResolutionResult(
            capability_name=capability_name,
            resolved=True,
            service_id=cap.service_id,
            state=cap.state,
            dependency_chain=full_chain,
        )

    def validate(self) -> list[dict[str, Any]]:
        errors = []
        for cap in self._capabilities.values():
            for dep in cap.dependencies:
                result = self.resolve(dep)
                if not result.resolved:
                    errors.append({
                        "capability": cap.capability_name,
                        "service_id": cap.service_id,
                        "dependency": dep,
                        "error": result.error,
                    })
        return errors

    def all(self) -> list[ServiceCapability]:
        return list(self._capabilities.values())

    def services_by_capability(self) -> dict[str, list[str]]:
        result: dict[str, list[str]] = defaultdict(list)
        for cap in self._capabilities.values():
            result[cap.capability_name].append(cap.service_id)
        return dict(result)

    def recent_events(self, n: int = 10) -> list[dict[str, Any]]:
        return self._events[-n:]

    def summary(self) -> dict[str, Any]:
        state_counts: dict[str, int] = {}
        for cap in self._capabilities.values():
            state_counts[cap.state.value] = state_counts.get(cap.state.value, 0) + 1
        return {
            "total_capabilities": len(self._capabilities),
            "services_publishing": len(set(c.service_id for c in self._capabilities.values())),
            "by_state": state_counts,
            "validation_errors": len(self.validate()),
            "total_events": len(self._events),
            "dependencies_validated": sum(len(c.dependencies) for c in self._capabilities.values()),
        }
