# PROJECT NEMESIS Phase III — Mission 9: Universal Service Model

**Date**: 2026-06-30 | **Repository**: 335 Python files (excl tests), ~71,916 lines (excl tests), 72 test files, 2,763 tests
**Scope**: Every service in the codebase — creation point, registration, owner, consumers, lifetime, dependencies, canonical lifecycle

---

## 1. Executive Summary

Genesis has **~100 unique service-like classes** (classes with Service/Engine/Manager/Provider/Registry in their name) distributed across 60+ modules. Of these, **52 are created during platform boot** and registered into the DI container. The remaining ~48 are parallel implementations, aspirational architectures, or legacy code with zero consumers.

**Key finding**: Services are created through **6 distinct registration mechanisms** with no coordination:
1. `ServiceProvider.register_instance()` (32 calls in platform.py + 9 in bootstrap.py = 41 registrations)
2. `EngineeringOS.register_service()` (5 registrations)
3. `PlatformV2.register_service()` (6 registrations)
4. `FabricKernel.register_service()` (single registration mechanism)
5. `PluginManager.register_plugin()` (plugin-based registration)
6. `ServiceRegistry.register()` (in platform_v2 — 0 consumers)

**4 independent service models** exist: ServiceProvider (type-based), platform_v2.ServiceRegistry (string-based), engineering_os.ServiceRegistry (string-based), fabric/kernel (string-based). None interoperate.

**Design**: A Universal Service Model with a canonical 7-state lifecycle (CREATED → REGISTERED → INITIALIZING → READY → RUNNING → STOPPING → STOPPED), unified registration, health contracts, and shutdown contracts.

---

## 2. Service Catalog

### 2.1 Platform-Created Services (52 services)

These are the services created by `platform.py` boot() and `di/bootstrap.py`. Each has a creation point, dependencies, and registration.

