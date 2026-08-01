# PROJECT NEMESIS — Mission 2: Capability Reconstruction

**Date**: 2026-06-30
**Scope**: Ignore file boundaries. Identify every capability the system provides. Build capability graph. Quantify overlaps.

---

## 1. What Is a Capability?

A **capability** is a functional unit that the system can perform — independent of how it's implemented, which file it lives in, or which class provides it.

Each capability is defined by:
- **Name**: what it does
- **Slots**: interface points (inputs/outputs)
- **Implementations**: how many ways it's currently done
- **Canonical owner**: which module SHOULD own this
- **Consumers**: who depends on it

---

## 2. Complete Capability Inventory

### 2.1 Infrastructure Capabilities

| # | Capability | Slots | Impl Count | Canonical Owner | Consumers |
|---|---|---|---|---|---|
| C01 | **Identity Generation** | generate_id(prefix, length) → str | 1 | `utils.identity` | **114 files** |
| C02 | **Event Bus** | publish/subscribe, emit, listen | 1 | `events.bus` | 14+ services |
| C03 | **DI Container** | register, resolve, lifecycle | 1 | `di.container` | platform.py |
| C04 | **Serialization** | serialize/deserialize objects | 1 | `utils.serialization` | ? |
| C05 | **Configuration** | load, access settings | 2 | `config.settings` | platform + each module |
| C06 | **Logging/Diagnostics** | health check, diagnostics | 1 | `diagnostics` | boot |

### 2.2 Persistence Capabilities

| # | Capability | Slots | Impl Count | Canonical Owner | Consumers |
|---|---|---|---|---|---|
| C07 | **SQLite Storage** | CRUD, query, transaction | 1 (shared) | `persistence.sqlite_store` | 6 store types |
| C08 | **Entity Store** | store/retrieve entities | 6 | NONE — 6 stores | All boot services |
| C09 | **Checkpoint Store** | save/restore snapshots | 2 | `persistence` | `CheckpointStore` + `os.checkpoint.CheckpointManager` |
| C10 | **Metadata Store** | key-value metadata | 1 | `persistence.MetadataStore` | MetadataEngine |
| C11 | **Knowledge Store** | graph-backed knowledge | 1 | `persistence.KnowledgeStore` | KnowledgeGraphEngine |
| C12 | **History Store** | execution history | 1 | `persistence.HistoryStore` | ExecutionEngine |
| C13 | **Artifact Store** | binary/text artifacts | 1 | `persistence.ArtifactStore` | Compiler |
| C14 | **Memory Store** | memory persistence | 1 | `persistence.MemoryStore` | MemoryEngine + 4 services |
| C15 | **UED Database** | universal engineering DB with collections, indexes, vector, timeseries | 1 | `ued.database` | EngineeringOrchestrator |

### 2.3 Graph/Knowledge Capabilities

| # | Capability | Slots | Impl Count | Canonical Owner | Consumers |
|---|---|---|---|---|---|
| C16 | **Entity Model** | define entities, relationships, types | **3** | `ontology` | relationship_engine, metamodel, uir |
| C17 | **Graph Storage** | store nodes/edges, query | **6** | NONE — worst overlap | See below |
| C18 | **Graph Query** | traverse, pattern match | 6 | (per graph) | |
| C19 | **Graph Analytics** | centrality, clustering | 2 | `graph_v2.analytics` | |
| C20 | **Graph Versioning** | versioned graphs | 1 | `graph_v2.versioning` | |
| C21 | **Graph Federation** | multi-source graph | 1 | `graph_v2.federation` | |
| C22 | **Knowledge Reasoning** | infer new facts | 2 | `reasoning` | Ω³ stack |
| C23 | **Ontology Registry** | canonical entity types | 1 | `ontology.CanonicalRegistry` | Ω³ stack |
| C24 | **Meta Model** | type system for entities | 2 | `meta_model` | Ω³ stack, metamodel |

