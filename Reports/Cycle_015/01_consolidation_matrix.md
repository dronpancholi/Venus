# Cycle 015 — Consolidation Matrix

## Architecture Decision Record

**Date:** Cycle 015  
**Status:** Approved  
**Impact:** Repository-wide  

---

## 1. KERNELS — 7 implementations → 1 canonical

### Competing Implementations

| Name | File | Lines | Consumers | Role |
|------|------|-------|-----------|------|
| **FabricKernel** | `fabric/kernel.py` | 354 | ~20 | Active runtime kernel |
| UniversalKernel | `kernel/kernel.py` | 80 | 4 | Legacy facade over 14 managers |
| ServiceKernel | `service_kernel.py` | 637 | 2 | VPS service lifecycle |
| VenusPlatform | `platform.py` | 725 | 8 | God-object boot orchestrator |
| PlatformAdapter | `platform_adapter.py` | 728 | 1 | Migration bridge |
| PlatformV2 | `platform_v2.py` | 512 | 4 | Service-oriented platform |
| EngineeringOS | `engineering_os.py` | 331 | 4 | OS abstraction |

### Decision

**Canonical: FabricKernel** (`genesis/fabric/kernel.py`)

**Rationale:** 
- Most consumers (~20 files including all desktop screens, server, watch, autonomous)
- Full lifecycle (BOOTING → RUNNING → DEGRADED → SHUTDOWN)
- Built-in MessageBus + EventRouter + ServiceRegistry + StorageEngine + Scheduler + PolicyEngine + Audit + Metrics
- Both VenusPlatform.boot() and PlatformAdapter.boot() instantiate it
- Desktop and server depend on it

**Migration:**
1. VenusPlatform → Keep for backward compatibility but no new development. Replace with direct FabricKernel instantiation.
2. PlatformAdapter → Migration bridge. Delete after all VenusPlatform consumers migrate.
3. UniversalKernel → Deprecate `kernel/`. Move SecurityManager, HealthManager, TaskScheduler into FabricKernel as optional extensions.
4. ServiceKernel → Absorb health/lifecycle logic into FabricKernel.
5. PlatformV2 → Historical artifact. No new consumers.
6. EngineeringOS → Historical artifact. No new consumers.

---

## 2. EVENT SYSTEMS — 4 implementations → 1 canonical

| Name | File | Lines | Consumers | Event Model |
|------|------|-------|-----------|-------------|
| **EventRouter** | `fabric/events.py` | 254 | ~7 | EngineeringEvent (18 fields) |
| EventRouter (kernel) | `kernel/event_router.py` | 103 | 3 | KernelEvent (6 fields) |
| EventBus | `events/bus.py` | 97 | ~30 | (type, data) tuple |
| EventRouter (P2) | `platform_v2.py` | inline | 0 | Plain dict |

### Decision

**Canonical: EventRouter** (`genesis/fabric/events.py`)

**Rationale:**
- Richest event model (correlation_id, causation_id, session_id, priority, severity, tags, confidence, TTL)
- Filtered subscriptions, bounded EventStore (50K events, 6 indexes), dead-letter queue, stats
- Thread-safe, designed for distributed Fabric architecture
- `EventBus` has 30 consumers but is primitive — no filtering, no event store, no query

**Migration:**
1. EventBus → Add `FabricEventBusAdapter` that wraps Fabric's EventRouter and exposes the same `subscribe(handler)`, `emit(type, data)` API. All 30 consumers continue to work unchanged.
2. Kernel EventRouter → Replace with Fabric EventRouter. Similar consumer interface.

---

## 3. GRAPH SYSTEMS — 5 implementations → 1 canonical

| Name | File | Lines | Consumers | Backend |
|------|------|-------|-----------|---------|
| **UnifiedGraph** | `graph_v2/core.py` | 269 | ~20 | In-memory with layers |
| KnowledgeGraphEngine | `graph/engine.py` | 305 | ~13 | UIRGraph + KnowledgeStore |
| PersistentGraphDB | `graphdb/__init__.py` | 835 | 5 | SQLite |
| KnowledgeGraph | `knowledge_graph.py` | 320 | ~25 | In-memory |
| Hypergraph | `hypergraph.py` | 648 | 6 | In-memory |