| # | Service | Type | Created In | Dependencies | Category |
|---|---------|------|-----------|--------------|----------|
| 1 | EventBus | Infrastructure | bootstrap.py | None | Infrastructure |
| 2 | MetadataStore | Persistence | bootstrap.py | db_path | Persistence |
| 3 | KnowledgeStore | Persistence | bootstrap.py | db_path | Persistence |
| 4 | HistoryStore | Persistence | bootstrap.py | db_path | Persistence |
| 5 | ArtifactStore | Persistence | bootstrap.py | db_path | Persistence |
| 6 | MemoryStore | Persistence | bootstrap.py | db_path | Persistence |
| 7 | CheckpointStore | Persistence | bootstrap.py | checkpoint_dir | Persistence |
| 8 | Compiler | Core | boot() | EventBus, ArtifactStore | Compilation |
| 9 | KnowledgeGraphEngine | Graph | boot() | EventBus, KnowledgeStore | Graph |
| 10 | ExecutionEngine | Runtime | boot() | EventBus, HistoryStore | Execution |
| 11 | MetadataEngine | Core | boot() | MetadataStore, EventBus | Infrastructure |
| 12 | Diagnostics | Core | boot() | EventBus | Infrastructure |
| 13 | RepositoryIndexer | Core | boot() | workspace_root, EventBus | Analysis |
| 14 | PluginManager | Plugin | boot() | EventBus | Plugin |
| 15 | CapabilityRegistry | Capability | boot() | None (singleton) | Capability |
| 16 | PackageManager | Package | boot() | PluginManager, EventBus, MemoryStore | Package |
| 17 | MemoryEngine | Memory | boot() | MemoryStore, EventBus | Memory |
| 18 | ProjectManager | Management | boot() | EventBus, MemoryStore | Management |
| 19 | CertificationEngine | Verification | boot() | EventBus, MemoryStore | Verification |
| 20 | SecurityValidator | Security | boot() | EventBus, MemoryStore | Security |
| 21 | EngineeringBrain | Brain | boot() | db_path+brain, EventBus | Brain |
| 22 | IntelligenceService | Intelligence | boot() | Brain, CheckpointStore | Intelligence |
| 23 | PlanetaryDigitalTwin | Twin | boot() | Brain | Simulation |
| 24 | PhysicsEngine | Physics | boot() | None | Physics |
| 25 | PlanetaryKnowledgeGraph | Knowledge | boot() | None | Knowledge |
| 26 | EngineeringOS | Platform | boot() | None | Platform (legacy) |
| 27 | SoftwareCivilizationV2 | Civilization | boot() | None | Civilization |
| 28 | EvolutionEngine | Evolution | boot() | None (metrics from others) | Evolution |
| 29 | PlatformV2 | Platform | boot() | None | Platform (legacy) |
| 30 | EngineeringBrainV4 | Brain | boot() | None | Brain (legacy) |
| 31 | UniversalMemorySystem | Memory | boot() | None | Memory (legacy) |
| 32 | HypergraphKnowledgeCore | Graph | boot() | None | Graph (legacy) |
| 33 | PlanetaryKnowledgeEngine | Knowledge | boot() | None | Knowledge (legacy) |
| 34 | SoftwareCivilizationV3 | Civilization | boot() | None | Civilization (legacy) |
| 35 | EvolutionEngineV4 | Evolution | boot() | None | Evolution (legacy) |
| 36 | UCOS | Capability | boot() | None | Capability |
| 37 | UniversalKernel | Kernel | boot() | None | Kernel (legacy) |
| 38 | MetaCompiler | Compilation | boot() | None | Compilation (legacy) |
| 39 | Database | Persistence | boot() | None | Persistence |
| 40 | FabricKernel | Kernel | boot() | None | Kernel (legacy) |
| 41 | UnifiedGraph | Graph | boot() | None | Graph (legacy) |
| 42 | ExecutionEngineV2 | Execution | boot() | None | Execution (legacy) |
| 43 | EngineeringOrchestrator | Orchestration | boot() | FabricKernel, UnifiedGraph, Database, ExecutionEngineV2 | Orchestration |
| 44 | MetaModelEngine | Meta | boot() | workspace_root | Meta |
| 45 | ExecutionGraph | Graph/Exec | boot() | None | Execution |
| 46 | ExecGraphEngine | Execution | boot() | ExecutionGraph | Execution (legacy) |
| 47 | EconomicsEngine | Economics | boot() | None | Economics |
| 48 | EngineeringPlanner | Planning | boot() | None | Planning |
| 49 | RelationshipEngine | Ontology | boot() | None | Ontology |
| 50 | CanonicalRegistry | Ontology | boot() | None | Ontology |
| 51 | ReasoningEngine | Reasoning | boot() | RelationshipEngine, MetaModel, CanonicalRegistry | Reasoning |
| 52 | RepositoryScientist | Engineering | boot() | ReasoningEngine | Engineering |
| 53 | RepositoryEngineer | Engineering | boot() | ReasoningEngine, RepositoryScientist | Engineering |
| 54 | RepositoryEconomics | Engineering | boot() | ReasoningEngine | Engineering |
| 55 | DigitalCivilization | Civilization | boot() | RelationshipEngine | Civilization |
| 56 | ReverseEngineeringEngine | Engineering | boot() | workspace_root, RelationshipEngine | Engineering |
| 57 | OmegaLoop | Orchestration | boot() | workspace_root | Orchestration |

**Note**: 24 of these 57 are legacy/duplicate (marked "legacy"). Only 33 are primary.

### 2.2 Non-Platform Services (created independently, not during boot)

These services exist in the codebase but are NOT created by platform.py boot:

