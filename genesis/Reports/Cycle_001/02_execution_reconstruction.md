# PROJECT NEMESIS — Mission 1: Execution Reconstruction

**Date**: 2026-06-30
**Scope**: Trace every object creation, ownership, dependency, consumer, destruction, and lifecycle across full boot → run → shutdown.

---

## 1. Entry Points

There are **4 entry points** into the system, with 3 distinct execution paths:

| Entry Point | Path | Triggers |
|---|---|---|
| `__main__.py` | CLI.run() | `python -m genesis` |
| `platform.py main()` | VenusPlatform.boot() | `venus platform boot` CLI |
| `platform.py main() --vrip-only` | IntelligenceService.run_all() | VRIP-only mode |
| `platform.py main() status` | platform.summary() | Status query |

### 1.1 Default Boot Path (`python -m genesis`)
```
__main__.main()
  → CLI().run(sys.argv[1:])
```

### 1.2 Full Platform Boot Path (`platform.boot()`)
This is the **canonical execution path**. 747-line constructor that instantiates ~50 objects.

---

## 2. Phase 0: Module-Level Imports (Side Effects at Import Time)

Before any code runs, `platform.py` imports 50+ modules at **module level** (lines 22–113). Every import triggers:

1. **DeprecationWarnings**: 7 deprecated modules fire warnings on import (discovery, scientist, simulator, evolution, civilization_v2, civilization_v3, brain_v4)
2. **ModulePluginRegistry initialization**: `plugin/registry.py` runs at import time (line 56 of omega_loop.py also imports this)
3. **mathematics.py** loads all classes (796 lines) — used by omega_loop at module level (lines 57–62) and platform.py (lines 67–71)

**Critical**: Importing `platform.py` alone triggers all ~50 module imports. This is why test collection fails without PYTHONPATH — the `from genesis.brain import EngineeringBrain` at line 22 cannot resolve.

### Module-Level Import Groups (platform.py lines 22–113)

| Group | Lines | Modules Imported | Count |
|---|---|---|---|
| Core platform | 22–50 | brain, digital_twin, intelligence, capability, certification, cli, compiler, config, core.metadata, di, diagnostics, events, graph, indexer, memory, package, persistence, plugin, project, runtime, security | 21 |
| GENESIS-VIII | 52–71 | memory.types, memory.consolidation, simulator, physics, discovery, knowledge_graph, engineering_os, civilization_v2, mathematics, evolution | 10 |
| GENESIS-IX | 74–83 | platform_v2, brain_v4, memory_system, hypergraph, simulator_v2, scientist, planetary_knowledge, mathematics_v2, civilization_v3, evolution_v4 | 10 |
| GENESIS-X | 85–86 | ucos, kernel | 2 |
| GENESIS-XI | 88–89 | meta, ued | 2 |
| GENESIS-XII | 91–101 | fabric, graph_v2, execution, autonomous, meta_model, execution_graph, economics | 7 |
| GENESIS-XIII/Ω³ | 102–113 | ontology, meta_model, reasoning, repository_scientist, repository_engineer, repository_economics, digital_civilization, reverse_engineer, omega_loop | 9 |

**Total: ~61 import statements importing from ~55+ distinct modules.**

---

## 3. Phase 1: DI Bootstrap (platform.bootstrap())

Called from `VenusPlatform.__init__()` if provider is None, or explicitly.

### Object Creation Order

```
bootstrap()
  ├── ServiceProvider()                                    # Empty DI container
  ├── EventBus()                                           # In-memory pub/sub
  │   └── DI: register_instance(EventBus)
  ├── MetadataStore(db_path)                               # SQLite-backed
  │   └── DI: register_instance(MetadataStore)
  ├── KnowledgeStore(db_path)                              # SQLite-backed
  │   └── DI: register_instance(KnowledgeStore)
  ├── HistoryStore(db_path)                                # SQLite-backed
  │   └── DI: register_instance(HistoryStore)
  ├── ArtifactStore(db_path)                               # SQLite-backed
  │   └── DI: register_instance(ArtifactStore)
  ├── MemoryStore(db_path)                                 # SQLite-backed
  │   └── DI: register_instance(MemoryStore)
  ├── CheckpointStore(checkpoint_dir)                      # JSON snapshots
  │   └── DI: register_instance(CheckpointStore, CheckpointService)
  └── Shutdown hook: _checkpoint_shutdown(checkpoint_store)
```

