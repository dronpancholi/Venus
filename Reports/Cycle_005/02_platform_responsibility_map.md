# Mission 21 — Phase 2 & 3
# Platform Responsibility Classification & Canonical Mapping

**Derived from:** Phase 1 engineering evidence (`01_platform_convergence_evidence.md`)
**Objective:** Classify every responsibility in VenusPlatform, map each to its canonical owner

---

## Classification Key

For each responsibility we determine:

| Attribute | Description |
|---|---|
| **Purpose** | What does this responsibility do? |
| **Owner** | Which generation/class owns it today? |
| **Consumers** | Who reads/writes this field or calls this method? |
| **Side effects** | What state changes happen? |
| **Dependencies** | What must exist before this can work? |
| **Complexity** | Cyclomatic complexity (1–25) |
| **Lifecycle phase** | bootstrap, boot, runtime, shutdown |
| **Canonical replacement** | Which Cycle 003/004 component replaces this? |
| **Migration strategy** | Adapter, delegate, inline, or remove |

---

## 1. Lifecycle Responsibilities

### 1.1 `__init__()` — Field Declaration (L107–181)
- **Purpose:** Declare all 51 fields as None
- **Owner:** VenusPlatform
- **Consumers:** All methods
- **Side effects:** None
- **Complexity:** ~1
- **Lifecycle:** Construction
- **Canonical replacement:** → `ServiceKernel.__init__()`
- **Migration strategy:** Adapter delegates field access to `ServiceKernel`

### 1.2 `_booted` flag (L111)
- **Purpose:** Prevent double-boot
- **Owner:** VenusPlatform
- **Consumers:** `boot()`, `summary()`
- **Canonical replacement:** → `LifecycleManager.state == ServiceState.HEALTHY`
- **Migration strategy:** Adapter delegates to `LifecycleManager`

### 1.3 `_started_at` (L112)
- **Purpose:** ISO timestamp of boot completion
- **Owner:** VenusPlatform
- **Consumers:** `boot()`, `shutdown()`, `summary()`
- **Canonical replacement:** → `MetricsCollector.boot_timestamp`
- **Migration strategy:** Adapter delegates to `MetricsCollector`

### 1.4 `bootstrap()` (L183–197)
- **Purpose:** Create DI container, register 6 persistence stores
- **Owner:** VenusPlatform
- **Consumers:** `boot()`, `test_compliance.py`
- **Complexity:** ~3
- **Canonical replacement:** → `ServiceKernel.boot()` (Mission 14) + DI bootstrap already exists as `genesis.di.bootstrap`
- **Migration strategy:** Adapter delegates boot sequence to `PlatformOrchestrator`; stores registered via DI container

### 1.5 `boot()` (L199–551) — 52-step monolith
- **Purpose:** Wire all 35+ services across 10 generations
- **Owner:** VenusPlatform
- **Consumers:** `test_compliance.py`, `main()`
- **Complexity:** ~52 (worst in codebase)
- **Canonical replacement:** → `PlatformOrchestrator.boot()` (Mission 13) with service definitions for each component
- **Migration strategy:** Each sub-section becomes a `ServiceDef` registered with `PlatformOrchestrator`. The 52-step sequence becomes a dependency graph.

### 1.6 `shutdown()` (L641–655)
- **Purpose:** Graceful teardown, save checkpoint, close stores
- **Owner:** VenusPlatform
- **Consumers:** DI shutdown hook, `test_compliance.py`, `main()`
- **Complexity:** ~5
- **Canonical replacement:** → `PlatformOrchestrator.shutdown()` (reverse-order, all services)
- **Migration strategy:** Adapter delegates to `PlatformOrchestrator.shutdown()`

### 1.7 `summary()` (L657–677)
- **Purpose:** Return platform status dict
- **Owner:** VenusPlatform
- **Consumers:** `main()` CLI, `test_compliance.py`
- **Complexity:** ~5
- **Canonical replacement:** → `ServiceKernel.summary()` (Mission 14) + `PlatformOrchestrator.boot_report()`
- **Migration strategy:** Adapter assembles from canonical components

---

## 2. Persistence Store Responsibilities

### 2.1 `event_bus` (L114)
- **Purpose:** Event-driven communication backbone
- **Owner:** bootstrap() via DI
- **Canonical:** Already canonical — `genesis.events.bus.EventBus`
- **Migration strategy:** No change needed; already managed by DI