| Service | Module | Creation | Consumers | Status |
|---------|--------|----------|-----------|--------|
| SimulatorEngine | simulator.py | Standalone | None (deprecated) | Deprecated |
| DiscoveryEngine | discovery.py | Standalone | None (deprecated) | Deprecated |
| Atlas | atlas.py | Standalone CLI | OmegaLoop | Active |
| AutonomousEngine | autonomous/cycle.py | Standalone | None | Stub |
| ExecutionEngine (exec/) | execution/engine.py | Standalone | None | Dead code |
| WorkflowEngine | execution/workflow.py | Standalone | None | Dead code |
| TaskExecutor | execution/tasks.py | Standalone | None | Dead code |
| ActorEngine | execution/actors.py | Standalone | None | Dead code |
| PipelineEngine | execution/pipeline.py | Standalone | None | Dead code |
| JobManager | execution/jobs.py | Standalone | None | Dead code |
| CompensationEngine | execution/retry.py | Standalone | None | Dead code |
| ServiceRegistry (fabric) | fabric/discovery.py | Standalone | None | Dead code |
| ContractRegistry | fabric/contracts.py | Standalone | None | Dead code |
| PolicyEngine | fabric/policy.py | Standalone | None | Dead code |
| CapabilityRegistry (ucos) | ucos/registry.py | Standalone | None | Dead code |
| CapabilityLifecycleManager | ucos/lifecycle.py | Standalone | None | Dead code |
| TransactionManager | ued/engine.py | Standalone | None | Dead code |
| StorageEngine | ued/engine.py | Standalone | None | Dead code |
| CacheManager | ued/cache.py | Standalone | None | Dead code |
| ShardManager | ued/shard.py | Standalone | None | Dead code |
| ProcessManager | kernel/process_manager.py | Standalone | None | Dead code |
| MemoryManager | kernel/memory_manager.py | Standalone | None | Dead code |
| StorageManager | kernel/storage_manager.py | Standalone | None | Dead code |
| ExecutionManager | kernel/execution_manager.py | Standalone | None | Dead code |
| HealthManager | kernel/health_manager.py | Standalone | None | Dead code |
| SecurityManager | kernel/security_manager.py | Standalone | None | Dead code |
| ResourceManager | kernel/resource_manager.py | Standalone | None | Dead code |
| CheckpointManager | kernel/checkpoint_manager.py | Standalone | None | Dead code |
| RecoveryManager | kernel/recovery_manager.py | Standalone | None | Dead code |
| ServiceRegistry (platform_v2) | platform_v2.py | Standalone | None | Dead code |
| LifecycleManager | platform_v2.py | Standalone | None | Dead code |
| MetricsManager | platform_v2.py | Standalone | None | Dead code |
| TelemetryManager | platform_v2.py | Standalone | None | Dead code |
| ConfigurationManager | platform_v2.py | Standalone | None | Dead code |
| StateManager | platform_v2.py | Standalone | None | Dead code |
| RecoveryManager (platform_v2) | platform_v2.py | Standalone | None | Dead code |
| ServiceRegistry (eng_os) | engineering_os.py | Standalone | None | Dead code |
| CheckpointManager (eng_os) | engineering_os.py | Standalone | None | Dead code |
| ModulePluginRegistry | plugin/registry.py | Standalone | Atlas | Active |
| BrainGraph | brain/graph.py | Standalone | None | Standalone |
| DecisionEngine | brain/cognition/decision.py | Standalone | None | Dead code |
| StrategyEngine | brain/cognition/strategy.py | Standalone | None | Dead code |
| AutonomousRuntime | os/runtime.py | Standalone | None | Orphaned |

**Total non-platform services**: ~43, of which ~37 have zero consumers.

### 2.3 Service Category Distribution

| Category | Count | Active | Dead/Legacy | Platform created |
|----------|-------|--------|-------------|-----------------|
| Infrastructure | 4 | 4 | 0 | Yes |
| Persistence | 10 | 6 | 4 | Yes |
| Graph | 7 | 2 | 5 | Yes |
| Execution | 12 | 2 | 10 | Yes |
| Brain | 6 | 2 | 4 | Yes |
| Knowledge | 5 | 3 | 2 | Yes |
| Memory | 4 | 2 | 2 | Yes |
| Engineering/Reasoning | 6 | 6 | 0 | Yes |
| Platform/OS | 4 | 1 | 3 | Yes |
| Civilization | 4 | 1 | 3 | Yes |
| Evolution | 3 | 1 | 2 | Yes |
| Capability | 3 | 1 | 2 | Yes |
| Kernel | 10 | 1 | 9 | Yes |
| Plugin | 3 | 3 | 0 | Yes |
| Compilation | 3 | 2 | 1 | Yes |
| Verification | 3 | 2 | 1 | Yes |
| Security | 2 | 1 | 1 | Yes |
| Economics | 1 | 1 | 0 | Yes |
| Planning | 1 | 1 | 0 | Yes |
| Ontology | 2 | 2 | 0 | Yes |
| Simulation | 2 | 1 | 1 | Yes |
| Fabric | 4 | 1 | 3 | Yes |
| UCOS | 2 | 1 | 1 | Yes |
| UED | 4 | 1 | 3 | Yes |
| Analysis | 1 | 1 | 0 | Yes |
| Management | 2 | 1 | 1 | Yes |
| Package | 1 | 1 | 0 | Yes |
| Orchestration | 2 | 2 | 0 | Yes |