### 2.4 Execution Capabilities

| # | Capability | Slots | Impl Count | Canonical Owner | Consumers |
|---|---|---|---|---|---|
| C25 | **Task Execution** | run tasks, DAGs, workflows | **3** | NONE | runtime, execution, execution_graph |
| C26 | **Workflow Engine** | define, execute workflows | 2 | `execution.workflow` | |
| C27 | **Pipeline** | sequential processing steps | 2 | `execution.pipeline` | |
| C28 | **Actor Model** | actor-based execution | 1 | `execution.actors` | |
| C29 | **Retry/Compensation** | retry logic, compensation | 1 | `execution.retry` | |
| C30 | **Job Management** | queue, schedule jobs | 3 | NONE | os, kernel, execution |

### 2.5 Memory Capabilities

| # | Capability | Slots | Impl Count | Canonical Owner | Consumers |
|---|---|---|---|---|---|
| C31 | **Episodic Memory** | store/recall episodes | 2 | `memory.EpisodicMemory` | + memory_system |
| C32 | **Semantic Memory** | store/recall facts | 2 | `memory.SemanticMemory` | + memory_system |
| C33 | **Procedural Memory** | store/recall procedures | 2 | `memory.ProceduralMemory` | + memory_system |
| C34 | **Architectural Memory** | store/recall architecture | 2 | `memory.ArchitecturalMemory` | + memory_system |
| C35 | **Research Memory** | store/recall research | 2 | `memory.ResearchMemory` | + memory_system |
| C36 | **Organizational Memory** | store/recall org data | 2 | `memory.OrganizationalMemory` | + memory_system |
| C37 | **Temporal Memory** | time-based recall | 2 | `memory.TemporalMemory` | + memory_system |
| C38 | **Causal Memory** | cause-effect recall | 2 | `memory.CausalMemory` | + memory_system |
| C39 | **Execution Memory** | execution trace recall | 2 | `memory.ExecutionMemory` | + memory_system |
| C40 | **Agent Memory** | agent state storage | 2 | `memory.AgentMemory` | + memory_system |
| C41 | **World Memory** | world model storage | 2 | `memory.WorldMemory` | + memory_system |
| C42 | **Graph Memory** | graph data storage | 2 | `memory.GraphMemory` | + memory_system |
| C43 | **Specification Memory** | spec storage | 2 | `memory.SpecificationMemory` | + memory_system |
| C44 | **Conversation Memory** | conversation storage | 2 | `memory.ConversationMemory` | + memory_system |
| C45 | **Simulation Memory** | simulation results | 2 | `memory.SimulationMemory` | + memory_system |
| C46 | **Reflection Memory** | reflection data | 2 | `memory.ReflectionMemory` | + memory_system |
| C47 | **Memory Consolidation** | merge, forget, prioritize | 2 | `memory.consolidation` | + memory_system |
| C48 | **Memory Engine** | unified memory interface | 2 | `memory.engine` | + memory_system |

**16 memory types × 2 implementations each = 32 memory classes. Each pair is a duplicate.**

### 2.6 Platform/Boot Capabilities

| # | Capability | Slots | Impl Count | Canonical Owner | Consumers |
|---|---|---|---|---|---|
| C49 | **Platform Bootstrap** | create DI, wire services | **4** | NONE | platform, platform_v2, engineering_os, os |
| C50 | **Service Registry** | register, resolve services | **4** | NONE | DI, EngineeringOS, PlatformV2, kernel |
| C51 | **Service Lifecycle** | boot, health, shutdown | **4** | NONE | same as C50 |
| C52 | **Plugin System** | load, manage plugins | 2 | `plugin.manager` | + kernel |
| C53 | **Capability Registry** | discover capabilities | 3 | `capability.registry` | + ucos, kernel |
| C54 | **Configuration Manager** | manage settings | 2 | `config.settings` | + platform_v2 |

### 2.7 Cognitive/Brain Capabilities

