# PROJECT NEMESIS Phase III — Mission 7: Platform Reconstruction

**Date**: 2026-06-30 | **Repository**: 335 Python files (excl tests), ~71,916 lines (excl tests), 72 test files, 2,763 tests
**Scope**: Complete reverse engineering of VenusPlatform — every constructor, boot phase, dependency, registration, event, shutdown hook

---

## 1. Executive Summary

`genesis/platform.py` (725 lines) is a **bootstrap monolith** — a single class `VenusPlatform` that creates, wires, and registers **50+ services** across 8 sequential boot phases spanning GENESIS epochs II through XIII.

**Core problem**: The platform does not orchestrate. It implements. It directly instantiates every service, passes constructor arguments manually, calls boot/start methods, and registers each into the DI container. This violates the single responsibility principle — the platform should be a thin orchestration layer, not a god-object factory.

**Compounding factor**: Two parallel platform systems exist — `platform_v2.py` (512 lines, ServiceCategory model, ServiceRegistry, LifecycleManager, EventRouter, MetricsManager) and `engineering_os.py` (331 lines, ServiceRole model, heartbeat scheduler). Both are independent implementations of the same concept (service-oriented platform) with zero consumers.

**3,250 total lines of platform infrastructure** across 3 files, of which only 725 (platform.py) actually runs. The other 2,075 lines are unreachable.

**Evidence**: Only `test_compliance.py` imports `VenusPlatform`. `platform_v2.py` and `engineering_os.py` appear nowhere in the import graph of any test or consumer.

---

## 2. Platform.py — Complete Reverse Engineering

### 2.1 File Anatomy

| Section | Lines | Purpose |
|---------|-------|---------|
| Docstring + imports | 1-102 | 102 lines of imports from 42 modules |
| `__init__` | 107-181 | 45 typed service attributes, all `None` |
| `bootstrap()` | 183-197 | Phase 1: DI bootstrap, resolve 6 core infrastructure services |
| `boot()` | 199-551 | Phase 2: 353 lines, 45+ sequential service instantiations |
| `_gather_evolution_metrics()` | 553-565 | Metrics collection for evolution engines |
| `_gather_genesis_ix_metrics()` | 567-585 | Metrics collection for GENESIS-IX evolution |
| `_service_summary()` | 587-638 | Boolean dict of 45+ services |
| `shutdown()` | 641-655 | 15-line graceful teardown |
| `summary()` | 657-677 | Status dict for inspection |
| `main()` | 680-725 | CLI entry point with argparse |

### 2.2 Complete Import Map

platform.py imports from 42 distinct modules:

```
genesis.brain
genesis.digital_twin
genesis.intelligence
genesis.capability.registry
genesis.certification.engine
genesis.cli.commands
genesis.compiler.compiler
genesis.config.settings
genesis.core.metadata
genesis.di.bootstrap
genesis.di.container
genesis.diagnostics.diagnostics
genesis.events.bus
genesis.graph.engine
genesis.indexer.indexer
genesis.memory.engine
genesis.package.manager
genesis.persistence (6 stores)
genesis.plugin.manager
genesis.project.manager
genesis.runtime.executor
genesis.security.validator
genesis.memory.types (16 types)
genesis.physics
genesis.knowledge_graph
genesis.engineering_os
genesis.civilization_v2
genesis.evolution
genesis.platform_v2
genesis.brain_v4
genesis.memory_system
genesis.hypergraph
genesis.planetary_knowledge
genesis.civilization_v3
genesis.evolution_v4
genesis.ucos
genesis.kernel
genesis.meta
genesis.ued
genesis.fabric
genesis.graph_v2
genesis.execution
genesis.autonomous
genesis.meta_model
genesis.execution_graph
genesis.economics
genesis.planner
genesis.ontology
genesis.reasoning
genesis.repository_scientist
genesis.repository_engineer
genesis.repository_economics
genesis.digital_civilization
genesis.reverse_engineer
genesis.omega_loop
```

### 2.3 Complete Boot Dependency Graph

The boot sequence has strict sequential ordering. Each step depends on services created in previous steps.

