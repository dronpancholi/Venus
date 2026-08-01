# PROJECT NEXUS — The Great Duplication Investigation

**Volume I — Capability Civilization**
**Part I — The Great Consolidation**
**Mission 3 Deliverable**

---

## Investigation Methodology

Every duplication cluster was investigated by:
1. Reading the source code of each implementation
2. Comparing public API surfaces (classes, methods, signatures)
3. Identifying unique vs overlapping features
4. Tracing consumer usage (who imports what)
5. Evaluating maturity (lines of code, test coverage, integration depth)
6. Determining canonical candidate based on evidence, not chronology

---

## 1. Scientific Method — 3 Implementations

### Files Involved

| File | Lines | Classes | Consumer |
|------|-------|---------|----------|
| discovery.py | 400 | 9 | OmegaLoop (_law_1_discovery) |
| scientist.py | 383 | 10 | OmegaLoop (_law_4_scientific_method) |
| repository_scientist.py | 247 | 3 | OmegaLoop (_phase_5_scientific_method) |

### Why Duplication Occurred

Each implementation was created at a different Genesis epoch without
consolidating the previous one:

- **GENESIS-VIII**: `discovery.py` (Program 5: Scientific Discovery Engine)
- **GENESIS-IX**: `scientist.py` (Phase 6: Engineering Scientist V2)
- **OmegaLoop integration**: `repository_scientist.py` (Phase 7: Repository Scientist)

Each successive implementation was not a replacement — it was a rewrite.
The old file was never removed, deprecated, or merged.

### Whether Duplication Is Accidental

**Accidental.** All three implement the same concept (scientific method
applied to software engineering) with the same pipeline
(observe → hypothesize → experiment → publish). The differences are
in implementation detail, not purpose.

No engineering decision record explains why a new implementation was
created instead of extending the existing one.

### Feature Comparison

| Feature | discovery.py | scientist.py | repository_scientist.py |
|---------|:---:|:---:|:---:|
| Observation | Yes | Yes | No |
| Hypothesis generation | Yes | Yes | No |
| Experiment design | Yes | Yes | No (experiments only) |
| Experiment execution | Yes | Yes | Yes |
| Statistical validation | t-test, effect size, p-value | t-test, effect size, bayesian | No |
| Literature review | Yes | Yes | No |
| Publication | Yes | Yes | No |
| Peer review | Yes | Yes | No |
| Evidence strength | Yes (5 levels) | No | No |
| Bayesian analysis | No | Yes (bayesian_factor) | No |
| OmegaLoop integration | No | No | Yes (direct API) |
| Full cycle automation | Yes (7 steps) | Yes (full_cycle) | No (propose/run only) |

### Which Implementation Is Strongest

**scientist.py** (EngineeringScientist V2) is the strongest:

1. Most complete feature set (all pipeline steps present)
2. Has Bayesian analysis (unique: bayesian_factor)
3. Cleanest class decomposition
4. V2 designation indicates it was designed to be the successor

### Which Implementation Should Become Canonical

**scientist.py** should become canonical, with unique features merged from:

- **discovery.py**: `EvidenceStrength` enum (5 levels: anecdotal through conclusive)
- **repository_scientist.py**: Simplified `propose()` / `run()` API for OmegaLoop
  integration; specific experiment types (canonicalization_audit,
  dependency_analysis, test_gap_analysis, risk_assessment, health_check)

### Migration Plan

1. Merge `EvidenceStrength` into `scientist.py`'s `Hypothesis` class
2. Add `repository_scientist.py`'s 5 experiment types as named presets
3. Add `run_simple(name, hypothesis, method)` convenience method for OmegaLoop
4. Create compatibility stub: `repository_scientist.py` imports from `scientist.py`
5. Add deprecation warning to `discovery.py`
6. Update OmegaLoop's `_phase_5_scientific_method` to use canonical API

**Estimated effort: 2-3 days**
**Lines removed: ~400 (discovery.py content merged, file deprecated)**

---

## 2. Civilization / Institutions — 3 Implementations

### Files Involved

| File | Lines | Classes | Consumer |
|------|-------|---------|----------|
| civilization_v2.py | 273 | 6 | platform.py |
| civilization_v3.py | 241 | 4 | platform.py |
| digital_civilization.py | 321 | 6 | platform.py, OmegaLoop |

### Why Duplication Occurred

Identical pattern to scientific method: each Genesis epoch created a
new version without removing the old one:

- **GENESIS-VIII**: `civilization_v2.py` (Program 8: Software Civilization V2)
- **GENESIS-IX**: `civilization_v3.py` (Phase 9: Software Civilization V3)
- **OmegaPhase**: `digital_civilization.py` (Phase 10: Digital Civilization)

The "V" numbers are misleading — v2 was not replaced by v3; they coexist.
digital_civilization is a parallel implementation with a different philosophy
(contracts + reputation + RelationshipEngine integration).