| # | Capability | Slots | Impl Count | Canonical Owner | Consumers |
|---|---|---|---|---|---|
| C55 | **Entity Brain** | entity storage, graph, sync | 1 | `brain` | platform boot |
| C56 | **Belief System** | beliefs, evidence, revision | 2 | `brain.cognition.belief` | + brain_v4 |
| C57 | **Goal Management** | goals, subgoals, progress | 2 | `brain.cognition.goals` | + brain_v4 |
| C58 | **Attention Mechanism** | focus, salience | 2 | `brain.cognition.attention` | + brain_v4 |
| C59 | **Decision Making** | alternatives, criteria | 2 | `brain.cognition.decision` | + brain_v4 |
| C60 | **Strategy** | planning, execution | 1 | `brain.cognition.strategy` | |
| C61 | **Reflection** | self-analysis | 2 | `brain.cognition.reflection` | + brain_v4 |
| C62 | **Reasoning (Brain)** | logical inference, analogy | 3 | `brain.cognition.reasoning` | + brain_v4, reasoning |
| C63 | **Orchestration** | agent coordination | 1 | `brain.cognition.orchestration` | |
| C64 | **Integration** | event-driven sync | 1 | `brain.integration` | |

### 2.8 Autonomous/Evolution Capabilities

| # | Capability | Slots | Impl Count | Canonical Owner | Consumers |
|---|---|---|---|---|---|
| C65 | **Evolution Engine** | observe, mutate, select | 2 | `evolution`? | + evolution_v4 |
| C66 | **Autonomous Cycle** | observe → decide → act | 1 | `autonomous.cycle` | |
| C67 | **Orchestrator** | coordinate subsystems | 1 | `autonomous.orchestrator` | |
| C68 | **Engineering Physics** | complexity, momentum, entropy | 2 | `physics`? | + mathematics |
| C69 | **Architecture Algebra** | algebraic architecture | 2 | `mathematics` | + mathematics_v2 |

### 2.9 Civilization/Governance Capabilities

| # | Capability | Slots | Impl Count | Canonical Owner | Consumers |
|---|---|---|---|---|---|
| C70 | **Civilization (Institutes)** | governance bodies | **4** | NONE | v2, v3, civilization/, digital_civilization |
| C71 | **Institute Management** | create, manage institutes | 3 | civilization.institute | |
| C72 | **Agent Framework** | research agents | 2 | civilization.agents | |
| C73 | **Overseer** | system oversight | 1 | civilization.overseer | |
| C74 | **Research** | conduct research | 1 | civilization.research | |
| C75 | **Review** | peer review | 1 | civilization.review | |
| C76 | **Publications** | publish results | 1 | civilization.publications | |
| C77 | **Formal Methods** | model checking | 1 | civilization.formal | |
| C78 | **World Model** | ecosystem modeling | 1 | civilization.world_model | |

### 2.10 Compilation/Analysis Capabilities

| # | Capability | Slots | Impl Count | Canonical Owner | Consumers |
|---|---|---|---|---|---|
| C79 | **AST Construction** | parse → AST | 1 | `compiler.ast` | |
| C80 | **IR Building** | AST → UIR | 1 | `compiler.uir_builder` | |
| C81 | **Compiler Passes** | transform IR | 1 | `compiler.passes` | |
| C82 | **Code Generation** | IR → output | 3 | `compiler.codegen` | graph, markdown, schema |
| C83 | **USIR Compilation** | multi-language USIR | 1 | `usir` | |
| C84 | **Repository Indexing** | scan, index codebase | 1 | `indexer` | |
| C85 | **Reverse Engineering** | extract architecture | 1 | `reverse_engineer` | |
| C86 | **Meta Compilation** | meta-level transforms | 1 | `meta.meta_compiler` | |

### 2.11 Intelligence/Observation Capabilities