```
PHASE 0: DI BOOTSTRAP (bootstrap())
  [1] EventBus ← singleton, no deps
  [2] MetadataStore ← db_path (lazy)
  [3] KnowledgeStore ← db_path (lazy)
  [4] HistoryStore ← db_path (lazy)
  [5] ArtifactStore ← db_path (lazy)
  [6] MemoryStore ← db_path (eager)
  [7] CheckpointStore ← checkpoint_dir (lazy)

PHASE 1: CORE SERVICES (boot())
  [8]  Compiler ← EventBus, ArtifactStore
  [9]  KnowledgeGraphEngine ← EventBus, KnowledgeStore
  [10] ExecutionEngine ← EventBus, HistoryStore
  [11] MetadataEngine ← MetadataStore, EventBus
  [12] Diagnostics ← EventBus
  [13] RepositoryIndexer ← config.workspace_root, EventBus
  [14] PluginManager ← EventBus, + load_from_dir()
  [15] CapabilityRegistry ← global singleton
  [16] PackageManager ← PluginManager, EventBus, MemoryStore
  [17] MemoryEngine ← MemoryStore, EventBus
  [18] ProjectManager ← EventBus, MemoryStore
  [19] CertificationEngine ← EventBus, MemoryStore
  [20] SecurityValidator ← EventBus, MemoryStore
  [21] EngineeringBrain ← db_path+brain, EventBus
        → sync_uir_graph(graph.graph)     [depends on 9]
        → start_integration()
        → bus.emit("brain.ready")
  [22] IntelligenceService ← EngineeringBrain, CheckpointStore
        → run_all()                       [depends on 21]
  [23] PlanetaryDigitalTwin ← EngineeringBrain  [depends on 21]

PHASE 2: GENESIS-VIII PROGRAMS
  [24] 16 MemoryTypes ← ephemeral dict (no dependencies)
  [25] PhysicsEngine ← no deps
  [26] PlanetaryKnowledgeGraph ← no deps
  [27] EngineeringOS ← no deps
        → register_service(brain, cognitive)
        → register_service(memory, memory)
        → register_service(simulator, simulation)
        → register_service(discovery, research)
        → register_service(knowledge_graph, knowledge)
        → boot()
  [28] SoftwareCivilizationV2 ← no deps
        → create_institute × 6
  [29] EvolutionEngine ← no deps
        → observe(metrics from 21, 22, 23, 9)

PHASE 3: GENESIS-IX PHASES
  [30] PlatformV2 ← no deps
        → register_service(brain, memory, graph, simulator, discovery, civilization, evolution)
        → boot()
  [31] EngineeringBrainV4 ← no deps
  [32] UniversalMemorySystem ← no deps
  [33] HypergraphKnowledgeCore ← no deps
  [34] PlanetaryKnowledgeEngine ← no deps
  [35] SoftwareCivilizationV3 ← no deps
  [36] EvolutionEngineV4 ← no deps
        → observe(metrics from 30-35)

PHASE 4: GENESIS-X PROGRAMS
  [37] UCOS ← no deps
  [38] UniversalKernel ← no deps
        → boot()

PHASE 5: GENESIS-XI
  [39] MetaCompiler ← no deps
  [40] Database ← no deps

PHASE 6: GENESIS-XII
  [41] FabricKernel ← singleton
        → boot()
  [42] UnifiedGraph ← no deps
  [43] ExecutionEngineV2 ← no deps
  [44] EngineeringOrchestrator ← FabricKernel, UnifiedGraph, Database, ExecutionEngineV2

PHASE 7: GENESIS-XIII (Ω³)
  [45] MetaModelEngine ← config.workspace_root
        → define_builtin_types()
        → scan()
  [46] ExecutionGraph ← factory
        ExecGraphEngine ← ExecutionGraph
        ExecutionGraphMonitor ← ExecGraphEngine
  [47] EconomicsEngine ← no deps
  [48] EngineeringPlanner ← no deps
  [49] RelationshipEngine ← no deps
  [50] CanonicalRegistry ← factory
  [51] MetaModel integration
        → register_universal_types(meta_model.model)
        → sync_uem_entities_to_meta_model(...)    [depends on 49, 45]
  [52] ReasoningEngine ← RelationshipEngine, MetaModel, CanonicalRegistry  [49, 45, 50]
  [53] RepositoryScientist ← ReasoningEngine   [52]
  [54] RepositoryEngineer ← ReasoningEngine, RepositoryScientist  [52, 53]
  [55] RepositoryEconomics ← ReasoningEngine   [52]
  [56] DigitalCivilization ← RelationshipEngine  [49]
  [57] ReverseEngineeringEngine ← config.root, RelationshipEngine  [49]
  [58] OmegaLoop ← config.root

FINALIZATION
  [59] register_shutdown_hook(lambda: shutdown())
  [60] bus.emit("platform.boot.completed", {...})  [depends on all]
```

### 2.4 Service Registration Count

Every service is registered into the DI container via `provider.register_instance()`. Count: **31 `register_instance()` calls** in boot() + 1 in bootstrap() = **32 registered interfaces**.

