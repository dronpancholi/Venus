# PROJECT NEXUS PHASE II — Mission 9: Engineering Reference Manual

**Date**: 2026-06-30 | **Version**: 1.0 | **Repository**: 407 Python files, 94,344 lines, 2,763 tests

---

## 1. Platform Philosophy

Genesis is an autonomous engineering intelligence platform. It observes codebases, understands their architecture, generates improvements, and evolves itself. The core principle is: **capability convergence** — every engineering capability should have exactly one canonical implementation, discoverable through a registry, and replaceable through a deprecation lifecycle.

### Design Tenets
1. **Canonical over Duplicate**: Never create a new abstraction without checking existing ones
2. **Lazy over Eager**: Defer instantiation until first use (engine imports, service creation)
3. **Composable over Monolithic**: Small, focused modules over large orchestrators
4. **Observable over Opaque**: Every execution produces measurable results
5. **Traceable over Ephemeral**: Every decision is documented in an Engineering Decision Record

## 2. Repository Structure

```
genesis/
├── __init__.py          # Package exports
├── __main__.py          # CLI entry point
├── omega_loop.py        # (6,575L) 18-Book GENESIS ∞ constitution
├── atlas.py             # (1,297L) 15-Stage analysis engine
├── platform.py          # (747L) Unified platform boot
│
├── ontology.py          # (1,398L) Universal Entity Model — 32 entity types
├── meta_model.py        # (711L) Meta-model engine
├── reasoning.py         # (364L) Engineering reasoning
├── reverse_engineer.py  # (910L) Code scanner and analyzer
├── census.py            # (863L) Repository census
│
├── plugin/              # Plugin system
│   ├── registry.py      #   ModulePluginRegistry (110L, CANONICAL)
│   ├── manager.py       #   PluginManager (236L)
│   └── manifest.py      #   PluginManifest (123L)
│
├── utils/               # Shared utilities (L0)
│   ├── graph_algorithms.py  # topsort, find_cycles, subgraph (167L)
│   ├── identity.py          # generate_id (35L)
│   └── serialization.py     # Serializable protocol (48L)
│
├── core/                # Core abstractions (L1)
│   ├── base.py          #   BaseEntity, BaseCapability (181L)
│   ├── types.py         #   SemanticType, type_registry (135L)
│   ├── uir.py           #   UIRNode, UIREdge, UIRGraph (398L)
│   └── metadata.py      #   MetadataEngine (213L)
│
├── persistence/         # Storage layer (L1)
│   ├── repository.py    #   InMemoryRepository (147L)
│   └── sqlite_store.py  #   SQLite-backed stores (572L)
│
├── os/                  # Operating system abstraction
│   ├── runtime.py       #   AutonomousRuntime (499L)
│   ├── scheduler.py     #   PersistentScheduler (199L)
│   ├── planner.py       #   PersistentPlanner (198L)
│   ├── task_graph.py    #   PersistentTaskGraph (197L)
│   ├── queue.py         #   DistributedQueue (154L)
│   ├── agent_runtime.py #   AgentProcess (142L)
│   ├── watchers.py      #   File/Git/Process watchers (397L)
│   ├── memory_manager.py#   Memory tiers (199L)
│   ├── checkpoint.py    #   CheckpointManager (146L)
│   ├── recovery.py      #   RecoveryManager (129L)
│   └── observation.py   #   ObservationManager (166L)
│
├── brain/               # Engineering brain (CANONICAL)
│   ├── __init__.py      #   EngineeringBrain (264L)
│   ├── entity.py        #   BrainEntity (499L)
│   ├── graph.py         #   Brain graph (263L)
│   ├── cognition/       #   Goals, beliefs, reasoning, attention
│   └── ...
│
├── brain_v4.py          # (731L, DEPRECATED) Old brain, use brain/
│
├── civilization/        # Civilization subsystem (CANONICAL)
│   ├── agents/          #   AI agents (895L)
│   ├── knowledge/       #   Knowledge flow (522L)
│   ├── world_model/     #   World model + Bayesian prediction (498L)
│   └── ...
│
├── digital_civilization.py  # (321L, CANONICAL) Civilization
├── civilization_v2.py       # (273L, DEPRECATED) Old civ, use digital_civilization
├── civilization_v3.py       # (241L, DEPRECATED) Old civ, use digital_civilization
│
├── repository_scientist.py  # (247L, CANONICAL) Experiment management
├── repository_engineer.py   # (221L, CANONICAL) Improvement generation
├── repository_economics.py  # (160L) Economic analysis
├── discovery.py             # (400L, DEPRECATED) Old science, use repository_scientist
├── scientist.py             # (383L, DEPRECATED) Old science, use repository_scientist
│
├── evolution_v4.py     # (352L, CANONICAL) Self-evolution
├── evolution.py         # (310L, DEPRECATED) Old evolution, use evolution_v4
│
├── simulator_v2.py      # (289L, CANONICAL) Multi-domain simulation
├── simulator.py         # (337L, DEPRECATED) Old simulator, use simulator_v2
│
├── mathematics.py       # (796L) Original mathematics — omega_loop still imports this
├── mathematics_v2.py    # (361L) Newer mathematics — platform imports this
│
├── ucos/                # Unified Capability Operating System (13 files, ~2,000L total)
│   ├── capability.py    #   Core capability definitions
│   ├── registry.py      #   Capability registry
│   ├── resolver.py      #   Dependency resolution
│   ├── planner.py       #   Capability planning
│   ├── lifecycle.py     #   Lifecycle management
│   ├── graph.py         #   Dependency graph analysis
│   ├── marketplace.py   #   Capability marketplace
│   ├── validator.py     #   Capability validation
│   ├── runtime.py       #   Capability execution runtime
│   ├── metrics.py       #   Capability metrics
│   ├── negotiator.py    #   Capability negotiation
│   └── ucos.py          #   UCOS facade
│
├── ued/                 # Unified Event-Driven Data Platform (13 files, ~2,200L total)
│   ├── types.py         #   Core types
│   ├── engine.py        #   Storage engine (MVCC, journal, page store)
│   ├── cache.py         #   Cache manager (LRU, TT)
│   ├── index.py         #   BTree, Hash, Inverted, Vector indexes
│   ├── stores.py        #   Document, Metadata, Version stores
│   ├── graph.py         #   Graph store (nodes, edges, paths)
│   ├── vector.py        #   Vector store (cosine, euclidean)
│   ├── timeseries.py    #   Time-series and event stores
│   ├── object.py        #   Object, snapshot, archive stores
│   ├── query.py         #   Query planner
│   ├── shard.py         #   Shard manager
│   └── database.py      #   Database facade
│
├── tests/               # Test suite (72 files, 2,763 tests)
│   ├── test_architecture.py  #   Layer compliance tests (633L)
│   ├── test_compliance.py    #   Platform lifecycle tests (102L)
│   ├── test_phase0.py        #   Core utility tests (446L)
│   ├── programs/             #   Legacy program tests (deprecated module tests)
│   └── ...
│
├── decisions/           # Engineering Decision Records
│   ├── EDR-001-plugin-registry-pattern.md
│   └── EDR-002-atlas-omegaloop-feedback-loop.md
│
├── _generated/          # Auto-generated outputs
│   ├── reports/         #     SREC, NEXUS, and other reports
│   ├── atlas/           #     Atlas stage outputs
│   └── nexus_phase_ii/  #     Current cycle outputs
│
├── config/              # Configuration
├── events/              # Event bus
├── di/                  # Dependency injection
├── compiler/            # USIR compiler
├── usir/                # Universal Software Intermediate Representation
├── digital_twin/        # Digital twin system
├── graph/               # Graph engine (OLD)
├── graph_v2/            # Unified graph (NEWER)
├── execution_graph.py   # Execution graph (standalone)
├── knowledge_graph.py   # Knowledge graph (standalone)
├── hypergraph.py        # Hypergraph (standalone)
├── graphdb/             # Graph database (standalone)
├── planner.py           # Engineering planner
├── planning/            # Multi-level planning system
├── economics.py         # Economics engine
├── physics.py           # Physics engine
├── marketplace/         # Capability marketplace
├── laboratory/          # Code mining and analysis
├── datalake/            # Data lake
├── observatory/         # Software observatory
├── acquisition/         # Data acquisition
├── temporal/            # Temporal event system
├── intelligence/        # VRIP intelligence
├── execution/           # Workflow execution
├── kernel/              # Universal kernel
├── fabric/              # Engineering fabric
├── meta/                # Meta compiler
├── autonomous/          # Autonomous engineering cycle
├── cli/                 # CLI commands
├── api/                 # API router
├── studio/              # Studio backend
├── integration/         # External integrations
├── memory/              # Memory stub services
├── capability/          # Capability registry
├── validation/          # Validation engine
├── runtime/             # Execution engine
├── indexer/             # Repository indexer
├── certification/       # Certification engine
├── package/             # Package manager
├── security/            # Security validator
├── project/             # Project manager
└── diagnostics/         # Diagnostics engine
```