| # | Capability | Slots | Impl Count | Canonical Owner | Consumers |
|---|---|---|---|---|---|
| C87 | **VRIP Intelligence** | multi-phase intelligence | 1 | `intelligence.engine` | |
| C88 | **Repository Analysis** | analyze repo structure | 1 | `intelligence.analysis` | |
| C89 | **Capability Intelligence** | discover capabilities | 1 | `intelligence.capability` | |
| C90 | **Gap Analysis** | find gaps | 1 | `intelligence.gaps` | |
| C91 | **Traceability** | trace requirements | 1 | `intelligence.traceability` | |
| C92 | **Atlas Engine** | 15-stage repository analysis | 1 | `atlas` | |
| C93 | **OmegaLoop** | 18-book engineering intelligence | 1 | `omega_loop` | platform |
| C94 | **Observatory** | observe external repos | 1 | `observatory` | |
| C95 | **Digital Twin** | model, simulate, predict | 1 | `digital_twin` | platform |

### 2.12 Economics/Marketplace Capabilities

| # | Capability | Slots | Impl Count | Canonical Owner | Consumers |
|---|---|---|---|---|---|
| C96 | **Engineering Economics** | cost, debt, ROI | 2 | `economics`? | + repository_economics |
| C97 | **Repository Economics** | repo-level economics | 1 | `repository_economics` | Ω³ |
| C98 | **Marketplace** | capability trading | 1 | `marketplace` | |
| C99 | **Budget** | resource budgeting | 1 | `marketplace` | |
| C100 | **Cost Simulation** | predict costs | 2 | `simulator`? | + simulator_v2 |

### 2.13 OS/Kernel Capabilities

| # | Capability | Slots | Impl Count | Canonical Owner | Consumers |
|---|---|---|---|---|---|
| C101 | **Process Management** | run processes | 2 | `os`? | + kernel |
| C102 | **Task Scheduling** | schedule tasks | **3** | NONE | os, kernel, execution |
| C103 | **Memory Management** | manage memory | 2 | `os` | + kernel |
| C104 | **Resource Allocation** | allocate resources | 2 | `os` | + kernel |
| C105 | **Recovery** | fault recovery | **3** | NONE | os, kernel, fabric |
| C106 | **IPC** | inter-process communication | 1 | `kernel.ipc` | |
| C107 | **Event Router** | route events | 2 | `events.bus` | + kernel |
| C108 | **Security** | validate, authorize | 1 | `security` | |
| C109 | **Watchers** | file system watches | 1 | `os.watchers` | |
| C110 | **Distributed Cluster** | cluster management | 1 | `os.distributed` | |

### 2.14 UCOS/Engineering Database Capabilities

| # | Capability | Slots | Impl Count | Canonical Owner | Consumers |
|---|---|---|---|---|---|
| C111 | **UCOS Runtime** | capability execution | 1 | `ucos.runtime` | |
| C112 | **Capability Lifecycle** | register → deploy → retire | 1 | `ucos.lifecycle` | |
| C113 | **Capability Negotiation** | SLA negotiation | 1 | `ucos.negotiator` | |
| C114 | **Capability Planning** | dependency planning | 1 | `ucos.planner` | |
| C115 | **Capability Validation** | validate capabilities | 1 | `ucos.validator` | |
| C116 | **Collection Store** | typed collections | 1 | `ued.database` | |
| C117 | **Vector Index** | vector search | 1 | `ued.vector` | |
| C118 | **Time Series** | time series storage | 1 | `ued.timeseries` | |
| C119 | **Graph Store** | graph storage | 1 | `ued.graph` | |
| C120 | **Object Store** | object storage | 1 | `ued.object` | |
| C121 | **B-Tree Index** | indexed lookup | 1 | `ued.index` | |
| C122 | **Cache** | caching layer | 1 | `ued.cache` | |

### 2.15 Laboratory/Acquisition Capabilities