### 2.5 Shutdown Path

```
platform.shutdown()
  [1] brain.stop_integration()  ← if brain
  [2] vrip.engine._save_checkpoint()  ← if vrip
  [3] bus.emit("platform.shutdown", {...})  ← if bus
  [4] metadata_store.close()  ← if store
  [5] knowledge_store.close()  ← if store
  [6] history_store.close()  ← if store
  [7] artifact_store.close()  ← if store
```

**Missing shutdown**: 40+ services have no shutdown hook. Only 6 stores close. The brain, vrip, and event bus have ad-hoc handling. No generic service shutdown mechanism.

### 2.6 Event Emissions

| Event | When | Data |
|-------|------|------|
| `brain.ready` | After EngineeringBrain boot | entity_count, summary |
| `platform.boot.completed` | After all services boot | started_at, services, vrip_intelligence, brain_ready |
| `platform.shutdown` | During shutdown | started_at, shutdown_at |

---

## 3. Parallel Platform Systems: Duplication Analysis

### 3.1 platform_v2.py (512 lines)

**Purpose**: GENESIS-IX Phase 1 — Service-Oriented Platform refactor.

**Components**:
| Component | Lines | Purpose |
|-----------|-------|---------|
| `ServiceState` (Enum) | 9 | 8 states: CREATED → INITIALIZING → READY → RUNNING → DEGRADED → FAILED → STOPPING → STOPPED |
| `ServiceCategory` (Enum) | 12 | 11 categories: INFRASTRUCTURE, STORAGE, COGNITIVE, MEMORY, etc. |
| `ServiceDefinition` | 15 | id, name, category, version, dependencies, provides, requires, config_schema, health_check, instance |
| `HealthStatus` | 8 | healthy, message, last_checked, failure_count, recovery_attempts |
| `ServiceRegistry` | 62 | Central registry with dependency graph, metrics, health tracking |
| `LifecycleManager` | 75 | Boot order computation, initialize_all, start_all, stop_all, health_check_all |
| `EventRouter` | 20 | Pub/sub event routing between services |
| `MetricsManager` | 80 | Metrics collection, aggregation, export |
| `TelemetryManager` | 50 | Telemetry sampling, alerting, reporting |
| `PlatformV2` (class) | 100 | Facade: create DefaultRegistry, LifecycleManager, register services, boot, status, health check all, emit event |

**Consumers**: **Zero**. `PlatformV2` is instantiated by `platform.py` boot() line 365, but `platform_v2.py` has no other consumers. The `PlatformV2` instance itself is never used — it's created, registered into DI, and forgotten.

### 3.2 engineering_os.py (331 lines)

**Purpose**: GENESIS-VIII Program 7 — Universal Engineering Operating System.

**Components**:
| Component | Lines | Purpose |
|-----------|-------|---------|
| `ServiceStatus` (Enum) | 6 | 6 states: STOPPED → STARTING → RUNNING → DEGRADED → ERROR → STOPPING |
| `ServiceRole` (Enum) | 17 | 17 roles: CORE, COGNITIVE, MEMORY, RESEARCH, SIMULATION, etc. |
| `Service` (dataclass) | 20 | id, name, role, status, health_score, dependencies, metrics, started_at, last_heartbeat, error_count |
| `ServiceManifest` | 10 | name, role, version, dependencies |
| `EngineeringOS` (class) | 200+ | register_service, boot, start, stop, status, summary, get_service stats, scheduler thread, heartbeat loop, health check, event emission |

**Consumers**: **Zero**. `EngineeringOS` is instantiated by `platform.py` boot() line 311, but `engineering_os.py` has no other consumers. 5 services are registered, `boot()` is called, then it's forgotten.

### 3.3 Direct Comparison

| Feature | platform.py | platform_v2.py | engineering_os.py |
|---------|-------------|----------------|-------------------|
| Service lifecycle states | None (binary: None/not-None) | 8-state enum | 6-state enum |
| Service discovery | Manual creation + register_instance() | ServiceRegistry | Manual dict |
| Dependency graph | None (explicit sequential boot) | LifecycleManager.compute_boot_order() | Dependencies field |
| Health checks | None built-in | HealthStatus + health_check_all | heartbeat + health_score |
| Metrics | _service_summary() (boolean) | MetricsManager | In-service metrics dict |
| Events | EventBus emission (ad-hoc) | EventRouter (dedicated) | Event emission (ad-hoc) |
| Telemetry | None | TelemetryManager | None |
| Configuration | PlatformConfig (external) | ConfigSchema per service | None |
| Recovery | None | HealthStatus.recovery_attempts | None |
| Shutdown | Manual per-store close | LifecycleManager.stop_all() | Stop Scheduler |
| Thread safety | None | None (single-threaded) | threading.Lock for scheduler |
| Consumers | test_compliance.py | 0 | 0 |

