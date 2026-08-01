# PROJECT NEMESIS — First Deliverable: Complete Repository Reconstruction

**Date**: 2026-06-30 | **Repository**: 407 Python files, 94,344 lines, 2,763 tests
**Scope**: Every subsystem, execution path, data flow, ownership, and overlap

---

## 1. Executive Summary

Genesis has evolved through 8+ architectural epochs (GENESIS PRIME → ZERO → EVOLUTION → ORION → ASCENSION → GENESIS ∞ → ATLAS → SREC → NEXUS). Each epoch added new subsystems without removing old ones. The result: 16 of 56 capabilities (28.6%) have 2+ competing implementations. The platform.py constructor creates 44+ services at boot time. Seven distinct execution models coexist. Six graph implementations share no common core.

**Core finding**: Genesis is not a coherent operating system. It is a federation of independently-developed subsystems that communicate through a shared ontology and a God-constructor platform. The canonicalization work begun in NEXUS Phase II is necessary but insufficient — deeper architectural reconstruction is required.

---

## 2. Every Subsystem: Origin, Purpose, Overlap, Canonicality

### 2.1 Orchestration Layer

| Subsystem | Lines | Purpose | Overlaps | Canonical? |
|-----------|-------|---------|----------|------------|
| `omega_loop.py` | 6,575 | 18-Book GENESIS ∞ constitution — sequential execution of all engineering phases | Atlas (different stage model) | Yes — primary orchestrator |
| `atlas.py` | 1,297 | 15-Stage repository reconstruction protocol | OmegaLoop (different execution model) | Yes — analysis engine |
| `platform.py` | 747 | God constructor — boots every service | platform_v2, engineering_os | **Anti-pattern** — should be thin |
| `autonomous/` | ~330 | Autonomous engineering cycle | OmegaLoop Book VIII, ExecutionEngine | **Should merge into OmegaLoop** |

**Why each exists**:
- OmegaLoop: GENESIS ∞ constitution — the master loop
- Atlas: "Eyes" — reconstructs repository state independently
- platform.py: Historical bootloader — grew from simple to god-object
- autonomous/: GENESIS-XII autonomous cycle — overlaps with OmegaLoop

**Data flow**: platform.py creates everything → calls OmegaLoop → OmegaLoop calls lazy engines → Atlas reads/writes filesystem → platform.shutdown()

### 2.2 Ontology & Meta-Model

| Subsystem | Lines | Purpose | Overlaps | Canonical? |
|-----------|-------|---------|----------|------------|
| `ontology.py` | 1,398 | 32 Universal Entity types, RelationshipEngine, URelType, canonical registry | metamodel/ (different entity model) | **Yes** — most consumed (22 consumers) |
| `meta_model.py` | 711 | MetaModelEngine — scans repo, builds entity schema | ontology.py (complementary) | Yes — extends ontology |
| `metamodel/` | ~800 | Workspace graph, entity registry, query | ontology.py, meta/ | **Legacy** — overlaps ontology.py |
| `reasoning.py` | 364 | Engineering reasoning engine | brain/cognition/reasoning.py | Yes |

**Critical finding**: `ontology.py` and `metamodel/` define DIFFERENT entity models. `ontology.py` has 32 UniversalEntity types with RelationshipEngine. `metamodel/` has EntityDefinition with UnifiedGraph. They serve the same purpose with incompatible APIs. `ontology.py` is canonical (22 consumers vs 5 for metamodel).

**Recommendation**: Deprecate `metamodel/`, port its features to `ontology.py`.

### 2.3 Graph Systems — THE WORST OVERLAP

| Subsystem | Lines | Purpose | Model | Canonical? |
|-----------|-------|---------|-------|------------|
| `graph/engine.py` | 305 | KnowledgeGraphEngine — event-driven graph | UIR-based | Legacy |
| `graph_v2/` | ~800 | UnifiedGraph — layered, partitioned, federated | GraphNode/Edge | **Should be canonical** |
| `graphdb/` | 835 | PersistentGraphDB — full graph database | Node/Edge/Query | **Standalone** (value) |
| `hypergraph.py` | 648 | HypergraphKnowledgeCore — hypergraph | HyperNode/HyperEdge | Legacy |
| `knowledge_graph.py` | 320 | PlanetaryKnowledgeGraph | KEntity/KRelation | Legacy |
| `execution_graph.py` | 420 | ExecutionGraph — DAG execution | ExecutionNode/Edge | Legacy |
| `core/uir.py` | 398 | UIR Graph — universal intermediate rep | UIRNode/UIREdge | **Core abstraction** |
| `usir/__init__.py` | 224 | USIR — language IR | USIRNode/Edge | **Core abstraction** |
| `ontology.py` | RelationshipEngine | Entity relationships | Entity/Relationship | — |
| `graph_v2/analytics.py` | 131 | Graph analytics | — | Unique capability |
| `graph_v2/federation.py` | 104 | Graph federation | — | Unique capability |