**6 storage providers + 1 event bus created.** All eagerly instantiated (not lazy).

---

## 4. Phase 2: boot() Core Services

Called from `VenusPlatform.boot()`. Creates 15 core services in sequence:

```
boot()
  │
  ├── set _started_at timestamp
  │
  ├── Compiler(event_bus, artifact_store)
  │   └── DI: register_instance(Compiler)
  │
  ├── KnowledgeGraphEngine(event_bus, knowledge_store)
  │   └── DI: register_instance(KnowledgeGraphEngine)
  │
  ├── ExecutionEngine(event_bus, history_store)              # genesis.runtime.executor
  │   └── DI: register_instance(ExecutionEngine)
  │
  ├── MetadataEngine(metadata_store, event_bus)
  │   └── DI: register_instance(MetadataEngine)
  │
  ├── Diagnostics(event_bus)
  │   └── DI: register_instance(Diagnostics)
  │
  ├── RepositoryIndexer(workspace_root, event_bus)
  │   └── DI: register_instance(RepositoryIndexer)
  │
  ├── PluginManager(event_bus)
  │   ├── load_from_dir() for each plugin_dir
  │   └── DI: register_instance(PluginManager)
  │
  ├── CapabilityRegistry (= capability_registry singleton)
  │   └── DI: register_instance(CapabilityRegistry)
  │
  ├── PackageManager(plugin_manager, event_bus, memory_store)
  │   └── DI: register_instance(PackageManager)
  │
  ├── MemoryEngine(memory_store, event_bus)
  │   └── DI: register_instance(MemoryEngine)
  │
  ├── ProjectManager(event_bus, memory_store)
  │   └── DI: register_instance(ProjectManager)
  │
  ├── CertificationEngine(event_bus, memory_store)
  │   └── DI: register_instance(CertificationEngine)
  │
  ├── SecurityValidator(event_bus, memory_store)
  │   └── DI: register_instance(SecurityValidator)
  │
  ├── EngineeringBrain(storage_path=brain_db, event_bus)
  │   ├── sync_uir_graph(graph.graph)
  │   ├── start_integration()
  │   ├── emit("brain.ready")
  │   └── DI: register_instance(EngineeringBrain)
  │
  ├── IntelligenceService(brain, checkpoint_store)           # VRIP
  │   ├── run_all()                                          # Runs immediately!
  │   └── DI: register_instance(IntelligenceService)
  │
  └── PlanetaryDigitalTwin(brain)
      └── DI: register_instance(PlanetaryDigitalTwin)
```

### Dependency Injection Matrix (Core Services)

| Service | Dependencies |
|---|---|
| Compiler | EventBus, ArtifactStore |
| KnowledgeGraphEngine | EventBus, KnowledgeStore |
| ExecutionEngine | EventBus, HistoryStore |
| MetadataEngine | MetadataStore, EventBus |
| Diagnostics | EventBus |
| RepositoryIndexer | workspace_root, EventBus |
| PluginManager | EventBus, plugin_dirs |
| PackageManager | PluginManager, EventBus, MemoryStore |
| MemoryEngine | MemoryStore, EventBus |
| ProjectManager | EventBus, MemoryStore |
| CertificationEngine | EventBus, MemoryStore |
| SecurityValidator | EventBus, MemoryStore |
| EngineeringBrain | storage_path, EventBus, graph.graph |
| IntelligenceService | EngineeringBrain, CheckpointStore |
| PlanetaryDigitalTwin | EngineeringBrain |