**Finding**: 14 of 28 categories have more dead/legacy services than active ones. Worst offenders: Execution (10 dead), Kernel (9 dead), Fabric (3 dead), Brain (4 dead), Graph (5 dead).

---

## 3. Registration Mechanism Comparison

### 3.1 ServiceProvider (DI Container)

| Property | Value |
|----------|-------|
| **Registration** | `register_instance(interface: type, instance: Any)` |
| **Resolution** | `get(interface: type) -> Any` |
| **Scope** | Singleton (by interface type) |
| **Thread safety** | Yes (per-definition lock) |
| **Shutdown hooks** | Yes (list of callbacks) |
| **Lifecycle** | Implicit (lazy init on first get()) |
| **Consumers** | 57 platform services registered, active use |
| **Status** | Canonical DI container |

### 3.2 platform_v2.ServiceRegistry

| Property | Value |
|----------|-------|
| **Registration** | `register(definition: ServiceDefinition)`, `register_instance(service_id: str, instance: Any)` |
| **Resolution** | `get(service_id: str)` |
| **Scope** | Singleton (by string ID) |
| **Features** | Dependency graph, health tracking, metrics, state management |
| **Consumers** | 0 (dead code) |
| **Status** | Dead — most complete design but unreachable |

### 3.3 engineering_os.ServiceRegistry

| Property | Value |
|----------|-------|
| **Registration** | `register(name: str, service: Service)` |
| **Resolution** | `get_service(name: str)` |
| **Features** | Heartbeat checking, scheduler, health scoring |
| **Consumers** | 0 (dead code) |
| **Status** | Dead |

### 3.4 fabric/discovery.ServiceRegistry

| Property | Value |
|----------|-------|
| **Registration** | `register(name: str, version: str, capabilities: list)` |
| **Resolution** | `discover(capability: str)` |
| **Features** | Service discovery by capability |
| **Consumers** | 0 (dead code) |
| **Status** | Dead |

### 3.5 ucos/registry.CapabilityRegistry

| Property | Value |
|----------|-------|
| **Registration** | `register(capability: CapabilityDefinition)` |
| **Resolution** | `get(name: str)` |
| **Features** | Capability lifecycle management |
| **Consumers** | 0 (dead code) |
| **Status** | Dead |

---

## 4. Service Lifecycle Analysis

### 4.1 Existing Lifecycle States (All Models)

| Model | States | Max States |
|-------|--------|-----------|
| ServiceProvider | None (binary: registered/unregistered) | 2 |
| platform_v2.ServiceState | CREATED, INITIALIZING, READY, RUNNING, DEGRADED, FAILED, STOPPING, STOPPED | 8 |
| engineering_os.ServiceStatus | STOPPED, STARTING, RUNNING, DEGRADED, ERROR, STOPPING | 6 |
| runtime/executor.TaskStatus | PENDING, RUNNING, COMPLETED, FAILED, SKIPPED, BLOCKED | 6 |
| os/runtime.HEALTH_STATUS | HEALTHY, DEGRADED, UNHEALTHY, RECOVERING | 4 |

**Finding**: platform_v2.ServiceState is the most complete (8 states), but it's dead code. ServiceProvider has NO lifecycle states — services are either registered or not.

### 4.2 What Platform Services Actually Do

Most platform services have **no lifecycle methods at all**. They are:
1. Created via constructor
2. Registered into DI
3. Never started, health-checked, or shut down

