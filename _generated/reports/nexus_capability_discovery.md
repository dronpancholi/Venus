# PROJECT NEXUS — Capability Discovery

**Volume I — Capability Civilization**
**Part I — The Great Consolidation**

## Engineering Lineage

This document is the output of PROJECT NEXUS Mission 1 (Capability Discovery) and
Mission 2 (Engineering Capability Graph). It reconstructs Genesis not as files or
packages, but as engineering abilities — capabilities the platform can actually
perform. This is the foundation for all subsequent consolidation work.

---

## How to Read This Document

Every capability is a node in the Engineering Capability Graph. Each entry describes:

- **Purpose** — Why this capability exists, what engineering problem required it
- **Owner** — The canonical subsystem/files that provide this capability
- **Consumers** — Which other capabilities depend on it
- **Maturity** — production / beta / alpha / legacy
- **Duplication** — How many independent implementations exist
- **Health** — Internal assessment
- **Replacement Cost** — Engineering effort to replace or merge

---

# CAPABILITY INVENTORY

---

## 1. Repository Scanning

**Why?** The platform must observe its own repository to make engineering decisions.
Reverse engineering turns raw files into typed, linked graphs.

**Owner:** `reverse_engineer.py` (910 lines) — `ReverseEngineeringEngine`
**Secondary:** `census.py` (863 lines) — `DeepCensusAnalyzer`

**Consumers:** OmegaLoop (all books), Atlas (Stage 1-3), Platform, Mathematics, Economics

**Maturity:** Production (reverse_engineer). Beta (census).

**Duplication:** census.py and reverse_engineer.py overlap significantly.
Both perform file scanning, AST analysis, and metric computation.
census.py was created as a v2 but never replaced reverse_engineer.
They are separate modules with overlapping responsibility.

**Health:** reverse_engineer.py is stable and well-tested. census.py has
duplicate logic for determining file language, counting classes/functions,
computing cyclomatic complexity.

**Replacement Cost:** Medium (2-3 days to merge into single scanning engine)

---

## 2. Ontology / Entity Management

**Why?** Every artifact in Genesis needs a canonical identity, type, and set of
relationships. The ontology is the universal type system.

**Owner:** `ontology.py` (1,398 lines) — `UniversalEntity`, `RelationshipEngine`,
`CanonicalRegistry`, 25+ entity types (UArtifact, UCapability, UProcess, etc.)

**Consumers:** Virtually everything — every module depends on ontology.

**Maturity:** Production

**Duplication:** None (single canonical implementation). However, graph_v2/
introduces a separate entity model (`UnifiedGraph`, `LayerType`) that overlaps
conceptually with ontology entities. The meta-model (`meta_model.py`) is a
separate but complementary type system.

**Health:** Strong. 1,398 lines of well-structured dataclass-based entities.
The `UniversalEntity` + `URelType` pattern is clean and extensible.

**Replacement Cost:** Very high (weeks). This is the foundation.

---

## 3. Meta-Modeling

**Why?** The platform needs a second-order type system that describes the structure
and relationships of types themselves (a model of the model).

**Owner:** `meta_model.py` (711 lines) — `MetaModelEngine`

**Consumers:** Ontology, Reasoning, Reverse Engineer

**Maturity:** Production

**Duplication:** None

**Health:** Good. Integrates with ontology through `register_universal_types`.

**Replacement Cost:** High (1 week)

---

## 4. Engineering Mathematics

**Why?** The platform needs quantitative models of software architecture:
algebra, topology, entropy, gravity, tensors.

**Owner:** `mathematics.py` (796 lines) — `RepositoryMathematics`, `EngineeringGravity`,
`TechnicalDebtTensor`, `RepositoryCurvature`, etc.
**Secondary:** `mathematics_v2.py` (361 lines) — Overlapping definitions

**Consumers:** OmegaLoop (Book IV), Physics, Economics, Evolution

**Maturity:** Production (mathematics.py). Beta (mathematics_v2.py).

**Duplication:** SIGNIFICANT. Both define:
- `ArchitectureAlgebra` (different implementations)
- Coupling/cohesion computations
- Entropy models
- Graph/tensor operations

mathematics.py is richer (796 lines, more models). mathematics_v2.py
was created as a v2 but never replaced v1. Both exist and are used.

**Health:** mathematics.py is the stronger implementation. mathematics_v2.py
should be deprecated and its unique algorithms (if any) merged into mathematics.py.

**Replacement Cost:** Medium (1-2 days to consolidate)