**Key observations**:
- EventBus is injected into 14/15 services (everyone except CapabilityRegistry)
- EngineeringBrain is the most-depended-on domain object (2 consumers: VRIP + DigitalTwin)
- MemoryStore powers 4 services (PackageManager, ProjectManager, Certification, Security)
- VRIP runs ALL of its intelligence during boot(), blocking the boot sequence

---

## 5. Phase 3: GENESIS-VIII Programs

```
  │
  ├── 16 Memory Types (dict: name → instance)
  │   ├── EpisodicMemory()
  │   ├── SemanticMemory()
  │   ├── ProceduralMemory()
  │   ├── ArchitecturalMemory()
  │   ├── ResearchMemory()
  │   ├── OrganizationalMemory()
  │   ├── TemporalMemory()
  │   ├── CausalMemory()
  │   ├── ExecutionMemory()
  │   ├── AgentMemory()
  │   ├── WorldMemory()
  │   ├── GraphMemory()
  │   ├── SpecificationMemory()
  │   ├── ConversationMemory()
  │   ├── SimulationMemory()
  │   └── ReflectionMemory()
  │
  ├── MemoryConsolidator()
  ├── ForgettingMechanism()
  ├── PhysicsEngine()
  │   └── DI: register_instance(PhysicsEngine)
  ├── PlanetaryKnowledgeGraph()
  │   └── DI: register_instance(PlanetaryKnowledgeGraph)
  ├── EngineeringOS()
  │   ├── register_service("brain", COGNITIVE)
  │   ├── register_service("memory", MEMORY)
  │   ├── register_service("simulator", SIMULATION)
  │   ├── register_service("discovery", RESEARCH)
  │   ├── register_service("knowledge_graph", KNOWLEDGE)
  │   └── boot()
  │   └── DI: register_instance(EngineeringOS)
  │
  ├── SoftwareCivilizationV2()
  │   ├── create_institute("Architecture Council", ARCHITECTURE_COUNCIL)
  │   ├── create_institute("AI Institute", AI_INSTITUTE)
  │   ├── create_institute("Physics Institute", PHYSICS_INSTITUTE)
  │   ├── create_institute("Knowledge Institute", KNOWLEDGE_INSTITUTE)
  │   ├── create_institute("Standards Committee", STANDARDS_COMMITTEE)
  │   ├── create_institute("Compiler Institute", COMPILER_INSTITUTE)
  │   ├── create_institute("Evolution Committee", EVOLUTION_COMMITTEE)
  │   └── DI: register_instance(SoftwareCivilizationV2)
  │
  ├── EvolutionEngine()
  │   └── observe({brain_entities, brain_confidence, twin_nodes, vrip_phases, graph_nodes, graph_edges})
  │   └── DI: register_instance(EvolutionEngine)
```

**Key observations**:
- PhysicsEngine, PlanetaryKnowledgeGraph, EngineeringOS all take ZERO arguments — no DI injection, no event bus
- 16 memory types are instantiated but NEVER registered in DI container — only stored in `self.memory_types` dict
- MemoryConsolidator and ForgettingMechanism are created but NEVER stored — they're created and immediately abandoned (will be garbage collected)
- EvolutionEngine.observe() depends on brain, digital_twin, vrip, graph being initialized (they are)

---

## 6. Phase 4: GENESIS-IX Phases

```
  │
  ├── PlatformV2()
  │   ├── register_service("brain", PLATFORM)
  │   ├── register_service("memory", PLATFORM)
  │   ├── register_service("graph", PLATFORM)
  │   ├── register_service("simulator", PLATFORM)
  │   ├── register_service("discovery", PLATFORM)
  │   ├── register_service("civilization", PLATFORM)
  │   ├── register_service("evolution", PLATFORM)
  │   └── boot()
  │   └── DI: register_instance(PlatformV2)
  │
  ├── EngineeringBrainV4()
  │   └── DI: register_instance(EngineeringBrainV4)
  ├── UniversalMemorySystem()
  │   └── DI: register_instance(UniversalMemorySystem)
  ├── HypergraphKnowledgeCore()
  │   └── DI: register_instance(HypergraphKnowledgeCore)
  ├── PlanetaryKnowledgeEngine()
  │   └── DI: register_instance(PlanetaryKnowledgeEngine)
  ├── SoftwareCivilizationV3()
  │   └── DI: register_instance(SoftwareCivilizationV3)
  ├── EvolutionEngineV4()
  │   └── observe({brain_v4_goals, brain_v4_beliefs, ums_entries, hypergraph_nodes, ...})
  │   └── DI: register_instance(EvolutionEngineV4)
```

