# PROJECT NEMESIS — Mission 3: Repository DNA

**Date**: 2026-06-30
**Scope**: Biological reasoning about the repository architecture. Model the codebase as a living organism.

---

## 1. The Genome

Every biological organism has DNA — the core genetic code that defines its structure, behavior, and identity. A software repository's DNA is its fundamental abstractions that everything else builds upon.

### 1.1 Core Genes (Essential — Deletion Would Kill the Organism)

| Gene | File | Expression | Function |
|---|---|---|---|
| `generate_id` | `utils/identity.py` | **114 files** | Identity — every entity needs a unique ID |
| `BaseEntity` | `core/base.py` | ~30 subclasses | Foundation type — everything is an entity |
| `EventBus` | `events/bus.py` | 14+ consumers | Nervous system — inter-component communication |
| `ServiceProvider` | `di/container.py` | platform.py | Circulatory system — distributes dependencies |
| `SQLiteStore` | `persistence/sqlite_store.py` | 6 stores | Metabolism — persistent storage |
| `MemoryEntry` | `memory/types.py` | 16 types | Memory — stores experiences |
| `UniversalEntity` | `ontology.py` | 22 files | Classification — type system |
| `UIRGraph` | `core/uir.py` | ~15 files | Knowledge representation — graph structure |

### 1.2 Regulatory Genes (Control Development)

| Gene | Expression | Function |
|---|---|---|
| `CONSTITUTION.md` | Design-time | Governs development rules |
| `VENUS_PLATFORM_SPECIFICATION.md` | Design-time | Platform specification |
| `GENESIS_II_ARCHITECTURE.md` | Design-time | Reference architecture |
| `ADR-*` (decisions/) | Design-time | Architecture decisions |
| `test_architecture.py` | CI | Architecture compliance |
| `test_compliance.py` | CI | Specification compliance |

### 1.3 Junk DNA (Expressed but Non-Functional)

| Gene | Expression | Notes |
|---|---|---|
| `MemoryConsolidator` | boot() | Created, never used |
| `ForgettingMechanism` | boot() | Created, never used |
| 6 `None` attributes | boot() | Declared, never instantiated |

---

## 2. Organ Systems

### 2.1 Nervous System — EventBus
```
EventBus (events/bus.py) — 97 lines
  ├── subscribe(type, handler) — 14+ subscribers
  ├── emit(type, data) — called in boot, brain, shutdown
  └── Synchronous in-memory pub/sub
```
**Health**: ⚕️ Functional but minimal. No async, no persistence, no replay, no dead-letter queue.

### 2.2 Circulatory System — ServiceProvider DI Container
```
ServiceProvider (di/container.py) — 207 lines
  ├── register(interface, implementation) — declared but never used
  ├── register_instance(interface, instance) — THE primary API (54 calls in boot)
  ├── get(interface) — used to resolve EventBus + 5 stores in bootstrap
  └── shutdown() — 17 shutdown hooks
```
**Health**: ⚕️ Functional but underutilized. No factory functions, no scoped lifetimes, no decorators.

### 2.3 Immune System — Architecture Tests
```
test_architecture.py — Architecture compliance tests
test_compliance.py   — Specification compliance tests
test_canonical.py    — Canonical registry tests
```
**Health**: 🟢 58 tests pass. Architecture tests exist and work.

### 2.4 Memory System (3 Overlapping Systems)
```
1. memory/types (16 types) + memory/engine + memory/consolidation
2. memory_system.py (UniversalMemorySystem — 18 typed stores)
3. brain/entity.py (BrainEntity — entity-level memory)
```
**Health**: 🔴 Three competing memory systems. No single source of truth.

### 2.5 Skeletal System — Platform Boot
```
VenusPlatform (platform.py) — 747 lines
  ├── __init__: 50 attribute declarations
  ├── bootstrap(): DI + 6 stores
  ├── boot(): 54 register_instance calls, ~71 objects
  └── shutdown(): brain.stop + vrip.checkpoint + stores.close
```
**Health**: 🔴 God constructor. Does everything. No decomposition.

### 2.6 Muscular System — Execution Engines
```
1. runtime/executor.py — ExecutionEngine (Phase 2)
2. execution/engine.py — ExecutionEngineV2 (Phase 7)
3. execution_graph.py — ExecGraphEngine (Phase 8)
```
**Health**: 🔴 Three sets of muscles. Conflicting movement.