### Whether Duplication Is Accidental

**Primarily accidental.** While each version added new concepts (v2:
projects/deliverables; v3: research/publishing; digital: contracts/
reputation), the core Institute concept is duplicated three times.
platform.py imports all three because no single one has all features.

### Feature Comparison

| Feature | v2 | v3 | digital |
|---------|:---:|:---:|:-------:|
| Institute creation | Yes | Yes | Yes |
| InstituteType | 13 types | 18 types | 18 types |
| Member management | Yes | Yes | Yes |
| Projects | Yes (Project, Deliverable) | No | No |
| Work cycles | Yes (work_cycle) | No | No |
| Research projects | No | Yes (ResearchProject) | No |
| Publishing | No | Yes (publish_paper) | No |
| Standards | No | Yes (propose_standard) | No |
| Governance | No | Yes (governance_action) | No |
| Contracts | No | No | Yes (Contract) |
| Reputation | No | No | Yes (ReputationEvent) |
| Capabilities | No | No | Yes (Institute.add_capability) |
| RelationshipEngine | No | No | Yes (full integration) |
| Factory function | No | No | Yes (build_default_civilization) |

### Which Implementation Is Strongest

**digital_civilization.py** is the strongest:

1. Integrates with the canonical `RelationshipEngine` (ontology)
2. Has the richest feature set: contracts, reputation, capabilities
3. Has `build_default_civilization()` factory function
4. 321 lines — more features per line than v2 or v3
5. Cleanest design (dataclass-based entities)

### Which Implementation Should Become Canonical

**digital_civilization.py** should become canonical, with features merged from:

- **v2**: `Project`, `Deliverable`, `WorkProduct`, `work_cycle()` method
- **v3**: `ResearchProject`, `publish_paper()`, `propose_standard()`,
  `governance_action()` methods

### Migration Plan

1. Add `Project`, `Deliverable` classes to `digital_civilization.py`
2. Add `ResearchProject` and research/publishing methods
3. Add `governance_action()` method
4. Add `build_default_civilization()` updated to create all institute types
5. Update platform.py to use only `digital_civilization`
6. Create compatibility stubs for v2/v3
7. Add deprecation warnings to v2/v3

**Estimated effort: 3-5 days**
**Lines removed: ~300 (v2/v3 merged into digital, then deprecated)**

---

## 3. Evolution / Simulation — 5 Implementations

### Files Involved

| File | Lines | Classes | Purpose |
|------|-------|---------|---------|
| evolution.py | 310 | 8 | Self-evolution: observe → analyze → reason → simulate → experiment → decide |
| evolution_v4.py | 352 | 11 | Evolution V4: metrics → hypotheses → experiments → rewards → retro |
| simulator.py | 337 | 9 | General simulation: inputs, scopes, scenarios, analysis |
| simulator_v2.py | 289 | 7 | Simulation V2: config, execution, scenarios, metrics |
| brain_v4.py | 731 | 12 | Engineering Brain: cognition + memory + evolution + learning |

### Why Duplication Occurred

This is the worst case in the repository. Five modules with overlapping
responsibility, created across four Genesis epochs:

1. `evolution.py` — GENESIS-VIII (first evolution model)
2. `simulator.py` — GENESIS-VIII (first simulation model)
3. `simulator_v2.py` — GENESIS-IX (simulation rewrite)
4. `evolution_v4.py` — GENESIS-IX (evolution rewrite — note the skip from v1→v4)
5. `brain_v4.py` — GENESIS-IX Phase 10 (unified brain/cognition/evolution)

The naming is chaotic: v4 of evolution coexists with v1 of evolution.
simulator v2 coexists with simulator v1. brain_v4 overlaps with all.

### Feature Comparison

| Feature | evo.py | evo_v4.py | sim.py | sim_v2.py | brain_v4.py |
|---------|:------:|:---------:|:------:|:---------:|:-----------:|
| Observation/metrics | Yes | Yes | No | No | Yes |
| Hypothesis generation | Yes | Yes | No | No | Yes |
| Simulation execution | Yes (sim) | No | Yes | Yes | Yes (sim) |
| Experiment lifecycle | Yes | Yes | No | Yes | Yes |
| Decision/verdict | Yes | Yes | No | No | Yes |
| Retrospective | No | Yes | No | No | No |
| Reward computation | No | Yes | No | No | Yes |
| Scenario planning | No | No | Yes | Yes | No |
| Fitness computation | Yes | No | No | No | Yes |
| Cognitive stages | No | No | No | No | Yes (10 stages) |
| Memory integration | No | No | No | No | Yes |
| Learning | No | No | No | No | Yes |
| Generation tracking | Yes (cycles) | Yes (epochs) | Yes (iterations) | Yes (runs) | Yes (cycles) |