**Key observations**:
- All 7 GENESIS-IX objects take ZERO constructor arguments — no DI, no wiring
- PlatformV2 creates 7 services that overlap with EngineeringOS services AND with the core boot() services — triplicate abstraction
- EngineeringBrainV4, UniversalMemorySystem, HypergraphKnowledgeCore, PlanetaryKnowledgeEngine, SoftwareCivilizationV3 are created but NEVER connected to any event bus or other service
- They are isolated silos

---

## 7. Phase 5-6: GENESIS-X and GENESIS-XI

```
  ├── UCOS()                                               # GENESIS-X
  │   └── DI: register_instance(UCOS)
  ├── UniversalKernel()
  │   └── boot()
  │   └── DI: register_instance(UniversalKernel)
  │
  ├── MetaCompiler()                                       # GENESIS-XI
  │   └── DI: register_instance(MetaCompiler)
  ├── Database()                                            # GENESIS-XI (UED)
  │   └── DI: register_instance(Database)
```

## 8. Phase 7: GENESIS-XII Programs

```
  ├── FabricKernel.instance()                              # Singleton — different from all others
  │   └── boot()
  │   └── DI: register_instance(FabricKernel)
  ├── UnifiedGraph()
  │   └── DI: register_instance(UnifiedGraph)
  ├── ExecutionEngineV2()                                  # DIFFERENT from runtime.executor
  │   └── DI: register_instance(ExecutionEngineV2)
  ├── EngineeringOrchestrator(fabric, graph, ued, execution)
  │   └── DI: register_instance(EngineeringOrchestrator)
```

**Key observations**:
- FabricKernel uses `.instance()` (singleton pattern), not constructor
- ExecutionEngineV2 is a DIFFERENT class from the ExecutionEngine created in Phase 2 — same role, different implementation, no relationship
- EngineeringOrchestrator is the FIRST GENESIS-XII object that receives dependencies

---

## 9. Phase 8: GENESIS-XIII / Ω³ Phases

```
  ├── MetaModelEngine(repo_path)
  │   ├── define_builtin_types()
  │   └── scan()
  │   └── DI: register_instance(MetaModelEngine)
  │
  ├── ExecutionGraph = build_default_execution_graph()
  ├── ExecGraphEngine(exec_graph)
  ├── ExecutionGraphMonitor(exec_graph_engine)
  │   └── DI: register_instance(ExecGraphEngine, ExecutionGraphMonitor)
  │
  ├── EconomicsEngine()
  │   └── DI: register_instance(EconomicsEngine)
  ├── EngineeringPlanner()
  │   └── DI: register_instance(EngineeringPlanner)
  ├── RelationshipEngine()
  │   └── DI: register_instance(RelationshipEngine)
  ├── initialize_canonical_registry()
  │   └── DI: register_instance(type, instance)
  │
  ├── register_universal_types(meta_model.model)            # Side effect on MetaModel
  ├── sync_uem_entities_to_meta_model(...)                  # Side effect on MetaModel
  │
  ├── ReasoningEngine(relationship_engine, meta_model, canonical_registry)
  │   └── DI: register_instance(ReasoningEngine)
  ├── RepositoryScientist(reasoning)
  │   └── DI: register_instance(RepositoryScientist)
  ├── RepositoryEngineer(reasoning, scientist)
  │   └── DI: register_instance(RepositoryEngineer)
  ├── RepositoryEconomics(reasoning)
  │   └── DI: register_instance(RepositoryEconomics)
  ├── DigitalCivilization = build_default_civilization(relationship_engine)
  │   └── DI: register_instance(DigitalCivilization)
  ├── ReverseEngineeringEngine(root, relationship_engine)
  │   └── DI: register_instance(ReverseEngineeringEngine)
  ├── OmegaLoop(repo_root)
  │   └── DI: register_instance(OmegaLoop)
  │
  ├── register_shutdown_hook(platform.shutdown)
  └── emit("platform.boot.completed")
```