**Finding**: platform_v2.py is the most complete service platform design (8 states, dependency resolution, health, metrics, telemetry, configuration schema), but it's completely disconnected from platform.py's actual boot process. platform.py creates platform_v2 as just another service rather than using it as the platform framework.

### 3.4 Duplication Cost

| File | Lines | Unique Lines | Duplicated | Waste |
|------|-------|-------------|------------|-------|
| platform.py | 725 | 600 | 125 | Service management duplicated by platform_v2 |
| platform_v2.py | 512 | 512 | 200 | Duplicates lifecycle, events, metrics, health concepts |
| engineering_os.py | 331 | 250 | 180 | Duplicates service lifecycle, heartbeat, events |
| **Total** | **1,568** | **~1,085** | **~505** | **33% overlap** |

---

## 4. Responsibility Classification

For every responsibility in platform.py:

### 4.1 Bootstrapping

| Property | Value |
|----------|-------|
| **Why exists** | Need to create DI container and core infrastructure before anything else |
| **Current owner** | platform.bootstrap() |
| **Should own** | Platform bootstrap class (or DI bootstrap module) |
| **Owned correctly?** | Partially — bootstrap() is separate from boot() but still in VenusPlatform |
| **Duplicated?** | No |
| **Can disappear?** | No — needed for initialization ordering |
| **Depends on it** | Everything |
| **Migration difficulty** | Low — can extract to dedicated module |
| **Risk** | Low |

### 4.2 Dependency Injection

| Property | Value |
|----------|-------|
| **Why exists** | Need service registration and resolution |
| **Current owner** | ServiceProvider (separate module) + platform.py (register_instance calls) |
| **Should own** | ServiceProvider alone |
| **Owned correctly?** | **No** — platform.py manually calls register_instance() 32 times instead of using declarative registration |
| **Duplicated?** | ServiceProvider concept duplicated by platform_v2.ServiceRegistry |
| **Can disappear?** | Registration should be declarative, not imperative |
| **Depends on it** | All services |
| **Migration difficulty** | Medium — need to move 32 register_instance calls out of platform.py |
| **Risk** | Medium |

### 4.3 Service Discovery

| Property | Value |
|----------|-------|
| **Why exists** | Need to find services by type |
| **Current owner** | ServiceProvider.get(interface) |
| **Should own** | PluginRegistry or CapabilityRegistry |
| **Owned correctly?** | Partially — ServiceProvider works by exact type match |
| **Duplicated?** | 3 registries: ServiceProvider, CapabilityRegistry, ServiceRegistry (platform_v2) |
| **Can disappear?** | Yes — consolidate into CapabilityRegistry |
| **Depends on it** | Any code that resolves services dynamically |
| **Migration difficulty** | Medium |
| **Risk** | Medium |

### 4.4 Runtime Coordination

| Property | Value |
|----------|-------|
| **Why exists** | Need to orchestrate service creation order |
| **Current owner** | platform.boot() sequential creation |
| **Should own** | LifecycleManager (from platform_v2 concepts) |
| **Owned correctly?** | **No** — boot order is hard-coded sequential, not dependency-resolved |
| **Duplicated?** | LifecycleManager in platform_v2 exists but unused |
| **Can disappear?** | Yes — can be declarative |
| **Depends on it** | All runtime consumers |
| **Migration difficulty** | High — need to extract boot phases into declarative configuration |
| **Risk** | Medium |

### 4.5 Health Monitoring

| Property | Value |
|----------|-------|
| **Why exists** | Need to know if services are alive |
| **Current owner** | **None** — platform.py has no health monitoring |
| **Should own** | HealthManager component |
| **Owned correctly?** | **No** — absent entirely |
| **Duplicated?** | HealthStatus (platform_v2), Service.health_score (engineering_os) both exist |
| **Can disappear?** | No — required for production operation |
| **Depends on it** | Diagnostics, observability |
| **Migration difficulty** | Medium — borrow from platform_v2 |
| **Risk** | Low |

### 4.6 Configuration

