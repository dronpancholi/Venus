"""
GENESIS-X Program A: Universal Capability Operating System (UCOS).

Everything inside Genesis becomes a capability — not a module, not a service.
Each capability has identity, semantic definition, contracts, dependencies,
consumers, providers, permissions, execution policies, version history,
maturity, health, ownership, verification, and metrics.

Exposed classes:
  Capability, CapabilityDefinition, CapabilityCategory, CapabilityState
  CapabilityRegistry, CapabilityResolver, CapabilityPlanner
  CapabilityLifecycleManager, CapabilityDependencyGraph
  CapabilityNegotiator, CapabilityMarketplace, CapabilityValidator
  CapabilityRuntime, CapabilityMetrics
  UniversalCapabilityOperatingSystem  — facade
"""

from genesis.ucos.capability import (
    Capability, CapabilityDefinition, CapabilityCategory, CapabilityState,
    CapabilityContract, CapabilityVersion, CapabilityHealth, CapabilityPermission,
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
from genesis.ucos.ucos import UCOS

__all__ = [
    "Capability", "CapabilityDefinition", "CapabilityCategory", "CapabilityState",
    "CapabilityContract", "CapabilityVersion", "CapabilityHealth", "CapabilityPermission",
    "CapabilityRegistry", "CapabilityResolver", "CapabilityPlanner",
    "CapabilityLifecycleManager", "CapabilityDependencyGraph",
    "CapabilityNegotiator", "CapabilityMarketplace", "CapabilityValidator",
    "CapabilityRuntime", "CapabilityMetrics",
    "UCOS",
]