| # | Capability | Slots | Impl Count | Canonical Owner | Consumers |
|---|---|---|---|---|---|
| C123 | **Acquisition Pipeline** | fetch external data | 1 | `acquisition` | |
| C124 | **Source Adapters** | github, pypi, npm, etc. | 16 | `acquisition.sources` | |
| C125 | **Laboratory** | experiments, genome | 1 | `laboratory` | |
| C126 | **Genome** | repo genome model | 1 | `laboratory.genome` | |
| C127 | **Subgraph Mining** | mine subgraphs | 1 | `laboratory.mining` | |
| C128 | **Census** | count, classify repos | 1 | `census` | |

### 2.16 Cross-Cutting Capabilities

| # | Capability | Slots | Impl Count | Canonical Owner | Consumers |
|---|---|---|---|---|---|
| C129 | **API Server** | REST/GraphQL API | 1 | `api.router` | |
| C130 | **CLI** | command line interface | 1 | `cli.commands` | |
| C131 | **Studio Backend** | studio APIs | 1 | `studio.backend` | |
| C132 | **Project Management** | manage projects | 1 | `project.manager` | |
| C133 | **Package Management** | manage packages | 1 | `package.manager` | |
| C134 | **Validation** | validate structure/names/schema | 1 | `validation` | |
| C135 | **Certification** | certify compliance | 1 | `certification` | |
| C136 | **Planning** | architecture planning | 2 | `planner` | + planning/ |

---

## 3. Duplication Analysis

### 3.1 Capabilities With Multiple Implementations

| Capability | Implementations | Duplication Factor |
|---|---|---|
| **Graph Storage** | graph/engine, graph_v2, hypergraph, knowledge_graph, brain/graph, graphdb | **6×** |
| **Civilization/Governance** | civilization_v2, civilization_v3, civilization/, digital_civilization | **4×** |
| **Platform Boot** | platform, platform_v2, engineering_os, kernel, fabric, os/ | **6×** |
| **Task Scheduling** | os/scheduler, kernel/task_scheduler, execution/tasks | **3×** |
| **Service Registry** | di/container, engineering_os, platform_v2, kernel | **4×** |
| **Memory Types (16×)** | memory/types, memory_system | **2× each** |
| **Belief System** | brain/cognition/belief, brain_v4 | **2×** |
| **Attention** | brain/cognition/attention, brain_v4 | **2×** |
| **Decision Making** | brain/cognition/decision, brain_v4 | **2×** |
| **Reasoning** | brain/cognition/reasoning, brain_v4 (AnalogicalReasoning), reasoning | **3×** |
| **Reflection** | brain/cognition/reflection, brain_v4 | **2×** |
| **Entity Model** | ontology, metamodel/entity, core/uir | **3×** |
| **Execution** | runtime/executor, execution/engine, execution_graph | **3×** |
| **Mathematics** | mathematics, mathematics_v2 | **2×** |
| **Economics** | economics, repository_economics | **2×** |
| **Recovery** | os/recovery, kernel/recovery_manager, fabric/policy | **3×** |
| **Memory Management** | os/memory_manager, kernel/memory_manager | **2×** |
| **Checkpoint** | persistence/CheckpointStore, os/checkpoint | **2×** |
| **Engine Simulator** | simulator, simulator_v2 | **2×** |
| **Evolution** | evolution, evolution_v4 | **2×** |
| **Planning** | planner, planning/ | **2×** |
| **Code Generation** | codegen/graph_gen, codegen/markdown_gen, codegen/schema_gen | **3×** |
| **Meta Model** | meta_model.py, metamodel/ | **2×** |
| **Plugin System** | plugin/manager, kernel/plugin_loader | **2×** |
| **Cost Simulation** | simulator/CostSimulator, simulator_v2/CostSimulator | **2×** |

**Total: 26 capability groups with 2+ implementations.**

### 3.2 Duplication Count Calculation