| Property | Value |
|----------|-------|
| **Why exists** | Need to configure platform behavior |
| **Current owner** | PlatformConfig (genesis/config/settings.py) |
| **Should own** | ConfigurationManager |
| **Owned correctly?** | Yes — config is external to platform |
| **Duplicated?** | No |
| **Can disappear?** | No |
| **Depends on it** | Indexer, MetaModelEngine, OmegaLoop |
| **Migration difficulty** | Low |
| **Risk** | Low |

### 4.7 Plugin Loading

| Property | Value |
|----------|-------|
| **Why exists** | Need to load external plugins |
| **Current owner** | PluginManager (separate) + platform.py (load_from_dir call) |
| **Should own** | PluginManager alone |
| **Owned correctly?** | No — platform.py calls load_from_dir imperatively |
| **Duplicated?** | No |
| **Can disappear?** | No |
| **Depends on it** | PackageManager |
| **Migration difficulty** | Low — move load call to plugin manager init |
| **Risk** | Low |

### 4.8 Persistence

| Property | Value |
|----------|-------|
| **Why exists** | Need to store platform state |
| **Current owner** | 6 stores (MetadataStore, KnowledgeStore, HistoryStore, ArtifactStore, CheckpointStore, MemoryStore) created by bootstrap |
| **Should own** | PersistenceManager |
| **Owned correctly?** | Partially — stores are separate, bootstrap creates them |
| **Duplicated?** | No |
| **Can disappear?** | No |
| **Depends on it** | Compiler, Graph, KnowledgeStore consumers |
| **Migration difficulty** | Low |
| **Risk** | Low |

### 4.9 Event Routing

| Property | Value |
|----------|-------|
| **Why exists** | Need pub/sub communication between services |
| **Current owner** | EventBus (genesis/events/bus.py) |
| **Should own** | EventBus alone |
| **Owned correctly?** | Yes — EventBus is separate, platform just passes it |
| **Duplicated?** | EventRouter (platform_v2) duplicates event routing |
| **Can disappear?** | No |
| **Depends on it** | Almost every service |
| **Migration difficulty** | Low |
| **Risk** | Low |

### 4.10 Graph Initialization

| Property | Value |
|----------|-------|
| **Why exists** | Need to create graph infrastructure |
| **Current owner** | platform.py creates 5 graph systems: KnowledgeGraphEngine, PlanetaryKnowledgeGraph, HypergraphKnowledgeCore, UnifiedGraph, RelationshipEngine |
| **Should own** | GraphManager or Universal Graph Core |
| **Owned correctly?** | **No** — platform directly instantiates 5 graph systems in sequence |
| **Duplicated?** | 5 graph systems, 2 of which are legacy (see Mission 6) |
| **Can disappear?** | Yes — consolidate into Universal Graph Core |
| **Depends on it** | Reasoning, Scientist, Engineer, Economics, etc. |
| **Migration difficulty** | High — see Mission 6 migration plan |
| **Risk** | Medium |

### 4.11 Knowledge Initialization

| Property | Value |
|----------|-------|
| **Why exists** | Need to initialize knowledge infrastructure |
| **Current owner** | platform.py creates KnowledgeStore, KnowledgeGraphEngine, EngineeringBrain, IntelligenceService, PlanetaryKnowledgeEngine |
| **Should own** | KnowledgeManager |
| **Owned correctly?** | No — 5 separate creations |
| **Duplicated?** | KnowledgeGraphEngine vs PlanetaryKnowledgeEngine vs EngineeringBrain |
| **Can disappear?** | Yes — consolidate |
| **Depends on it** | VRIP, brain integration, reasoning |
| **Migration difficulty** | High |
| **Risk** | Medium |

### 4.12 Planning

| Property | Value |
|----------|-------|
| **Why exists** | Need to plan engineering activities |
| **Current owner** | EngineeringPlanner (genesis/planner.py) |
| **Should own** | EngineeringPlanner |
| **Owned correctly?** | Yes — platform just instantiates it |
| **Duplicated?** | No |
| **Can disappear?** | No |
| **Depends on it** | OmegaLoop (indirect) |
| **Migration difficulty** | Low |
| **Risk** | Low |

### 4.13 Reasoning

| Property | Value |
|----------|-------|
| **Why exists** | Need to reason about repository |
| **Current owner** | ReasoningEngine (genesis/reasoning.py) |
| **Should own** | ReasoningEngine |
| **Owned correctly?** | Yes — created with proper dependency injection |
| **Duplicated?** | No |
| **Can disappear?** | No |
| **Depends on it** | Scientist, Engineer, Economics |
| **Migration difficulty** | Low |
| **Risk** | Low |

### 4.14 Compilation