---

## 5. Scientific Method

**Why?** The platform needs to observe, hypothesize, experiment, and publish —
the complete scientific method applied to software engineering.

**Owner:** THREE independent implementations:
- `discovery.py` (400 lines) — `ScientificDiscovery` — Observe > Hypotheses > Design > Execute > Validate > Publish
- `scientist.py` (383 lines) — `EngineeringScientist` — Full V2 pipeline with peer review
- `repository_scientist.py` (247 lines) — `RepositoryScientist` — Lightweight, OmegaLoop-integrated

**Consumers:** OmegaLoop (Book VII), Atlas (Stage 6)

**Maturity:** Beta (all three)

**Duplication:** CRITICAL. Three independent implementations of the same concept:
- All have Hypothesis classes
- All have Experiment classes
- All have propose/execute/publish workflows
- Different API surfaces, different data models, incompatible

discovery.py was GENESIS-VIII. scientist.py was GENESIS-IX V2.
repository_scientist.py was created for OmegaLoop integration.

**Health:** Poor. Three implementations means knowledge split three ways.
Each has unique features the others lack:
- discovery.py: literature review, evidence strength
- scientist.py: peer review, publication, world model update
- repository_scientist.py: OmegaLoop integration, 5 experiment types

**Replacement Cost:** Medium (2-3 days). Requires merging all three into
one canonical `EngineeringScientist` with all features.

---

## 6. Reasoning

**Why?** The platform needs to query relationships, detect duplicates,
trace dependencies, and score health across the entire entity graph.

**Owner:** `reasoning.py` (364 lines) — `ReasoningEngine`

**Consumers:** RepositoryScientist, RepositoryEngineer, RepositoryEconomics,
OmegaLoop (Book VI), Platform

**Maturity:** Production

**Duplication:** None (single implementation)

**Health:** Good. Clean query/result pattern with evidence tracking.

**Replacement Cost:** High (3-5 days). Many consumers depend on specific API.

---

## 7. Planning

**Why?** The platform needs hierarchical planning: Vision > Mission > Program >
Portfolio > Roadmap > Milestone > Project > Epic > Capability > Feature > Task > Action.

**Owner:** `planner.py` (315 lines) — `EngineeringPlanner`
**Secondary:** OmegaLoop's `_tier_11_autonomous_roadmap`, Atlas Stage 15

**Consumers:** Platform, OmegaLoop, Economics

**Maturity:** Beta

**Duplication:** Partial. planner.py provides the formal planning hierarchy.
OmegaLoop has ad-hoc roadmapping in Book XII and Book XIII.
Atlas Stage 15 independently generates roadmaps. Three planning
capabilities with different levels of formality.

**Health:** Moderate. planner.py is well-designed but isolated —
OmegaLoop and Atlas don't use it; they have their own roadmap logic.

**Replacement Cost:** Medium (1-2 days to unify roadmapping)

---

## 8. Platform / Service Registry

**Why?** The platform needs a bootstrapper that wires all services together,
manages service lifecycle, and provides dependency injection.

**Owner:** `platform_v2.py` (512 lines) — `ServiceRegistry`, `LifecycleManager`,
`EventRouter`, `MetricsManager`
**Secondary:** `platform.py` (767 lines) — `VenusPlatform` — the concrete bootstrapper

**Consumers:** CLI, API, Integration, all services

**Maturity:** Production (platform.py). Beta (platform_v2.py).

**Duplication:** SIGNIFICANT. platform.py is a 767-line bootstrapper that
imports EVERYTHING and wires it together. platform_v2.py has a cleaner
ServiceRegistry abstraction. platform.py uses platform_v2.py but also
does its own wiring outside the registry.

**Health:** Moderate. platform.py is the canonical bootstrapper but has
grown to 767 lines with 50+ direct imports. platform_v2.py's ServiceRegistry
is cleaner but not used by all subsystems.

**Replacement Cost:** Medium (2-3 days to refactor platform.py to use
platform_v2.py exclusively)

---

## 9. Civilization / Institutions

**Why?** The platform models autonomous engineering institutions
(universities, companies, foundations, research labs) and the contracts,
reputation, and knowledge flow between them.

**Owner:** THREE independent implementations:
- `civilization_v2.py` (273 lines) — `SoftwareCivilization` with institutes, projects, deliverables
- `civilization_v3.py` (241 lines) — `SoftwareCivilizationV3` with research, publishing, governance
- `digital_civilization.py` (321 lines) — `DigitalCivilization` with contracts, reputation events

