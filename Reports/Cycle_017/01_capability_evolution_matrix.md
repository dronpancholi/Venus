# Capability Evolution Matrix — Cycle 001 → 017

> Cycle 017 — Project Aether
> Traces the creation, consolidation, and obsolescence of every major subsystem

---

## How to Read

Each row represents a component or concept. The matrix shows when it was:
- **Created** (first appearance)
- **Consolidated** (designated canonical among competing implementations)
- **Enhanced** (significant feature additions)
- **Deprecated** (superseded but not removed)
- **Dead** (never worked or no longer used)
- **Wired** (connected to production consumers)

---

## 1. Foundational Layer (genesis/fabric/)

| Component | 001 | 005 | 008 | 010 | 012 | 013 | 014 | 015 | 016 | 017 (Plan) |
|-----------|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----------|
| **FabricKernel** | — | — | — | Created | — | Lazy-load subsystems | DGRADED enum (dead) | — | — | M121: Engineering Object model |
| **EventBus** (legacy) | Created | — | — | — | — | — | Orphaned | — | — | Remove |
| **EventRouter** | — | Created | — | — | — | — | Indexes unused (dead) | — | — | M122: Knowledge Engine |
| **MessageBus** | — | Created | — | — | — | — | — | — | — | M121: Merge with EventRouter |
| **EventStore** (bounded) | — | — | — | Created | — | TTL/expiry (dead) | — | — | — | M125: SQLite reads wired |
| **StorageEngine** | — | — | — | Created | — | 8 query methods dead | — | — | — | M121: Unify persistence |
| **SchemaManager** | — | — | — | Created | — | No migrations beyond v1 | — | — | — | M131: Versioned API |
| **ServiceRegistry** | — | Created (kernel) | — | — | — | — | Triple overlap | — | — | M121: Unify with DI |
| **AuditLog** | — | — | — | Created | — | Triple audit path | — | — | — | M121: Single audit pipeline |

### Evolution Summary

The Fabric layer was created in Cycle 010 as the canonical kernel, replacing UniversalKernel (001-009). EventRouter and MessageBus coexisted since Cycle 005. The EventStore's TTL/expiry was implemented in Cycle 014 but never enforced. The StorageEngine has 8 query methods that are only tested (never queried in production). The SchemaManager records version but has no actual migration steps.

**Cycle 017 Opportunity**: Unify EventRouter + MessageBus, wire TTL enforcement, make SQLite the canonical event query source, add migrations.

---

## 2. Desktop Layer (genesis/desktop/)

| Component | 010 | 011 | 012 | 013 | 014 | 015 | 016 | 017 (Plan) |
|-----------|-----|-----|-----|-----|-----|-----|-----|-----------|
| **GenesisDesktop App** | Created | — | — | Screen cache (dead) | — | — | Screen cache fixed(?) → still broken | M121-M132 |
| **InspectorScreen** | Created | — | — | — | — | — | — | M124: Copilot integration |
| **HomeScreen** | Created | — | — | — | — | — | Redesigned (6 widgets) | M132: Intelligence dashboard |
| **MemoryExplorer** | — | Created | — | — | — | — | — | M122: Knowledge Engine consumer |
| **TimelineScreen** | — | — | Created | — | — | — | — | M125: Merged with Memory |
| **KnowledgeGraphScreen** | — | — | Created | — | — | — | Graph→Tree (Cycle 016) | M127: Live Knowledge Graph |
| **AgentScreen** | — | Created | — | — | — | — | — | M124: Copilot workspace |
| **AIScreen** | — | — | Created | — | — | — | — | M124: Copilot settings |
| **CEScreen** | — | — | — | Created | — | — | — | M129: Autonomous Review UI |
| **ReportsScreen** | — | — | Created | — | — | — | — | M122: Merged with Memory |
| **SettingsScreen** | — | — | Created | — | — | — | Still read-only | M131: Real settings |
| **CommandPalette** | — | Created | — | — | — | 5 redundant commands | — | M124: Copilot-aware |
| **SearchEverywhere** | — | Created | — | — | — | 10 sources | Debounce still missing | M122: Knowledge Engine search |
| **ActivityBar** | — | — | Created | — | Orphaned | — | — | Remove or wire |
| **EventLog/LiveActivityFeed** | — | Created | — | — | 3× duplication | — | — | M122: Unified event viewer |

### Evolution Summary

Desktop started with 5 screens in Cycle 010, grew to 9 by Cycle 012, and reached 11 by Cycle 014. Cycle 016 was the first major redesign (Home, Workspace, Spotlight, KnowledgeGraph). Three widgets have been orphaned since Cycle 012-014. The screen cache has been broken since Cycle 013.

**Cycle 017 Opportunity**: All screens become consumers of Engineering Objects. Memory + Timeline merge. Reports merge into Memory. Widget duplication eliminated. Copilot-aware command palette.