| Metric | Value |
|---|---|
| Total unique capabilities | **136** |
| Capabilities with 1 implementation | 110 |
| Capabilities with 2 implementations | 19 |
| Capabilities with 3 implementations | 4 |
| Capabilities with 4+ implementations | 3 |
| **Implementation ratio** | **136 caps / ~??? total impls** |
| **Overlap count** | **26 overlapping capability groups** |
| **Effective duplication rate** | **26/136 = 19.1%** of capability groups have duplication |

### 3.3 Worst Offenders (Ranked by Impact)

| Rank | Capability | Impact | Reason |
|---|---|---|---|
| 1 | **Graph Storage** (6×) | Critical | Every subsystem builds its own graph. No shared core. Data fragmentation. |
| 2 | **Platform Boot** (6×) | Critical | 6 competing frameworks for the same job: wire services, manage lifecycle. |
| 3 | **Civilization** (4×) | High | 4 competing governance models. Which is canonical? |
| 4 | **Service Registry** (4×) | High | 4 service registration systems. No single source of truth. |
| 5 | **Memory Types** (2× ×16) | High | 32 memory classes doing the same 16 things. |
| 6 | **Reasoning** (3×) | Medium | 3 reasoning engines with different APIs. |
| 7 | **Execution** (3×) | Medium | 3 execution engines, same role. |
| 8 | **Task Scheduling** (3×) | Medium | 3 schedulers. |
| 9 | **Entity Model** (3×) | Medium | 3 entity models with different APIs. |
| 10 | **Recovery** (3×) | Medium | 3 recovery systems. |

---

## 4. Capability Dependency Graph

### 4.1 Root Capabilities (No Dependencies)

```
Identity Generation (C01)        — used by 114 files
Event Bus (C02)                 — used by 14+ services
Serialization (C04)             — utility
Configuration (C05)             — platform config
SQLite Storage (C07)            — base persistence
```

### 4.2 Tier 1 Capabilities (Depend Only on Roots)

```
DI Container (C03)              ← Configuration
Entity Store (C08)              ← SQLite Storage
Metadata Store (C10)            ← SQLite Storage
Knowledge Store (C11)           ← SQLite Storage
Historical Store (C12)          ← SQLite Storage
Artifact Store (C13)            ← SQLite Storage
Memory Store (C14)              ← SQLite Storage
AST Construction (C79)          ← Identity
```

### 4.3 Tier 2 Capabilities (Depend on Tier 1)

```
Entity Model (C16)              ← Identity, Entity Store
Graph Storage (C17)             ← Entity Model, Knowledge Store
Memory Types (C31-C46)          ← Identity, Memory Store
Task Execution (C25)            ← History Store, Event Bus
Platform Bootstrap (C49)        ← DI Container, Event Bus, all Stores
```

### 4.4 Tier 3 Capabilities (Orchestration Layer)

```
Engineering Brain (C55)         ← Entity Model, Graph Storage, Event Bus
VRIP Intelligence (C87)         ← Engineering Brain, Checkpoint
Atlas Engine (C92)              ← Repository Indexing, Graph Storage
OmegaLoop (C93)                 ← Mathematics, Graph, Reasoning, everything
Digital Twin (C95)              ← Engineering Brain, Graph
Engineering Physics (C68)       ← Mathematics
```

### 4.5 Tier 4 Capabilities (Meta Layer)

```
Reasoning Engine (C62)          ← Ontology, Meta Model, Canonical Registry
Repository Scientist (C88 alt)  ← Reasoning
Repository Engineer (C84 alt)   ← Reasoning, Repository Scientist
Repository Economics (C97)      ← Reasoning
Digital Civilization (C70)      ← Relationship Engine
Autonomous Cycle (C66)          ← Everything
```

### 4.6 Tier 5 Capabilities (External Interfaces)

```
API Server (C129)               ← Most internal caps
CLI (C130)                      ← Most internal caps
Studio Backend (C131)           ← Most internal caps
Acquisition Pipeline (C123)     ← External sources, Entity Model
```