### 2.2 `metadata_store`, `knowledge_store`, `history_store`, `artifact_store`, `checkpoint_store`, `memory_store` (L115–120)
- **Purpose:** SQLite-backed persistence for each domain
- **Owner:** bootstrap() via DI + MemoryStore(disk)
- **Canonical:** Already canonical — `genesis.persistence.*`
- **Migration strategy:** Group into `PersistenceManager` service; register as managed services with `PlatformOrchestrator`

---

## 3. Core Service Responsibilities

### 3.1 `compiler` — `Compiler` (L210)
- **Purpose:** Compile UIR → executable code
- **Canonical:** Already canonical in `genesis.compiler.compiler`
- **Strategy:** Register as managed service via ServiceDef

### 3.2 `graph` — `KnowledgeGraphEngine` (L214)
- **Purpose:** Graph-based knowledge representation (legacy V1)
- **Canonical replacement:** → `UnifiedGraph` (GENESIS-XII)
- **Consumers:** `brain.sync_uir_graph()`, evolution metrics
- **Strategy:** Deprecate → redirect to `UnifiedGraph`; keep adapter for `sync_uir_graph`

### 3.3 `executor` — `ExecutionEngine` V1 (L218)
- **Purpose:** Execute compiled plans (legacy)
- **Canonical replacement:** → `ExecutionEngineV2` (GENESIS-XII)
- **Strategy:** Deprecate → redirect to `ExecutionEngineV2`

### 3.4 `metadata` — `MetadataEngine` (L222)
- **Purpose:** Track repository metadata records
- **Canonical replacement:** → `MetaModelEngine` (GENESIS-XIII)
- **Strategy:** Deprecate → merge into `MetaModelEngine`

### 3.5 `diagnostics` — `Diagnostics` (L226)
- **Purpose:** System diagnostics and health reporting
- **Canonical replacement:** → `ServiceKernel.HealthManager`
- **Strategy:** Adapter — `HealthManager` provides richer diagnostics

### 3.6 `indexer` — `RepositoryIndexer` (L230)
- **Purpose:** Index repository files
- **Canonical replacement:** → `SelfAnalyzer` (Mission 20)
- **Strategy:** Adapter — `SelfAnalyzer.analyze()` supersedes `RepositoryIndexer`

### 3.7 `plugins` — `PluginManager` (L234–239)
- **Purpose:** Load and manage plugins
- **Canonical:** Already canonical in `genesis.plugin.manager`
- **Strategy:** Register as managed service

### 3.8 `capabilities` — `CapabilityRegistry` (L242)
- **Purpose:** Service capability discovery (legacy)
- **Canonical replacement:** → `EngineCapabilityRegistry` (Mission 15)
- **Strategy:** Adapter wraps `EngineCapabilityRegistry`

### 3.9 `package` — `PackageManager` (L246)
- **Purpose:** Package management
- **Canonical:** Already canonical in `genesis.package.manager`
- **Strategy:** Register as managed service

### 3.10 `memory_engine` — `MemoryEngine` (L250)
- **Purpose:** Memory persistence (legacy V1)
- **Canonical replacement:** → `EngineeringMemory` (Mission 16) + `UniversalMemorySystem`
- **Strategy:** Adapter delegates to `EngineeringMemory`

---

## 4. Project & Security Responsibilities

### 4.1 `project_mgr` — `ProjectManager` (L254)
- **Canonical:** Already canonical
- **Strategy:** Register as managed service

### 4.2 `certification` — `CertificationEngine` (L258)
- **Canonical:** Already canonical
- **Strategy:** Register as managed service

### 4.3 `security` — `SecurityValidator` (L262)
- **Canonical replacement:** → `Governance` (Mission 19) composes `PolicyEngine` + `AuditTrail`
- **Strategy:** Adapter delegates auth/audit to `Governance`

---

## 5. Intelligence Responsibilities

### 5.1 `brain` — `EngineeringBrain` (L267–278)
- **Purpose:** Universal entity model with UIR graph sync
- **Canonical replacement:** → `EngineeringBrainV4` (GENESIS-IX)
- **Consumers:** `vrip`, `digital_twin`, evolution metrics, `brain/integration.py`
- **Strategy:** Adapter preserves `sync_uir_graph()`, `start_integration()`, `summary()`; delegates to `EngineeringBrainV4`

### 5.2 `vrip` — `IntelligenceService` (L281–283)
- **Purpose:** VRIP intelligence — runs automatically on boot, syncs to brain
- **Canonical replacement:** → `AutonomousEngine` + `EngineeringOrchestrator`
- **Consumers:** boot event metrics, checkpoint save in shutdown
- **Strategy:** Delegate to `EngineeringOrchestrator.run_cycle()`