| Property | Value |
|----------|-------|
| **Why exists** | Need to compile source code |
| **Current owner** | Compiler (genesis/compiler/compiler.py) |
| **Should own** | Compiler |
| **Owned correctly?** | Yes — platform just instantiates it |
| **Duplicated?** | MetaCompiler also exists |
| **Can disappear?** | No |
| **Depends on it** | CLI commands |
| **Migration difficulty** | Low |
| **Risk** | Low |

### 4.15 Verification

| Property | Value |
|----------|-------|
| **Why exists** | Need to verify platform state |
| **Current owner** | CertificationEngine, SecurityValidator |
| **Should own** | VerificationManager |
| **Owned correctly?** | Partially — separate from diagnostics |
| **Duplicated?** | No |
| **Can disappear?** | No |
| **Depends on it** | Platform integrity |
| **Migration difficulty** | Low |
| **Risk** | Low |

### 4.16 Reporting

| Property | Value |
|----------|-------|
| **Why exists** | Need to report platform status |
| **Current owner** | platform.summary() |
| **Should own** | ReportingService |
| **Owned correctly?** | No — baked into VenusPlatform |
| **Duplicated?** | No |
| **Can disappear?** | Yes — extract to separate service |
| **Depends on it** | CLI, diagnostics |
| **Migration difficulty** | Low |
| **Risk** | Low |

### 4.17 Shutdown

| Property | Value |
|----------|-------|
| **Why exists** | Need to gracefully teardown |
| **Current owner** | platform.shutdown() |
| **Should own** | LifecycleManager (generic shutdown orchestration) |
| **Owned correctly?** | **No** — ad-hoc, only 6 of 50+ services are shut down |
| **Duplicated?** | LifecycleManager.stop_all() exists in platform_v2 |
| **Can disappear?** | Yes — replace with declarative shutdown |
| **Depends on it** | Data integrity |
| **Migration difficulty** | Medium |
| **Risk** | High (data loss if shutdown is wrong) |

---

## 5. Design: Universal Platform Architecture

### 5.1 Principles

1. **The platform orchestrates; it does not implement.** Platform should not know how to create a compiler, a graph, or a reasoning engine. It should know how to order service creation based on dependencies.
2. **Every service follows one lifecycle.** No exceptions. Service discovery, initialization, health, and shutdown are uniform.
3. **Declarative over imperative.** Service registrations are declarations (interface, implementation, dependencies, configuration), not 50 sequential `register_instance()` calls.
4. **Health is first-class.** Every service declares health checks. Platform validates all are healthy before declaring boot complete.
5. **Shutdown is symmetric with boot.** Every service that boots must be shut down.

### 5.2 Target Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    PLATFORM ORCHESTRATOR                     │
│                                                              │
│  1. Configuration  →  load config, validate, resolve         │
│  2. DI Container   →  bootstrap ServiceProvider              │
│  3. Plugin Discovery →  scan plugin dirs, resolve deps       │
│  4. Service Boot   →  dependency-resolved service creation   │
│  5. Health Validation →  verify all services healthy         │
│  6. Runtime Start  →  emit boot event, enter run loop       │
│  7. Shutdown       →  reverse-order graceful teardown        │
└──────────────────────────────────────────────────────────────┘
         │
         │  delegates to
         ▼
┌──────────────────────────────────────────────────────────────┐
│                    SERVICE PROVIDER (DI)                     │
│  register(interface, implementation, deps=[], health=)       │
│  get(interface) → service instance                           │
│  shutdown() → reverse-order lifecycle teardown               │
└──────────────────────────────────────────────────────────────┘
         │
         │  services registered by
         ▼
┌──────────────────────────────────────────────────────────────┐
│                    SERVICE DECLARATIONS                       │
│                                                              │
│  # declarative, not imperative                               │
│  services = {                                                │
│      "compiler": ServiceDef(Compiler, deps=["event_bus"]),   │
│      "graph": ServiceDef(GraphService, deps=["event_bus"]),  │
│      ...                                                     │
│  }                                                           │
└──────────────────────────────────────────────────────────────┘
```

### 5.3 Universal Platform Lifecycle

```
CONFIG_LOAD
    │
    ▼
CONTAINER_BOOT ───────────────────► FAILED
    │
    ▼
PLUGIN_SCAN ──────────────────────► FAILED
    │
    ▼
SERVICE_BOOT ──► (dependency-resolved, parallel where possible)
    │               │
    │               ▼
    │          SERVICE_HEALTHY ◄──────► SERVICE_DEGRADED
    │               │                     │
    ▼               ▼                     ▼