**Consumers:** OmegaLoop (Book XV), Platform

**Maturity:** Beta (all three)

**Duplication:** CRITICAL. Three independent implementations:
- civilation_v2: institutes + projects + deliverables
- civilation_v3: institutes + research + publishing + governance
- digital_civilization: institutes + contracts + reputation + capabilities

Each has Institute/InstituteType — different classes, different APIs.

platform.py imports ALL THREE (line 66: v2, line 82: v3, line 110: digital).

**Health:** Poor. Triple implementation with no clear canonical choice.
digital_civilization appears most mature (321 lines, contracts, reputation),
but platform.py still creates v3 instances (line 428).

**Replacement Cost:** Medium-high (3-5 days). Must audit platform.py's
usage of all three, create unified API, migrate consumers.

---

## 10. Evolution / Simulation

**Why?** The platform simulates repository evolution using biological models:
species, fitness, selection, generation.

**Owner:** FIVE independent implementations:
- `evolution.py` (310 lines) — `EvolutionEngine` — observe, analyze, reason, simulate, experiment, decide
- `evolution_v4.py` (352 lines) — `EvolutionEngineV4` — metrics, hypotheses, experiments, rewards, retros
- `simulator.py` (337 lines) — `SimulatorEngine` — simulation runs, inputs, scopes, scenarios
- `simulator_v2.py` (289 lines) — `SimulatorEngineV2` — config, execution, analysis
- `brain_v4.py` (731 lines) — `EngineeringBrainV4` — cognition, memory, evolution, learning

**Consumers:** OmegaLoop (Book IV, V), Platform

**Maturity:** Alpha-Beta (all five)

**Duplication:** EXTREME. Five overlapping modules:
- evolution.py + evolution_v4.py: same concept, different data models
- simulator.py + simulator_v2.py: same concept, different APIs
- brain_v4.py: overlaps with both evolution AND memory/cognition

This is the worst duplication in the repository.

**Health:** Poor. Five modules doing related things with incompatible APIs.
No clear canonical implementation.

**Replacement Cost:** High (4-5 days). Requires consolidating 5 modules into
one evolution engine with pluggable simulation backends.

---

## 11. Graph Systems

**Why?** The platform needs multiple graph views: dependency graphs, knowledge
graphs, execution graphs, hypergraphs, topological graphs.

**Owner:** Multiple:
- `graph/engine.py` — Original graph engine
- `graph_v2/` (9 files) — V2 with analytics, compression, federation, indexing, layers, partitioning, versioning
- `knowledge_graph.py` (320 lines) — `KnowledgeGraph`, `PlanetaryKnowledgeGraph`
- `hypergraph.py` (648 lines) — `HypergraphKnowledgeCore`
- `execution_graph.py` (420 lines) — `ExecutionGraph`, `ExecutionEngine`
- `repository_graph.py` (241 lines) — `RepositoryGraph`

**Consumers:** Every subsystem

**Maturity:** Mixed

**Duplication:** SIGNIFICANT. At least 6 distinct graph systems, each with
different APIs, entity models, and query interfaces. graph_v2/ attempts
to replace graph/ but both exist. knowledge_graph.py and hypergraph.py
address knowledge representation differently. execution_graph.py is unique
(workflow graphs) but could build on graph_v2.

**Health:** Moderate. Each serves a purpose but there is no unified graph
abstraction. graph_v2/ (9 files, ~2,000+ lines) is the most comprehensive
but is unused by most subsystems.

**Replacement Cost:** Very high (1-2 weeks). Graph consolidation is a
major architectural effort.

---

## 12. Memory Systems

**Why?** The platform persists and retrieves engineering knowledge, observations,
and entity state across sessions.

**Owner:** Multiple:
- `memory/engine.py` — Memory engine
- `memory/types.py` — Memory types
- `memory/consolidation.py` — Consolidation + forgetting
- `memory_system.py` (413 lines) — `UniversalMemorySystem`

**Consumers:** OmegaLoop, Platform, Brain, Knowledge Graph

**Maturity:** Beta

**Duplication:** Significant. memory_system.py was created as a unified
memory system but memory/ subpackage already existed. They overlap in
types, storage, and consolidation logic.

**Health:** Moderate. memory/ is simpler and better integrated. memory_system.py
is more comprehensive but disconnected.

**Replacement Cost:** Medium (2-3 days to merge)

---

## 13. Plugin / Registry