### Which Implementation Is Strongest

**evolution_v4.py** is the strongest evolution implementation:
- Most complete feature set (hypotheses, experiments, rewards, retrospective)
- Clean class hierarchy (EvolutionMetric, EvolutionHypothesis, EvolutionExperiment)
- Reward/retro feedback loop not present in evolution.py

**simulator_v2.py** is the strongest simulation implementation:
- Cleaner API than simulator.py
- Configuration-driven (SimulationConfig)
- Scenario analysis with metrics

**brain_v4.py** is a separate concern (cognitive architecture) that happens
to include evolution features.

### Recommended Action

This cluster cannot be merged into a single module — the concerns are
legitimately different (evolution ≠ simulation ≠ cognition). However,
the boundaries are currently blurred.

**Canonical consolidation plan:**

1. **evolution_v4.py** → canonical evolution engine
2. **simulator_v2.py** → canonical simulation engine (with simulator.py deprecated)
3. **brain_v4.py** → canonical cognitive/brain engine
4. **evolution.py** → merge unique features into evolution_v4.py, deprecate
5. **simulator.py** → merge unique scenarios into simulator_v2.py, deprecate

Unique features to preserve from deprecated files:
- evolution.py: `SelfObserver.trend()`, `EvolutionEngine.evolution_cycle()` lifecycle
- simulator.py: `SimulationScope`, scenario classification

**Estimated effort: 4-5 days**
**Lines removed: ~1,000 (evolution.py + simulator.py + overlap)**

---

## 4. Mathematics — 2 Implementations

### Files Involved

| File | Lines | Classes |
|------|-------|---------|
| mathematics.py | 796 | 20+ |
| mathematics_v2.py | 361 | 8+ |

### Why Duplication Occurred

Standard pattern: GENESIS-VIII (mathematics.py) → GENESIS-IX (mathematics_v2.py)
without removing v1. mathematics_v2.py was intended as an improved version
but v1 was never deprecated.

### Feature Comparison

Both define `ArchitectureAlgebra` with different methods:
- mathematics_v2.py: matrix-based coupling computation (unique)
- mathematics.py: rich model suite (engineering gravity, debt tensor,
  knowledge diffusion, architecture momentum, dependency energy,
  repository curvature, module metrics)

### Which Implementation Is Strongest

**mathematics.py** by far — 796 lines vs 361, vastly more models,
better test coverage.

**mathematics_v2.py** should be deprecated. Its unique matrix-based
algorithms should be ported to mathematics.py.

### Migration Plan

1. Port unique v2 algorithms (`coupling_product`, `cohesion` matrix
   methods) into mathematics.py's `ArchitectureAlgebra`
2. Add deprecation warning to mathematics_v2.py
3. Update any consumers (grep shows limited usage)

**Estimated effort: 1 day**
**Lines removed: ~300 (v2 deprecated after port)**

---

## 5. Platform / Service — 2 Implementations

### Files Involved

| File | Lines | Classes |
|------|-------|---------|
| platform.py | 767 | VenusPlatform |
| platform_v2.py | 512 | 8+ (ServiceRegistry, LifecycleManager, EventRouter, MetricsManager) |

### Why Duplication Occurred

platform_v2.py was created as a cleaner service-abstraction layer.
platform.py (the bootstrapper) grew organically to 767 lines with 50+
direct imports. platform.py uses platform_v2.py's ServiceRegistry
but also does its own direct wiring.

### Which Implementation Is Strongest

**platform_v2.py** has the cleaner architecture (ServiceRegistry pattern).
**platform.py** is the actual running system. They are complementary
rather than duplicative — platform_v2 provides the framework, platform.py
provides the concrete wiring.

The duplication is in their overlap: both manage service lifecycle,
both track service state, both have event-like mechanisms.

### Migration Plan

1. Refactor platform.py to use platform_v2.py exclusively for all
   service registration and lifecycle management
2. Move concrete service definitions out of platform.py into their
   respective modules
3. platform.py becomes a thin bootstrapper (100-200 lines)

**Estimated effort: 2-3 days**
**Lines removed: ~300-400 (platform.py shrinks)**

---

## 6. Graph Systems — 6 Implementations

### Files Involved

| System | Location | Lines |
|--------|----------|-------|
| Graph v1 | graph/engine.py | ~300 |
| Graph v2 | graph_v2/ (9 files) | ~2,000+ |
| Knowledge Graph | knowledge_graph.py | 320 |
| Hypergraph | hypergraph.py | 648 |
| Execution Graph | execution_graph.py | 420 |
| Repository Graph | repository_graph.py | 241 |

### Why Duplication Occurred

Each graph system serves a different purpose — but they use different
entity models, query interfaces, and storage backends.