---

## 5. Canonical Ownership Gaps

### 5.1 Capabilities With NO Clear Canonical Owner

| Capability | Competing Owners | What Should Own It |
|---|---|---|
| Graph Storage | graph/, graph_v2/, hypergraph, knowledge_graph, brain/graph, graphdb | **NEW: graph/core** |
| Execution | runtime/, execution/, execution_graph | **NEW: execution/core** |
| Platform Boot | platform, platform_v2, engineering_os, kernel, fabric, os | **platform** (thin) |
| Civilization | civilization_v2, civilization_v3, civilization/, digital_civilization | **civilization/core** |
| Memory | memory/types, memory_system | **memory/core** |
| Mathematics | mathematics, mathematics_v2 | **mathematics** (merge) |
| Economics | economics, repository_economics | **economics** (merge) |
| Planning | planner, planning/ | **planning** (merge) |
| Entity Model | ontology, metamodel, core/uir | **ontology** |
| Meta Model | meta_model.py, metamodel/ | **meta_model.py** |
| Recovery | os/recovery, kernel/recovery_manager, fabric/policy | **os/recovery** |
| Belief System | brain/cognition/belief, brain_v4 | **brain/cognition/belief** |
| Attention | brain/cognition/attention, brain_v4 | **brain/cognition/attention** |
| Decision | brain/cognition/decision, brain_v4 | **brain/cognition/decision** |

### 5.2 Capabilities With Clear Canonical Owners

| Capability | Canonical Owner | Status |
|---|---|---|
| Identity Generation | `utils.identity` | ✅ SINGLE |
| Event Bus | `events.bus` | ✅ SINGLE |
| DI Container | `di.container` | ✅ SINGLE |
| VRIP Intelligence | `intelligence.engine` | ✅ SINGLE |
| Atlas | `atlas` | ✅ SINGLE |
| OmegaLoop | `omega_loop` | ✅ SINGLE |
| Observatory | `observatory` | ✅ SINGLE |
| Reverse Engineering | `reverse_engineer` | ✅ SINGLE |
| Digital Twin | `digital_twin` | ✅ SINGLE |
| USIR | `usir` | ✅ SINGLE |
| UED | `ued` | ✅ SINGLE |
| UCOS | `ucos` | ✅ SINGLE |
| Laboratory | `laboratory` | ✅ SINGLE |
| Acquisition | `acquisition` | ✅ SINGLE |
| Census | `census` | ✅ SINGLE |
| CLI | `cli` | ✅ SINGLE |
| API | `api` | ✅ SINGLE |
| Studio | `studio` | ✅ SINGLE |
| Project | `project` | ✅ SINGLE |
| Package | `package` | ✅ SINGLE |
| Security | `security` | ✅ SINGLE |
| Certification | `certification` | ✅ SINGLE |
| Validation | `validation` | ✅ SINGLE |
| Diagnostics | `diagnostics` | ✅ SINGLE |
| Plugin | `plugin` | ✅ SINGLE (though kernel duplicates) |
| Compilation | `compiler` | ✅ SINGLE |
| Indexing | `indexer` | ✅ SINGLE |
| Engineering Brain | `brain` | ✅ SINGLE |

---

## 6. Consumer Heatmap (Top Consumers)

| Component | Consumes | Consumed By |
|---|---|---|
| **`utils.identity`** | — | **114 files** |
| **`ontology`** | identity | **22 files** |
| **`core/uir`** | identity | ~15 files |
| **`events.bus`** | — | 14+ services |
| **`di.container`** | — | platform.py |
| **`brain`** | identity, ontology, events | platform boot, VRIP, DigitalTwin |
| **`graph/engine`** | identity, ontology, events | Compiler, VRIP |
| **`graph_v2`** | identity | EngineeringOrchestrator |
| **`hypergraph`** | identity | platform (self.hypergraph_core) |
| **`knowledge_graph`** | identity | platform (self.knowledge_graph) |
| **`graphdb`** | identity | self-contained |
| **`execution`** | identity | stand alone |
| **`execution_graph`** | identity | MetaModel |
| **`runtime.executor`** | identity | platform core |
| **`omega_loop`** | ontology, mathematics, meta_model, plugin | platform boot |