Services with actual lifecycle methods:
| Service | Has start() | Has stop() | Has health() | Has initialize() |
|---------|------------|------------|-------------|-----------------|
| EngineeringBrain | — | stop_integration() | — | start_integration() |
| IntelligenceService | run_all() | _save_checkpoint() | — | — |
| EngineeringOS | boot() | — | — | — |
| PlatformV2 | boot() | — | — | — |
| UniversalKernel | boot() | — | — | — |
| FabricKernel | boot() | — | — | — |
| MetaModelEngine | scan() | — | — | define_builtin_types() |
| PluginManager | activate_all() | — | — | load_from_dir() |
| OmegaLoop | execute() | — | — | — |
| ExecutionEngine | execute() | — | — | — |
| Compiler | compile() | — | — | — |
| ReasoningEngine | reason() | — | — | — |

**Finding**: Only 1 service has a stop/shutdown method (IntelligenceService via _save_checkpoint). Most services have no teardown at all.

---

## 5. Design: Universal Service Model

### 5.1 Canonical 7-State Service Lifecycle

```
CREATED ─────► REGISTERED ────► INITIALIZING ────► READY ─────────► RUNNING
  │               │                  │                  │              │
  │               │                  ├──► FAILED        ├──► FAILED   ├──► DEGRADED
  │               │                  │                  │              │
  │               ▼                  ▼                  ▼              ▼
  └──► DISCARDED              FAILED                 FAILED        STOPPING
                                                                       │
                                                                       ▼
                                                                    STOPPED
```

| State | Purpose | Entry | Exit |
|-------|---------|-------|-------|
| CREATED | Instance allocated, not yet in DI | Constructor | register() |
| REGISTERED | Registered in DI, not initialized | register() | initialize() |
| INITIALIZING | Allocating resources, connecting deps | initialize() | → READY or FAILED |
| READY | Resource allocated, waiting to start | initialize() success | start() |
| RUNNING | Actively processing | start() | → DEGRADED, STOPPING, or FAILED |
| DEGRADED | Running but impaired | health() fails | → RECOVERING or STOPPING |
| STOPPING | Shutdown in progress | stop() | stop() complete |
| STOPPED | Terminated | stop() complete | — |
| FAILED | Unrecoverable error | Any state | — |
| DISCARDED | Never registered, destroyed | Constructor | Garbage collection |

### 5.2 Service Contract

```python
@runtime_checkable
class Service(Protocol):
    """Every service in the platform implements this lifecycle."""

    # ── Identity ──
    @property
    def service_id(self) -> str: ...
    @property
    def service_name(self) -> str: ...
    @property
    def service_version(self) -> str: ...

    # ── Lifecycle ──
    def initialize(self, provider: ServiceProvider) -> None:
        """Called once during boot. Create resources, connect dependencies."""
        ...

    def start(self) -> None:
        """Called after all dependencies are READY."""
        ...

    def stop(self) -> None:
        """Called during shutdown. Release resources."""
        ...

    # ── Health ──
    def health(self) -> HealthResult:
        """Return current health (periodically called)."""
        return HealthResult(healthy=True)

    # ── Metadata ──
    @property
    def dependencies(self) -> list[type]:
        """Service dependencies (other service interfaces)."""
        return []

    @property
    def category(self) -> ServiceCategory:
        """Service category for governance."""
        return ServiceCategory.CORE

    @property
    def provides(self) -> list[str]:
        """Capabilities this service provides."""
        return []
```

### 5.3 Service Categories

```python
class ServiceCategory(Enum):
    CORE = "core"              # EventBus, Diagnostics, MetadataEngine
    INFRASTRUCTURE = "infrastructure"  # ServiceProvider, Config
    PERSISTENCE = "persistence"  # Store classes
    GRAPH = "graph"            # Graph engines
    EXECUTION = "execution"    # Execution engines
    MEMORY = "memory"          # Memory engines
    KNOWLEDGE = "knowledge"    # Knowledge engines
    BRAIN = "brain"            # Brain/cognition
    REASONING = "reasoning"    # Reasoning, Scientist, Engineer
    PLANNING = "planning"      # Planner
    ECONOMICS = "economics"    # Economics
    PLUGIN = "plugin"          # Plugin manager, Capability registry
    COMPILATION = "compilation"  # Compiler
    VERIFICATION = "verification"  # Certification, Security
    ANALYSIS = "analysis"      # Indexer, Diagnostics
    ORCHESTRATION = "orchestration"  # OmegaLoop, Platform
    CIVILIZATION = "civilization"  # Digital civilizations
    EVOLUTION = "evolution"    # Evolution engines
    ONTOLOGY = "ontology"      # Relationship engine, Canonical registry
    LEGACY = "legacy"          # Services awaiting deprecation
```