## 3. Core Abstractions

### UniversalEntity
- Defined in `ontology.py` (1,398L)
- 32 entity types: Artifact, Capability, Process, Evidence, Decision, Execution, Knowledge, Research, Prediction, Experiment, Economics, History, Memory, Simulation, Metric, Validation, Contract, Specification, Policy, Service, Agent, Component, Graph, Timeline, Version, Identity, Ontology, Runtime, Compiler, Platform
- Base for all typed entities in the system
- Provides: generate_id(), versioning, timestamps, fingerprints, evidence linking

### UIR (Universal Intermediate Representation)
- Defined in `core/uir.py` (398L)
- Directed graph representation of code architecture
- UIRNode (typed nodes), UIREdge (typed edges), UIRGraph (graph container)
- Sub-types: DependencyGraph, CapabilityGraph, ValidationGraph, ExecutionGraph

### USIR (Universal Software IR)
- Defined in `usir/` (multi-language)
- Represents source code in any language as a typed graph
- Language adapters: Python (382L), TypeScript/JavaScript (647L)
- Used by compiler for cross-language analysis

### ModulePluginRegistry
- Defined in `plugin/registry.py` (110L, CANONICAL)
- Dict-based registry mapping engine names to modules
- Lazy imports: engines are imported only when accessed
- Discovery via `to_dict()` for programmatic enumeration
- 5 engines registered: reasoning, scientist, engineer, economics, reverse_engineer