### 5.3 `digital_twin` — `PlanetaryDigitalTwin` (L286)
- **Purpose:** Digital representation of the platform
- **Canonical replacement:** → This IS the target for Mission 28 (EngineeringDigitalTwin)
- **Strategy:** Keep as managed service placeholder until Mission 28

---

## 6. GENESIS-VIII Legacy Responsibilities (All Deprecated)

| Field | Purpose | Canonical Replacement | Strategy |
|---|---|---|---|
| `memory_types` (16x) | Legacy memory subtypes | `UniversalMemorySystem` | Deprecate; delegate to UMS |
| `physics` | Engineering Physics V2 | `genesis.physics` (standalone) | Register as managed service |
| `knowledge_graph` | Planetary Knowledge Graph | `UnifiedGraph` | Adapter on `UnifiedGraph` |
| `engineering_os` | Engineering OS | `ServiceKernel` | Adapter on `ServiceKernel` |
| `civilization` | Software Civilization V2 | `DigitalCivilization` | Adapter on `DigitalCivilization` |
| `evolution` | Evolution Engine V1 | `EvolutionEngineV4` | Adapter on `EvolutionEngineV4` |

---

## 7. GENESIS-IX Legacy Responsibilities (All Deprecated)

| Field | Purpose | Canonical Replacement | Strategy |
|---|---|---|---|
| `platform_v2` | Platform refactor V2 | **Self-referential** → `ServiceKernel` | Remove — this is the same god-object pattern refactored |
| `brain_v4` | Engineering Brain V4 | Already canonical | Register as managed service |
| `ums` | Universal Memory V3 | `EngineeringMemory` | Adapter on `EngineeringMemory` |
| `hypergraph_core` | Hypergraph Knowledge Core | `UnifiedGraph` | Adapter on `UnifiedGraph` |
| `planetary_knowledge` | Planetary Knowledge Engine | `UnifiedGraph` | Adapter on `UnifiedGraph` |
| `civilization_v3` | Software Civilization V3 | `DigitalCivilization` | Adapter on `DigitalCivilization` |
| `evolution_v4` | Evolution Engine V4 | Already canonical | Register as managed service |

---

## 8. GENESIS-X/XI/XII Responsibilities (Already Canonical)

| Field | Status | Action |
|---|---|---|
| `ucos` | Legacy → `EngineCapabilityRegistry` + `Governance` | Adapter |
| `kernel` | Legacy → `ServiceKernel` | Adapter |
| `meta_compiler` | Already canonical | Register as managed service |
| `ued` | Already canonical | Register as managed service |
| `fabric` | Already canonical | Register as managed service |
| `unified_graph` | Already canonical | Register as managed service |
| `execution_engine` (V2) | Already canonical | Register as managed service |
| `orchestrator` | Already canonical | Register as managed service |

---

## 9. GENESIS-XIII / Ω³ Responsibilities (Already Canonical)

| Field | Status | Action |
|---|---|---|
| `meta_model` | Already canonical | Register as managed service |
| `exec_graph` | → `UnifiedGraph` | Adapter |
| `exec_graph_engine` | → `ExecutionEngineV2` | Adapter |
| `exec_graph_monitor` | → `ServiceKernel.HealthManager` | Adapter |
| `economics` | → `RepositoryEconomics` | Adapter |
| `planner` | → `ImprovementPlanner` | Adapter |
| `relationship_engine` | → `UnifiedGraph` | Adapter |
| `canonical_registry` | → `UnifiedGraph` | Adapter |
| `reasoning_engine` | → ProofEngine (Mission 25) | Placeholder |
| `repository_scientist` | → `SelfAnalyzer` | Adapter |
| `repository_engineer` | → `CodeGenerator` | Adapter |
| `repository_economics` | → `RepositoryMathematics` | Adapter |
| `digital_civilization` | → `Governance` | Adapter |
| `reverse_engineering_engine` | → `SelfAnalyzer` | Adapter |
| `omega_loop` | → `AutonomousEngine` | Adapter |

---

## 10. Responsibility Count Summary

| Category | Count | Already Canonical | Needs Adapter | Deprecated |
|---|---|---|---|---|
| Lifecycle | 7 | 0 | 7 | 0 |
| Persistence Stores | 7 | 7 | 0 | 0 |
| Core Services | 10 | 3 | 7 | 0 |
| Project/Security | 3 | 2 | 1 | 0 |
| Intelligence | 3 | 0 | 2 | 0 (1 kept as placeholder) |
| GENESIS-VIII | 6 | 0 | 5 | 1 (memory_types → UMS) |
| GENESIS-IX | 7 | 2 | 4 | 1 (platform_v2 removed) |
| GENESIS-X | 2 | 0 | 2 | 0 |
| GENESIS-XI | 2 | 2 | 0 | 0 |
| GENESIS-XII | 4 | 4 | 0 | 0 |
| GENESIS-XIII/Ω³ | 15 | 0 | 14 | 0 |
| **Total** | **66** | **20** | **42** | **2** |