### Decision

**Canonical: UnifiedGraph** (`genesis/graph_v2/core.py`)

**Rationale:**
- Broadest usage (~20 consumers including metamodel, autonomous, acquisition, datalake, temporal)
- Multi-layer architecture (STRUCTURAL, SEMANTIC, CAPABILITY, KNOWLEDGE, COLLABORATION, EVOLUTION)
- Already has adapters from KnowledgeGraphEngine and Hypergraph
- Integrated with repository graph, platform, and desktop

**Migration:**
1. KnowledgeGraphEngine → Already has adapter in `graph_v2/adapter.py`. Deprecate direct usage.
2. PersistentGraphDB → Keep as UnifiedGraph's persistence backend. Already has `load_from_unified_graph()`.
3. KnowledgeGraph/PlanetaryKnowledgeGraph → Migrate consumers to UnifiedGraph layers.
4. Hypergraph → Wrap as UnifiedGraph layer with hyperedge extension.

---

## 4. STORAGE SYSTEMS — 4 implementations → 1 canonical

| Name | File | Lines | Tables | Consumers |
|------|------|-------|--------|-----------|
| **SQLiteStore** | `persistence/sqlite_store.py` | 572 | 6 | ~18 |
| StorageEngine | `fabric/storage.py` | 957 | 10 | ~8 |
| Repository[T] | `persistence/repository.py` | 147 | Generic | 2 |
| StorageManager | `kernel/storage_manager.py` | 93 | None | 3 |

### Decision

**Canonical: SQLiteStore** (`genesis/persistence/sqlite_store.py`) for platform-level storage, **StorageEngine** (`fabric/storage.py`) for fabric-level storage. Unify connection management.

**Rationale:**
- SQLiteStore/StorageEngine serve different purposes (platform vs fabric) but both use SQLite+WAL
- Repository[T] is a good abstract interface — keep as base for new stores
- StorageManager (kernel) is in-memory only with no real consumers — delete

**Migration:**
1. Unify SQLiteStore and StorageEngine under a common `BaseStore` with shared connection management
2. Delete StorageManager (kernel/storage_manager.py)
3. Keep Repository[T] as abstract base for typed stores

---

## 5. EXECUTION ENGINES — 4 implementations → 1 canonical

| Name | File | Lines | Consumers | AI Integration |
|------|------|-------|-----------|----------------|
| **AgentExecutionEngine** | `fabric/execution.py` | 473 | 5 | Yes (AIRouter + role prompts) |
| ExecutionEngine | `execution/engine.py` | 105 | 7 | No |
| ExecutionEngine | `runtime/executor.py` | 266 | 8 | No |
| AutonomousRuntime | `os/runtime.py` | 499 | 3 | No |

### Decision

**Canonical: AgentExecutionEngine + TaskExecutor** (`genesis/fabric/execution.py`) for AI-powered execution; **execution/engine.py** for general execution.