**Key observations**:
- OmegaLoop takes `repo_root` — but `self.config.workspace_root` might be just `"."` (default)
- ReasoningEngine is the center of the Ω³ graph — 3 consumers
- RelationshipEngine is the other hub — powers ReasoningEngine, DigitalCivilization, ReverseEngineeringEngine
- The canonical_registry, meta_model, and relationship_engine are all connected after creation via side-effect functions (register_universal_types, sync_uem_entities_to_meta_model)

---

## 10. Object Creation Summary

### Total Objects Created in boot()

| Group | Objects | Registered in DI |
|---|---|---|
| Phase 1 (DI Bootstrap) | 7 | 7 |
| Phase 2 (Core Services) | 15 | 15 |
| Phase 3 (GENESIS-VIII) | 22 | 5 |
| Phase 4 (GENESIS-IX) | 7 | 7 |
| Phase 5 (GENESIS-X) | 2 | 2 |
| Phase 6 (GENESIS-XI) | 2 | 2 |
| Phase 7 (GENESIS-XII) | 4 | 4 |
| Phase 8 (Ω³) | 12 | 12 |
| **Total** | **~71 objects** | **~54 registered** |

### Objects NOT Registered in DI
- 16 memory type instances (only in `self.memory_types` dict)
- MemoryConsolidator (created, not stored)
- ForgettingMechanism (created, not stored)
- 2 simulator_v2/scientist instances (declared in __init__ but NEVER created in boot())

### Objects Declared in __init__ but NEVER Instantiated in boot()
These are `None` after `boot()` completes:

| Variable | Purpose |
|---|---|
| `self.simulator` (SimulatorEngine) | Genesis-VIII, never created |
| `self.discovery` (DiscoveryEngine) | Genesis-VIII, never created |
| `self.simulator_v2` (SimulatorEngineV2) | Genesis-IX, never created |
| `self.scientist` (EngineeringScientist) | Genesis-IX, never created |
| `self.mathematics_v2` (EngineeringMathematics) | Genesis-IX, never created |
| `self.meta_compiler` (MetaCompiler) | DI registered but created elsewhere? |

**6 declared objects that are never created during boot()** — vestigial declarations.

---

## 11. Shutdown Flow

```
shutdown()
  └── brain.stop_integration()                              # Stops brain event loop
  └── vrip.engine._save_checkpoint()                        # Saves VRIP state
  └── event_bus.emit("platform.shutdown", {...})            # Notifies subscribers
  └── metadata_store.close()
  └── knowledge_store.close()
  └── history_store.close()
  └── artifact_store.close()
```

**17 services with shutdown hooks registered** (DI bootstrap checkspoint + platform.py shutdown).

**Missing shutdown**:
- graph/KnowledgeGraphEngine — no close/shutdown
- PhysicsEngine — no shutdown
- EngineeringOS — no shutdown
- PlatformV2 — no shutdown
- UCOS, UniversalKernel — no shutdown
- MetaCompiler, Database (UED) — no shutdown
- FabricKernel, UnifiedGraph, ExecutionEngineV2 — no shutdown
- MetaModelEngine — no shutdown
- EconomicsEngine, EngineeringPlanner — no shutdown
- ReasoningEngine, RepositoryScientist, etc. — no shutdown
- OmegaLoop — no shutdown

---

## 12. Ownership Graph