---

## 7. Critical Findings

### F1: The 6-Graph Problem
Six graph implementations mean:
- Data in `graph/engine` is not visible to `graph_v2`
- Data in `hypergraph` is not visible to `knowledge_graph`
- Data in `brain/graph` is not visible to `graphdb`
- No cross-graph queries possible
- Each has its own entity model, query API, and persistence strategy

**Impact**: Fragmented knowledge. No unified view of the repository.

### F2: The 6-Platform Problem
Six platform/boot frameworks mean:
- `VenusPlatform` at `platform.py` is the god constructor (creates everything)
- `PlatformV2` at `platform_v2.py` is a competing service registry
- `EngineeringOS` at `engineering_os.py` is a competing OS abstraction
- `UniversalKernel` at `kernel/` is a competing kernel
- `FabricKernel` at `fabric/` is a competing fabric
- `os/` is a competing OS layer

**Impact**: 5 of these 6 are unused vestiges — only `platform.py` actually boots. The others are created but never drive any real behavior.

### F3: brain_v4 — The Parallel Brain
`brain_v4.py` (738 lines) reimplements:
- Belief system (Belief, BeliefRevision) — duplicates `brain/cognition/belief`
- Goals — duplicates `brain/cognition/goals`
- Attention system — duplicates `brain/cognition/attention`
- Causal inference — partially duplicates `brain/cognition/reasoning`
- Analogical reasoning — unique to brain_v4
- Reflection — duplicates `brain/cognition/reflection`

**Impact**: 6 cognitive capabilities duplicated. brain_v4 is a parallel universe brain.

### F4: The Ω³ Stack — Why It's Different
The Ω³ stack (ReasoningEngine → RepositoryScientist → RepositoryEngineer → RepositoryEconomics → DigitalCivilization → ReverseEngineeringEngine → OmegaLoop) is the ONLY chain that passes dependencies through constructors. Everything else uses no-arg constructors. This suggests the Ω³ stack was built with a different architectural philosophy — proper dependency injection vs. god constructor.

### F5: Memory Proliferation
- 16 memory types × 2 implementations = 32 classes
- Plus MemoryConsolidator + ForgettingMechanism (×2)
- Plus MemoryEngine (×2)
- Plus UniversalMemorySystem
- **Total: ~37 memory-related classes**
- Only `memory/types` and `memory/engine` have consumers

---

## 8. Capability Count Summary

| Area | Capabilities | With Duplicates | Duplicate Rate |
|---|---|---|---|
| Infrastructure | 6 | 1 | 16.7% |
| Persistence | 9 | 2 | 22.2% |
| Graph/Knowledge | 9 | 4 | 44.4% |
| Execution | 6 | 3 | 50.0% |
| Memory | 18 | 16 | 88.9% |
| Platform/Boot | 6 | 4 | 66.7% |
| Cognitive/Brain | 10 | 5 | 50.0% |
| Autonomous/Evolution | 5 | 2 | 40.0% |
| Civilization | 9 | 4 | 44.4% |
| Compilation/Analysis | 8 | 1 | 12.5% |
| Intelligence/Observation | 9 | 0 | 0.0% |
| Economics/Marketplace | 5 | 2 | 40.0% |
| OS/Kernel | 10 | 5 | 50.0% |
| UCOS/UED | 12 | 0 | 0.0% |
| Laboratory/Acquisition | 6 | 0 | 0.0% |
| Cross-Cutting | 8 | 1 | 12.5% |
| **TOTAL** | **136** | **50 (in 26 groups)** | **19.1%** |

---

**End of Mission 2: Capability Reconstruction.**