**Rationale:**
- `fabric/execution.py` is the only engine that integrates with AI providers (Genesis's core mission)
- `execution/engine.py` is the most comprehensive non-AI engine (workflows, tasks, actors, pipelines, jobs)
- `runtime/executor.py` is legacy from GENESIS-II era — replace all consumers
- `os/runtime.py` has agent assignment but less mature

**Migration:**
1. `runtime/executor.py` consumers → migrate to `fabric/execution.py` (AI tasks) or `execution/engine.py` (non-AI tasks)
2. `os/runtime.py` → autonomous process execution should go through Fabric's AgentExecutionEngine

---

## 6. MEMORY SYSTEMS — 7 implementations → 1 canonical

| Name | File | Lines | Consumers | Type Model |
|------|------|-------|-----------|------------|
| **UniversalMemorySystem** | `memory_system.py` | 413 | 6 | 18 memory types |
| EngineeringMemory | `memory/engineering.py` | 252 | 6 | Sessions + cross-indexing |
| InstitutionalMemory | `memory/institutional.py` | 259 | 1 | Knowledge objects + timeline |
| MemoryTypes | `memory/types.py` | 488 | 4 | 16 legacy types |
| EngineeringBrain | `brain/` package | ~1,600 | ~20 | Full cognitive architecture |
| MemoryEngine | `memory/engine.py` | 65 | 7 | Simple key-value |
| MemoryManager | `kernel/memory_manager.py` | 105 | 3 | Abstract blocks |

### Decision

**Canonical: UniversalMemorySystem** (`genesis/memory_system.py`) — EngineeringMemory and InstitutionalMemory are valid extensions.

**Rationale:**
- UniversalMemorySystem defines the canonical `MemoryType` enum (18 types) and `MemoryEntry` dataclass
- EngineeringMemory and InstitutionalMemory build on it with sessions and knowledge objects
- EngineeringBrain is a higher-level cognitive system, not just memory — keep separate
- MemoryTypes (16 legacy) are fully duplicated by UniversalMemorySystem's 18 types

**Migration:**
1. `memory/types.py` → replace all imports with `memory_system.py` equivalents
2. `MemoryEngine` → replace with `EngineeringMemory`
3. `MemoryManager` (kernel) → delete

---

## 7. PLUGIN SYSTEMS — 3 implementations → 1 canonical

| Name | File | Lines | Consumers | Features |
|------|------|-------|-----------|----------|
| **PluginManager** | `plugin/manager.py` | 236 | ~7 | Manifest, lifecycle, hooks, deps, hot-reload, sandbox |
| PluginLoader | `kernel/plugin_loader.py` | 105 | 3 | Module discovery, generic hooks |
| ModulePluginRegistry | `plugin/registry.py` | 110 | 3 | Name-to-instance engine registry |

### Decision

**Canonical: PluginManager** (`genesis/plugin/manager.py`)

**Rationale:** Only one with full lifecycle management, manifest-based discovery, dependency resolution, hot-reload, sandboxing, validation.

**Migration:**
1. PluginLoader → Add `load_module()` convenience to PluginManager, then deprecate
2. ModulePluginRegistry → Keep as-is (different purpose — lightweight engine registry)

---

## 8. DI CONTAINERS — 2 implementations → 1 canonical

| Name | File | Lines | Consumers | Type Safety |
|------|------|-------|-----------|-------------|
| **ServiceProvider** | `di/container.py` | 207 | 6 | Strong (Python types) |
| DIKernel | `kernel/di_kernel.py` | 96 | 4 | Weak (strings) |

### Decision

**Canonical: ServiceProvider** (`genesis/di/container.py`)

**Rationale:** Type-safe (Python types as keys), lazy init, singleton scoping, constructor injection, shutdown hooks. DIKernel uses strings (error-prone) and lacks lifecycle.

**Migration:**
1. Add `register_factory()` and `find_by_tag()` to ServiceProvider for feature parity
2. Migrate DIKernel consumers to ServiceProvider
3. Deprecate DIKernel

---

## Summary

| Priority | Area | Canonical Path | Status |
|----------|------|----------------|--------|
| P0 | Server launcher | `server.py:run_server()` | ✅ FIXED |
| P0 | WS async safety | `server.py` async queue pattern | ✅ FIXED |
| P0 | Dead run_desktop | Removed from `__main__.py` | ✅ FIXED |
| P1 | EventBus migration | Adapter pattern | 📋 Planned |
| P1 | Storage connection | Common BaseStore | 📋 Planned |
| P1 | Desktop tests | conftest.py + pilot | 📋 Planned |
| P2 | Kernel consolidation | FabricKernel canonical | 📋 In progress |
| P2 | Graph consolidation | UnifiedGraph canonical | 📋 In progress |
| P2 | Memory consolidation | UniversalMemorySystem canonical | 📋 In progress |