---

## 3. AI Platform (genesis/ai/)

| Component | 010 | 011 | 012 | 013 | 014 | 015 | 016 | 017 (Plan) |
|-----------|-----|-----|-----|-----|-----|-----|-----|-----------|
| **AIProvider base class** | Created | — | — | — | — | — | — | M124: Copilot provider |
| **ProviderRegistry** | — | Created | — | — | Empty startup | — | — | M124: Auto-registration |
| **AIRouter** | — | Created | — | — | Fallback unused | — | — | M123: Reasoning + fallback |
| **NvidiaNIMProvider** | — | — | Created | — | — | — | — | M124: Copilot provider |
| **OllamaProvider** | — | — | Created | — | — | — | — | M124: Local copilot |
| **OpenAICompatible** | — | — | — | Created | — | — | — | M124: Cloud copilot |
| **prompts.py** | — | — | — | — | Stub | Moved to fabric/ | — | M122: Knowledge Engine prompts |
| **Rate limiter, context mgr, etc.** | — | — | — | — | — | Listed but never created | — | M123: Reasoning engine |

### Evolution Summary

The AI platform has a solid abstract foundation but is **completely disconnected** from production. Providers are never auto-registered. The router's fallback chain is never tried. Streaming reads character-by-character. The prompt system lives in `fabric/execution.py` instead of in the AI layer.

**Cycle 017 Opportunity**: Wire AI platform into production. Auto-register providers. Make fallback work. Move prompts to AI layer. Add Reasoning Engine as AI-aware but LLM-agnostic.

---

## 4. Server Layer (genesis/server.py + api/)

| Component | 005 | 010 | 013 | 014 | 016 | 017 (Plan) |
|-----------|-----|-----|-----|-----|-----|-----------|
| **FastAPI GenesisAPI** | Created (21 endpoints) | — | WS async queue | WS queue never drained | WS security design | M131: Public API |
| **WebSocket** | — | Added | Fixed (async queue) | Queue never consumed | Auth gap identified | M131: Full WS API |
| **Auth** | — | Added | — | Disabled by default | HMAC design | M131: Real auth |
| **APIRouter** (legacy, 36 routes) | Created | — | — | — | — | Remove |
| **SecurityManager** | Created | — | — | — | Disconnected from SecurityValidator | M131: Unify |

### Evolution Summary

The server has been fully functional since Cycle 005 but has **never had a single production consumer**. Every endpoint works but no code in the repository connects to it. The legacy APIRouter (36 routes) exists in parallel. Two security systems coexist, both disconnected.

**Cycle 017 Opportunity**: Genesis Public API (M131) means stabilizing existing endpoints, adding auth, fixing WS, and providing a path for external consumers (AgentOS).

---

## 5. Brain & Cognition

| Component | 010 | 012 | 014 | 016 | 017 (Plan) |
|-----------|-----|-----|-----|-----|-----------|
| **EngineeringBrain** (entity CRUD) | Created | — | — | — | M121: Engineering Object consumer |
| **BrainGraph** | Created | — | — | — | M127: Part of Live Knowledge Graph |
| **Sync Adapters** (6) | — | Created | — | — | M121: Universal object sync |
| **EmbeddingStore** (storage) | — | Created | Storage-only (no ML) | — | M122: Knowledge Engine embeddings |
| **BrainEntityType** (91 types) | — | Created | 85 unused | — | M121: Engineering Object types |
| **Cognitive Architecture** (10 subsystems) | — | Created | NEVER used | — | M123-M130: Wire cognition |
| **brain_v4.py** (deprecated) | Created | Expanded (738 lines) | Deprecated but instantiated | — | Remove |
| **Brain Integration** (7 events) | — | Created | 2 stubs | — | M130: Continuous Learning |

### Evolution Summary

The EngineeringBrain (entity CRUD, graph, sync adapters) is production-tested and working. But the rich cognitive architecture (2,340 lines across 10 subsystems) has never been wired into production — it exists only in tests. brain_v4.py remains instantiated despite being deprecated. The EmbeddingStore stores vectors but never computes them.

**Cycle 017 Opportunity**: Wire the cognitive architecture into production. The ReasoningEngine can become M123. The DecisionEngine can become M126. The Orchestrator can become M124 (Copilot) architecture. The BeliefSystem/AttentionMechanism can inform M130 (Continuous Learning). Embedding computation can begin.

---

## 6. Graph Systems

| Component | 001 | 005 | 008 | 010 | 012 | 014 | 016 | 017 (Plan) |
|-----------|-----|-----|-----|-----|-----|-----|-----|-----------|
| **KnowledgeGraphEngine** | Created | — | — | — | — | — | — | M127 (replace) |
| **HypergraphKnowledgeCore** | — | Created | — | — | — | — | — | M127 (replace) |
| **PersistentGraphDB** | — | — | Created | — | — | — | — | M127 (backend) |
| **BrainGraph** | — | — | — | Created | — | Canonical | — | M127: Live graph |
| **GraphV2 (12 files, 1,765 lines)** | — | — | — | — | Created | Unused | — | M127: Wire or deprecate |
| **MetaModelGraph** | — | — | — | — | Created | Name collision | — | M121: Rename |