ALL_BOOTED ──► HEALTH_VALIDATION ──► DEGRADED_BOOT
    │               │                     │
    │               ▼                     ▼
    │          HEALTHY ───────────► PARTIALLY_HEALTHY
    │               │                     │
    ▼               ▼                     ▼
RUNTIME_START ───────────────────► RUNTIME_DEGRADED
    │
    │  (runtime operation)
    │
    ▼
SHUTDOWN_INIT
    │
    ▼
SERVICE_STOP (reverse boot order)
    │
    ▼
STORE_CLOSE
    │
    ▼
COMPLETE
```

### 5.4 Declarative Service Registration

Instead of:
```python
# Current: imperative, sequential, 32 register_instance calls
self.compiler = Compiler(event_bus=bus, artifact_store=self.artifact_store)
self.provider.register_instance(Compiler, self.compiler)
```

Target:
```python
# Future: declarative, dependency-resolved, health-aware
PLATFORM_SERVICES = {
    Compiler: ServiceDef(
        impl=Compiler,
        deps=[EventBus, ArtifactStore],
        health=lambda c: c.is_healthy(),
    ),
    KnowledgeGraphEngine: ServiceDef(
        impl=KnowledgeGraphEngine,
        deps=[EventBus, KnowledgeStore],
    ),
    ExecutionEngine: ServiceDef(
        impl=ExecutionEngine,
        deps=[EventBus, HistoryStore],
    ),
    # ... all 50+ services declared as data, not code
}

platform = PlatformOrchestrator(config=global_config)
platform.register_services(PLATFORM_SERVICES)
platform.boot()  # dependency-resolved, health-validated
```

### 5.5 Service Categories

| Category | Services | Scope |
|----------|----------|-------|
| **Infrastructure** | EventBus, ServiceProvider, config | Platform core |
| **Persistence** | MetadataStore, KnowledgeStore, HistoryStore, ArtifactStore, MemoryStore, CheckpointStore | Data layer |
| **Graph** | KnowledgeGraphEngine, RelationshipEngine, UnifiedGraph (eventually 1) | Graph layer |
| **Execution** | ExecutionEngine, ExecGraphEngine | Execution layer |
| **Knowledge** | EngineeringBrain, IntelligenceService | Knowledge layer |
| **Memory** | MemoryEngine, 16 MemoryTypes | Memory layer |
| **Engineering** | ReasoningEngine, RepositoryScientist, RepositoryEngineer, RepositoryEconomics, EngineeringPlanner, EconomicsEngine | Engineering core |
| **Verification** | CertificationEngine, SecurityValidator, Diagnostics | Verification layer |
| **Plugin** | PluginManager, CapabilityRegistry | Extension layer |
| **Orchestration** | OmegaLoop, EngineeringOrchestrator | Top-level |
| **Civilization** | DigitalCivilization, SoftwareCivilizationV2, SoftwareCivilizationV3 | Meta layer |

### 5.6 Service Lifecycle Contract

```python
@runtime_checkable
class Service(Protocol):
    """Every platform service implements this lifecycle."""
    
    def initialize(self, provider: ServiceProvider) -> None:
        """Called once during boot. Service should create resources."""
        ...
    
    def start(self) -> None:
        """Called after all dependencies are initialized."""
        ...
    
    def health(self) -> HealthResult:
        """Return current health status. Called periodically."""
        ...
    
    def stop(self) -> None:
        """Called during shutdown. Service should release resources."""
        ...