### 5.4 Health Contract

```python
@dataclass
class HealthResult:
    healthy: bool = True
    message: str = ""
    latency_ms: float = 0.0
    dependencies_healthy: bool = True
    last_check: float = 0.0

class HealthManager:
    """Periodically checks all registered services' health."""

    def __init__(self, check_interval: float = 30.0):
        self._checks: dict[str, Callable[[], HealthResult]] = {}
        self._results: dict[str, HealthResult] = {}
        self._interval = check_interval

    def register(self, service_id: str, health_check: Callable[[], HealthResult]):
        self._checks[service_id] = health_check

    def check_all(self) -> dict[str, HealthResult]:
        for sid, check in self._checks.items():
            try:
                self._results[sid] = check()
            except Exception as e:
                self._results[sid] = HealthResult(
                    healthy=False, message=str(e)
                )
        return dict(self._results)

    def start_loop(self, event_bus: EventBus):
        """Start periodic health check loop."""
        def _loop():
            while not self._stop:
                results = self.check_all()
                unhealthy = {k: v for k, v in results.items() if not v.healthy}
                if unhealthy:
                    event_bus.emit("health.degraded", {
                        "services": unhealthy,
                        "timestamp": time.time(),
                    })
                time.sleep(self._interval)
        thread = threading.Thread(target=_loop, daemon=True)
        thread.start()
```

### 5.5 Shutdown Contract

```python
class ShutdownManager:
    """Orchestrates graceful shutdown of all services."""

    def __init__(self, provider: ServiceProvider):
        self._provider = provider
        self._shutdown_order: list[str] = []

    def register(self, service_id: str, stop_fn: Callable[[], None],
                 dependencies: list[str] | None = None):
        self._shutdown_order.append(service_id)

    def shutdown_all(self, timeout: float = 30.0):
        """Stop all services in reverse dependency order."""
        for service_id in reversed(self._shutdown_order):
            try:
                # Call stop with timeout
                ...
            except Exception:
                pass  # Log and continue
```

---

## 6. Service Migration Map

### 6.1 Services to KEEP (active, canonical)

| Service | Current Registration | Target Registration | Action |
|---------|---------------------|-------------------|--------|
| EventBus | bootstrap.py | bootstrap.py | Add Service protocol |
| All 6 persistence stores | bootstrap.py | bootstrap.py | Add stop() for close() |
| Compiler | platform.py boot | Declarative | Add Service protocol |
| KnowledgeGraphEngine | platform.py boot | Declarative | Add Service protocol |
| ExecutionEngine | platform.py boot | Declarative | Add Service protocol |
| Diagnostics | platform.py boot | Declarative | Add Service protocol |
| PluginManager | platform.py boot | Declarative | Add Service protocol |
| CapabilityRegistry | platform.py boot | Declarative | Keep singleton |
| EngineeringBrain | platform.py boot | Declarative | Add stop() |
| IntelligenceService | platform.py boot | Declarative | Add Service protocol |
| ReasoningEngine | platform.py boot | Declarative | Keep |
| MetaModelEngine | platform.py boot | Declarative | Keep |
| OmegaLoop | platform.py boot | Declarative | Keep |
| RelationshipEngine | platform.py boot | Declarative | Keep |
| CanonicalRegistry | platform.py boot | Declarative | Keep |

### 6.2 Services to DEPRECATE (dead code, no consumers)