**Why?** The platform needs dynamic service discovery and plugin registration.

**Owner:** `plugin/manager.py` (236 lines) — `PluginManager`
`plugin/manifest.py` (123 lines) — `PluginManifest`
`plugin/registry.py` (110 lines) — `ModulePluginRegistry` (new)

**Consumers:** Platform, OmegaLoop

**Maturity:** Beta (PluginManager). Production (ModulePluginRegistry).

**Duplication:** Intentional. PluginManager is for external plugins (YAML
manifests, sandboxing, hot reload). ModulePluginRegistry is for internal
engine discovery (lightweight, no manifests). They serve different purposes.

**Health:** Good. Clean separation of concerns.

---

## 14. Physics / Engineering Physics

**Why?** The platform discovers statistically-derived laws of software
engineering physics.

**Owner:** `physics.py` (287 lines) — `PhysicsEngine`

**Consumers:** OmegaLoop (Book IV), Mathematics

**Maturity:** Beta

**Duplication:** None (single implementation)

**Health:** Good. Unique capability, well-isolated.

---

## 15. Economics / Engineering Economics

**Why?** The platform models engineering economics: cost, debt, ROI,
knowledge capital.

**Owner:** `economics.py` (243 lines) — `EconomicsEngine`
`repository_economics.py` (160 lines) — `RepositoryEconomics`

**Consumers:** OmegaLoop (Book IX), Platform, Planner

**Maturity:** Beta

**Duplication:** Moderate. economics.py is the general economics engine.
repository_economics.py is a lightweight OmegaLoop wrapper. They overlap
in debt/ROI computation but have different APIs.

**Health:** Moderate. Two implementations should be unified.

**Replacement Cost:** Low (1 day)

---

## 16. Engineering OS

**Why?** The platform provides an operating-system abstraction for engineering
services: manifests, roles, service lifecycle.

**Owner:** `engineering_os.py` (331 lines) — `EngineeringOS`, `ServiceManifest`, `ServiceRole`

**Consumers:** Platform, OmegaLoop

**Maturity:** Beta

**Duplication:** Overlaps with platform_v2.py ServiceRegistry. Both provide
service registration and lifecycle. Different API, same concept.

**Health:** Moderate. Would benefit from consolidation with platform_v2.

**Replacement Cost:** Low-Medium (1-2 days)

---

## 17. Execution / Orchestration

**Why?** The platform needs two master execution loops: OmegaLoop's 18-Book
constitution and Atlas's 15-stage protocol.

**Owner:** `omega_loop.py` (6,575 lines) — `OmegaLoop`
`atlas.py` (1,297 lines) — `Atlas`

**Consumers:** CLI, API

**Maturity:** Production (OmegaLoop). Production (Atlas).

**Duplication:** Intentional and documented. OmegaLoop executes the GENESIS
Infinity constitution. Atlas treats the repo as unknown and reconstructs
understanding. They serve different purposes.

**Health:** Good for both. OmegaLoop is large (6,575 lines) but well-structured.
Atlas is smaller (1,297 lines) and more focused.

