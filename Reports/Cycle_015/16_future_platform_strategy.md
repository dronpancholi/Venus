# Cycle 015 — Future Platform Strategy

## After Consolidation: The Clean Architecture

After Cycle 015, Genesis moves from this:

```
7 kernels | 4 event systems | 5 graphs | 4 storage | 4 execution | 7 memory | 3 plugins
```

To this:

```
1 kernel  | 1 event system | 1 graph | 2 storage | 2 execution | 1 memory | 1 plugin
```

## Six-Layer Architecture (Target)

```
Layer 5: PLUGIN        External extensions via PluginManager (M90)
Layer 4: PLATFORM      Desktop, Server, CLI, Watch, SDK
Layer 3: INTELLIGENCE  Brain, Cognition, Planning, Reasoning, Ontology
Layer 2: DOMAIN        Agents, Execution, Tasks, Conversations, Memory, Storage, Graph
Layer 1: KERNEL        FabricKernel — EventRouter, ServiceRegistry, Metrics, Audit, Scheduler
Layer 0: FOUNDATION    Core types, Utils, DI Container, Base classes
```

**Dependency rule:** A layer may only depend on itself and layers below it. No upward dependencies.

## Cycle 016 — API Platform

| Mission | Description |
|---------|-------------|
| M110 | API v2 — stabilized interface for all subsystems |
| M111 | SDK v1 — Python SDK for third-party development |
| M112 | Remote Kernel — FabricKernel over network (gRPC) |

## Cycle 017 — Multi-Process Distribution

| Mission | Description |
|---------|-------------|
| M113 | Process isolation for plugins |
| M114 | Distributed execution across workers |
| M115 | Event sourcing with replay |

## Cycle 018 — Cognitive Autonomy

| Mission | Description |
|---------|-------------|
| M116 | Self-modifying agents |
| M117 | Continuous self-improvement curriculum |
| M118 | Cross-project engineering memory |

## Architectural Invariants

These must never be broken:

1. **One kernel** — FabricKernel is the single runtime entry point
2. **One event backbone** — all communication flows through EventRouter
3. **PluginManager is the only extension mechanism**
4. **UnifiedGraph is the canonical graph model**
5. **UniversalMemorySystem is the canonical memory model**
6. **ServiceProvider is the canonical DI container**
7. **All persistence goes through BaseStore** (StorageEngine or SQLiteStore)
8. **All execution goes through AgentExecutionEngine** or **execution/engine.py**

## Platform Maturity Roadmap

| Metric | Cycle 015 (Target) | Cycle 016 (Target) | Cycle 018 (Target) |
|--------|--------------------|--------------------|--------------------|
| Competing kernels | 1 | 1 | 1 |
| Desktop tests | 0 | 50+ | 200+ |
| API tests | 10 | 50+ | 100+ |
| Plugin tests | 0 | 30+ | 100+ |
| Documentation coverage | Module-level only | Full API reference | Interactive guides |
| CI pipeline | None | pytest + lint | Full integration suite |
| Average maturity | 0.68 | 0.80 | 0.95 |