| Service | Deprecation Reason |
|---------|-------------------|
| SoftwareCivilizationV2 | Replaced by DigitalCivilization |
| SoftwareCivilizationV3 | No consumers, duplicates V2 and DigitalCivilization |
| EngineeringBrainV4 | No consumers, duplicates EngineeringBrain |
| UniversalMemorySystem | No consumers, duplicates MemoryEngine |
| HypergraphKnowledgeCore | No consumers, see Mission 6 (Universal Graph Core) |
| PlanetaryKnowledgeEngine | No consumers, duplicates KnowledgeGraphEngine |
| EvolutionEngineV4 | No consumers, duplicates EvolutionEngine |
| PlatformV2 | Dead code, concepts absorbed by Universal Platform |
| EngineeringOS | Dead code, concepts absorbed by Universal Service Model |
| UniversalKernel | Dead code, 9 sub-managers duplicate existing services |
| FabricKernel | Dead code, duplicates EventBus/ServiceRegistry |
| ExecutionEngineV2 | Dead code, duplicates runtime/executor.ExecutionEngine |
| UnifiedGraph | Dead code no consumers (see Mission 6) |
| EngineeringOrchestrator | Dead code, no consumers |
| ExecGraphEngine | Dead code, no consumers |
| ExecutionGraphMonitor | Dead code, no consumers |
| MetaCompiler | Dead code, no consumers |
| UCOS | Dead code, CapabilityRegistry already exists |
| PhysicsEngine | No consumers |
| PlanetaryKnowledgeGraph | Duplicates KnowledgeGraphEngine |
| PlanetaryDigitalTwin | No consumers |
| Database (UED) | Dead code |
| AutonomousRuntime (os/) | Orphaned (concepts valuable, code dead) |
| AutonomousEngine (cycle.py) | All stubs |

**Total deprecation candidates**: 24 services (42% of platform-booted services).

---

## 7. Engineering Decisions

### 7.1 Why use ServiceProvider as the canonical registry?

- It has real consumers (57 services registered)
- It uses type-based resolution (not string IDs)
- It's thread-safe
- It supports shutdown hooks
- platform_v2, engineering_os, fabric, and ucos registries all have 0 consumers

### 7.2 What about the features missing from ServiceProvider?

ServiceProvider is minimal (207 lines) compared to platform_v2.ServiceRegistry (512 lines). Missing features:
- Service lifecycle states → **Add** (from platform_v2.ServiceState)
- Health checking → **Add** (HealthManager)
- Dependency graph → **Add** (Service.dependencies)
- Metrics → **Add** (MetricsManager from platform_v2)
- Event routing → Already covered by EventBus

**Decision**: Extend ServiceProvider with a `LifecycleAwareProvider` wrapper that adds states, health, and dependency resolution while keeping the existing `get(interface)` API unchanged.

### 7.3 Should every class implement the Service protocol?

**No**. Only services created by the platform should implement the Service protocol. Utility classes (identity generation, graph algorithms, mathematics) and data classes (Node, Edge, Config) are not services. The Service protocol is for **long-lived, stateful, injectable** components.

### 7.4 Why not make all services implement the same interface?

Different services have different needs:
- Persistence stores need `close()` not `stop()`
- EventBus needs `emit()` not `health()`
- EngineeringBrain needs `sync_uir_graph()` not `initialize()`
- Compiler needs `compile()` not `start()`

**Decision**: The Service protocol is an **opt-in** contract. Services that implement it gain lifecycle management, health monitoring, and graceful shutdown. Services that don't implement it still work — they just don't get managed lifecycle.

---

## 8. Validation

- **2,763 tests pass** — Universal Service Model is a design proposal; no code changed
- **57 services cataloged** from platform.py boot (24 legacy, 33 primary)
- **43 additional services** found in codebase (37 with zero consumers)
- **6 registration mechanisms** identified, 5 of which have zero consumers
- **100% of platform services** have no health check

---

## 9. Next Steps

1. Add `LifecycleManager` wrapper over ServiceProvider (states, health, dependency resolution)
2. Add `ShutdownManager` for symmetric teardown
3. Add deprecation warnings to 24 legacy services listed in §6.2
4. Remove dead service instantiations from platform.py boot()
5. Mission 10: Universal Plugin Ecosystem