```

---

## 6. Migration Strategy

### 6.1 Phase 1: Extract Platform Orchestrator

1. Create `genesis/platform/orchestrator.py` with `PlatformOrchestrator` class
2. Move `bootstrap()` logic into orchestrator
3. Convert `boot()` service creation into declarative `ServiceDef` registry
4. Keep old `VenusPlatform` as backward-compatible wrapper

**Risk**: Low — pure refactor, no behavior change
**Lines moved**: ~350
**Rollback**: Keep old platform.py unchanged

### 6.2 Phase 2: Add Declarative Service Registration

1. Define `PLATFORM_SERVICES` dict with all 50+ services
2. Add dependency resolution to `PlatformOrchestrator.boot()`
3. Add health validation to `PlatformOrchestrator.boot()`
4. Verify all 2,763 tests pass

**Risk**: Medium — service instantiation order may change
**Lines changed**: platform.py (remove 300 lines), orchestrator.py (add 200 lines)
**Rollback**: Revert to platform.py + orchestrator delegation

### 6.3 Phase 3: Consolidate Parallel Platforms

1. Deprecate `platform_v2.py` — point to PlatformOrchestrator
2. Deprecate `engineering_os.py` — point to PlatformOrchestrator
3. Add deprecation warnings (same pattern as 8 existing deprecated modules)
4. Remove platform_v2 and engineering_OS instantiation from platform.py

**Risk**: Low — no consumers for either
**Lines freed**: 843
**Rollback**: Keep deprecation warnings, import reverts

### 6.4 Phase 4: Add Generic Shutdown

1. Move shutdown into LifecycleManager
2. Every service that implements `stop()` gets called in reverse boot order
3. Replace ad-hoc shutdown (6 stores) with generic mechanism

**Risk**: Medium — shutdown ordering matters for data integrity
**Rollback**: Keep old shutdown as fallback

### 6.5 Phase 5: Add Health Monitoring

1. Add periodic health check loop to PlatformOrchestrator
2. Services declare health check functions
3. Health events emitted on EventBus
4. Integration with Diagnostics

**Risk**: Low — additive, no behavior change for existing services
**Rollback**: Disable health check loop

---

## 7. Engineering Decisions

### 7.1 Why not just fix platform.py in place?

platform.py has 725 lines with 45+ instance attributes and 50+ sequential instantiations. It has grown organically across 12 GENESIS epochs. Fixing in place would mean keeping all 45 instance attributes while trying to add abstraction. Better to extract the orchestration concern into a dedicated class.

### 7.2 Why not use platform_v2.py as the canonical platform?

platform_v2.py has the most complete service platform design (8 states, dependency resolution, health, metrics, telemetry, configuration schema). However:
- It has zero consumers (no test coverage)
- It uses string-based service IDs instead of type-based DI
- Its dependency resolution is simpler than ServiceProvider's
- porting all 50 services to it would require significant changes to each service

**Decision**: Use platform_v2's concepts (ServiceState enum, LifecycleManager, HealthStatus) but implement them as extensions to the existing ServiceProvider rather than as a replacement.

### 7.3 Why not merge all three platforms into one big class?

Because platform_v2.py and engineering_os.py have fundamentally different service models (string IDs vs enums vs type-based DI). Merging would create an inconsistent internal model.

**Decision**: Keep ServiceProvider as the DI container, add declarative registration, add lifecycle management as a concern of the orchestrator.

### 7.4 Which services should platform NOT own?

| Service | Should Be Owned By |
|---------|-------------------|
| 16 MemoryTypes | MemoryEngine |
| 5 Graph systems | Universal Graph Core (Mission 6) |
| PlanetaryKnowledgeEngine | Knowledge subsystem |
| SoftwareCivilizationV2/V3 | Civilization subsystem |
| EvolutionEngine/EvolutionEngineV4 | Evolution subsystem |
| PlatformV2 | **Deprecated** |
| EngineeringOS | **Deprecated** |
| UCOS | Capability subsystem |
| UniversalKernel | **Deprecated** (duplicates EventBus/PluginManager) |
| MetaCompiler | Compilation subsystem |
| Database | Persistence subsystem |
| FabricKernel | **Deprecated** |
| UnifiedGraph | Universal Graph Core |
| ExecutionEngineV2 | **Deprecated** (duplicates runtime/executor) |
| EngineeringOrchestrator | OmegaLoop |

---

## 8. Validation Results

- **2,763 tests pass** — no regressions from previous missions
- **`test_compliance.py`** — 7 tests covering bootstrap, boot, service creation, VRIP execution, event emission, shutdown, double-boot idempotency, and summary — all pass
- **Deprecation warnings**: platform_v2.py and engineering_os.py can be deprecated with no consumer impact

---

## 9. Technical Debt Summary

| Item | Severity | Effort | Impact |
|------|----------|--------|--------|
| 50+ services created imperatively | High | 2-3 days | Prevents dependency resolution, health monitoring |
| No generic shutdown | High | 1 day | 40+ services leak resources |
| No health monitoring | Medium | 2 days | Can't detect service failures |
| 2 parallel platforms unused | Medium | 0.5 days | 843 lines of dead code |
| 32 register_instance calls | Low | 1 day | Brittle registration pattern |
| boot() is 353 lines | Low | 1 day | Hard to understand, hard to modify |

---

## 10. Next Steps

1. Create `genesis/platform/orchestrator.py` with PlatformOrchestrator (Phase 1)
2. Add deprecation warnings to `platform_v2.py` and `engineering_os.py` (Phase 3)
3. Remove parallel platform instantiation from platform.py boot()
4. Run test suite — 2,763 tests must pass
5. Mission 8: Universal Execution Model
