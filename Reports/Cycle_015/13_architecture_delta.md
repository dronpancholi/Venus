# Cycle 015 — Architecture Delta Report

**Document Status:** Permanent Engineering Record  
**Classification:** Architecture Decision Record  
**Cycle Theme:** Project Eclipse — The Consolidation Cycle  
**Date:** Cycle 015  

---

## Table of Contents

1. [Historical Context](#1-historical-context)
2. [Current Architecture (As-Is)](#2-current-architecture-as-is)
3. [Target Architecture (To-Be)](#3-target-architecture-to-be)
4. [Consolidation Impact](#4-consolidation-impact)
5. [Key Interfaces](#5-key-interfaces)
6. [Migration Strategy](#6-migration-strategy)
7. [Future Evolution](#7-future-evolution)

---

## 1. Historical Context

### 1.1 Genesis

Genesis began as a monolithic Python application — a single codebase with a single entry point, a single event loop, and a single kernel. Its original architecture was a flat `genesis/` package with service-oriented modules communicating through a shared `EventBus`.

The system grew organically across 15 development cycles, driven by the demands of an autonomous engineering platform: agents needed a runtime, tasks needed a graph, memory needed persistence, the desktop needed a TUI, and so on. Each cycle added new subsystems — but instead of refactoring existing ones, new implementations were layered alongside the old.

### 1.2 The Fragmentation Problem

By Cycle 014, Genesis had grown into:

| Metric | Value |
|--------|-------|
| Python files | 464 |
| Lines of Python | 111,820 |
| Packages | 73 |
| ABC/protocol interfaces | 9 ABC + 17 protocols |
| Dataclasses | ~192 |
| Tests (census) | ~10,709 (3,274 baseline verified) |
| Modules with tests | 139/390 (35.6%) |
| Average module maturity | 0.679 |

More critically, the organic growth produced **competing implementations** for every core abstraction:

| Area | Competing Impls | Spanning |
|------|----------------|----------|
| **Kernels** | 7 | `fabric/kernel.py`, `kernel/kernel.py`, `service_kernel.py`, `platform.py`, `platform_adapter.py`, `platform_v2.py`, `engineering_os.py` |
| **Event Systems** | 4 | `fabric/events.py`, `kernel/event_router.py`, `events/bus.py`, `platform_v2.py` (inline) |
| **Graph Systems** | 5 | `graph_v2/core.py`, `graph/engine.py`, `graphdb/__init__.py`, `knowledge_graph.py`, `hypergraph.py` |
| **Storage Systems** | 4 | `persistence/sqlite_store.py`, `fabric/storage.py`, `persistence/repository.py`, `kernel/storage_manager.py` |
| **Execution Engines** | 4 | `fabric/execution.py`, `execution/engine.py`, `runtime/executor.py`, `os/runtime.py` |
| **Memory Systems** | 7 | `memory_system.py`, `memory/engineering.py`, `memory/institutional.py`, `memory/types.py`, `brain/` (~1,600 lines), `memory/engine.py`, `kernel/memory_manager.py` |
| **Plugin Systems** | 3 | `plugin/manager.py`, `kernel/plugin_loader.py`, `plugin/registry.py` |
| **DI Containers** | 2 | `di/container.py`, `kernel/di_kernel.py` |
| **Platform Abstractions** | 5 | `platform.py` (725 lines), `platform_adapter.py` (728 lines), `platform_v2.py` (512 lines), `VenusPlatform`, `PlatformAdapter` |

### 1.3 Root Causes

The fragmentation arose from:

1. **No canonical decisions**: New features defaulted to new implementations because no canonical choice was documented or enforced.
2. **Independent layer directories**: The `Layer_*` directories defined a high-level architecture, but the actual `genesis/` source tree never conformed to it.
3. **Migration inertia**: Legacy implementations remained because "they work" and "migration is risky."
4. **Lack of interface contracts**: Without formal protocols or ABCs, each implementation defined its own API surface.
5. **Test gaps**: Only ~35% of modules had tests, making refactoring high-risk and low-confidence.

### 1.4 Prior Consolidation Attempts

Previous cycles attempted partial consolidation:

- **Cycle 007**: Introduced `FabricKernel` as an alternative to `VenusPlatform` but kept both.
- **Cycle 010**: Analyzed executor architecture and identified `AgentExecutionEngine` as canonical but did not migrate consumers.
- **Cycle 012**: Documented the architecture fragmentation problem in `01_architecture_delta.md`.
- **Cycle 013**: Produced `01_architecture_delta.md` continuing the documentation but without enforcement.
- **Cycle 014**: Produced `09_kernel_architecture.md` proving `UniversalKernel` had zero runtime consumers and recommending FabricKernel as the ONE kernel.

By Cycle 015, the cost of fragmentation was measurable: new developers spent weeks understanding which implementation to use, bugs were fixed in one implementation but not its duplicates, and the codebase was 2-3x larger than needed.

---

## 2. Current Architecture (As-Is)

### 2.1 Logical Layering vs. Physical Structure

Genesis has an **implied** layered architecture documented in the `Layer_*` directories, but the actual `genesis/` source tree does not reflect it. The physical code is organized as a flat namespace with deep but ad-hoc package nesting.

### 2.2 Current Layer Map (Derived from Actual Dependencies)

```
┌──────────────────────────────────────────────────────────────┐
│  LAYER 4: PLATFORM & APPLICATIONS                             │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐ │
│  │ desktop/ │ │ server.py│ │ cli/     │ │ watch/           │ │
│  │ (TUI app)│ │ (FastAPI)│ │ (CMDs)   │ │ (file/git watch) │ │
│  └──────────┘ └──────────┘ └──────────┘ └──────────────────┘ │
├──────────────────────────────────────────────────────────────┤
│  LAYER 3: INTELLIGENCE & COGNITION                            │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │ brain/ (EngineeringBrain, CognitiveArchitecture)        │  │
│  │  └─ cognition/ (Beliefs, Goals, Reasoning, Memory,      │  │
│  │       Attention, Reflection, Strategy, Decision,        │  │
│  │       Orchestration)                                     │  │
│  │  └─ graph.py, entity.py, sync.py, embeddings.py         │  │
│  └─────────────────────────────────────────────────────────┘  │
│  ┌────────────┐ ┌──────────┐ ┌────────┐ ┌──────────────────┐ │
│  │ planning/  │ │reasoning │ │compiler│ │ intelligence/    │ │
│  │ (planner)  │ │ .py      │ │ /      │ │                  │ │
│  └────────────┘ └──────────┘ └────────┘ └──────────────────┘ │
├──────────────────────────────────────────────────────────────┤
│  LAYER 2: DOMAIN SERVICES                                     │
│  ┌────────────────────┐ ┌──────────────────────────────────┐ │
│  │ fabric/agent.py    │ │ fabric/execution.py              │ │
│  │ fabric/tasks.py    │ │ (AgentExecutionEngine,           │ │
│  │ (AgentRuntime,     │ │  TaskExecutor)                   │ │
│  │  AgentInstance)    │ └──────────────────────────────────┘ │
│  ┌────────────────────┐ ┌──────────────────────────────────┐ │
│  │ memory_system.py   │ │ fabric/storage.py                │ │
│  │ (UniversalMemory)  │ │ graph_v2/core.py                 │ │
│  │ memory/*           │ │ (UnifiedGraph)                    │ │
│  └────────────────────┘ └──────────────────────────────────┘ │
│  ┌────────────────────┐ ┌──────────────────────────────────┐ │
│  │ fabric/agents.py   │ │ execution/engine.py              │ │
│  │ (conversations)    │ │ (non-AI execution)               │ │
│  └────────────────────┘ └──────────────────────────────────┘ │
├──────────────────────────────────────────────────────────────┤
│  LAYER 1: KERNEL & MIDDLEWARE                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │ FABRIC KERNEL (fabric/kernel.py)                        │  │
│  │  └─ MessageBus, EventRouter, ServiceRegistry,           │  │
│  │     Scheduler, PolicyEngine, Metrics, Audit, Storage    │  │
│  └─────────────────────────────────────────────────────────┘  │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐ │
│  │ kernel/  │ │platform*│ │events/   │ │ engineering_os.py │ │
│  │ (legacy) │ │ (.py)   │ │(legacy)  │ │ (legacy)          │ │
│  └──────────┘ └──────────┘ └──────────┘ └──────────────────┘ │
├──────────────────────────────────────────────────────────────┤
│  LAYER 0: FOUNDATION                                          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐ │
│  │ core/    │ │ utils/   │ │ di/      │ │ ai/              │ │
│  │ (types,  │ │ (id gen, │ │ (Service │ │ (providers,      │ │
│  │  errors, │ │  config) │ │ Provider)│ │  router)         │ │
│  │  UIR)    │ │          │ │          │ │                  │ │
│  └──────────┘ └──────────┘ └──────────┘ └──────────────────┘ │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐ │
│  │ security/│ │ meta/    │ │ metamodel│ │ plugin/          │ │
│  │ (auth,   │ │ (meta    │ │ /        │ │ (manager.py)     │ │
│  │  tokens) │ │  models) │ │          │ │                  │ │
│  └──────────┘ └──────────┘ └──────────┘ └──────────────────┘ │
└──────────────────────────────────────────────────────────────┘
```

### 2.3 Legacy Parallel Structures

Running alongside the Fabric-based architecture (above) are these complete or partial systems:

```
KERNEL/ PACKAGE (legacy, ~1,800 lines)    PLATFORM FILES (legacy, ~2,000 lines)
┌──────────────────────────────┐          ┌──────────────────────────────┐
│ UniversalKernel              │          │ VenusPlatform (725 lines)   │
│  ├─ ProcessManager          │          │ PlatformAdapter (728 lines) │
│  ├─ TaskScheduler           │          │ PlatformV2 (512 lines)      │
│  ├─ MemoryManager           │          │ EngineeringOS (331 lines)   │
│  ├─ StorageManager          │          └──────────────────────────────┘
│  ├─ EventRouter (103 lines) │          ┌──────────────────────────────┐
│  ├─ PluginLoader            │          │ RUNTIME/ PACKAGE             │
│  ├─ DIKernel                │          │ runtime/executor.py (266)   │
│  ├─ SecurityManager         │          │ os/runtime.py (499 lines)   │
│  ├─ HealthManager           │          └──────────────────────────────┘
│  └─ ... (15 sub-managers)   │
└──────────────────────────────┘
```

### 2.4 Current Dependency Problems

1. **Circular dependencies**: Several packages import from each other, requiring the FabricKernel to use lazy `__import__()` in its `boot()` method for `AgentRuntime`, `TaskGraph`, `AgentExecutionEngine`, and `TaskExecutor`.
2. **God-object platform**: `VenusPlatform` (725 lines) and `PlatformAdapter` (728 lines) both boot 50+ services but neither is used by actual runtime code.
3. **Two event systems in use**: The legacy `EventBus` (~30 consumers) and the Fabric `EventRouter` (~7 consumers) operate simultaneously with no interoperability.
4. **Two storage engines**: `fabric/storage.py` (957 lines) and `persistence/sqlite_store.py` (572 lines) both manage SQLite connections but use different schemas and connection patterns.
5. **Cross-layer coupling**: Desktop screens import directly from `fabric.kernel`, `fabric.agents`, and `graph_v2` — bypassing any service abstraction.

---

## 3. Target Architecture (To-Be)

### 3.1 Six-Layer Architecture

The target architecture defines six strict layers, each with a single responsibility and a well-defined interface boundary. Dependencies flow strictly **downward** — a layer may depend on any layer below it but never on a layer above it.

```
LAYER 5: PLUGIN
┌──────────────────────────────────────────────────────────────┐
│  PluginManager — external extensions via manifest+lifecycle  │
│  All plugins are loaded into this layer.                     │
│  Plugins may consume any lower-layer service.                │
├──────────────────────────────────────────────────────────────┤
│              INTERFACE BOUNDARY (Plugin → Platform API)      │
├──────────────────────────────────────────────────────────────┤
LAYER 4: PLATFORM
┌──────────────────────────────────────────────────────────────┐
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────────────┐  │
│  │ desktop/ │ │ server/  │ │ cli/     │ │ watch/         │  │
│  │ (TUI)    │ │ (FastAPI)│ │ (cmds)   │ │ (engineering)  │  │
│  └──────────┘ └──────────┘ └──────────┘ └────────────────┘  │
├──────────────────────────────────────────────────────────────┤
│              INTERFACE BOUNDARY (Platform → Domain API)      │
├──────────────────────────────────────────────────────────────┤
LAYER 3: INTELLIGENCE
┌──────────────────────────────────────────────────────────────┐
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ brain/ (EngineeringBrain + CognitiveArchitecture)       │ │
│  │  └─ cognition/ (Beliefs, Goals, Reasoning, Memory,      │ │
│  │       Attention, Reflection, Strategy, Decision,        │ │
│  │       Orchestration)                                     │ │
│  │  └─ graph.py, entity.py, sync.py                        │ │
│  └─────────────────────────────────────────────────────────┘ │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐ │
│  │ planning │ │ reasoning│ │ compiler │ │ intelligence/    │ │
│  │ /        │ │ .py      │ │ /        │ │                  │ │
│  └──────────┘ └──────────┘ └──────────┘ └──────────────────┘ │
├──────────────────────────────────────────────────────────────┤
│              INTERFACE BOUNDARY (Intelligence → Domain API)  │
├──────────────────────────────────────────────────────────────┤
LAYER 2: DOMAIN
┌──────────────────────────────────────────────────────────────┐
│  ┌──────────────────┐ ┌────────────────────────────────┐    │
│  │ fabric/agents.py │ │ fabric/execution.py            │    │
│  │ fabric/tasks.py  │ │ (AgentExecutionEngine +       │    │
│  │ (AgentRuntime,   │ │  TaskExecutor)                 │    │
│  │  AgentInstance,  │ │ execution/engine.py            │    │
│  │  Conversations)  │ │ (non-AI execution)             │    │
│  └──────────────────┘ └────────────────────────────────┘    │
│  ┌──────────────────┐ ┌────────────────────────────────┐    │
│  │ memory_system.py │ │ fabric/storage.py              │    │
│  │ (UniversalMemory) │ │ (persistence)                  │    │
│  │ memory/          │ │ graph_v2/core.py               │    │
│  │ (EngineeringMem) │ │ (UnifiedGraph)                  │    │
│  └──────────────────┘ └────────────────────────────────┘    │
├──────────────────────────────────────────────────────────────┤
│              INTERFACE BOUNDARY (Domain → Kernel API)        │
├──────────────────────────────────────────────────────────────┤
LAYER 1: KERNEL
┌──────────────────────────────────────────────────────────────┐
│  FabricKernel (fabric/kernel.py)                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ ├─ MessageBus    — Pub/sub messaging with priorities │   │
│  │ ├─ EventRouter   — Structured EngineeringEvents      │   │
│  │ ├─ ServiceRegistry — Service lifecycle + discovery   │   │
│  │ ├─ Scheduler     — Distributed periodic tasks        │   │
│  │ ├─ PolicyEngine  — Rule-based policy enforcement     │   │
│  │ ├─ Metrics       — FabricMetrics collection          │   │
│  │ ├─ Audit         — AuditLog for all operations       │   │
│  │ └─ Storage       — StorageEngine for persistence     │   │
│  └──────────────────────────────────────────────────────┘   │
├──────────────────────────────────────────────────────────────┤
│              INTERFACE BOUNDARY (Kernel → Foundation API)    │
├──────────────────────────────────────────────────────────────┤
LAYER 0: FOUNDATION
┌──────────────────────────────────────────────────────────────┐
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────────────┐  │
│  │ core/    │ │ utils/   │ │ di/      │ │ events/        │  │
│  │ (types,  │ │ (identity,│ │ (Service │ │ (EventBus      │  │
│  │  errors, │ │  config, │ │ Provider)│ │  adapter)      │  │
│  │  UIR)    │ │  helpers)│ │          │ │                │  │
│  └──────────┘ └──────────┘ └──────────┘ └────────────────┘  │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────────────┐  │
│  │ security/│ │ meta/    │ │ ai/      │ │ plugin/        │  │
│  │ (auth,   │ │ (meta    │ │ (providers│ │ (manager.py —  │  │
│  │  tokens) │ │  models) │ │  router) │ │  at foundation) │  │
│  └──────────┘ └──────────┘ └──────────┘ └────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

### 3.2 Layer Definitions

#### Layer 0: Foundation
**Purpose:** Primitive types, identity generation, error hierarchy, DI container, security primitives, AI provider abstractions, event bus adapter, and plugin manager base.

**Contents:**
- `core/` — `BaseEntity`, `UIRNode`, `UIRGraph`, `SemanticType`, `GenesisError` hierarchy
- `utils/` — `generate_id()`, configuration, string utilities, hashing
- `di/` — `ServiceProvider` (type-safe dependency injection)
- `ai/` — `AIProvider`, `ProviderRegistry`, `AIRouter`, `Message`, `MessageRole`
- `security/` — `SecurityManager`, token management, auth primitives
- `plugin/` — `PluginManager`, `PluginManifest`, `PluginInstance`, `Sandbox`
- `events/bus.py` — Legacy `EventBus` (retained via `FabricEventBusAdapter`)

**Key principle:** No Layer 0 component imports from any layer above. Layer 0 has zero knowledge of kernels, agents, tasks, or the fabric.

#### Layer 1: Kernel
**Purpose:** The system kernel — provides message passing, event routing, service discovery, scheduling, policy enforcement, metrics, audit, and persistence to every component above.

**Contents:**
- `fabric/kernel.py` — `FabricKernel` (the ONE kernel)
- `fabric/bus.py` — `MessageBus`, `TypedChannel`, `Message`
- `fabric/events.py` — `EventRouter`, `EngineeringEvent`, `EventStore`, `EventSubscription`
- `fabric/context.py` — `Context` (correlation/transaction/session tracking)
- `fabric/discovery.py` — `ServiceRegistry`, `ServiceInstance`, `ServiceHealth`
- `fabric/scheduler.py` — `DistributedScheduler`
- `fabric/policy.py` — `PolicyEngine`
- `fabric/metrics.py` — `FabricMetrics`
- `fabric/audit.py` — `AuditLog`

**Key principle:** FabricKernel is a **singleton** in the process. It is the sole mediator for all inter-component communication. No domain component talks to another domain component directly — all communication passes through FabricKernel (MessageBus for commands, EventRouter for events).

#### Layer 2: Domain
**Purpose:** Business domain logic — agents, task graphs, execution, memory, storage, and conversations. These are the components that give Genesis its engineering capabilities.

**Contents:**
- `fabric/agents.py` — `AgentRuntime`, `AgentInstance`, `AgentSpec`, `AgentTask`, `AgentMessage`, `AgentScheduler`
- `fabric/tasks.py` — `TaskGraph`, `TaskNode`, `TaskGraphBuilder`, `TaskNodeType`, `TaskStatus`
- `fabric/execution.py` — `AgentExecutionEngine`, `TaskExecutor`
- `execution/engine.py` — `ExecutionEngine` (non-AI: workflows, tasks, actors, pipelines, jobs)
- `memory_system.py` — `UniversalMemorySystem`, `MemoryType`, `MemoryEntry`, `MemoryStore`
- `memory/` — `EngineeringMemory`, `InstitutionalMemory` (extensions of UniversalMemorySystem)
- `fabric/storage.py` — `StorageEngine`, `SchemaManager` (Fabric-wide persistence)
- `persistence/sqlite_store.py` — `SQLiteStore`, `MetadataStore`, `KnowledgeStore`, `HistoryStore`, `ArtifactStore`, `CheckpointStore`
- `graph_v2/core.py` — `UnifiedGraph`, `GraphLayer`, `GraphNode`, `GraphEdge`

**Key principle:** Domain components are **stateless with respect to each other** — they share state only through FabricKernel (events, storage, messages). Domain components never import Platform or Intelligence layers.

#### Layer 3: Intelligence
**Purpose:** Cognitive and intelligence systems — the Engineering Brain with beliefs, goals, reasoning, memory, attention, reflection, strategy, decision-making, and multi-agent orchestration.

**Contents:**
- `brain/__init__.py` — `EngineeringBrain` (facade for cognitive operations)
- `brain/entity.py` — `BrainEntity`, `BrainEntityType`, `Relationship`, `Confidence`, `Lineage`
- `brain/graph.py` — `BrainGraph`
- `brain/sync.py` — Sync adapters (DigitalTwin, UIR, KnowledgeArtifact, VRIP, GraphDB)
- `brain/embeddings.py` — `EmbeddingStore`
- `brain/cognition/` — `CognitiveArchitecture` containing:
  - `belief.py` — `BeliefSystem`, `Belief`, `BeliefEvidence`
  - `goals.py` — `GoalHierarchy`, `Goal`, `GoalPriority`
  - `reasoning.py` — `ReasoningEngine`, `CausalLink`, `Inference`
  - `memory.py` — `WorkingMemory`, `EpisodicMemory`
  - `attention.py` — `AttentionMechanism`, `AttentionFocus`
  - `reflection.py` — `ReflectionEngine`, `Reflection`
  - `strategy.py` — `StrategyEngine`, `Tool`, `Strategy`
  - `decision.py` — `DecisionEngine`, `Alternative`, `Criterion`
  - `orchestration.py` — `Orchestrator`, `CognitiveAgent`
- `planning/` — Planner components
- `compiler/` — DSL compilation pipeline
- `intelligence/` — Future intelligence subsystems

**Key principle:** The Intelligence layer consumes Domain services (agents, memory, graphs) through FabricKernel but does not import Platform components. It produces events that Platform components consume.

#### Layer 4: Platform
**Purpose:** End-user facing applications — desktop TUI, API server, CLI, and continuous engineering watchers. These are the interfaces through which humans and external systems interact with Genesis.

**Contents:**
- `desktop/` — `GenesisDesktop` (Textual TUI), 10+ screens, command palette, search everywhere
- `server.py` — `GenesisAPI` (FastAPI REST + WebSocket + Auth)
- `cli/` — `CLI` (command-line interface)
- `watch/` — `ContinuousEngineering`, `FilesystemWatcher`, `GitWatcher`, `ProviderWatcher`

**Key principle:** Platform components are **thin** — they contain UI/API logic only. All business logic is delegated to Domain and Intelligence layers through FabricKernel.

#### Layer 5: Plugin
**Purpose:** External extensions loaded at runtime via `PluginManager`. Plugins are self-contained packages with a manifest, dependency declarations, and lifecycle hooks.

**Contents:**
- `plugin/manager.py` — `PluginManager`, `PluginInstance`, `Sandbox`
- `plugin/manifest.py` — `PluginManifest`
- `plugin/registry.py` — `ModulePluginRegistry` (lightweight engine registry)

**Key principle:** Plugins operate at the highest layer and may consume any service exposed by lower layers. They are loaded, activated, and deactivated at runtime with no system restart. The `PluginManager` itself lives at Layer 0 (it is a foundation capability) but the plugins it manages operate at Layer 5.

### 3.3 Dependency Rule

```
Layer 5 (Plugin)     → Layers 0-4 (anything exposed via Platform API)
Layer 4 (Platform)   → Layers 0-3 (via FabricKernel)
Layer 3 (Intelligence) → Layers 0-2 (via FabricKernel)
Layer 2 (Domain)     → Layers 0-1 (via FabricKernel)
Layer 1 (Kernel)     → Layer 0 only
Layer 0 (Foundation) → Nothing (no internal imports from other layers)
```

**Enforcement:** A layer may import from any layer below it. A layer must never import from any layer above it. All cross-component communication in Layers 2-4 uses FabricKernel as the mediator (MessageBus or EventRouter), not direct imports.

---

## 4. Consolidation Impact

This section describes what each consolidation decision means for the target architecture.

### 4.1 Kernel Consolidation (7 → 1)

| Implementation | Destiny | Impact on Architecture |
|----------------|---------|------------------------|
| `fabric/kernel.py` (FabricKernel) | **Canonical** — remains | Layer 1 centerpiece |
| `kernel/kernel.py` (UniversalKernel) | Deprecated | Sub-managers absorbed into FabricKernel as optional extensions |
| `service_kernel.py` | Deprecated | Health/lifecycle logic merged into FabricKernel |
| `platform.py` (VenusPlatform) | Deprecated for runtime | Replaced by direct FabricKernel instantiation |
| `platform_adapter.py` | Deleted after migration | Migration bridge — remove when no consumers remain |
| `platform_v2.py` | Historical artifact | No new consumers |
| `engineering_os.py` | Historical artifact | No new consumers |

**Why it matters:** With ONE kernel, every component in the system has a single, predictable entry point. New engineers learn one kernel API, not seven. Bug fixes apply once. The singleton pattern ensures consistent lifecycle management.

### 4.2 Event System Consolidation (4 → 1)

| Implementation | Destiny | Impact on Architecture |
|----------------|---------|------------------------|
| `fabric/events.py` (EventRouter) | **Canonical** — remains | Primary event infrastructure |
| `events/bus.py` (EventBus) | Retained via adapter | `FabricEventBusAdapter` wraps EventRouter; 30 consumers unchanged |
| `kernel/event_router.py` | Replaced | Consumers migrate to Fabric EventRouter |
| `platform_v2.py` (inline dict) | Removed | Zero consumers |

**Why it matters:** A single event model (`EngineeringEvent` with 18 fields — correlation_id, causation_id, session_id, priority, severity, tags, confidence, TTL) enables cross-component observability. The `EventStore` (50K event buffer, 6 indexes, dead-letter queue) provides queryable event history that powers audit, debugging, and replay.

### 4.3 Graph Consolidation (5 → 1)

| Implementation | Destiny | Impact on Architecture |
|----------------|---------|------------------------|
| `graph_v2/core.py` (UnifiedGraph) | **Canonical** — remains | Primary graph: multi-layer (STRUCTURAL through EVOLUTION) |
| `graph/engine.py` (KnowledgeGraphEngine) | Adapter in `graph_v2/adapter.py` | All consumers migrate to UnifiedGraph |
| `graphdb/__init__.py` (PersistentGraphDB) | Retained as persistence backend | `load_from_unified_graph()` bridges layers |
| `knowledge_graph.py` | Deprecated | Consumers migrate to UnifiedGraph layers |
| `hypergraph.py` | Wrapped as UnifiedGraph layer | Hyperedge extension on UnifiedGraph |

**Why it matters:** UnifiedGraph's layer architecture (12 `LayerType` values) replaces five different graph implementations with a single, extensible graph platform. Any new graph use case adds a layer, not a new implementation.

### 4.4 Storage Consolidation (4 → 2)

| Implementation | Destiny | Impact on Architecture |
|----------------|---------|------------------------|
| `persistence/sqlite_store.py` (SQLiteStore) | **Canonical** — platform-level | 5 normative stores: Metadata, Knowledge, History, Artifact, Checkpoint |
| `fabric/storage.py` (StorageEngine) | **Canonical** — fabric-level | Manages 10 tables across agents, tasks, events, conversations, audit, metrics, services |
| `persistence/repository.py` (Repository[T]) | **Retained** as abstract base | Typed repository pattern for new stores |
| `kernel/storage_manager.py` | **Deleted** | Zero real consumers |

**Why it matters:** Two storage engines with shared connection management (`BaseStore`), each optimized for its use case: `SQLiteStore` for platform-level CRUD (metadata, knowledge graph, compilation cache) and `StorageEngine` for fabric-level event-sourced persistence (events, agents, tasks, conversations, audit).

### 4.5 Execution Engine Consolidation (4 → 2)

| Implementation | Destiny | Impact on Architecture |
|----------------|---------|------------------------|
| `fabric/execution.py` (AgentExecutionEngine) | **Canonical** — AI execution | AI-powered task execution via AIRouter + role prompts |
| `execution/engine.py` (ExecutionEngine) | **Canonical** — general execution | Workflows, tasks, actors, pipelines, jobs |
| `runtime/executor.py` | Deprecated | All consumers migrate to one of the two canonical engines |
| `os/runtime.py` | Deprecated | Autonomous execution goes through AgentExecutionEngine |

**Why it matters:** Clear separation of AI-powered execution (AgentExecutionEngine + TaskExecutor, which wires agent roles to AI providers) from general-purpose execution (ExecutionEngine with workflows, pipelines, jobs). Both operate through FabricKernel.

### 4.6 Memory Consolidation (7 → 1)

| Implementation | Destiny | Impact on Architecture |
|----------------|---------|------------------------|
| `memory_system.py` (UniversalMemorySystem) | **Canonical** — remains | 18 memory types, cognitive architecture |
| `memory/engineering.py` | **Retained** as extension | Sessions + cross-indexing on top of UniversalMemorySystem |
| `memory/institutional.py` | **Retained** as extension | Knowledge objects + timeline on top of UniversalMemorySystem |
| `memory/types.py` | **Replaced** | All imports redirect to `memory_system.py` |
| `brain/` (EngineeringBrain) | **Retained separately** | Higher-level cognitive system (not just memory) |
| `memory/engine.py` | **Replaced** | Consumers migrate to EngineeringMemory |
| `kernel/memory_manager.py` | **Deleted** | Zero real consumers |

**Why it matters:** UniversalMemorySystem defines the canonical `MemoryType` enum (18 types), `MemoryEntry` dataclass, `MemoryStore` with recall, query, similarity search, temporal query, and consolidation. EngineeringMemory and InstitutionalMemory are valid specializations. EngineeringBrain uses it but is architecturally distinct (Layer 3 Intelligence vs. Layer 2 Domain memory).

### 4.7 Plugin Consolidation (3 → 1)

| Implementation | Destiny | Impact on Architecture |
|----------------|---------|------------------------|
| `plugin/manager.py` (PluginManager) | **Canonical** — remains | Full lifecycle management |
| `kernel/plugin_loader.py` | Deprecated | `load_module()` convenience added to PluginManager |
| `plugin/registry.py` | **Retained separately** | Different purpose — lightweight engine registry |

### 4.8 DI Consolidation (2 → 1)

| Implementation | Destiny | Impact on Architecture |
|----------------|---------|------------------------|
| `di/container.py` (ServiceProvider) | **Canonical** — remains | Type-safe DI with Python types as keys |
| `kernel/di_kernel.py` | Deprecated | Consumers migrate to ServiceProvider |

### 4.9 Summary: What the Architecture Gains

| After Consolidation | Before Consolidation |
|---------------------|---------------------|
| 1 kernel to learn | 7 kernels to navigate |
| 1 event model with 18 fields | 4 event models with incompatible fields |
| 1 graph with 12 layers | 5 graphs with no interoperability |
| 2 storage engines (platform + fabric) | 4 storage engines with 3 connection patterns |
| 2 execution engines (AI + general) | 4 execution engines with no clear separation |
| 1 memory system with 2 extensions | 7 memory systems with overlapping type models |
| 1 plugin manager | 3 plugin loading mechanisms |
| 1 DI container | 2 DI containers (one type-safe, one string-based) |

---

## 5. Key Interfaces

This section defines the canonical interfaces that every component must use to interact with the architecture. These are the contracts — if a component follows these interfaces, it will work correctly at its designated layer.

### 5.1 FabricKernel Interface (Layer 1 — Kernel API)

The `FabricKernel` is the primary API surface for all layers above Layer 1.

```python
class FabricKernel:
    """Central fabric kernel. Every subsystem registers here."""

    # ── Singleton Access ────────────────────────────────────
    @classmethod
    def instance(cls, storage_path: str | None = None,
                 enable_persistence: bool = True) -> FabricKernel: ...

    # ── Lifecycle ────────────────────────────────────────────
    def boot(self): ...
    def shutdown(self): ...
    def health(self) -> ServiceHealth: ...
    def stats(self) -> KernelStats: ...

    # ── Messaging (MessageBus) ──────────────────────────────
    def send(self, topic: str, body: Any,
             correlation_id: str | None = None,
             source: str | None = None) -> Message: ...
    def subscribe(self, topic: str, handler: Callable): ...

    # ── Events (EventRouter) ────────────────────────────────
    def emit(self, event_type: str, payload: dict[str, Any] | None = None,
             origin: str = "fabric", correlation_id: str = "",
             causation_id: str = "", session_id: str = "",
             repository_id: str = "",
             priority: EventPriority = EventPriority.NORMAL,
             severity: EventSeverity = EventSeverity.INFO,
             tags: list[str] | None = None,
             confidence: float = 1.0) -> EngineeringEvent: ...
    def on_event(self, event_type: str,
                 handler: Callable[[EngineeringEvent], None],
                 filter_fn: Callable[[EngineeringEvent], bool] | None = None): ...
    def query_events(self, **kwargs) -> list[EngineeringEvent]: ...

    # ── Service Registry ────────────────────────────────────
    def register_service(self, name: str, version: str = "1.0.0",
                         capabilities: list[str] | None = None) -> ServiceInstance: ...
    def unregister_service(self, instance_id: str) -> bool: ...

    # ── Sessions ─────────────────────────────────────────────
    def begin_session(self, session_type: str = "engineering",
                      metadata: dict[str, Any] | None = None) -> Context: ...
    def end_session(self, session_id: str): ...

    # ── Scheduling ───────────────────────────────────────────
    def schedule(self, interval_secs: float, callback: Callable,
                 name: str = "") -> str: ...

    # ── Property Accessors ──────────────────────────────────
    @property
    def bus(self) -> MessageBus: ...
    @property
    def events(self) -> EventRouter: ...
    @property
    def registry(self) -> ServiceRegistry: ...
    @property
    def scheduler(self) -> DistributedScheduler: ...
    @property
    def policy(self) -> PolicyEngine: ...
    @property
    def metrics(self) -> FabricMetrics: ...
    @property
    def audit(self) -> AuditLog: ...
    @property
    def storage(self) -> StorageEngine | None: ...
```

### 5.2 Event Contract (Layer 1 — Event Model)

All events in the system MUST use `EngineeringEvent`. This is the canonical event data structure.

```python
@dataclass
class EngineeringEvent:
    id: str                          # Unique event identifier
    type: str                        # Event type (dot-notation: "kernel.booted")
    timestamp: float                 # Unix timestamp
    origin: str                      # Source subsystem name
    correlation_id: str              # Links related events across subsystems
    causation_id: str                # Links cause-and-effect chain
    session_id: str                  # Links to engineering session
    repository_id: str               # Links to repository context
    priority: EventPriority          # DEBUG, LOW, NORMAL, HIGH, CRITICAL
    severity: EventSeverity          # TRACE, DEBUG, INFO, WARNING, ERROR, CRITICAL
    payload: dict[str, Any]          # Event-specific data
    metadata: dict[str, Any]         # Arbitrary metadata
    tags: list[str]                  # Searchable tags
    confidence: float                # 0.0-1.0 certainty
    ttl_secs: float                  # Time-to-live for expiration

    @property
    def expired(self) -> bool: ...

    def to_dict(self) -> dict[str, Any]: ...
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> EngineeringEvent: ...
```

### 5.3 EngineeringEvent Type Naming Convention

All event types MUST follow the `{origin}.{action}` dot-notation pattern:

| Origin | Examples |
|--------|----------|
| `kernel` | `kernel.booted`, `kernel.shutdown` |
| `service` | `service.registered`, `service.unregistered` |
| `session` | `session.begun`, `session.ended` |
| `agent` | `agent.spawned`, `agent.terminated`, `agent.task.assigned` |
| `task_graph` | `task_graph.node.added`, `task_graph.node.status` |
| `agent_execution_engine` | `agent.execution.completed`, `agent.execution.failed` |
| `task_executor` | `task_executor.started`, `task_executor.node.completed` |
| `fs` (watcher) | `fs.file.created`, `fs.file.changed`, `fs.file.deleted` |
| `git` (watcher) | `git.commit.pushed` |
| `provider` (watcher) | `provider.status.changed` |
| `continuous_engineering` | `continuous_engineering.started` |
| `plugin` | `plugin.registered`, `plugin.activated` |

### 5.4 MessageBus Contract (Layer 1 — Command/Query)

For point-to-point command/query patterns:

```python
@dataclass
class Message:
    id: str
    topic: str
    body: Any
    priority: MessagePriority   # LOW, NORMAL, HIGH, CRITICAL
    correlation_id: str
    source: str
    timestamp: float
    ttl_secs: float
    retry_count: int

class MessageBus:
    def subscribe(self, topic: str, handler: Callable): ...
    def unsubscribe(self, topic: str, handler: Callable): ...
    def publish(self, topic: str, body: Any, context: Any = None,
                source: str = "", priority: MessagePriority = NORMAL) -> Message: ...
    def start(self): ...
    def stop(self): ...
```

### 5.5 ServiceProvider Interface (Layer 0 — DI)

```python
class ServiceProvider:
    def register(self, interface: type, implementation: type,
                 singleton: bool = True, lazy: bool = True): ...
    def register_instance(self, interface: type, instance: Any): ...
    def get(self, interface: type) -> Any: ...
    def is_registered(self, interface: type) -> bool: ...
    def initialize_all(self): ...
    def shutdown(self): ...

    @classmethod
    def get_default(cls) -> ServiceProvider: ...
```

### 5.6 PluginManager Interface (Layer 0 — Plugin Foundation)

```python
class PluginManager:
    def register_plugin(self, manifest: PluginManifest) -> PluginInstance: ...
    def load_from_dir(self, plugin_dir: str | Path) -> list[PluginInstance]: ...
    def activate(self, name: str) -> bool: ...
    def deactivate(self, name: str): ...
    def activate_all(self): ...
    def get(self, name: str) -> PluginInstance | None: ...
    def all(self) -> list[PluginInstance]: ...
    def trigger_hook(self, hook_type: str, name: str, *args, **kwargs) -> list[Any]: ...
    def hot_reload(self, name: str) -> bool: ...
    def validate_all(self) -> list[dict[str, Any]]: ...
```

### 5.7 Key Domain Interfaces (Layer 2)

```python
# ── Agent Runtime ────────────────────────────────────────────
class AgentRuntime:
    def spawn(self, spec: AgentSpec) -> str: ...
    def terminate(self, agent_id: str): ...
    def get_agent(self, agent_id: str) -> AgentInstance | None: ...
    def send_message(self, sender_id: str, recipient_id: str, ...) -> AgentMessage: ...
    def list_agents(self) -> list[AgentInstance]: ...

# ── Task Graph ───────────────────────────────────────────────
class TaskGraph:
    def add_node(self, node: TaskNode) -> str: ...
    def get_node(self, node_id: str) -> TaskNode | None: ...
    def update_status(self, node_id: str, status: TaskStatus): ...
    def add_dependency(self, node_id: str, depends_on_id: str): ...
    def get_ready_tasks(self) -> list[TaskNode]: ...
    def critical_path(self) -> list[TaskNode]: ...

# ── Unified Graph ────────────────────────────────────────────
class UnifiedGraph:
    def create_layer(self, name: str, layer_type: LayerType) -> GraphLayer: ...
    def get_layer(self, name: str) -> GraphLayer | None: ...
    def list_layers(self, layer_type: LayerType | None = None) -> list[GraphLayer]: ...
    def snapshot(self) -> GraphSnapshot: ...

class GraphLayer:
    def add_node(self, node: GraphNode) -> str: ...
    def get_node(self, node_id: str) -> GraphNode | None: ...
    def add_edge(self, edge: GraphEdge) -> str: ...
    def neighbors(self, node_id: str, edge_type: str | None = None) -> list[GraphNode]: ...
    def find_nodes(self, property_filter=None, labels=None) -> list[GraphNode]: ...

# ── Universal Memory System ──────────────────────────────────
class UniversalMemorySystem:
    def store(self, memory_type: MemoryType, key: str, content: Any, ...) -> MemoryEntry: ...
    def recall(self, memory_type: MemoryType, key: str) -> Any | None: ...
    def query(self, memory_type: MemoryType | None = None, ...) -> list[MemoryEntry]: ...
    def search(self, query: str) -> list[MemoryEntry]: ...
    def consolidate(self): ...
    def summary(self) -> dict[str, Any]: ...

# ── Storage Engine ───────────────────────────────────────────
class StorageEngine:
    def connect(self): ...
    def disconnect(self): ...
    def store_event(self, event: Any) -> str: ...
    def store_agent(self, agent_data: dict[str, Any]) -> str: ...
    def store_agent_task(self, task_data: dict[str, Any]) -> str: ...
    def store_task_node(self, node_data: dict[str, Any]) -> str: ...
    def store_conversation(self, conv_data: dict[str, Any]) -> str: ...
    def store_audit_entry(self, entry_data: dict[str, Any]) -> str: ...
    def store_metric(self, metric_data: dict[str, Any]) -> str: ...
```

### 5.8 EngineeringBrain Interface (Layer 3 — Intelligence)

```python
class EngineeringBrain:
    def __init__(self, storage_path: str = "", event_bus=None): ...

    # Entity CRUD
    def entity(self, label: str = "", entity_type: str = "unknown", ...) -> BrainEntity: ...
    def register(self, entity: BrainEntity) -> BrainEntity: ...
    def get(self, brain_id: str) -> BrainEntity | None: ...
    def find_by_type(self, entity_type: str) -> list[BrainEntity]: ...
    def find_by_label(self, label_contains: str) -> list[BrainEntity]: ...
    def remove(self, brain_id: str) -> bool: ...

    # Relationships
    def relate(self, source_id: str, target_id: str, relation: str = "references", ...) -> bool: ...
    def neighbors(self, brain_id: str, relation: str | None = None) -> list[BrainEntity]: ...

    # Synchronization
    def sync_digital_twin(self, twin) -> int: ...
    def sync_uir_graph(self, uir_graph) -> int: ...
    def sync_knowledge_base(self, knowledge_base) -> int: ...

    # Cognitive access
    @property
    def cognition(self) -> CognitiveArchitecture: ...

    @property
    def graph(self) -> BrainGraph: ...
```

### 5.9 Platform Interfaces (Layer 4)

```python
# ── Desktop Application ──────────────────────────────────────
class GenesisDesktop:
    def __init__(self, kernel: FabricKernel | None = None): ...
    def run(self): ...

# ── API Server ───────────────────────────────────────────────
class GenesisAPI:
    def __init__(self, kernel: FabricKernel | None = None, require_auth: bool = False): ...
    def run(self, host: str = "0.0.0.0", port: int = 8765): ...
    def stop(self): ...

# ── Continuous Engineering Watcher ────────────────────────────
class ContinuousEngineering:
    def add_watcher(self, watcher: Watcher): ...
    def start_all(self): ...
    def stop_all(self): ...
    def setup_defaults(self, repo_path: str | Path = "."): ...

class Watcher(ABC):
    @abstractmethod
    def scan(self) -> list[EngineeringEvent]: ...
    def start(self): ...
    def stop(self): ...
```

### 5.10 Cross-Cutting: Identity Generation

All system-wide IDs use a single function:

```python
def generate_id(prefix: str, length: int = 12) -> str:
    """Generate a unique identifier with a type prefix.

    Usage:
        generate_id("agent", 12)    → "agent_a1b2c3d4e5f6"
        generate_id("evt", 16)      → "evt_a1b2c3d4e5f6g7h8"
        generate_id("corr", 12)     → "corr_a1b2c3d4e5f6"

    Standard prefixes (used across the codebase):
        agent  — Agent instances        corr  — Correlation IDs
        evt    — EngineeringEvents      atask — Agent tasks
        msg    — Messages               sess  — Session IDs
        gn     — Graph nodes            ge    — Graph edges
        mem    — Memory entries         tng   — Task graph nodes
        sched  — Scheduled tasks        gsnap — Graph snapshots
        txn    — Transaction IDs
    """
```

---

## 6. Migration Strategy

### 6.1 Principles

1. **Never break a consumer.** All migrations use the adapter pattern or backwards-compatible wrappers.
2. **Adapters over rewrites.** Existing consumers continue to work with their existing API while the underlying implementation is replaced.
3. **Deprecation before deletion.** A component is deprecated (documented, no new consumers) for at least one full cycle before it is deleted.
4. **One canonical per area.** After the migration, each architectural area has exactly one canonical implementation.
5. **Test before delete.** No legacy implementation is removed until the replacement has equivalent or better test coverage.

### 6.2 Migration Phases

#### Phase 1: Foundation Alignment (Cycle 015)

**Goal:** Establish canonical choices with adapters for backward compatibility.

| Step | Action | Risk | Verification |
|------|--------|------|-------------|
| 1.1 | P0 bug fixes: `run_server()`, WS async safety, dead `run_desktop()` | Low | All platforms start clean |
| 1.2 | Create `FabricEventBusAdapter` — wraps Fabric EventRouter with EventBus-subscribe API | Low | All 30 EventBus consumers work unchanged |
| 1.3 | Add `register_factory()` and `find_by_tag()` to ServiceProvider | Low | DIKernel consumers can migrate |
| 1.4 | Create common `BaseStore` for SQLiteStore + StorageEngine connection management | Medium | Both stores share connection pool |
| 1.5 | Document canonical interfaces | Low | New engineers use correct APIs |

#### Phase 2: Kernel Unification (Cycle 016)

**Goal:** FabricKernel is the only kernel.

| Step | Action | Risk | Verification |
|------|--------|------|-------------|
| 2.1 | Absorb UniversalKernel sub-managers into FabricKernel as optional extensions | Medium | All sub-manager consumers import from FabricKernel |
| 2.2 | Replace VenusPlatform.boot() with direct FabricKernel.instance().boot() | Medium | Desktop, server, watch all boot from FabricKernel |
| 2.3 | Merge ServiceKernel health/lifecycle into FabricKernel | Low | Health endpoints work via FabricKernel |
| 2.4 | Deprecate PlatformAdapter | Low | No new consumers |
| 2.5 | Delete PlatformV2, EngineeringOS from runtime paths | Low | No runtime code uses them |

**Migration pattern for kernel consumers:**

```python
# Before:
from genesis.platform import VenusPlatform
platform = VenusPlatform()
platform.boot()
platform.register_service("my_service")

# After:
from genesis.fabric.kernel import FabricKernel
kernel = FabricKernel.instance()
kernel.boot()
kernel.register_service("my_service")
```

#### Phase 3: Event System Unification (Cycle 016)

**Goal:** All events use EngineeringEvent through Fabric EventRouter.

| Step | Action | Risk | Verification |
|------|--------|------|-------------|
| 3.1 | Deploy `FabricEventBusAdapter` | Low | All EventBus consumers use adapter |
| 3.2 | Migrate kernel/event_router.py consumers to Fabric EventRouter | Low | Subscribe API is identical |
| 3.3 | Add event_type naming convention lint check | Low | CI enforces naming |
| 3.4 | Deprecate direct EventBus usage | Low | No new EventBus consumers |

**Adapter pattern for EventBus consumers:**

```python
# The adapter wraps Fabric EventRouter and exposes the same (type, data) tuple API
class FabricEventBusAdapter:
    def __init__(self, event_router: EventRouter):
        self._router = event_router

    def subscribe(self, event_type: str,
                  handler: Callable[[str, dict[str, Any]], None]):
        self._router.subscribe(event_type, lambda ev: handler(ev.type, ev.payload))

    def emit(self, event_type: str, data: dict[str, Any] | None = None):
        self._router.emit_raw(event_type=event_type, payload=data or {})

# Existing EventBus consumers use this adapter with zero code changes:
bus = FabricEventBusAdapter(kernel.events)  # Drop-in replacement for EventBus()
```

#### Phase 4: Graph Unification (Cycle 016-017)

**Goal:** All graph operations use UnifiedGraph.

| Step | Action | Risk | Verification |
|------|--------|------|-------------|
| 4.1 | Verify KnowledgeGraphEngine → UnifiedGraph adapter | Medium | All KGE consumers read/write via adapter |
| 4.2 | Add layer: migrate KnowledgeGraph consumers to UnifiedGraph.SEMANTIC layer | Medium | Query equivalence verified |
| 4.3 | Add hyperedge extension to UnifiedGraph | Medium | Hypergraph consumers use UnifiedGraph |
| 4.4 | Deprecate standalone graph implementations | Low | No new consumers |

#### Phase 5: Storage Unification (Cycle 016-017)

**Goal:** Single `BaseStore` with shared connection management.

| Step | Action | Risk | Verification |
|------|--------|------|-------------|
| 5.1 | Create common `BaseStore` with shared WAL connection pool | Medium | Both StorageEngine and SQLiteStore use it |
| 5.2 | Delete `kernel/storage_manager.py` | Low | No consumers |
| 5.3 | Verify `Repository[T]` as abstract base for typed stores | Low | New typed stores use it |

#### Phase 6: Execution Unification (Cycle 017)

**Goal:** AI tasks go through AgentExecutionEngine; non-AI through ExecutionEngine.

| Step | Action | Risk | Verification |
|------|--------|------|-------------|
| 6.1 | Migrate `runtime/executor.py` consumers to `fabric/execution.py` (AI) or `execution/engine.py` (non-AI) | Medium | Each consumer classified and migrated |
| 6.2 | Migrate `os/runtime.py` consumers to AgentExecutionEngine | Medium | Autonomous execution uses FabricKernel |
| 6.3 | Deprecate `runtime/executor.py` and `os/runtime.py` | Low | No new consumers |

#### Phase 7: Memory Unification (Cycle 017)

**Goal:** All memory uses UniversalMemorySystem or its extensions.

| Step | Action | Risk | Verification |
|------|--------|------|-------------|
| 7.1 | Replace all `from genesis.memory.types` imports with `from genesis.memory_system` | Medium | Functionally identical type enums |
| 7.2 | Replace MemoryEngine with EngineeringMemory | Low | Same key-value API |
| 7.3 | Delete `memory/types.py` | Medium | All imports verified replaced |
| 7.4 | Delete `memory/engine.py` | Low | No consumers |
| 7.5 | Delete `kernel/memory_manager.py` | Low | No consumers |

#### Phase 8: Cleanup (Cycle 018)

**Goal:** Remove all deprecated code paths.

| Step | Action | Risk | Verification |
|------|--------|------|-------------|
| 8.1 | Delete `kernel/` package (all sub-managers migrated or absorbed) | Medium | Full integration test pass |
| 8.2 | Delete `platform.py`, `platform_adapter.py`, `platform_v2.py`, `engineering_os.py` | Low | All boot paths use FabricKernel |
| 8.3 | Delete `runtime/executor.py`, `os/runtime.py` | Low | No consumers |
| 8.4 | Delete `memory/types.py`, `memory/engine.py`, `kernel/memory_manager.py` | Low | No consumers |
| 8.5 | Verify circular imports resolved — no more lazy `__import__()` in FabricKernel.boot() | Medium | Clean import graph |

### 6.3 Consumer Migration Decision Tree

When a component needs to interact with a consolidated area, use this decision tree to determine which canonical implementation to use:

```
Q: Does this component need to persist data?
  → YES: Use StorageEngine (fabric/storage.py) for fabric entities;
          SQLiteStore (persistence/sqlite_store.py) for platform metadata.
  → NO: Continue.

Q: Does this component need event pub/sub?
  → Use EventRouter via kernel.events (FabricKernel's EventRouter).
  → If using EventBus API, use FabricEventBusAdapter.

Q: Does this component need a graph?
  → Use UnifiedGraph (graph_v2/core.py).
  → If you need persistence, use PersistentGraphDB as backend.

Q: Does this component need to execute tasks?
  → AI-powered agent tasks: AgentExecutionEngine (fabric/execution.py).
  → Non-AI workflows/pipelines/jobs: ExecutionEngine (execution/engine.py).

Q: Does this component need memory?
  → In-memory cognitive memory: UniversalMemorySystem (memory_system.py).
  → Session-based engineering memory: EngineeringMemory (memory/engineering.py).
  → Long-term knowledge: InstitutionalMemory (memory/institutional.py).

Q: Does this component need DI?
  → Use ServiceProvider (di/container.py). Use ServiceProvider.get_default().

Q: Does this component need to load plugins?
  → Use PluginManager (plugin/manager.py).

Q: Does this component need a kernel?
  → Use FabricKernel.instance().
  → Never instantiate FabricKernel directly — always use the singleton.
```

### 6.4 Backward Compatibility Guarantees

| Period | Guarantee |
|--------|-----------|
| Cycle 015 | All existing code continues to work with zero changes |
| Cycle 016 | Canonical APIs stable; legacy APIs deprecated (warnings on import) |
| Cycle 017 | Legacy APIs removed; adapter layer available for critical paths |
| Cycle 018+ | Clean architecture; no legacy APIs; all code uses canonical interfaces |

---

## 7. Future Evolution

### 7.1 How This Architecture Enables Cycles 016+

The target architecture is designed to support Genesis's evolution for the next 5+ years without requiring another consolidation cycle. Key architectural enablers:

### 7.2 Cycle 016: API Surface Stabilization

**Objective:** Make Genesis a platform that external tools can build on.

**Enabled by the new architecture:**
- Layer 4 (Platform) already separates API concerns from business logic
- `GenesisAPI` (server.py) is the single REST/WebSocket entry point
- All domain operations go through FabricKernel, which can expose a formal SDK

**Specific work:**
- Extract `genesis/api/` into a proper REST SDK with generated OpenAPI specs
- Create `GenesisClient` library for external Python applications
- Stabilize WebSocket event broadcasting for real-time UIs
- Document every endpoint with the canonical event type naming

### 7.3 Cycle 017: Multi-Process Distribution

**Objective:** Scale Genesis beyond a single process.

**Enabled by the new architecture:**
- FabricKernel's `EventRouter` already has `correlation_id`, `causation_id`, `session_id` — the foundation for distributed tracing
- `MessageBus` already supports priority queues and dead-letter handling
- `StorageEngine` persists every event, agent, task, and conversation — enabling state reconstruction after process restart

**Specific work:**
- Replace in-process `MessageBus` with Redis/NATS-backed distributed bus
- Replace in-process `EventRouter` with partitioned, cluster-aware event router
- Add remote service discovery to `ServiceRegistry`
- Add distributed `DistributedScheduler` with leader election

### 7.4 Cycle 018: Plugin Ecosystem Maturity

**Objective:** Allow third-party developers to extend Genesis.

**Enabled by the new architecture:**
- Layer 5 (Plugin) is already defined as the extension layer
- `PluginManager` supports manifests, dependencies, lifecycle hooks, hot-reload, and sandboxing
- All Platform (Layer 4) components use FabricKernel, which plugins can access

**Specific work:**
- Define formal Plugin API contract (public SDK)
- Add plugin marketplace directory and package format
- Add plugin version resolution and dependency graph visualization
- Add permission tokens for sandboxed plugins

### 7.5 Cycle 019+: Cognitive Evolution

**Objective:** Make the Engineering Brain fully autonomous.

**Enabled by the new architecture:**
- Layer 3 (Intelligence) cleanly separates cognition from infrastructure
- `CognitiveArchitecture` integrates beliefs, goals, reasoning, memory, attention, reflection, strategy, and decisions
- `Orchestrator` already manages multi-agent cognitive workflows
- All cognitive operations consume Domain services through FabricKernel, making them replaceable

**Specific work:**
- Add reinforcement learning for strategy optimization
- Add meta-cognition: the system reflects on its own reasoning quality
- Add autonomous goal generation from high-level objectives
- Add cross-session learning: EngineeringMemory as a persistent cognitive store

### 7.6 Architectural Invariants

The following invariants must never be violated, regardless of the cycle:

1. **FabricKernel is the ONE kernel.** No alternative kernel implementation will ever be created.
2. **EngineeringEvent is the ONE event model.** No alternative event data structure will be used for inter-component communication.
3. **Dependencies flow downward.** No layer imports a layer above it.
4. **Adapters bridge, not replace.** When a new implementation replaces an old one, an adapter preserves backward compatibility.
5. **Every component has one canonical home.** If a component could live in two layers, it must be explicitly assigned to one.
6. **The six-layer model is stable.** Layers are not added or removed — only the content within them evolves.

### 7.7 Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Circular imports between layers | Medium | High | Enforce dependency direction; `__import__()` only in boot sequence |
| Consumer resistance to migration | Medium | Medium | Adapters provide zero-break migration path |
| New components using deprecated APIs | High | Medium | CI lint rules; deprecation warnings; code review gates |
| Legacy storage data migration | Low | High | `BaseStore` dual-writes during migration period |
| Plugin sandbox bypass | Low | Critical | `Sandbox` module-allowlist; capability-based permissions |

---

## Appendix A: Current Package Inventory by Layer

This table maps each existing `genesis/` package to its target layer. Packages marked with **†** are deprecated and will be removed by Cycle 018.

| Package | Target Layer | Destiny |
|---------|-------------|---------|
| `genesis/core/` | Layer 0 (Foundation) | Retain |
| `genesis/utils/` | Layer 0 (Foundation) | Retain |
| `genesis/di/` | Layer 0 (Foundation) | Retain |
| `genesis/ai/` | Layer 0 (Foundation) | Retain |
| `genesis/security/` | Layer 0 (Foundation) | Retain |
| `genesis/plugin/` | Layer 0 (Foundation) | Retain |
| `genesis/events/` | Layer 0 (Foundation) | Retain (via adapter) |
| `genesis/meta/` | Layer 0 (Foundation) | Retain |
| `genesis/fabric/` (kernel.py + bus.py + events.py + ...) | Layer 1 (Kernel) | Retain |
| `genesis/fabric/` (agents.py + tasks.py + execution.py) | Layer 2 (Domain) | Retain |
| `genesis/graph_v2/` | Layer 2 (Domain) | Retain |
| `genesis/memory_system.py` | Layer 2 (Domain) | Retain |
| `genesis/memory/` | Layer 2 (Domain) | Retain (engineering + institutional) |
| `genesis/execution/` | Layer 2 (Domain) | Retain |
| `genesis/persistence/` | Layer 2 (Domain) | Retain |
| `genesis/brain/` | Layer 3 (Intelligence) | Retain |
| `genesis/planning/` | Layer 3 (Intelligence) | Retain |
| `genesis/compiler/` | Layer 3 (Intelligence) | Retain |
| `genesis/intelligence/` | Layer 3 (Intelligence) | Retain |
| `genesis/desktop/` | Layer 4 (Platform) | Retain |
| `genesis/server.py` | Layer 4 (Platform) | Retain |
| `genesis/cli/` | Layer 4 (Platform) | Retain |
| `genesis/watch/` | Layer 4 (Platform) | Retain |
| `genesis/kernel/**` † | — | **Delete by C018** |
| `genesis/platform.py` † | — | **Delete by C018** |
| `genesis/platform_adapter.py` † | — | **Delete by C018** |
| `genesis/platform_v2.py` † | — | **Delete by C018** |
| `genesis/engineering_os.py` † | — | **Delete by C018** |
| `genesis/service_kernel.py` † | — | **Delete by C018** |
| `genesis/runtime/executor.py` † | — | **Delete by C018** |
| `genesis/os/runtime.py` † | — | **Delete by C018** |

## Appendix B: Interface Compliance Checklist

Every component at each layer SHOULD follow these rules:

**Layer 0 (Foundation):**
- [ ] Imports only from `genesis.core`, `genesis.utils`, `genesis.di`, `genesis.ai`
- [ ] Uses `generate_id()` for all identifiers
- [ ] Raises `GenesisError` subclasses for all errors
- [ ] Never imports from `genesis.fabric`, `genesis.kernel`, `genesis.desktop`, `genesis.server`

**Layer 1 (Kernel):**
- [ ] All inter-component communication uses `FabricKernel.send()` or `FabricKernel.emit()`
- [ ] All events use `EngineeringEvent` with proper type naming
- [ ] Never imports `genesis.desktop`, `genesis.server`, `genesis.cli`

**Layer 2 (Domain):**
- [ ] Gets `FabricKernel` via `FabricKernel.instance()` (always the singleton)
- [ ] Delegates persistence to `FabricKernel.storage` (not direct SQLite connections)
- [ ] All state changes emit `EngineeringEvent` through `FabricKernel.emit()`
- [ ] Never imports `genesis.brain`, `genesis.desktop`, `genesis.server`

**Layer 3 (Intelligence):**
- [ ] Uses `EngineeringBrain` as the cognitive facade
- [ ] Consumes Domain services through `FabricKernel` event subscriptions
- [ ] All cognitive output events use `EngineeringEvent`
- [ ] Never imports `genesis.desktop`, `genesis.server`, `genesis.cli`

**Layer 4 (Platform):**
- [ ] Thin: UI/API logic only, no business logic
- [ ] All operations delegate to Domain or Intelligence layers via `FabricKernel`
- [ ] Uses `EngineeringEvent` for all platform-originated events
- [ ] Can import any layer below

**Layer 5 (Plugin):**
- [ ] Declares manifest with name, version, dependencies, hooks
- [ ] Activates/deactivates cleanly (no side effects on load)
- [ ] Sandbox-compatible: only uses allowed modules
- [ ] All I/O goes through `PluginManager`-provided APIs

---

*End of Architecture Delta Report — Cycle 015*  
*Next review: Cycle 016*
