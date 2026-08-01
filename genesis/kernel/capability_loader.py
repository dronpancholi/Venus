"""
Universal Kernel: CapabilityLoader — Instantiate and wire capabilities.
"""

from __future__ import annotations

import time
from collections import defaultdict
from typing import Any

from genesis.kernel.di_kernel import DIKernel
from genesis.kernel.types import DiServiceRegistration
from genesis.ucos.capability import (
    Capability, CapabilityDefinition, CapabilityState,
)
from genesis.utils.identity import generate_id


class CapabilityLoader:
    """Instantiates capabilities from definitions, wires dependencies."""

    def __init__(self, di_kernel: DIKernel | None = None):
        self._di = di_kernel or DIKernel()
        self._loaded: dict[str, Capability] = {}
        self._load_order: list[str] = []
        self._history: list[dict[str, Any]] = []

    @property
    def di(self) -> DIKernel:
        return self._di

    def load(self, definition: CapabilityDefinition) -> Capability | None:
        existing = self._loaded.get(definition.id)
        if existing:
            return existing
        deps = {}
        for dep_id in definition.dependencies:
            dep = self._loaded.get(dep_id)
            if not dep:
                dep_def = CapabilityDefinition(
                    id=dep_id, name=f"Auto_{dep_id}"
                )
                dep = Capability(dep_def)
                self._loaded[dep_id] = dep
            deps[dep_id] = dep
        cap = Capability(definition)
        cap.state = CapabilityState.REGISTERED
        self._loaded[definition.id] = cap
        self._load_order.append(definition.id)
        self._history.append({
            "action": "load",
            "capability_id": definition.id,
            "name": definition.name,
            "dependencies_resolved": len(deps),
            "timestamp": time.time(),
        })
        return cap

    def get(self, capability_id: str) -> Capability | None:
        return self._loaded.get(capability_id)

    def unload(self, capability_id: str) -> bool:
        cap = self._loaded.pop(capability_id, None)
        if cap:
            cap.state = CapabilityState.OBSOLETE
            if capability_id in self._load_order:
                self._load_order.remove(capability_id)
            return True
        return False

    def load_order(self) -> list[str]:
        return list(self._load_order)

    def wire_dependencies(self, capability_id: str) -> bool:
        cap = self._loaded.get(capability_id)
        if not cap:
            return False
        for dep_id in cap.definition.dependencies:
            dep = self._loaded.get(dep_id)
            if not dep:
                return False
        return True

    def all_loaded(self) -> list[Capability]:
        return list(self._loaded.values())

    def summary(self) -> dict[str, Any]:
        states: dict[str, int] = {}
        for c in self._loaded.values():
            states[c.state.value] = states.get(c.state.value, 0) + 1
        return {
            "loaded": len(self._loaded),
            "by_state": states,
            "load_order_length": len(self._load_order),
            "di_services": self._di.summary()["services"],
            "total_operations": len(self._history),
        }