### Who Owns What (from VenusPlatform instance)

```
VenusPlatform (self)
  ├── Owns (direct reference):
  │   ├── config, provider, event_bus, metadata_store, knowledge_store
  │   ├── history_store, artifact_store, checkpoint_store, memory_store
  │   ├── compiler, graph, executor, metadata, diagnostics, indexer
  │   ├── plugins, capabilities, package, memory_engine, project_mgr
  │   ├── certification, security, vrip, brain, digital_twin
  │   ├── memory_types (16), memory_consolidator, forgetting
  │   ├── physics, knowledge_graph, engineering_os, civilization, evolution
  │   ├── platform_v2, brain_v4, ums, hypergraph_core
  │   ├── planetary_knowledge, civilization_v3, evolution_v4
  │   ├── ucos, kernel, meta_compiler, ued
  │   ├── fabric, unified_graph, execution_engine, orchestrator
  │   ├── meta_model, exec_graph, exec_graph_engine, exec_graph_monitor
  │   ├── economics, planner, relationship_engine, canonical_registry
  │   ├── reasoning_engine, repository_scientist, repository_engineer
  │   ├── repository_economics, digital_civilization
  │   ├── reverse_engineering_engine, omega_loop
  │
  ├── Owns (via DI container - shared ownership):
  │   └── All ~54 registered instances (ServiceProvider._instances)
  │
  └── Subscribe to (via EventBus):
      └── EventBus subscriber list (per event type)
```

### Cross-Service Dependency Graph (Who Depends on What)

```
EngineeringBrain
  ├── depended on by: IntelligenceService, PlanetaryDigitalTwin
  ├── owns: graph, integration

IntelligenceService (VRIP)
  └── depends on: EngineeringBrain, CheckpointStore

ReasoningEngine
  ├── depended on by: RepositoryScientist, RepositoryEngineer, RepositoryEconomics
  └── depends on: RelationshipEngine, MetaModelEngine, canonical_registry

EventBus
  └── depended on by: 14+ services (nearly everything)

MemoryStore
  └── depended on by: PackageManager, ProjectManager, CertificationEngine,
                       SecurityValidator, MemoryEngine

FabricKernel
  └── depended on by: EngineeringOrchestrator

UnifiedGraph
  └── depended on by: EngineeringOrchestrator

Database (UED)
  └── depended on by: EngineeringOrchestrator

ExecutionEngineV2
  └── depended on by: EngineeringOrchestrator
```

---

## 13. Critical Violations Found

### V1: Duplicate Execution Engines
Two `ExecutionEngine` classes exist:
- `genesis.runtime.executor.ExecutionEngine` (created Phase 2, registered)
- `genesis.execution.ExecutionEngine as ExecutionEngineV2` (created Phase 7, registered)

Same role. Different module. No relationship. No delegation.

### V2: Duplicate Graph Engines
Six graph implementations:
- `genesis.graph.engine.KnowledgeGraphEngine` (Phase 2, wired to EventBus + storage)
- `genesis.graph_v2.UnifiedGraph` (Phase 7, standalone)
- `genesis.hypergraph.HypergraphKnowledgeCore` (Phase 4, standalone)
- `genesis.knowledge_graph.PlanetaryKnowledgeGraph` (Phase 3, standalone)
- `genesis.graphdb` (separate module, 835L)
- `genesis.brain.graph` (inside EngineeringBrain)

### V3: Duplicate Civilization Engines
- `genesis.civilization_v2.SoftwareCivilization` (Phase 3)
- `genesis.civilization_v3.SoftwareCivilizationV3` (Phase 4)
- `genesis.digital_civilization.DigitalCivilization` (Phase 8)
- `genesis.civilization/` (module directory, 16+ files)

### V4: Duplicate Platform/OS Frameworks
- `genesis.platform.VenusPlatform` (God constructor)
- `genesis.platform_v2.PlatformV2` (Phase 4)
- `genesis.engineering_os.EngineeringOS` (Phase 3)
- `genesis.kernel.UniversalKernel` (Phase 5)
- `genesis.fabric.FabricKernel` (Phase 7)
- `genesis.os/` (module directory, 14 files)