- graph/engine.py: Original graph engine (simple adjacency)
- graph_v2/: Comprehensive V2 (analytics, federation, partitioning, versioning)
- knowledge_graph.py: Knowledge/semantic graph (PlanetaryKnowledgeGraph)
- hypergraph.py: Hypergraph with typed nodes/edges
- execution_graph.py: Workflow/execution DAG
- repository_graph.py: Repository dependency graph

### Which Implementation Is Strongest

**graph_v2/** is the most comprehensive graph system (9 files, ~2,000+ lines)
but is unused by most consumers. Each consumer built its own graph
because graph_v2 was not ready or discoverable.

### Recommended Action

This is a multi-cycle effort. Short-term:
1. Identify gaps in graph_v2 that forced consumers to build their own
2. Add adapter layers so knowledge_graph, hypergraph, etc. can use
   graph_v2 as backend

**Long-term: Make graph_v2 the canonical graph implementation.**
**Estimated effort: 1-2 weeks (complete unification)**

---

## 7. Memory — 2 Implementations

### Files Involved

| File | Lines |
|------|-------|
| memory/ (3 files) | ~400 |
| memory_system.py | 413 |

### Which Implementation Is Strongest

**memory/** is simpler and better integrated. **memory_system.py** is more
comprehensive but disconnected.

### Migration Plan

Merge memory_system.py's unique features (UniversalMemorySystem,
MemoryType) into memory/ engine.

**Estimated effort: 2-3 days**

---

## 8. Economics — 2 Implementations

**economics.py** (243 lines) — general economics engine
**repository_economics.py** (160 lines) — OmegaLoop wrapper

Merge repository_economics.py features into economics.py,
make repository_economics.py a thin import wrapper.

**Estimated effort: 1 day**

---

## 9. Events — 2 Implementations

**events/bus.py** (EventBus) — widely used, clean
**platform_v2.py** (EventRouter) — parallel implementation

Unify on EventBus. Port EventRouter unique features (subscription
patterns, recent event history) into EventBus.

**Estimated effort: 1 day**

---

## 10. Brain / Cognition — 3 Implementations

**brain/** (subpackage with cognition modules) — inline
**brain_v4.py** (731 lines) — standalone EngineeringBrainV4
**intelligence/** — separate approach

This requires deeper investigation. brain_v4.py appears strongest
but also largest. brain/ has cleaner decomposition.

**Estimated effort: 3-5 days** (requires investigation first)

---

# CONSOLIDATION SUMMARY

## Priority Ranking

| Priority | Cluster | Effort | Lines Removed | Risk | ROI |
|----------|---------|--------|---------------|------|-----|
| P1 | Scientific Method (3→1) | 2-3d | ~400 | Medium | Very High |
| P2 | Civilization (3→1) | 3-5d | ~300 | Medium-High | Very High |
| P3 | Mathematics (2→1) | 1d | ~300 | Low | High |
| P4 | Events (2→1) | 1d | ~100 | Low | High |
| P5 | Economics (2→1) | 1d | ~100 | Low | High |
| P6 | Evolution/Sim (5→3) | 4-5d | ~1,000 | High | High |
| P7 | Platform (2→1) | 2-3d | ~400 | Medium | High |
| P8 | Memory (2→1) | 2-3d | ~200 | Medium | Medium |
| P9 | Brain/Cognition (3→1) | 3-5d | ~500 | High | Medium |
| P10 | Graph Systems (6→1) | 1-2wk | ~2,000 | Very High | Very High |

## Total Consolidation Impact

- **Implementations consolidated**: ~30+ modules → ~15 canonical
- **Lines removed**: 4,000-6,000
- **Total effort**: 20-35 engineering days
- **Duplication rate**: ~65% of capability areas have at least one duplicate
- **Worst offender**: Evolution/Simulation (5 implementations, 2,019 lines)
- **Cleanest areas**: Ontology (1), Reasoning (1), Physics (1), USIR (1)

---

## Root Cause Analysis

Every duplication follows the same pattern:

1. **Genesis epoch expansion**: Each epoch (VIII, IX, OmegaPhase) created
   new versions of capabilities without removing old ones.
2. **No deprecation policy**: Old files were never deprecated, just abandoned.
3. **No Architecture Review Board**: No gate checked whether a new abstraction
   could reuse an existing one.
4. **No canonical registry**: No discoverable list of "what already exists."
5. **Platform.py as the attractor**: platform.py (767 lines) imports everything,
   creating coupling that makes it hard to remove old modules.

**The cure**: A mandatory Architecture Review Board that checks existing
abstractions before approving new ones. This is Atlas P6 (ROI 0.90).

---

## Next: Mission 4 — Engineering Design Review

Each major subsystem will undergo a formal design review covering:
- Original problem
- Current architecture
- Strengths/weaknesses
- Scaling limitations
- Maintainability
- Extensibility
- Alternative designs
- Whether past rejection decisions remain valid