**Replacement Cost:** Very high (can't merge — different purposes)

---

## 18. USIR / Multi-Language Compilation

**Why?** The platform compiles engineering understanding into a universal
intermediate representation across 20 target languages.

**Owner:** `compiler/` — `compiler.py`, `ast.py`, `parser.py`, `uir_builder.py`,
`codegen/`, `passes/`

**Consumers:** OmegaLoop (Book II)

**Maturity:** Alpha

**Duplication:** None (single implementation)

**Health:** Nascent. Only Python codegen appears functional.

**Replacement Cost:** High (unique capability)

---

## 19. Events

**Why?** The platform needs event-driven communication between subsystems.

**Owner:** `events/bus.py` — `EventBus`

**Consumers:** Platform, PluginManager, all subsystems

**Maturity:** Production

**Duplication:** Overlaps with platform_v2.py EventRouter. Both provide
publish/subscribe. Different API, same concept.

**Health:** Good. EventBus is simpler and more widely used. EventRouter
in platform_v2 is a parallel implementation.

**Replacement Cost:** Low (1 day to merge)

---

## 20. Persistence

**Why?** The platform stores state across sessions.

**Owner:** `persistence/` — Store abstractions

**Consumers:** Platform, Memory, Knowledge Graph

**Maturity:** Production

**Duplication:** None significant

---

## 21. Validation

**Why?** The platform validates entities, relationships, and transformations.

**Owner:** `validation/`

**Consumers:** All subsystems

**Maturity:** Beta

---

## 22. Intelligence / Cognitive

**Why?** The platform has cognitive functions: attention, perception, learning,
reasoning, planning, memory, creativity.

**Owner:** `intelligence/`
`brain/` — `cognition/`, `embeddings.py`, `entity.py`, `graph.py`, `sync.py`
`brain_v4.py` (731 lines) — `EngineeringBrainV4`

**Consumers:** OmegaLoop, Platform

**Maturity:** Alpha-Beta

**Duplication:** Significant. brain/ is a subpackage with cognition modules.
brain_v4.py is a standalone brain implementation. intelligence/ is another
approach. Three overlapping cognitive architectures.

**Health:** Poor for duplication. The brain concept exists in 3 forms.

**Replacement Cost:** High (3-5 days)

---

## 23. Discovery / Pattern Detection

**Why?** The platform discovers patterns in code: anti-patterns, design patterns,
architectural violations.

**Owner:** `discovery.py` (400 lines) — `ScientificDiscovery`
(included in Scientific Method duplication above)

---

## 24. Diagnostics

**Why?** The platform diagnoses its own health and performance.

**Owner:** `diagnostics/`

**Maturity:** Alpha

**Duplication:** Overlaps with census, reverse_engineer, benchmarks

---

## 25. Kernel / OS

**Why?** The platform has a universal kernel and operating system abstraction.

**Owner:** `kernel/`, `os/`

**Maturity:** Alpha

---

## 26. Capability Registry

**Why?** The platform tracks its own capabilities.

**Owner:** `capability/`

**Maturity:** Alpha

---

## 27. API / CLI / Integration

**Why?** External interfaces: REST API, CLI, integration adapters.

**Owner:** `api/`, `cli/`, `integration/`

**Maturity:** Alpha

---

## 28. Security

**Why?** The platform validates permissions and security constraints.

**Owner:** `security/`

**Maturity:** Alpha

---

## 29. Digital Twin

**Why?** The platform maintains a digital twin of itself.

**Owner:** `digital_twin/`

**Maturity:** Alpha

---

## 30. Temporal / Time

**Why?** The platform tracks time-series data and temporal relationships.

**Owner:** `temporal/`

**Maturity:** Alpha

---

# DUPLICATION SUMMARY

| Capability | Implementations | Severity | Recommendation |
|-----------|-----------------|----------|---------------|
| Scientific Method | 3 (discovery, scientist, repository_scientist) | CRITICAL | Merge into one canonical EngineeringScientist |
| Evolution/Simulation | 5 (evolution, evolution_v4, simulator, simulator_v2, brain_v4) | EXTREME | Consolidate to one engine with backends |
| Civilization | 3 (v2, v3, digital_civilization) | CRITICAL | digital_civilization as canonical, deprecate v2/v3 |
| Mathematics | 2 (mathematics, mathematics_v2) | HIGH | Merge v2 unique content into v1, deprecate v2 |
| Platform/Service | 2 (platform.py, platform_v2.py) | HIGH | platform.py should use platform_v2 exclusively |
| Graph Systems | 6 (graph, graph_v2, knowledge_graph, hypergraph, execution_graph, repository_graph) | EXTREME | Long-term unification needed |
| Memory | 2 (memory/, memory_system.py) | HIGH | Merge into memory/ |
| Economics | 2 (economics, repository_economics) | MODERATE | Merge lightweight into general |
| Events | 2 (events/bus.py, platform_v2 EventRouter) | MODERATE | Unify on EventBus |
| Engineering OS | overlaps platform_v2 | MODERATE | Merge service lifecycle |
| Brain/Cognition | 3 (brain/, brain_v4, intelligence/) | HIGH | Unify cognitive architecture |
| Planning/Roadmapping | 3 (planner, OmegaLoop ad-hoc, Atlas Stage 15) | MODERATE | Planner should be canonical |
| Repository Scanning | 2 (reverse_engineer, census) | MODERATE | Merge census into reverse_engineer |

## Total Duplicate Modules Identified: ~30+ modules across 12 capability areas
## Estimated Consolidation Effort: 20-35 engineering days
## Estimated Lines Removed After Consolidation: ~4,000-6,000 lines

---

# NEXT: Mission 3 — The Great Duplication Investigation

Each duplicate cluster will be investigated in detail:
- Why duplication occurred
- Which implementation is strongest
- Which should become canonical
- Migration plan
- Engineering evidence