### V5: Unused Object Creation
- `SimulatorEngine` — imported, declared in __init__, NEVER created in boot()
- `DiscoveryEngine` — imported, declared in __init__, NEVER created in boot()
- `SimulatorEngineV2` — imported, declared in __init__, NEVER created in boot()
- `EngineeringScientist` — imported, declared in __init__, NEVER created in boot()
- `EngineeringMathematics` — imported, declared in __init__, NEVER created in boot()
- `MemoryConsolidator` — created in boot(), never stored or used
- `ForgettingMechanism` — created in boot(), never stored or used

### V6: Abandoned Instances
- The 16 memory type instances in `self.memory_types` dict are created but:
  - Never registered in DI
  - Never connected to the memory_engine or MemoryStore
  - Only accessible via `platform.memory_types["EpisodicMemory"]`
  - No event bus subscription
  - Essentially orphaned

### V7: VRIP Blocks Boot
- `IntelligenceService.run_all()` runs SYNCHRONOUSLY during boot() — the platform does not finish booting until VRIP completes
- VRIP is a potentially expensive multi-phase intelligence pipeline

### V8: Import-Time Side Effects
- `platform.py` module-level imports trigger 7 DeprecationWarnings
- `ModulePluginRegistry` initializes at import time
- Any file that does `import platform` (like pytest's doctest plugin) breaks because of import cascade

### V9: No Health Checks for 70% of Services
- Only 4 stores have `.close()` in shutdown
- No health/liveness probes exist
- No startup verification that services initialized correctly

---

## 14. Lifecycle Analysis

### Eager Initialization
ALL services are eagerly created during `boot()`. The DI container's lazy initialization feature (`lazy=True` default) is never used — every service uses `register_instance()`, which bypasses lazy loading.

### Synchronous Initialization
Everything runs in the caller's thread, sequentially. No async, no parallelism.

### No Retry/Resilience
If EngineeringBrain fails to initialize, the entire boot fails. There are no retry mechanisms, no fallback strategies, no partial boot mode.

### VRIP Boot Dependency
`IntelligenceService.run_all()` is the heaviest single call in boot(). It blocks all subsequent initialization until complete.

---

## 15. Metrics

| Metric | Value |
|---|---|
| Total Python files (excl tests) | 335 |
| Total lines (excl tests) | 71,916 |
| Test files | 72 |
| Test count (collected) | 2,763 |
| Objects created in boot() | ~71 |
| Services registered in DI | ~54 |
| Module-level imports in platform.py | ~61 |
| Deprecated modules imported at module level | 7 |
| Objects declared but never created | 6 |
| Objects created but never used | 2 (MemoryConsolidator, ForgettingMechanism) |
| Shutdown hooks registered | 17 |
| Services with no shutdown | ~50 |
| Duplicate execution engines | 2 |
| Duplicate graph engines | 6 |
| Duplicate civilization engines | 4 |
| Duplicate platform/OS frameworks | 6 |

---

## 16. Execution Travel (Data Flow Through the System)

```
boot() → EventBus created first → all later services get EventBus reference
       → EngineeringBrain gets graph.graph reference from KnowledgeGraphEngine
       → VRIP uses brain, which has graph access
       → VRIP writes results back through brain + checkpoint_store
       → EvolutionEngine observes metrics from brain, digital_twin, vrip, graph
       → MetaModelEngine scans repo_path
       → OmegaLoop gets repo_root (same as workspace_root)
       → boot.completed event emitted with VRIP results + service map

run()  → CLI.run() (interactive) or platform daemon mode
       → OmegaLoop.run() if invoked (not auto-started)

shutdown() → brain stops integration
           → VRIP saves checkpoint
           → shutdown event emitted
           → 4 stores close
```

**End of Mission 1: Execution Reconstruction.**