### 2.7 Cardiovascular System — Import Graph
```
platform.py imports 50+ modules at module level
omega_loop.py imports mathematics at module level (blocking deprecation)
Every import triggers side effects (DeprecationWarnings)
```
**Health**: 🔴 Import-time side effects. Fragile initialization.

---

## 3. Cellular Structure (Module Anatomy)

### 3.1 Cell Types

| Cell Type | Examples | Characteristics |
|---|---|---|
| **Stem Cells** | `utils/identity.py` | Undifferentiated, used everywhere |
| **Muscle Cells** | `runtime/executor.py` | Do work, consume energy |
| **Neural Cells** | `events/bus.py`, `brain/` | Transmit signals |
| **Epithelial Cells** | `persistence/sqlite_store.py` | Line boundaries, protect internals |
| **Fat Cells** | `brain_v4.py` (duplicate), `civilization_v3.py` | Store unused potential |
| **Cancer Cells** | `kernel/`, `fabric/`, `os/` (unused) | Grow without regulation |

### 3.2 Cell Specialization Score

| Module | Specialization | Purpose Clarity |
|---|---|---|
| `events/bus.py` | 1.0 — Pure event bus | Crystal clear |
| `di/container.py` | 1.0 — Pure DI | Crystal clear |
| `memory/types.py` | 1.0 — Pure memory types | Crystal clear |
| `atlas.py` | 0.9 — Analysis engine | Clear |
| `omega_loop.py` | 0.3 — Everything engine | Unclear (6575 lines, 18 books) |
| `platform.py` | 0.4 — God constructor | Unclear (wires everything) |
| `kernel/` | 0.2 — Competing OS | Shouldn't exist |
| `fabric/` | 0.2 — Competing OS | Shouldn't exist |

---

## 4. Diseases

### 4.1 Cancer — Uncontrolled Growth
**Affected organs**: `kernel/` (18 files), `fabric/` (11 files), `os/` (14 files)
**Symptoms**: 
- Three directories implementing complete operating systems
- Each duplicates capabilities that already exist elsewhere
- None are actively consumed by the running system
- They grow independently, adding more features without integration

**Stage**: Stage II — localized but spreading. No metastasis yet.

### 4.2 Parasites — Resource-Consuming Dead Code
**Affected organs**: `memory/consolidation.py`, boot() abandoned instances
**Symptoms**:
- `MemoryConsolidator` and `ForgettingMechanism` consume memory at boot
- 6 declared attributes never instantiated
- `SimulatorEngine`, `DiscoveryEngine`, etc. imported but never created

**Treatment**: Surgical removal.

### 4.3 Atrophy — Disused Organs
**Affected organs**: `brain_v4.py` (14KB), `civilization_v3.py` (10KB)
**Symptoms**:
- brain_v4 duplicates brain/cognition but is NOT referenced by any consumer
- civilization_v3 duplicates civilization_v2 but is NOT referenced by any consumer
- These are large files that consume maintenance effort but provide no runtime value

**Treatment**: Deprecation.

### 4.4 Fibrosis — Scar Tissue Buildup
**Affected areas**: Import chains, shutdown complexity
**Symptoms**:
- `platform.py` import chain: import platform.py → triggers 50+ imports → 7 DeprecationWarnings
- Shutdown touches only 4 of ~50 services

### 4.5 Auto-Immune — Tests Attacking Healthy Code
**Symptoms**:
- `test_architecture.py` passes (immune system works)
- But architecture violations persist in production code

---

## 5. Vital Signs

| Vital | Value | Health |
|---|---|---|
| **Body Mass** | 71,916 lines (excl tests) | 🟢 Manageable |
| **Cell Count** | 335 files | 🟢 Reasonable |
| **Organ Count** | 102 top-level dirs/files | 🟡 High (42 sub-packages) |
| **Duplicate Organs** | 6 graph, 4 civ, 3 exec, 3 platform | 🔴 26 groups |
| **Cancer Mass** | ~5,300 lines (kernel + fabric + os) | 🔴 7.4% of body |
| **Junk DNA** | ~200 lines abandoned instances | 🟡 Low |
| **Immune Health** | 2,763 tests | 🟢 Strong |
| **Heart Rate** | Single-threaded sync boot | 🟡 Adequate |
| **Nerve Conduction** | EventBus, synchronous | 🟡 Adequate |
| **Metabolic Rate** | All services eager-initialized | 🔴 Wastes energy |
| **Lifespan** | Process-scoped (no daemon mode) | 🟡 Limited |