## 4. Execution Engines

### OmegaLoop (6,575 lines)
18 sequential Books implementing the GENESIS ∞ constitution:
1. Complete Digital Universe — canonical engineering graph
2. Multi-Language Compilation — expand USIR to 20 languages
3. Planetary Observatory — observe software worldwide
4. Engineering Physics — statistically derived laws
5. Engineering Biology — ecosystems, evolution, extinction
6. Engineering Cognition — complete engineering mind
7. Engineering Science — hypothesis, replication, archive
8. Autonomous Engineering — observe, simulate, deploy, learn
9. Engineering Economics — cost, debt, ROI, capital
10-18. Marketplace, Foundation Models, Self-Evolution, Validation, Convergence, Civilization, Meta-Intelligence, Impact, Recursive Future

**Key pattern**: Lazy imports for all engines (module-level imports only for ontology, meta_model, plugin, mathematics).

### Atlas (1,297 lines)
15 sequential stages for repository reconstruction:
1-5: Inventory → Discovery → Goals → Subsystem → Relationships
6-10: Problems → Hypotheses → Designs → Measurements → Tests
11-15: Benchmarks → Roadmap → Report → Archive → Finish

**Key pattern**: Stage 9 measures actual code (registry existence, import counts). Stage 10 runs pytest as subprocess. Atlas→OmegaLoop feedback via filesystem IPC.

