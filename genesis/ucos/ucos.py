"""
UCOS: Universal Capability Operating System — Main facade.
"""

from __future__ import annotations

from typing import Any

from genesis.ucos.capability import (
    Capability, CapabilityCategory, CapabilityDefinition, CapabilityState,
    MaturityLevel,
)
from genesis.ucos.registry import CapabilityRegistry
from genesis.ucos.resolver import CapabilityResolver
from genesis.ucos.planner import CapabilityPlanner
from genesis.ucos.lifecycle import CapabilityLifecycleManager
from genesis.ucos.graph import CapabilityDependencyGraph
from genesis.ucos.negotiator import CapabilityNegotiator
from genesis.ucos.marketplace import CapabilityMarketplace
from genesis.ucos.validator import CapabilityValidator
from genesis.ucos.runtime import CapabilityRuntime
from genesis.ucos.metrics import CapabilityMetrics


class UCOS:
    """Universal Capability Operating System — the foundation of GENESIS X."""

    def __init__(self, name: str = "UCOS"):
        self.name = name
        self.registry = CapabilityRegistry()
        self.resolver = CapabilityResolver(self.registry)
        self.planner = CapabilityPlanner(self.registry)
        self.lifecycle = CapabilityLifecycleManager(self.registry)
        self.graph = CapabilityDependencyGraph(self.registry)
        self.negotiator = CapabilityNegotiator(self.registry)
        self.marketplace = CapabilityMarketplace(self.registry)
        self.validator = CapabilityValidator(self.registry)
        self.runtime = CapabilityRuntime(self.registry)
        self.metrics = CapabilityMetrics(self.registry)

    def register(self, item, implementation=None) -> Capability | None:
        if isinstance(item, CapabilityDefinition):
            return self.registry.register(item, implementation)
        if isinstance(item, Capability):
            return self.registry.register(item.definition)
        return None

    def get(self, capability_id: str) -> Capability | None:
        return self.registry.get(capability_id)

    def resolve_dependencies(self) -> list[str]:
        ids = [c.id for c in self.registry.all]
        result = []
        for cid in ids:
            deps = self.resolver.resolve(cid)
            for d in deps:
                if d.id not in result:
                    result.append(d.id)
        return result

    def boot_order(self) -> list[str]:
        order = self.resolver.compute_boot_order()
        return [c.id for c in order]

    def plan(self, goal: str, capability_id) -> Any:
        if isinstance(capability_id, list):
            capability_id = capability_id[0] if capability_id else None
        if not capability_id:
            return None
        return self.planner.create_plan(capability_id)

    def validate(self, capability_id: str) -> Any:
        return self.validator.validate(capability_id)

    def validate_all(self) -> dict[str, Any]:
        return self.validator.validate_all()

    def execute(self, capability_id: str, **inputs) -> Any:
        return self.runtime.execute(capability_id, **inputs)

    def start(self, capability_id: str) -> bool:
        return self.lifecycle.start(capability_id)

    def stop(self, capability_id: str) -> bool:
        return self.lifecycle.stop(capability_id)

    def check_health(self) -> dict[str, Any]:
        return self.metrics.snapshot_state()

    def overview(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "capabilities": self.registry.count,
            "by_category": self.metrics.snapshot_state()["by_category"],
            "by_state": self.metrics.snapshot_state()["by_state"],
            "avg_health": self.metrics.snapshot_state()["avg_health"],
            "has_cycles": self.graph.has_cycles(),
            "boot_order": self.boot_order(),
        }