---

## 6. Ecological Niche

### 6.1 What This Organism Does
```
Input:  Python repository (self)
Process: Analyze → Model → Reason → Evolve
Output: Architecture reports, knowledge graphs, improved codebase
```

### 6.2 Trophic Level
```
Primary Consumer:
  Consumes: repository source code, file structure, git history
  Produces: knowledge graphs, architecture analysis, intelligence reports

Secondary Consumer:
  Consumes: primary consumer outputs
  Produces: evolution plans, engineering decisions, civilization governance

Tertiary Consumer (OmegaLoop):
  Consumes: everything
  Produces: unified engineering intelligence
```

### 6.3 Evolutionary Adaptations
- **Metamorphosis**: NEXUS Phase II added deprecation warnings (evolutionary pressure)
- **Redundancy**: 6 graph systems = evolutionary insurance (but costly)
- **Specialization**: Memory types = niche adaptation to different data forms
- **Social behavior**: Civilization module = multi-agent cooperation

---

## 7. Evolutionary History (Inferred from Structure)

```
Generation 1 — Genesis Core
  └── utils, core, events, di, persistence

Generation 2 — Platform
  └── platform.py (god constructor), cli, api, plugin

Generation 3 — Intelligence
  └── brain, intelligence (VRIP), graph, runtime

Generation 4 — VIII Programs
  └── simulator, physics, discovery, knowledge_graph, engineering_os
  └── civilization_v2, evolution, mathematics

Generation 5 — IX Phases
  └── platform_v2, brain_v4, memory_system, hypergraph
  └── simulator_v2, scientist, planetary_knowledge, mathematics_v2
  └── civilization_v3, evolution_v4

Generation 6 — X Programs
  └── ucos, kernel

Generation 7 — XI Programs
  └── meta, ued

Generation 8 — XII Programs
  └── fabric, graph_v2, execution_v2, autonomous

Generation 9 — XIII/Ω³ Phases
  └── meta_model, execution_graph, ontology, reasoning
  └── repository_scientist, repository_engineer, repository_economics
  └── digital_civilization, reverse_engineer, omega_loop
```

**Evolutionary Pattern**: Each generation adds MORE of everything — more graphs, more platforms, more memories, more brains. No generation removes anything. This is **evolution by accretion**.

---

## 8. Health Assessment

### 8.1 What's Healthy
- **Identity generation**: Single source of truth, 114 consumers — the most successful gene
- **Event bus**: Single implementation, clear interface
- **DI container**: Clean protocol-based design, thread-safe
- **Test suite**: 2,763 tests, strong coverage
- **Ω³ stack**: Proper dependency injection pattern
- **Persistence stores**: Clean SQLite abstraction

### 8.2 What's Sick
- **Cancer (kernel, fabric, os)**: Uncontrolled growth, no regulation
- **Fibrosis (platform.py)**: Cannot refactor without touching everything
- **Atrophy (brain_v4, civ_v3)**: Large disused organs
- **Parasites (abandoned objects)**: Created but never used

### 8.3 What's Dying
- `discovery.py`, `scientist.py`, `simulator.py`, `evolution.py` — deprecated
- `mathematics.py` — can't be deprecated because omega_loop depends on it

---

## 9. Prescription

### Phase 1 — Surgery
- Remove cancer: `kernel/`, `fabric/`, `os/` (or merge into one canonical OS)
- Remove parasites: abandoned instances in boot()
- Remove atrophy: deprecate brain_v4, civ_v3

### Phase 2 — Organ Merge
- 6 graphs → 1 canonical graph core
- 3 execution engines → 1 canonical executor
- 4 civilization models → 1 canonical civilization
- 2 mathematics → 1 canonical mathematics (unblock omega_loop)

### Phase 3 — Nervous System Upgrade
- EventBus → AsyncEventBus with persistence
- ServiceProvider → Scoped lifetimes, factory functions

### Phase 4 — Immune Boost
- Add import cycle detection
- Add architectural fitness functions
- Add runtime health checks

---

**End of Mission 3: Repository DNA.**