**Net simplification:** 66 responsibilities today → 20 managed services + 42 adapters (which become managed services over time) + 2 removals.

---

## 11. Target State Architecture

```
PlatformAdapter (preserves VenusPlatform API)
  │
  ├──→ ServiceKernel (lifecycle, health, failure, heartbeat, metrics)
  │     └──→ PlatformOrchestrator (boot graph, dependency resolution, shutdown order)
  │
  ├──→ Governance (policy, audit, concurrency, circuit breakers)
  │
  ├──→ EngineeringMemory (memory, sessions, associations)
  │
  ├──→ UnifiedGraph (all graph representations: structural, dependency, knowledge, execution)
  │     └──→ GraphTraversal, GraphSearch, GraphTransform
  │
  ├──→ EngineCapabilityRegistry (service capabilities, discovery, resolution)
  │
  ├──→ AutonomousEngine (observe → understand → plan → generate → validate → learn)
  │     ├──→ SelfAnalyzer
  │     ├──→ ImprovementPlanner
  │     └──→ CodeGenerator
  │
  ├──→ ExecutionEngineV2 (workflow execution)
  │
  ├──→ DI Container (ServiceProvider) — unchanged
  │
  ├──→ EventBus — unchanged
  │
  ├──→ PersistenceManager (all stores as managed services)
  │
  └──→ Legacy Adapters (for components not yet migrated)
        ├──→ EngineeringBrain → EngineeringBrainV4 adapter
        ├──→ IntelligenceService → AutonomousEngine adapter
        ├──→ PlatformV2 → ServiceKernel adapter
        └──→ [New Genesis] components awaiting migration
```

---

## 12. Adapter Interface Design

The `PlatformAdapter` class:
```python
class PlatformAdapter:
    """Preserves VenusPlatform API while delegating to canonical components."""
    
    def __init__(self, config, db_path):
        # Create canonical kernel instead of 51 fields
        self._kernel = ServiceKernel()
        self._governance = Governance()
        self._memory = EngineeringMemory()
        self._graph = UnifiedGraph()
        self._capabilities = EngineCapabilityRegistry()
        self._autonomous = AutonomousEngine()
        self._planner = ImprovementPlanner()
        self._analyzer = SelfAnalyzer()
        self._codegen = CodeGenerator()
        
        # Legacy fields preserved for compatibility
        self.provider = None  # DI container (unchanged)
        self.event_bus = None
        # ... (only fields that external consumers actually use)
    
    def bootstrap(self):
        # Delegate to DI + register stores as managed services
        self.provider = di_bootstrap(...)
        self._kernel.register(store_service_defs)
        return self.provider
    
    def boot(self):
        # Delegate to PlatformOrchestrator with all service definitions
        self._kernel.boot()
        return self
    
    def shutdown(self):
        # Delegate to PlatformOrchestrator (reverse-order shutdown)
        self._kernel.shutdown()
    
    def summary(self):
        # Assemble from canonical components
        return {
            "booted": self._kernel.state == "HEALTHY",
            "services": self._kernel.service_summary(),
            ...
        }
```

---

## 13. Migration Sequencing

The migration must be done in dependency order:

| Step | What | Depends On | Risk |
|---|---|---|---|
| 1 | Create `PlatformAdapter` class | None (new file) | Low |
| 2 | Move lifecycle to `ServiceKernel` | Step 1 | Low |
| 3 | Move persistence stores to managed services | Step 2 | Low |
| 4 | Move core services (compiler, plugins, etc.) | Step 2 | Low |
| 5 | Move intelligence (brain, vrip) to adapters | Step 2 | Medium |
| 6 | Replace legacy GENESIS-VIII/IX/X fields with canonical | Step 2 | Medium |
| 7 | Replace GENESIS-XII/XIII fields with canonical | Step 2 | Low |
| 8 | Replace Ω³ fields with canonical | Step 2 | Medium |
| 9 | Verify `test_compliance.py` passes | All above | Critical |
| 10 | Deprecate `platform.py` (keep as thin re-export) | Step 9 | Low |
| 11 | Update `main()` to use `PlatformAdapter` | Step 10 | Low |

**Total estimated effort:** 3–5 days for complete migration
**Rollback plan:** Keep original `platform.py` intact; `PlatformAdapter` lives alongside it