### Evolution Summary

Genesis has accumulated 3 separate graph systems:
1. **PersistentGraphDB** (Cycle 008) — the durable storage backend
2. **BrainGraph** (Cycle 010) — wraps PersistentGraphDB with entity relationships — **canonical production graph**
3. **GraphV2** (Cycle 012) — ambitious multi-layer system with 1,765 lines of analytics/traversal/federation/versioning — **barely used**
4. **MetaModelGraph** (Cycle 012) — entity-relation graph for metamodel — name collision with GraphV2's UnifiedGraph

**Cycle 017 Opportunity**: Designate BrainGraph as canonical for entity storage, consider GraphV2 features for M127 (Live Knowledge Graph analytics, traversal, versioning), and rename MetaModelGraph to avoid collision.

---

## 7. Plugin Systems

| Component | 001 | 005 | 010 | 014 | 017 (Plan) |
|-----------|-----|-----|-----|-----|-----------|
| **PluginLoader** (kernel-level) | Created | — | — | 3rd system identified | Remove |
| **PluginManager** (external plugins) | — | Created | — | Canonical but not desktop | M132: Desktop plugin mgmt |
| **ModulePluginRegistry** (engines) | — | — | Created | Minimal overlap | Keep (engine factory) |
| **PluginManifest** | — | — | Created | Rich schema (deps, hooks, cmds) | M132: AgentOS manifest |

### Evolution Summary

Three systems with different owners — PluginManager (VenusPlatform), ModulePluginRegistry (OmegaLoop), PluginLoader (UniversalKernel). PluginManager is designated canonical but not connected to desktop. No desktop plugin management exists.

**Cycle 017 Opportunity**: Connect PluginManager to desktop. Remove PluginLoader (owned by deprecated UniversalKernel). Keep ModulePluginRegistry for engine factories (different concern). Stabilize PluginManifest for AgentOS.

---

## 8. Memory & Reports

| Component | 001 | 010 | 012 | 014 | 015 | 016 | 017 (Plan) |
|-----------|-----|-----|-----|-----|-----|-----|-----------|
| **UniversalMemorySystem** | — | Created | — | — | — | — | M122: Knowledge Engine backend |
| **ConversationEngine** | — | Created | — | — | — | — | M122: Structured knowledge |
| **Reports** (markdown files) | Created | — | — | Audit | Consolidation | 28 reports | M122: Knowledge Engine (structured) |
| **Cycle merged reports** | — | — | — | — | Merged format | 2,075-line merged | M122: Knowledge extraction |

### Evolution Summary

Reports started as free-form markdown. Cycles 014-016 standardized the format with audit/spec/design/validation categories. Cycle 016 introduced merged reports. But reports are still unstructured markdown — not machine-readable knowledge.

**Cycle 017 Opportunity**: M122: Reports become structured knowledge (entities, concepts, decisions, patterns, lessons, risks). Engineering Knowledge Engine extracts and indexes report content automatically.

---

## 9. Evolution Drivers

### What Drove Creation
- **Cycle 001-009**: Foundational exploration — multiple competing systems emerged (UniversalKernel, DiKernel, FabricKernel; KnowledgeGraphEngine, Hypergraph, PersistentGraphDB)
- **Cycle 010**: First engineering review → FabricKernel designated canonical, BrainGraph created
- **Cycle 012**: Cognitive architecture + GraphV2 created (ambitious, ahead of production needs)
- **Cycle 013**: Event-driven UI migration (performance-driven)
- **Cycle 014**: First product audit (quality-driven)
- **Cycle 015**: Consolidation — "one way to do things" (engineering hygiene)
- **Cycle 016**: UX transformation — "feel like a real product" (user-driven)

### What Remains Unresolved
- **Legacy test burden**: ~900 tests on deprecated UniversalKernel/DiKernel
- **Unused cognition**: 2,340 lines of cognitive architecture waiting for wiring
- **Unused graph**: 1,765 lines of GraphV2 waiting for a consumer
- **Unused server**: 21 endpoints with no consumers
- **Unwired AI**: Providers never auto-registered, router fallback never tried
- **Untested desktop**: Zero Textual pilot tests across 2,576 lines of UI

### What Cycle 017 Changes
Cycle 017 is the first cycle to directly address the **intelligence gap** — all the cognitive and knowledge infrastructure exists but is disconnected. M121-M132 wire it together under the Engineering Object Model, transforming Genesis from an operating system into an intelligence platform.
