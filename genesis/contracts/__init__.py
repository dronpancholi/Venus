"""
Integration Contracts (Missions 185-187) — frozen APIs for Venus, BuildIT, AgentOS.

These contracts define exactly how each product consumes Genesis.
No internal dependencies. All provider-neutral.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


# ── Common contract types ──────────────────────────────────────────

@dataclass
class ServiceContract:
    name: str
    version: str = "1.0"
    methods: list[dict[str, Any]] = field(default_factory=list)
    events_consumed: list[str] = field(default_factory=list)
    events_emitted: list[str] = field(default_factory=list)
    requires: list[str] = field(default_factory=list)


@dataclass
class IntegrationBoundary:
    """Defines the boundary between Genesis and a consuming product.

    - `consumes`: Genesis APIs the product calls
    - `provides`: Product APIs Genesis may call
    - `shared_models`: Data models both sides understand
    - `events`: Event types exchanged
    """

    product: str
    version: str = "1.0.0"
    consumes: list[str] = field(default_factory=list)
    provides: list[str] = field(default_factory=list)
    shared_models: list[str] = field(default_factory=list)
    events: list[str] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)


# ── Venus Contract ─────────────────────────────────────────────────

VENUS_CONTRACT = IntegrationBoundary(
    product="venus",
    version="1.0.0",
    consumes=[
        "fabric.kernel.instance()",        # Boot Genesis platform
        "fabric.kernel.emit()",             # Emit events
        "fabric.kernel.query_events()",     # Read events
        "fabric.kernel.search()",           # Universal search
        "fabric.kernel.registry",           # Service discovery
        "fabric.kernel.engineering",        # Engineering objects
        "ai.registry",                       # AI provider registry
        "ai.router",                         # AI routing
        "knowledge.search",                  # Knowledge search
        "memory.institutional",              # Institutional memory
        "graph_v2.query",                    # Graph queries
        "lifecycle.state",                   # Platform lifecycle
        "resources.monitor",                 # Resource monitoring
        "performance.monitor",               # Performance benchmarks
        "query.engine",                      # Universal query
        "runtime.apps",                      # App runtime
        "terminal.commands",                 # Terminal commands
        "workspace.manager",                 # Workspace templates
    ],
    provides=[
        "venus.platform.boot()",             # Venus-specific boot
        "venus.platform.shutdown()",         # Venus-specific shutdown
        "venus.services.*",                  # Venus services
        "venus.events.*",                    # Venus events
    ],
    shared_models=[
        "EngineeringObject",
        "EngineeringEvent",
        "PlatformLifecycle",
        "ResourceMetric",
        "QueryResult",
        "AppManifest",
    ],
    events=[
        "venus.platform.boot.completed",
        "venus.platform.shutdown",
        "venus.service.registered",
        "venus.service.unregistered",
    ],
    constraints=[
        "Venus MUST use Genesis Fabric for all inter-subsystem communication",
        "Venus MUST NOT import internal genesis modules directly",
        "Venus MUST register all services with FabricKernel",
        "Venus MUST use AIRouter for all AI operations",
        "Venus MUST emit events for all significant state changes",
    ],
)


# ── BuildIT Contract ────────────────────────────────────────────────

BUILDIT_CONTRACT = IntegrationBoundary(
    product="buildit",
    version="1.0.0",
    consumes=[
        "fabric.kernel.instance()",        # Boot
        "fabric.kernel.emit()",             # Events
        "fabric.kernel.engineering",         # Engineering objects
        "fabric.kernel.search()",           # Search
        "knowledge.engine",                  # Knowledge
        "memory.engineering",                # Engineering memory
        "graph_v2.query",                    # Graph
        "performance.monitor",               # Build performance
        "query.engine",                      # Universal query
        "terminal.commands",                 # Terminal
    ],
    provides=[
        "buildit.build()",                   # Build system
        "buildit.test()",                    # Test runner
        "buildit.compile()",                 # Compiler
        "buildit.events.*",                  # Build events
    ],
    shared_models=[
        "EngineeringObject",
        "EngineeringEvent",
        "Benchmark",
        "QueryResult",
    ],
    events=[
        "buildit.build.started",
        "buildit.build.completed",
        "buildit.build.failed",
        "buildit.test.passed",
        "buildit.test.failed",
    ],
    constraints=[
        "BuildIT MUST consume Genesis knowledge for build optimization",
        "BuildIT MUST NOT duplicate Genesis AI infrastructure",
        "BuildIT MUST emit events for all build/test lifecycle changes",
        "BuildIT MUST use Genesis performance monitoring for build benchmarks",
    ],
)


# ── AgentOS Contract ────────────────────────────────────────────────

AGENTOS_CONTRACT = IntegrationBoundary(
    product="agentos",
    version="2.0.0",
    consumes=[
        "fabric.kernel.instance()",        # Boot
        "fabric.kernel.emit()",             # Events
        "fabric.kernel.agent_runtime",      # Agent lifecycle
        "fabric.kernel.task_graph",         # Task DAG
        "fabric.kernel.execution_engine",   # Execute tasks
        "ai.registry",                       # AI providers
        "ai.router",                         # AI routing
        "knowledge.engine",                  # Knowledge
        "memory.engineering",                # Memory
        "graph_v2.query",                    # Graph
        "lifecycle.state",                   # Platform lifecycle
        "performance.monitor",               # Agent performance
        "query.engine",                      # Universal query
        "runtime.apps",                      # App runtime
    ],
    provides=[
        "agentos.agent.spawn()",             # Create agents
        "agentos.agent.destroy()",           # Destroy agents
        "agentos.agent.message()",           # Send agent messages
        "agentos.schedule()",                # Schedule agent tasks
        "agentos.events.*",                  # Agent events
    ],
    shared_models=[
        "EngineeringEvent",
        "AgentInstance",
        "TaskNode",
        "QueryResult",
        "AppInstance",
    ],
    events=[
        "agentos.agent.created",
        "agentos.agent.destroyed",
        "agentos.agent.message_sent",
        "agentos.agent.message_received",
        "agentos.task.scheduled",
        "agentos.task.completed",
    ],
    constraints=[
        "AgentOS MUST interact only through FabricKernel APIs",
        "AgentOS MUST NOT import genesis internals directly",
        "AgentOS MUST use AIRouter for all AI operations",
        "AgentOS MUST be provider-neutral (no hardcoded AI provider)",
        "AgentOS MUST emit events for all agent lifecycle changes",
        "AgentOS MUST NOT duplicate Fabric event infrastructure",
    ],
)


ALL_CONTRACTS: dict[str, IntegrationBoundary] = {
    "venus": VENUS_CONTRACT,
    "buildit": BUILDIT_CONTRACT,
    "agentos": AGENTOS_CONTRACT,
}


def get_contract(name: str) -> IntegrationBoundary | None:
    return ALL_CONTRACTS.get(name)


def list_contracts() -> list[dict[str, Any]]:
    return [
        {"product": c.product, "version": c.version,
         "consumes": len(c.consumes), "provides": len(c.provides)}
        for c in ALL_CONTRACTS.values()
    ]


def check_compliance(product: str, actual_imports: list[str]) -> list[str]:
    """Check if a product's actual imports comply with the contract."""
    contract = ALL_CONTRACTS.get(product)
    if not contract:
        return [f"Unknown product: {product}"]
    violations: list[str] = []
    for imp in actual_imports:
        allowed = False
        for allowed_imp in contract.consumes:
            if imp.startswith(allowed_imp.split("(")[0].split(".")[0]):
                allowed = True
                break
        if not allowed and not imp.startswith("genesis.contracts"):
            violations.append(f"Import not in contract: {imp}")
    return violations