### Platform (747 lines)
Three-phase lifecycle:
1. bootstrap() — Create DI container, register infrastructure
2. boot() — Wire domain services, run VRIP intelligence
3. shutdown() — Graceful teardown, checkpoint save

**Note**: Currently a "god constructor" with ~50 imports. Lazy service registry is the planned refactor.

## 5. Ontology & Meta-Model

### Entity Types (32)
```
UArtifact, UCapability, UProcess, UEvidence, UDecision,
UExecution, UKnowledge, UResearch, UPrediction, UExperiment,
UEconomics, UHistory, UMemory, USimulation, UMetric,
UValidation, UContract, USpecification, UPolicy, UService,
UAgent, UComponent, UGraph, UTimeline, UVersion,
UIdentity, UOntology, URuntime, UCompiler, UPlatform
```

### Relationship Types (32)
Each entity has dedicated relationship types defined in URelType enum.

### Meta-Model Engine
- `meta_model.py` (711L)
- `MetaModelEngine` scans repository and builds entity schema
- `register_universal_types()` registers canonical types
- `sync_uem_entities_to_meta_model()` syncs ontology entities

## 6. Plugin System

### ModulePluginRegistry
```python
class ModulePluginRegistry:
    """Central registry for engine plugins with lazy loading."""

    def __init__(self):
        self._plugins: dict[str, EnginePlugin] = {}

    def register(self, name: str, module_path: str, engine_class: str,
                 description: str = ""):
        self._plugins[name] = EnginePlugin(
            name=name, module_path=module_path,
            engine_class=engine_class, description=description,
        )

    def get(self, name: str) -> Any:
        """Lazy-import and instantiate engine."""
        plugin = self._plugins[name]
        if plugin._instance is None:
            mod = importlib.import_module(plugin.module_path)
            cls = getattr(mod, plugin.engine_class)
            plugin._instance = cls()
        return plugin._instance

    def to_dict(self) -> dict[str, dict]:
        """Programmatic discovery."""
```

Used by OmegaLoop:
```python
# In OmegaLoop._register_plugins()
self._plugins = ModulePluginRegistry()
self._plugins.register("reasoning", "genesis.reasoning", "ReasoningEngine")
self._plugins.register("scientist", "genesis.repository_scientist", "RepositoryScientist")
self._plugins.register("engineer", "genesis.repository_engineer", "RepositoryEngineer")
self._plugins.register("economics", "genesis.repository_economics", "RepositoryEconomics")
self._plugins.register("reverse_engineer", "genesis.reverse_engineer", "ReverseEngineeringEngine")
```

## 7. Persistence

### Stores (in persistence/)
- MetadataStore: Key-value metadata with tags
- KnowledgeStore: Knowledge graph (nodes + edges)
- HistoryStore: Append-only event log
- ArtifactStore: Large artifact storage
- MemoryStore: Namespace-based memory
- CheckpointStore: Execution checkpoint save/restore
- SQLite-backed via persistence/sqlite_store.py

### Repositories (in persistence/repository.py)
- InMemoryRepository: Generic repository pattern
- CRUD operations with find() by predicate

## 8. Capability System (UCOS)

13 files under ucos/ implementing a complete capability management system:

- **Capability**: Core unit with state, version, health, permissions
- **CapabilityRegistry**: Register, find, search capabilities
- **CapabilityResolver**: Dependency resolution, boot ordering, cycle detection
- **CapabilityPlanner**: Execution planning with parallel groups, resource estimation
- **CapabilityLifecycleManager**: State machine (verify → ready → running → failed → degraded → recovering)
- **CapabilityDependencyGraph**: Graph analysis (critical path, layers, fan-in/fan-out)
- **CapabilityNegotiator**: Provider-consumer agreements with proposals and contracts
- **CapabilityMarketplace**: Search, alternatives, reviews, rankings
- **CapabilityValidator**: Health checks, custom rules, dependency validation
- **CapabilityRuntime**: Execution with context, middleware, retry
- **CapabilityMetrics**: Counters, gauges, histograms, snapshots
- **UCOS**: Facade combining all subsystems

## 9. Data Platform (UED)

13 files under ued/ implementing a complete data platform:

- **Types**: CollectionType, StorageConfig, IsolationLevel, Query, QueryResult, ShardKey, CompressionType, CachePolicy
- **StorageEngine**: MVCC store with page allocator, journal, transaction manager, catalog
- **CacheManager**: LRU with TTL, hit rate tracking, invalidation
- **Indexes**: BTree (range scans), Hash (exact match), Inverted (text search), Vector (cosine/euclidean)
- **Stores**: Document, Metadata, Version
- **GraphStore**: Directed graph with BFS, shortest path
- **VectorStore**: ANN search with filters
- **TimeSeriesStore**: Aggregation, downsampling, subscription
- **EventStore**: Append-only event streams with categories
- **ObjectStore**: Chunked, deduplicated, compression (zstd, lz4)
- **QueryPlanner**: Plan, explain, optimize, history
- **ShardManager**: Consistent hashing, range-based sharding
- **Database**: Facade combining all stores

## 10. Testing

- **Framework**: pytest 9.0.3
- **Total**: 2,763 tests (all passing)
- **72 test files** covering:
  - Core utilities (utils/identity, utils/graph_algorithms, utils/serialization)
  - Platform lifecycle (bootstrap, boot, shutdown, summary, double-boot)
  - Architecture compliance (layers, circular deps via import graph)
  - OS services (scheduler, planner, task_graph, queue, watchers, runtime)
  - Capability system (UCOS — 10 test files, 130+ tests)
  - Data platform (UED — 1 test file, 122 tests)
  - Persistence (all 6 stores)
  - Ontology and meta-model
  - Reasoning engine
  - Repository scientist, engineer, economics
  - Legacy program tests (16 old test files for deprecated modules)

## 11. Deprecation Lifecycle

Currently deprecated modules (all with DeprecationWarning):

| Module | Use Instead |
|--------|-------------|
| genesis.discovery | genesis.repository_scientist.RepositoryScientist |
| genesis.scientist | genesis.repository_scientist.RepositoryScientist |
| genesis.simulator | genesis.simulator_v2.SimulatorEngineV2 |
| genesis.evolution | genesis.evolution_v4.EvolutionEngineV4 |
| genesis.civilization_v2 | genesis.digital_civilization.DigitalCivilization |
| genesis.civilization_v3 | genesis.digital_civilization.DigitalCivilization |
| genesis.brain_v4 | genesis.brain.EngineeringBrain |

## 12. Future Evolution

### Near-term (Phase II)
1. **Consolidation execution**: Migrate all old modules to canonical (P1-P9)
2. **OmegaLoop decomposition**: Extract 6,575-line file into package
3. **Platform reconstruction**: Lazy service registry
4. **Universal execution model**: Unified ExecutionPhase interface

### Medium-term
1. **Self-improvement engine**: Autonomous problem discovery → simulation → implementation → rollback
2. **Architecture governance**: CanonicalRegistry + pre-commit checks
3. **Engineering knowledge store**: Queryable, linkable knowledge artifacts
4. **Quality metrics dashboard**: Real-time engineering health

### Long-term
1. **Multi-agent governance**: Autonomous architecture review board
2. **Predictive simulation**: Atlas-style reconstruction for any codebase
3. **Full autonomy**: Close the observe-analyze-plan-implement-verify cycle
4. **Epoch X readiness**: Self-designing platform capability