**6 distinct graph models**:
1. `UIRGraph` (core/uir.py) — UIRNode, UIREdge — architecture analysis
2. `USIRGraph` (usir/) — USIRNode — multi-language parsing
3. `PersistentGraphDB` (graphdb/) — full database with query builder
4. `HypergraphKnowledgeCore` (hypergraph.py) — hyperedges
5. `UnifiedGraph` (graph_v2/) — layered, partitioned, versioned
6. `RelationshipEngine` (ontology.py) — entity relationship traversal

**Recommendation**: graph_v2/ is the most architecturally complete. Port unique features from graph/, hypergraph.py, knowledge_graph.py, execution_graph.py into graph_v2/. Keep graphdb/ as standalone (it's a dedicated graph database). Keep RelationshipEngine for entity relationships. Keep UIR and USIR as dedicated IRs.

### 2.4 Execution Systems (7 models)

| Subsystem | Model | Status |
|-----------|-------|--------|
| OmegaLoop | Sequential 18-Phase | Canonical orchestrator |
| Atlas | Sequential 15-Stage | Canonical analyzer |
| Platform | boot() lifecycle | Needs reconstruction |
| `os/runtime.py` | Tick-based loop | Canonical for OS |
| `runtime/executor.py` | Workflow/Task | Legacy — use os/ |
| `execution/` | Engine/Pipeline/Job/Actor | Genesis-XII — unique |
| `autonomous/` | Observe-Plan-Act | Merge into OmegaLoop |
| `execution_graph.py` | DAG execution | Merge into graph_v2/ |

**Recommendation**: Define ONE execution model (UniversalExecutionPhase from NEXUS Phase II design). Everything becomes an adapter.

### 2.5 Planner Systems (3 models)

| Subsystem | Model | Status |
|-----------|-------|--------|
| `planner.py` | EngineeringPlanner — hierarchical plan tree | Unique value |
| `planning/` | Multi-level planner (strategic→implementation) | **Should be canonical** |
| `os/planner.py` | PersistentPlanner — OS-level planning | OS component |

**Recommendation**: planning/ is the most complete. planner.py has PlanNode tree — port to planning/. os/planner.py stays as OS component (uses different abstraction level).

### 2.6 Memory Systems (3 models)

| Subsystem | Model | Status |
|-----------|-------|--------|
| `memory/` | Types (14 memory types) + Consolidation + Engine | Canonical |
| `memory_system.py` | UniversalMemorySystem — 18 typed stores | **Duplicate** — merge into memory/ |
| `os/memory_manager.py` | Memory tiers (working/long-term/archival) | OS component — different purpose |

**Recommendation**: memory_system.py duplicates memory/ types. Port features to memory/ and deprecate.

### 2.7 Scientific Method (4 modules → still 2 canonical)

Current state from NEXUS Phase II:
- `discovery.py` (407L) — DEPRECATED, warning active
- `scientist.py` (390L) — DEPRECATED, warning active
- `repository_scientist.py` (247L) — CANONICAL
- `repository_engineer.py` (221L) — CANONICAL companion

**Still to do**: Actually migrate platform.py consumers from discovery/scientist to repository_scientist.

### 2.8 Civilization (4 modules → 1 canonical)

- `civilization_v2.py` (280L) — DEPRECATED, warning active
- `civilization_v3.py` (248L) — DEPRECATED, warning active
- `digital_civilization.py` (321L) — CANONICAL
- `civilization/` (full subpackage) — ACTIVE

**Still to do**: civilization/ subpackage (knowledge, world_model, agents, etc.) is a large (~4,500L) independent system with no overlap with digital_civilization.py. They serve different purposes: civilization/ = agent society, digital_civilization = institute/contract/reputation system.

### 2.9 Brain Systems (2 models)

- `brain/` (~2,800L) — CANONICAL — EngineeringBrain, BrainEntity, cognition/
- `brain_v4.py` (738L) — DEPRECATED

**Status**: Deprecation warning added in NEXUS Phase II. platform.py still imports and instantiates it.

### 2.10 Mathematics (2 models)

- `mathematics.py` (796L) — OLD but ACTIVE — omega_loop imports module-level
- `mathematics_v2.py` (361L) — NEWER — platform imports it

**Critical constraint**: omega_loop.py lines 57-62 import from OLD mathematics.py at module level:
```python
from genesis.mathematics import (
    RepositoryMathematics, RepositoryEntropy, RepositoryStability,
    KnowledgeDiffusion, ArchitectureMomentum, DependencyEnergy,
    EngineeringGravity, TechnicalDebtTensor, RepositoryCurvature,
    ModuleMetrics,
)
```
These classes DO NOT EXIST in mathematics_v2.py. Different API. Cannot simply swap imports.

**Recommendation**: Port the omega_loop-needed classes to mathematics_v2.py or create a compatibility shim in mathematics.py that delegates to mathematics_v2.py.

---

## 3. Complete Execution Path

### 3.1 Startup Sequence
```
Python interpreter
  └── __main__.py
      └── from genesis.platform import VenusPlatform
          └── Triggers 50+ module-level imports (EVERYTHING)
              ├── genesis.ontology → genesis.utils.*
              ├── genesis.meta_model → genesis.ontology
              ├── genesis.reasoning → genesis.ontology, genesis.meta_model
              ├── genesis.brain → genesis.graphdb, genesis.ontology, genesis.utils
              ├── genesis.digital_twin → genesis.brain, genesis.ontology
              ├── genesis.intelligence → genesis.brain, genesis.persistence
              ├── genesis.compiler.compiler → genesis.ontology, genesis.usir
              ├── genesis.repository_scientist → genesis.reasoning
              ├── genesis.discovery (DEPRECATED)
              ├── genesis.scientist (DEPRECATED)
              ├── genesis.simulator (DEPRECATED)
              ├── genesis.evolution (DEPRECATED)
              ├── genesis.civilization_v2 (DEPRECATED)
              ├── genesis.civilization_v3 (DEPRECATED)
              ├── genesis.brain_v4 (DEPRECATED)
              ├── genesis.platform_v2
              ├── genesis.engineering_os
              ├── genesis.omega_loop → genesis.mathematics (OLD), genesis.ontology, genesis.plugin
              └── genesis.atlas → genesis.ontology, genesis.reverse_engineer
      └── platform = VenusPlatform(config)
      └── platform.bootstrap()
          └── di_bootstrap → creates ServiceProvider
          └── Registers 6 stores in DI
      └── platform.boot()
          └── Tier 1: Infrastructure (compiler, graph, executor, metadata, etc.)
          └── Tier 2: Brain + Intelligence (brain, vrip, digital_twin)
          └── Tier 3: GENESIS-VIII (memory_types, engineering_os, civilization, evolution)
          └── Tier 4: GENESIS-IX (platform_v2, brain_v4, ums, civilization_v3, evolution_v4)
          └── Tier 5: GENESIS-X (ucos, kernel)
          └── Tier 6: GENESIS-XI (meta_compiler, ued)
          └── Tier 7: GENESIS-XII (fabric, graph_v2, execution, autonomous)
          └── Tier 8: GENESIS-XIII (meta_model, execution_graph, economics, planner,
                        relationship_engine, reasoning, repository_scientist/engineer/economics,
                        digital_civilization, reverse_engineer, omega_loop)
          └── Emits platform.boot.completed
      └── platform.omega_loop.run()
          └── See "OmegaLoop Execution" below
      └── platform.shutdown()
```

### 3.2 OmegaLoop Execution
```
OmegaLoop.run()
  └── Book I:   Complete Digital Universe (reverse_engineer scan → UIR graph)
  └── Book II:  Multi-Language Compilation (USIR parsers)
  └── Book III: Planetary Observatory (observatory miners)
  └── Book IV:  Engineering Physics (statistical models from mathematics.py)
  └── Book V:   Engineering Biology (ecosystem analysis)
  └── Book VI:  Engineering Cognition (brain integration)
  └── Book VII: Engineering Science (reasoning engine → hypotheses)
  └── Book VIII:Autonomous Engineering (simulate → deploy)
  └── Book IX:  Engineering Economics (repository_scientist → economics)
  └── Book X:   Engineering Marketplace
  └── Book XI:  Engineering Foundation Models
  └── Book XII: Self Evolution (Atlas feedback → roadmap)
  └── Book XIII:External Validation
  └── Book XIV: Continuous Convergence
  └── Book XV:  Engineering Civilization (digital_civilization)
  └── Book XVI: Meta Intelligence
  └── Book XVII:Planetary Impact
  └── Book XVIII:Recursive Future
  └── Each Book writes PhaseDeliverable → JSON in _generated/omega/
```

### 3.3 Shutdown
```
platform.shutdown()
  └── brain.stop_integration()
  └── vrip.engine._save_checkpoint()
  └── bus.emit("platform.shutdown", {started_at, shutdown_at})
  └── Close all store connections
```

---

## 4. Data Flow Diagrams

### 4.1 Import Dependency Flow (Genesis→External)
```
genesis/ → external stdlib (json, os, time, pathlib, typing, etc.)
    ↓
utils/ → genesis.core.uir (UIRGraph)
    ↓
core/ → utils/ (identity, graph_algorithms)
    ↓
events/ → core/ (EventBus)
    ↓
persistence/ → sqlite3
    ↓
ontology/ → utils/ (identity)
    ↓
di/ → events/, persistence/, core/ (ServiceProvider)
    ↓
plugin/ → events/, core/ (ModulePluginRegistry)
    ↓
ALL OTHER SUBSYSTEMS → ontology/, utils/ (the two most consumed modules)
    ↓
platform.py → ALL OF THE ABOVE (god constructor)
    ↓
omega_loop.py, atlas.py → ontology/, meta_model/, mathematics/
```

### 4.2 Service Registration Flow
```
platform.bootstrap()
  └── ServiceProvider.register(MetadataStore, factory)
  └── ServiceProvider.register(KnowledgeStore, factory)
  └── ServiceProvider.register(HistoryStore, factory)
  └── ServiceProvider.register(ArtifactStore, factory)
  └── ServiceProvider.register(CheckpointStore, factory)
  └── ServiceProvider.register(MemoryStore, factory)

platform.boot()
  └── ServiceProvider.register(Compiler, compiler)
  └── ServiceProvider.register(KnowledgeGraphEngine, graph)
  └── ServiceProvider.register(ExecutionEngine, executor)
  └── ServiceProvider.register(MetadataEngine, metadata)
  └── ... (+40 more register_instance calls)
```

### 4.3 Atlas → OmegaLoop Feedback Flow
```
Atlas.run() completes
  └── Writes _generated/atlas/atlas_findings.json
  └── Contains: problems[], hypotheses[], roadmap[]

OmegaLoop Book XII starts
  └── Checks _generated/atlas/atlas_findings.json exists
  └── If yes: parse → generate [ATLAS] roadmap items → integrate
  └── If no: skip (graceful degradation)
```

### 4.4 Knowledge Flow
```
Platform services → generate data
    ↓
Store in persistence stores (SQLite):
  ├── MetadataStore: key-value metadata with tags
  ├── KnowledgeStore: knowledge graph (nodes + edges)
  ├── HistoryStore: append-only event log
  ├── ArtifactStore: large artifacts
  ├── MemoryStore: namespace-based memory
  └── CheckpointStore: execution checkpoints
    ↓
OmegaLoop/Atlas → generate reports
    ↓
Write filesystem reports (_generated/, Reports/)
    ↓
(NO FEEDBACK LOOP) — reports are written but never re-read by the system
```

**Critical gap**: Reports are generated but never consumed programmatically. No feedback loop closes: knowledge is produced but not reused.

---

## 5. Ownership Map

### 5.1 Capability → Owner (Canonical)

| Capability | Canonical Owner | Line Count | Duplicates |
|-----------|----------------|------------|------------|
| Ontology | `ontology.py` | 1,398 | metamodel/ (~800L) |
| Meta-Model | `meta_model.py` | 711 | None |
| Reasoning | `reasoning.py` | 364 | brain/cognition/reasoning.py |
| Persistence | `persistence/` | ~770 | None |
| Events | `events/bus.py` | 97 | fabric/bus.py (~185L) |
| Plugin | `plugin/registry.py` | 110 | plugin/manager.py (~236L, different role) |
| Graph Core | `graph_v2/` | ~800 | 5+ other graph implementations |
| Graph DB | `graphdb/` | 835 | None (unique value proposition) |
| UIR | `core/uir.py` | 398 | None |
| USIR | `usir/` | ~1,300 | None (multi-language parsing) |
| Execution OS | `os/runtime.py` | 499 | runtime/executor.py, execution/ |
| Scheduler | `os/scheduler.py` | 199 | kernel/task_scheduler.py (~155L) |
| Queue | `os/queue.py` | 154 | None |
| Task Graph | `os/task_graph.py` | 197 | execution_graph.py (420L) |
| Planner (OS) | `os/planner.py` | 198 | execution/tasks.py |
| Planner (Eng) | `planning/` | 621 | planner.py (315L) |
| Memory (OS) | `os/memory_manager.py` | 199 | None |
| Memory (Types) | `memory/` | ~600 | memory_system.py (413L) |
| Brain | `brain/` | ~2,800 | brain_v4.py (738L) |
| Civilization | `civilization/` | ~4,500 | digital_civilization.py (321L — different flavor) |
| Scientist | `repository_scientist.py` | 247 | discovery (407L), scientist (390L) |
| Engineer | `repository_engineer.py` | 221 | None |
| Economics | `repository_economics.py` | 160 | economics.py (243L) |
| Mathematics | `mathematics.py` | 796 | mathematics_v2.py (361L) |
| Simulation | `simulator_v2.py` | 289 | simulator.py (344L) |
| Evolution | `evolution_v4.py` | 352 | evolution.py (317L) |
| Compiler | `compiler/` | ~500 | usir/compiler.py (~142L — different role) |
| Capability System | `ucos/` | ~2,000 | capability/registry.py (269L) |
| Data Platform | `ued/` | ~2,200 | None (unique value) |
| Orchestrator | `omega_loop.py` | 6,575 | atlas.py (1,297L — different model) |
| Platform Boot | `platform.py` | 747 | platform_v2.py (512L), engineering_os.py (331L) |

### 5.2 Which Subsystems Should Disappear

| Subsystem | Lines | Reason | Migration Target |
|-----------|-------|--------|-----------------|
| `metamodel/` | ~800 | Duplicates ontology.py entity model | ontology.py |
| `hypergraph.py` | 648 | Duplicates graph_v2/ capabilities | graph_v2/ |
| `knowledge_graph.py` | 320 | Duplicates graph/engine.py | graph_v2/ |
| `execution_graph.py` | 420 | Duplicates graph_v2/ + execution/ | graph_v2/ + execution/ |
| `memory_system.py` | 413 | Duplicates memory/ types | memory/ |
| `planner.py` | 315 | Duplicates planning/ | planning/ |
| `economics.py` | 243 | Duplicates repository_economics | repository_economics |
| `engineering_os.py` | 331 | Duplicates platform.py boot logic | platform.py |
| `platform_v2.py` | 512 | Service registry — merge into platform | platform.py |
| `graph/engine.py` | 305 | Duplicates graph_v2/ | graph_v2/ |
| `autonomous/` | ~330 | Merge into OmegaLoop Books | omega_loop/ |
| `brain_v4.py` | 738 | Already deprecated | brain/ |
| `discovery.py` | 407 | Already deprecated | repository_scientist |
| `scientist.py` | 390 | Already deprecated | repository_scientist |
| `simulator.py` | 344 | Already deprecated | simulator_v2 |
| `evolution.py` | 317 | Already deprecated | evolution_v4 |
| `civilization_v2.py` | 280 | Already deprecated | digital_civilization |
| `civilization_v3.py` | 248 | Already deprecated | digital_civilization |
| `genesis_viii.py` | 24 | Empty shell | Delete |
| `fabric/` | ~1,500 | Independent subsystem — needs evaluation | Keep or deprecate |

**Total lines removable**: ~8,300 (8.8% of repository)
**Total lines that should eventually be removed** (including deprecated): ~11,000 (11.7%)

### 5.3 Which Subsystems Should Survive (Core Canonical)

| Subsystem | Lines | Role |
|-----------|-------|------|
| `ontology.py` | 1,398 | Entity model + relationships |
| `meta_model.py` | 711 | Meta-model engine |
| `reasoning.py` | 364 | Engineering reasoning |
| `persistence/` | ~770 | Storage layer |
| `events/bus.py` | 97 | Event system |
| `plugin/` | ~475 | Plugin system |
| `core/` | ~800 | UIR, BaseEntity, types, metadata |
| `utils/` | ~250 | Identity, graph algorithms, serialization |
| `os/` | ~2,500 | Runtime, scheduler, planner, queue, watchers |
| `brain/` | ~2,800 | Engineering brain |
| `civilization/` | ~4,500 | Agent civilization |
| `digital_civilization.py` | 321 | Institute/contract system |
| `repository_scientist.py` | 247 | Experiment management |
| `repository_engineer.py` | 221 | Improvement generation |
| `repository_economics.py` | 160 | Economic analysis |
| `planning/` | 621 | Multi-level planning |
| `memory/` | ~600 | Memory types + consolidation |
| `graph_v2/` | ~800 | Core graph (after merging others) |
| `graphdb/` | 835 | Graph database |
| `compiler/` | ~500 | USIR compiler pipeline |
| `usir/` | ~1,300 | Multi-language IR |
| `ucos/` | ~2,000 | Capability system |
| `ued/` | ~2,200 | Data platform |
| `omega_loop.py` | 6,575 | Master orchestrator (needs decomposition) |
| `atlas.py` | 1,297 | Repository analysis engine |
| `reverse_engineer.py` | 910 | Code scanner |
| `census.py` | 863 | Repository census |
| `platform.py` | 747 | Thin orchestrator (needs reconstruction) |
| `cli/` | 263 | CLI commands |
| `di/` | ~325 | Dependency injection |
| `validation/` | ~260 | Validation engine |
| `evalution_v4.py` | 352 | Self-evolution |
| `simulator_v2.py` | 289 | Multi-domain simulation |
| `mathematics.py` | 796 | Math library (needs unification with v2) |
| `mathematics_v2.py` | 361 | Math library v2 |

---

## 6. Overlap Heatmap

```
                    Has Subsystem
Needs Subsystem     ont meta reas pers even plug core util os  brain civ  sci  eng  econ plan memo gv2  gdb  comp usir ucos ued  omeg atla rev  cens plat
ontology            ─   C   C    C    .    .    C    C    .    .    .    .    .    .    .    .    .    .    .    .    .    .    C    C    C    .    C
meta_model          C   ─   .    .    .    .    .    .    .    .    .    .    .    .    .    .    .    .    .    .    .    .    C    C    .    .    C
reasoning           C   .   ─    .    .    .    .    .    .    .    .    .    .    .    .    .    .    .    .    .    .    .    C    .    .    .    C
persistence         C   .   .    ─    .    .    .    .    .    .    .    .    .    .    .    C    .    .    .    .    .    C    .    .    .    .    C
events              .   .   .    .    ─    .    .    .    C    .    .    .    .    .    .    .    .    .    .    .    .    .    .    .    .    .    C
plugin              .   .   .    .    C    ─    .    .    .    .    .    .    .    .    .    .    .    .    .    .    .    .    C    C    .    .    C
core                C   .   .    C    .    .    ─    C    .    .    .    .    .    .    .    .    .    .    .    .    .    .    .    .    .    .    C
utils               C   .   .    .    .    .    .    ─    .    .    .    .    .    .    .    .    .    .    .    .    .    .    .    .    .    .    .
os                  .   .   .    .    C    .    .    .    ─    .    .    .    .    .    C    .    .    .    .    .    .    .    .    .    .    .    C
brain               C   .   C    .    .    .    .    .    C    ─    C    .    .    .    .    .    .    C    .    .    .    .    .    .    .    .    C
civilization        .   .   .    .    .    .    .    .    .    C    ─    .    .    .    .    .    .    .    .    .    .    .    .    .    .    .    .
scientist           C   .   C    .    .    .    .    .    .    .    .    ─    C    C    .    .    .    .    .    .    .    .    C    .    .    .    C
engineer            C   .   C    .    .    .    .    .    .    .    .    C    ─    C    .    .    .    .    .    .    .    .    C    .    .    .    C
economics           C   .   .    .    .    .    .    .    .    .    .    C    C    ─    .    .    .    .    .    .    .    .    C    .    .    .    C
planning            .   .   .    .    .    .    .    .    .    C    .    .    .    .    ─    .    .    .    .    .    .    .    .    .    .    .    .
memory              .   .   .    C    .    .    .    .    .    .    .    .    .    .    .    ─    .    .    .    .    .    .    .    .    .    .    C
graph_v2            .   .   .    .    .    .    .    .    .    .    .    .    .    .    .    .    ─    .    .    .    .    .    .    .    .    .    C
graphdb             .   .   .    .    .    .    .    .    .    C    C    .    .    .    .    .    .    ─    .    .    .    .    .    .    .    .    .
compiler            C   .   .    .    .    .    C    .    .    .    .    .    .    .    .    .    .    .    ─    C    .    .    .    .    .    .    C
usir                .   .   .    .    .    .    .    .    .    .    C    .    .    .    .    .    .    .    C    ─    .    .    .    .    .    .    .
ucos                .   .   .    .    .    .    .    C    .    .    .    .    .    .    .    .    .    .    .    .    ─    .    .    .    .    .    C
ued                 .   .   .    .    .    .    .    .    .    .    .    .    .    .    .    .    .    .    .    .    .    ─    .    .    .    .    C
omega_loop          C   C   C    .    .    C    .    .    .    .    C    C    C    C    .    .    .    .    .    .    .    .    ─    .    C    .    .
atlas               C   C   .    .    .    C    .    .    .    .    .    .    .    .    .    .    .    .    .    .    .    .    .    ─    C    .    .
reverse_engineer    .   .   .    .    .    .    .    .    .    .    .    .    .    .    .    .    .    .    .    .    .    .    C    C    ─    .    .
census              .   .   .    .    .    .    .    .    .    .    .    .    .    .    .    .    .    .    .    .    .    .    .    .    .    ─    .
platform            C   C   C    C    C    C    C    .    C    C    C    C    C    C    C    C    C    .    C    .    C    C    C    .    C    .    ─

Legend: C = consumes, . = no dependency
```

---

## 7. Biological Architecture (Repository DNA)

| Biological System | Engineering Analog | Genesis Implementation |
|-------------------|-------------------|----------------------|
| **DNA** | Core abstractions | `utils/identity`, `utils/graph_algorithms`, `core/base.py`, `ontology.py` |
| **Cells** | Individual modules | Each .py file |
| **Organs** | Subsystems | `brain/`, `civilization/`, `os/`, `compiler/`, `ucos/` |
| **Nervous system** | Event bus | `events/bus.py` + `fabric/bus.py` |
| **Circulatory system** | Import graph | Module-level imports (no DI for source modules) |
| **Immune system** | Architecture tests | `tests/test_architecture.py` — layer compliance |
| **Brain** | Engineering brain | `brain/` (EngineeringBrain + cognition) |
| **Memory** | Memory systems | `memory/`, `os/memory_manager/`, `memory_system.py` |
| **Digestive system** | Compilation pipeline | `compiler/` + `usir/` — parse → analyze → generate |
| **Skeletal system** | Persistence layer | `persistence/` (SQLite stores) |
| **Muscular system** | Execution engines | `os/runtime.py`, `execution/`, `autonomous/` |
| **Endocrine system** | Signaling/events | EventBus |
| **Reproductive system** | Plugin system | `plugin/registry.py` — new capabilities via plugins |
| **Evolution** | Self-evolution | `evolution_v4.py`, OmegaLoop Book XII |
| **Mutation** | Deprecation/change | NEXUS Phase II deprecation warnings |
| **Natural selection** | Architecture governance | Not yet implemented (designed in NEXUS Phase II) |
| **Homeostasis** | Self-monitoring | Atlas (incomplete — Stage 10-11 unfilled) |
| **Symbiosis** | External integrations | `acquisition/`, `integration/project31a.py` |
| **Parasites** | Dead code | Deprecated modules still imported by platform.py |
| **Cancer** | Uncontrolled growth | platform.py god constructor, omega_loop.py 6,575L |

---

## 8. Critical Architecture Violations

1. **platform.py imports deprecated modules**: Lines 61-83 import discovery (deprecated), scientist (deprecated), simulator (deprecated), evolution (deprecated), civilization_v2/v3 (deprecated), brain_v4 (deprecated). These generate DeprecationWarnings on every boot.

2. **omega_loop.py imports module-level mathematics (OLD)**: Lines 57-62 import from the old mathematics.py. This is a hard coupling that prevents mathematics.py from being deprecated.

3. **Tests/programs/ test deprecated modules**: 16 test files under tests/programs/ test the deprecated modules. They still pass and contribute to the 2,763 count, but they prevent cleanup.

4. **metamodel/ duplicates ontology.py**: Different entity model, different graph model, different query API. ~800 lines of overlapping functionality.

5. **fabric/ is an independent OS**: The fabric subsystem (~1,500L) has its own kernel, bus, scheduler, session, policy, metrics, audit, discovery, contracts. It duplicates many OS capabilities.

6. **kernel/ is another independent OS**: The kernel subsystem (~1,800L) has its own execution manager, task scheduler, plugin loader, event router, memory manager, process manager, security manager. It duplicates os/ capabilities.

7. **graph_v2/ + graph/ + graphdb/ + hypergraph/ + knowledge_graph/ + execution_graph/ = 6 graph implementations**: No shared graph core. Each implements its own traversal, query, persistence.

---

## 9. Recommended Transformation

### Phase 1: Cleanup (3-5 days)
- Remove platform.py imports of deprecated modules (they only use type annotations, which with `from __future__ import annotations` are lazy strings)
- Move tests/programs/ to a `_legacy_tests/` directory (they test deprecated modules)
- Move mathematics.py classes used by omega_loop into mathematics_v2.py
- Remove unused instantiations from platform.py (5 already done, 10 more possible)

### Phase 2: Graph Unification (5-10 days)
- Design `GraphCore` in graph_v2/ — base node, edge, traversal, persistence
- Port graph/, hypergraph/, knowledge_graph/, execution_graph/ features to graph_v2/
- Add adapters for backward compatibility

### Phase 3: Runtime Unification (5-10 days)
- Implement UniversalExecutionPhase from NEXUS Phase II design
- Create adapters for OmegaLoop, Atlas, os/runtime, execution/, autonomous/
- One execution model for everything

### Phase 4: Platform Reconstruction (3-5 days)
- Implement LazyServiceRegistry
- Remove direct attribute access from platform.py
- Platform becomes thin orchestrator (discover → boot → observe → shutdown)

### Phase 5: Knowledge OS (3-5 days)
- Implement EngineeringKnowledgeStore
- All reports, metrics, decisions saved as KnowledgeArtifacts
- Queryable, linkable, versioned

### Phase 6: Governance (2-3 days)
- Implement CanonicalRegistry
- Pre-commit checks for duplication
- Deprecation lifecycle enforcement

---

## 10. Data Locality Analysis

| Data Type | Stored In | Accessed By | Persistence |
|-----------|-----------|------------|-------------|
| Entity metadata | MetadataStore | All services | SQLite |
| Knowledge graph | KnowledgeStore | Graph, brain, reasoning | SQLite |
| Event history | HistoryStore | Diagnostics, analytics | SQLite |
| Artifacts | ArtifactStore | Compiler, reports | SQLite |
| Checkpoints | CheckpointStore | Runtime, recovery | SQLite |
| Memory | MemoryStore | Brain, memory system | SQLite |
| Atlas outputs | _generated/atlas/*.json | OmegaLoop Book XII | Filesystem |
| Omega outputs | _generated/omega/*.json | Reports | Filesystem |
| Reports | _generated/reports/*.md | Humans | Filesystem |
| Decisions | genesis/decisions/*.md | Humans | Filesystem |
| Brain entities | brain_db (SQLite) | Brain | SQLite |

**Locality violation**: Engineering knowledge (reports, decisions, benchmarks) is stored in unstructured files that are never consumed programmatically. The ONLY feedback loop is Atlas→OmegaLoop via filesystem IPC (single JSON file).

---

*End of First Deliverable — Complete Repository Reconstruction*
