# Phase 0: Complete System Reverse Engineering — Repository Archaeology

> Cycle 017 — Project Aether
> Date: 2026-07-03
> Scope: Full platform archaeology across all 16 cycles, 464+ source files, ~112K lines

---

## Executive Summary

This report catalogs everything discovered during a complete system reverse engineering of the Genesis Engineering Platform. The archaeology reveals:

- **~7,000+ lines of production-unused code** (4,500+ in brain/cognition + graph_v2 features; 700+ in desktop; 1,500+ in server/AI; ~200+ in kernel/events)
- **5+ overlapping/duplicate systems** (3 pub-sub, 3 DI/Service, 2 security, 3 graph, 3 plugin, 2 API routing)
- **21 server endpoints with zero production consumers**
- **3 orphaned desktop widgets**, **5 dead CSS selectors**
- **1 critical test infrastructure bug**: conftest.py in wrong directory (22 fixtures never loaded)
- **2,340 lines of cognitive architecture never used in production**
- **3 competing "UnifiedGraph" implementations** with different type systems

The Phase 0 findings directly inform every M121-M132 decision. No implementation begins without understanding what already exists.

---

## 1. Kernel & Fabric Core

### 1.1 Three Pub-Sub Systems — Only Two Are Alive

| System | File:Line | Delivery | Consumers | Status |
|--------|-----------|----------|-----------|--------|
| **Hooks** (`_hooks`/`_emit`/`on()`) | kernel.py:85,212-220 | Synchronous, no filtering | **DEAD** — `_emit()` never called |
| **EventRouter** (`on_event`/`emit`) | kernel.py:222-243, events.py:191 | Filtered, stored, dead-letter | **ACTIVE** — core event pipeline |
| **MessageBus** (`subscribe`/`send`) | kernel.py:200-210, bus.py:75 | Topic-based, priority queue | **ACTIVE** — `send()` bridges to EventRouter |

**Critical finding**: `kernel.on(handler)` registers a callback that **will never fire**. Any external code using `on()` creates a silent orphan. `_emit()` (hooks path) has zero callers.

**Fragile naming**: `_emit` (dead, private) vs `emit` (live, public) differ by a single underscore.

### 1.2 EventStore Indexes — Built But Never Queried

The `EventStore` maintains 5 indexes (`_by_type`, `_by_origin`, `_by_session`, `_by_repository`, `_by_tag`) on every `append()`, but `query()` performs a **linear scan** of `_events` for every filter. Only `count_by_type()` uses `_by_type`.

Additionally:
- `_prune_index()` uses `is` (identity) comparison — fragile, only removes first element
- `by_tag` index is **never pruned** — not in the loop tuple
- TTL (`EngineeringEvent.ttl_secs`, `expired`) defined but **never enforced** in query or delivery
- Dead-letter queue (`EventRouter._dead_letter`) written but **never drained, retried, or inspected**

### 1.3 Dual Event Persistence

Every `kernel.emit()` stores to **both** `EventStore._events` (in-memory) AND SQLite `events` table. But `query_events()` only reads from the in-memory store — SQLite events are never queried in production.

### 1.4 StorageEngine — 8 Query Methods Never Called in Production

`query_agents()`, `query_agent_tasks()`, `query_messages()`, `query_task_nodes()`, `query_conversations()`, `query_audit()`, `query_metrics()`, `count_audit()`, `purge_old_events()`, `clear_all()` — all only tested, never used in production.

### 1.5 Three Separate DI/Service Systems

| System | File | Purpose | Production Usage |
|--------|------|---------|-----------------|
| **ServiceProvider** | di/container.py | Interface-based DI container | Registration-only — `get()` never called in production |
| **FabricKernel registry** | fabric/kernel.py:174-198 | Fabric service singleton + lifecycle | Active — `register_service()` used by all subsystems |
| **DiKernel** | kernel/di_kernel.py | Legacy DI with tag-based discovery | Legacy — still present, not integrated |

### 1.6 Kernel State — DEGRADED Never Used

`KernelState` has 4 values (BOOTING, ACTIVE, DEGRADED, SHUTDOWN) but `DEGRADED` is never set. `KernelStats.messages_dropped` is declared but never populated.

### 1.7 Exception Hierarchy — 7 of 10 Exceptions Never Raised

`ValidationError`, `CapabilityError`, `GraphError`, `MetadataError`, `IndexerError`, `ConfigurationError`, `ContractError` — all dead code. `RuntimeError` (genesis version at core/exceptions.py:42) **shadows Python's built-in**.

---

## 2. Desktop UI

### 2.1 Screen Inventory (11 screens)

| Screen | screen_id | Lines | Data Sources | Subscriptions | Unique Features |
|--------|-----------|-------|-------------|--------------|-----------------|
| FabricInspectorScreen | inspector | 125 (37-161) | event_store, query_events, stats, metrics, contexts, scheduler | EventRouter + 30s poll | TrafficLight, 3 views (events/metrics/sessions) |
| GenesisHome | home | 92 (162-253) | 6 child widgets + health | EventRouter + 30s poll | AttentionWidget, greeting with uptime |
| AgentCollaborationScreen | agents | 156 (254-409) | agent_runtime, task_graph, conversation_engine | EventRouter + 30s poll | Agent hierarchy graph, 3 views |
| EngineeringMemoryExplorer | memory | 193 (448-640) | query_events, audit, conversation_engine, task_graph, Reports/ | EventRouter + 30s poll | **6 views** (most), nav + detail |
| RepositoryScreen | repository | 129 (642-770) | registry, health, stats, CE, file system | **None** (poll-only) | File tree, architecture, health |
| EngineeringTimelineScreen | timeline | 136 (771-906) | query_events, audit, conversation_engine, task_graph | EventRouter + 30s poll | Flat log, filter input |
| KnowledgeGraphScreen | graph | 178 (907-1084) | registry, agent_runtime, task_graph, conversation_engine | EventRouter + 30s poll | **Tree-based entity browser** (Cycle 016) |
| AIOrchestrationCenter | ai | 98 (1085-1182) | health, provider registry, router | EventRouter + 30s poll | Provider ecosystem display |
| ContinuousEngineeringScreen | ce | 105 (1183-1287) | _continuous_engineering, watch module | EventRouter + 30s poll | Start/stop watchers, watch mode |
| ReportsScreen | reports | 74 (1288-1361) | File system (Reports/) | **None** (poll-only) | File content reading |
| SettingsScreen | settings | 55 (1362-1416) | stats, health, registry, storage | **None, no poll** | 4 DataPanels (read-only!) |

### 2.2 Critical Overlap: MemoryExplorer ≈ TimelineScreen (80% Identical)

`EngineeringMemoryExplorer` and `EngineeringTimelineScreen` share identical event/audit/conversations/tasks rendering code (compare screens.py:502-569 vs 812-874). Both have `/` filter, RichLog display, 30s polling, EventRouter subscription. MemoryExplorer adds a nav ListView and 2 extra views (reports, decisions). TimelineScreen is a flat log without navigation.

**Recommendation**: Merge into a single canonical screen.

### 2.3 3 Orphaned Widgets (Never Mounted)

| Widget | File:Line | Lines | Purpose |
|--------|-----------|-------|---------|
| `ActivityBar` | widgets.py:191-219 | 28 | Left sidebar with 11 navigation buttons |
| `ContextSidebar` | widgets.py:222-235 | 13 | Right sidebar for context content |
| `MetricsTimeline` | widgets.py:450-483 | 33 | Events/s metrics timeline |

### 2.4 5 Dead CSS Selectors

`#kg-entity-list`, `#agent-list`, `#task-summary`, `#mem-legend`, `#repo-legend` — styled but no widget has these IDs.

### 2.5 5 Redundant Palette Commands

Commands `kernel_stats`, `emit_event`, `inspector_metrics`, `inspector_sessions`, `tasks` all navigate to the **same** Inspector screen. False affordances.

### 2.6 Duplicated CE Lifecycle Code

`CommandPalette._start_ce()` (palette.py:116-127) and `ContinuousEngineeringScreen.action_start_watchers()` (screens.py:1249-1263) are copy-paste identical. Same for stop logic.

### 2.7 Screen Cache Is Broken

`_screen_cache` stores instances but `navigate_to()` always creates a fresh one. The cache is **never read from**. Scroll position, filter text, and selections are always lost on navigation.

### 2.8 Bugs Found

1. **Missing `defaultdict` import** (screens.py:317) — `AgentCollaborationScreen._refresh_agents()` will raise `NameError`
2. **`_debounce_timer` unused** (palette.py:169) — SearchEverywhere fires on every keystroke with no debounce
3. **`action_go_events` unbound** (app.py:273) — defined but no keyboard binding
4. **Advertised shortcuts don't work** — palette shows `ctrl+h`, `ctrl+shift+f`, etc. but actual bindings are single-letter keys

### 2.9 CSS Consolidation Opportunities

12+ repeated patterns for title bars, content panels, status bars across 11 screens. `genesis/ui/tokens.css` (183 lines of design tokens) is **completely unused** by the desktop.

---

## 3. Server & API

### 3.1 All 21 Endpoints Have Zero Production Consumers

Every FastAPI route works (test-verified) but **no code in the repository makes an HTTP request to the server**. The desktop accesses `FabricKernel.instance()` in-process. The server is a facade with no consumers.

### 3.2 WebSocket Queue Never Drained

`_ws_queue` (server.py:39-46) receives events via `put_nowait` but there is **no background task draining it**. Events pushed to the queue are silently dropped. No heartbeat, no timeout cleanup for stale clients.

### 3.3 Auth Disabled by Default

Auth is `require_auth=False` by default. When enabled, WebSocket has **no auth** at all (no token check on WS upgrade). SecurityManager uses SHA256-based tokens, not proper JWT.

### 3.4 Legacy APIRouter (36 routes) Still Exists

`genesis/api/router.py` has 36 hand-defined routes with manual parameterized matching — completely separate from the FastAPI server. Used only by CLI `genesis info` command.

### 3.5 Two Separate Security Systems

| System | Used By | Status |
|--------|---------|--------|
| `genesis/kernel/security_manager.py` | `server.py` (JWT token issue/revoke/status) | Disconnected — no production callers |
| `genesis/security/validator.py` | **Nothing** — different EventBus/MemoryStore | Dead — `validate()` always returns `"passed": True` |

---

## 4. AI Platform

### 4.1 Expected Files That Do NOT Exist

The following files were expected (based on architecture discussions) but do not exist on disk:
- `genesis/ai/prompts.py` — prompt template system
- `genesis/ai/rate_limiter.py`
- `genesis/ai/context_manager.py`
- `genesis/ai/fallback_handler.py`
- `genesis/ai/response_optimizer.py`
- `genesis/ai/stream_handler.py`

### 4.2 Actual AI Files (Only 5)

| File | Lines | Purpose |
|------|-------|---------|
| `genesis/ai/__init__.py` | 173 | Base types, abstract provider, capability enums |
| `genesis/ai/registry.py` | 88 | ProviderRegistry (class-level) |
| `genesis/ai/router.py` | 140 | AIRouter (capability-based scoring) |
| `genesis/ai/providers/nvidia.py` | 225 | NvidiaNIMProvider |
| `genesis/ai/providers/ollama.py` | 164 | OllamaProvider |
| `genesis/ai/providers/openai_compat.py` | 204 | OpenAICompatibleProvider |

### 4.3 Providers Are NEVER Auto-Registered

There is no startup code that instantiates and registers any provider. `ProviderRegistry` starts empty. `AgentExecutionEngine` calls `ProviderRegistry.list_providers()` which always returns `[]` unless someone manually registers providers.

### 4.4 Prompt System Lives in fabric/execution.py

The 18 role prompts (Chief Engineer → Release Engineer) are hardcoded in `fabric/execution.py:30-132` as a dict — completely disconnected from the AI layer.

### 4.5 Router Fallback Is Never Used

`AIRouter.routing_decision()` builds a `fallback_chain` but `chat()`/`stream_chat()` never falls back — if the first provider fails, the error propagates immediately.

### 4.6 Two Overlapping Routing Layers

`AIRouter` (capability-based scoring) and `AgentExecutionEngine.execute()` (fabric/execution.py:166-237) both do provider routing with overlapping logic. When `provider_id` + `model` is specified, `AgentExecutionEngine` bypasses `AIRouter` entirely.

### 4.7 ProviderRegistry.summarize() Returns Malformed Dict

Desktop code at `screens.py:1132` accesses `summary.get("available", [])` but this key is **never populated** — only `"providers"` exists.

### 4.8 Streaming Is Inefficient

All 3 providers read streaming responses **character-by-character** (`resp.read(1)` at openai_compat.py:103, nvidia.py:101, ollama.py:99).

---

## 5. Brain & Cognitive Architecture

### 5.1 Entire Cognitive Architecture (2,340 Lines) Never Used in Production

The full cognitive architecture in `brain/cognition/` (10 files, 10 subsystems) is **only exercised in tests** (`tests/test_cognition.py`):

| Subsystem | File | Lines | Production Usage |
|-----------|------|-------|-----------------|
| BeliefSystem | belief.py | 328 | **NONE** |
| GoalHierarchy | goals.py | 289 | **NONE** |
| ReasoningEngine | reasoning.py | 261 | **NONE** |
| WorkingMemory | memory.py | 165 | **NONE** |
| EpisodicMemory | memory.py | 272 | **NONE** |
| AttentionMechanism | attention.py | 156 | **NONE** |
| ReflectionEngine | reflection.py | 190 | **NONE** |
| StrategyEngine | strategy.py | 220 | **NONE** |
| DecisionEngine | decision.py | 225 | **NONE** |
| Orchestrator | orchestration.py | 323 | **NONE** |

`CognitiveArchitecture` is instantiated by `EngineeringBrain.__init__()` (brain/__init__.py:91) but **no production caller ever accesses `brain.cognition`** or calls any cognitive method.

### 5.2 brain_v4.py — Deprecated But Still Instantiated

`brain_v4.py` (738 lines) has its own duplicate copies of: Goal hierarchy, Belief revision, Causal inference, Attention, Reflection, Executive memory. It is imported in `platform.py:67` with a deprecation warning but **still instantiated at `platform.py:375`** — `self.brain_v4 = EngineeringBrainV4()`.

### 5.3 EmbeddingStore — Storage Only, No Computation

`brain/embeddings.py` (110 lines) defines 5 embedding kinds (semantic, knowledge, structural, behavioral, evolution) but the docstring explicitly says: **"Current: storage only. Actual embedding computation will be added in later phases."** No vector similarity search, no ML model integration.

### 5.4 Event Integration Has 2 Stub Handlers

`brain/integration.py` registers 7 event subscriptions. Two are stubs:
- `knowledge.graph.loaded` handler (line 137) — only increments a counter
- `memory.stored` handler (line 141) — only increments a counter

### 5.5 91 Entity Types Defined But Many Unused

`BrainEntityType` enum (brain/entity.py:20-91) defines 91 entity types. The sync adapters (brain/sync.py) only map 6 source systems — the remaining 85 types have no production path to instantiation.

---

## 6. Graph Systems — Three Competing Implementations

| System | File | Type System | Production Use |
|--------|------|------------|----------------|
| **GraphV2 UnifiedGraph** | graph_v2/core.py | GraphNode/GraphEdge, 12 layers | Instantiated at platform.py:428 (empty, no data) |
| **MetaModel UnifiedGraph** | metamodel/graph.py | UnifiedEntity/EntityRelation | Used by MetaModel system |
| **PersistentGraphDB** (via BrainGraph) | brain/graph.py, graphdb/ | BrainEntity with relationships | Used by EngineeringBrain — **canonical graph for production** |

### 6.1 GraphV2 — 1,765 Lines, Barely Used

- Adapter system (480 lines), analytics (131 lines), compression (73 lines), federation (104 lines), index (65 lines), partition (76 lines), versioning (132 lines), traversal (441 lines) — all **only tested, never used in production**
- The `UnifiedGraph` instance at platform.py:428 is created with no layers and no data

### 6.2 Name Collision

Two different classes are both called `UnifiedGraph` — one in `graph_v2/core.py` (layer-based) and one in `metamodel/graph.py` (entity-relation). This is dangerous.

---

## 7. Plugin Systems — Three Different Owners

| System | File | Owner | Purpose | Hook System |
|--------|------|-------|---------|-------------|
| **PluginManager** | plugin/manager.py | VenusPlatform (platform.py:234) | External plugins from YAML/JSON manifests | Yes (hook_type + handler) |
| **ModulePluginRegistry** | plugin/registry.py | OmegaLoop (omega_loop.py:143) | Internal engine factories | No |
| **PluginLoader** | kernel/plugin_loader.py | UniversalKernel (kernel/kernel.py:45) | Kernel-level module loading | Yes (hook_name + handler) |

The three systems have **minimal functional overlap** but confusing naming. `PluginManager` is the canonical extensibility system (sandbox, dependency resolution, hot reload). `PluginLoader`'s hook system partially duplicates `PluginManager`'s but they are never used together.

PluginManager is **not connected to the desktop** — there is no plugin management UI.

---

## 8. Tests & Infrastructure

### 8.1 CRITICAL: Conftest Discovery Bug

The conftest.py at `tests/conftest.py` (22 shared fixtures, autouse singleton reset, custom markers) is **never loaded by pytest**. Test files live under `genesis/tests/` — the ancestor chain is `genesis/` → project root, but the conftest is in the sibling `tests/` directory.

**Impact**: Entire Cycle 015 M108 Test Infrastructure Modernization is dead code. Every test continues to use the old `FabricKernel._instance = None` pattern manually.

### 8.2 Zero Desktop/Auth/WS/Plugin Tests

Despite custom markers being defined (`desktop`, `integration`, `slow`, `ai`, `auth`, `plugin`, `ws`, `storage`), **zero tests use them**. No Textual pilot tests exist. No auth tests. No WebSocket tests. No plugin tests.

### 8.3 ~900 Tests on Deprecated Code

A significant portion of the 93 test files test `UniversalKernel`, `DIKernel`, and other legacy systems instead of the canonical `FabricKernel`.

### 8.4 146 Reports Across 16 Cycles

| Cycle | Reports | Lines (est.) | Theme |
|-------|---------|-------------|-------|
| 001-009 | Minimal | — | Foundational/early exploration |
| 010 | 4 | ~500 | Executor, Architecture, Storage |
| 011 | 6 | ~800 | Workspace Architecture, Design Decisions |
| 012 | 3 | ~400 | Architecture Delta, UX, Roadmap |
| 013 | 3 | ~400 | Architecture Delta, Future Roadmap |
| 014 | 17 | ~3,400 | **First comprehensive audit** |
| 015 | 25 | ~3,600 | **Consolidation cycle** |
| 016 | 29 (1 merged) | ~4,500 | **Project Aurora — product transformation** |

---

## 9. Capability Evolution Matrix

This matrix traces the evolution of key capabilities across cycles, showing when components were created, consolidated, or became obsolete.

### 9.1 Event System Evolution

| Cycle | Event | State |
|-------|-------|-------|
| 001 | Basic EventBus | Created (now legacy) |
| 005 | EventRouter with subscriptions | Created |
| 010 | EventStore with bounded queue + indexes | Created |
| 013 | Event-driven UI migration (17 timers → subscriptions) | Consolidation |
| 014 | EventStore TTL/expiry defined | Added but never enforced |
| 015 | EventStore indexes built but unused by query | Status quo |
| 017 | **M122-M127**: Knowledge Engine, Timeline, Knowledge Graph | Planned |

### 9.2 Kernel Evolution

| Cycle | Kernel | State |
|-------|--------|-------|
| 001 | UniversalKernel | Created (now legacy — still tested, ~900 tests) |
| 005 | DiKernel + ServiceRegistry | Created (now legacy) |
| 010 | FabricKernel singleton | Created — **canonical kernel** |
| 013 | Lazy-loaded subsystems (agent_runtime, task_graph, etc.) | Created |
| 014 | Hooks dead code identified | Identified but not removed |
| 015 | WIP dead code removal from __main__.py | Partial |
| 017 | **M121**: Engineering Object Model across all kernel subsystems | Planned |

### 9.3 Desktop Evolution

| Cycle | Feature | State |
|-------|---------|-------|
| 010 | Initial TUI screens (5 screens) | Created |
| 011 | Command Palette, Search Everywhere | Created |
| 012 | Expanded screens (9 total) | Created |
| 013 | Event-driven UI, screen navigation | Improved |
| 014 | Color map consolidation, orphan removal | Partial |
| 015 | Dead code removal, import cleaning | Partial |
| 016 | **Genesis Home redesign**, Unified Workspace, Engineering Spotlight, KnowledgeGraph→Tree | **Major redesign** |
| 017 | **M121-M132**: All screens become Engineering Object consumers | Planned |

### 9.4 AI Platform Evolution

| Cycle | Capability | State |
|-------|-----------|-------|
| 010 | Basic AI provider interface | Created |
| 011 | ProviderRegistry, AIRouter | Created |
| 012 | NvidiaNIM + Ollama providers | Created |
| 013 | OpenAICompatible provider | Created |
| 014 | Provider auto-registration missing, router fallback unused | Identified |
| 015 | Prompt system moved to fabric/execution.py, never in ai/ | WIP |
| 017 | **M123-M124**: Reasoning Engine, Engineering Copilot | Planned |

### 9.5 Graph System Evolution

| Cycle | Graph | State |
|-------|-------|-------|
| 001 | KnowledgeGraphEngine | Created |
| 005 | HypergraphKnowledgeCore | Created |
| 008 | PersistentGraphDB | Created |
| 010 | BrainGraph (wraps PersistentGraphDB) | Created — **canonical graph** |
| 012 | GraphV2 layer-based system (1,765 lines) | Created — **unused in production** |
| 014 | KnowledgeGraphScreen with graph visualization | Attempted, failed (no graph shown) |
| 016 | KnowledgeGraphScreen → Tree widget entity browser | **Working but basic** |
| 017 | **M121, M127**: Engineering Object Model + Live Knowledge Graph | Planned |

### 9.6 Server Evolution

| Cycle | Server | State |
|-------|--------|-------|
| 005 | GenesisAPI with FastAPI (21 endpoints) | Created |
| 010 | WebSocket event broadcast | Added |
| 013 | WS async safety (queue + run_coroutine_threadsafe) | Fixed |
| 014 | WS queue never drained, auth not wired | Identified |
| 016 | WS security design (not implemented) | Designed only |
| 017 | **M131**: Genesis Public API — stable, versioned, documented | Planned |

### 9.7 Brain/Cognition Evolution

| Cycle | Brain | State |
|-------|-------|-------|
| 010 | EngineeringBrain with entity CRUD | Created — **canonical brain** |
| 010 | brain_v4.py (deprecated twin) | Created — **still instantiated** |
| 012 | brain_v4 expansion (738 lines) | Expanded |
| 012 | Full cognitive architecture (10 subsystems, 2,340 lines) | Created — **NEVER USED** |
| 014 | EmbeddingStore — storage only, no computation | Identified |
| 014 | Cognitive architecture unused in production | Identified |
| 017 | **M121-M132**: Engineering Intelligence Platform | Planned to finally wire cognition |

### 9.8 Continuous Engineering Evolution

| Cycle | CE | State |
|-------|-----|-------|
| 010 | Basic watchers | Created |
| 012 | ContinuousEngineering class | Created |
| 013 | CE lifecycle + desktop integration | Added |
| 016 | CE screen, watcher ecosystem | Improved |
| 017 | **M129**: Autonomous Engineering Review | Planned |

### 9.9 Plugin System Evolution

| Cycle | Plugin | State |
|-------|--------|-------|
| 001 | PluginLoader (kernel-level) | Created |
| 005 | PluginManager (external plugins) | Created |
| 010 | ModulePluginRegistry (internal engines) | Created |
| 014 | Three plugin systems identified | Identified |
| 017 | PluginManager → designated canonical, but not connected to desktop | Status quo |

### 9.10 Memory System Evolution

| Cycle | Memory | State |
|-------|--------|-------|
| 010 | UniversalMemorySystem | Created — **canonical memory** |
| 012 | Memory Explorer + Timeline screens | Created (80% duplicate) |
| 014 | Memory/Timeline consolidation pending | Identified |
| 017 | **M121, M122, M125**: Engineering Object → Knowledge Engine → Timeline | Planned |

---

## 10. Consolidated Technical Debt Inventory

### 10.1 Production-Unused Code (~7,000+ lines)

| System | Lines | Component | Action |
|--------|-------|-----------|--------|
| brain/cognition/ | 2,340 | Full cognitive architecture (10 subsystems) | Wire into production or document as disconnected |
| graph_v2/ features | 1,502 | adapter, analytics, compression, federation, index, partition, versioning, traversal | Wire into production or deprecate |
| brain_v4.py | 738 | Deprecated twin of EngineeringBrain | Remove instantiation from platform.py |
| desktop/widgets.py | 74 | ActivityBar, ContextSidebar, MetricsTimeline (3 orphaned widgets) | Remove or wire into screens |
| server endpoints | ~500 | 21 endpoints with no consumers | Either connect to desktop or remove |
| EventStore indexes | ~100 | 5 indexes built but only 1 queried | Wire into query() or remove index maintenance |
| Kernel hooks | ~30 | _hooks, on(), _emit() (dead pub-sub system) | Remove dead code |
| 7 unused exceptions | ~30 | ValidationError, CapabilityError, etc. | Remove or wire into error handling |
| unbound action_go_events | ~5 | Method defined with no keyboard binding | Remove or bind |
| Screen cache | ~10 | Cache populated but never read | Fix cache logic or remove |
| SecurityValidator | ~62 | Always returns passed, disconnected | Remove or wire to SecurityManager |

### 10.2 Overlapping/Duplicate Systems

| Systems | Nature | Resolution |
|---------|--------|------------|
| Hooks / EventRouter / MessageBus (3 pub-sub) | 1 dead, 2 live with overlap | Remove hooks, merge EventRouter + MessageBus |
| ServiceProvider / FabricKernel / DiKernel (3 DI) | 3 systems with overlapping concerns | Unify into FabricKernel as canonical, remove others |
| SecurityManager / SecurityValidator (2 security) | 2 systems, both disconnected | Consolidate into SecurityManager |
| GraphV2 / MetaModelGraph / BrainGraph (3 graph) | 3 competing UnifiedGraph implementations | Designate canonical, migrate others |
| PluginManager / PluginLoader / ModulePluginRegistry (3 plugin) | 3 owners, 2 with hook systems | PluginManager is canonical — connect to desktop |
| FastAPI / APIRouter (2 API) | 2 routing systems, 1 with no consumers | FastAPI is canonical — remove APIRouter |
| MemoryExplorer / TimelineScreen (2 screens) | 80% code duplication | Merge into canonical screen |
| CE lifecycle (2 locations) | Duplicated in palette + screens | Extract to shared helper |
| 5 redundant palette commands | All navigate to inspector | Remove or specialize |

### 10.3 Infrastructure Bugs

| Bug | Impact | Fix |
|-----|--------|-----|
| conftest.py in wrong directory | 22 fixtures never loaded, M108 dead | Move to genesis/tests/ |
| screen cache never read | Always fresh screens, lost scroll/filter | Fix navigate_to() cache hit |
| WS queue never drained | Events silently dropped | Add background consumer task |
| Missing defaultdict import | AgentCollaborationScreen crashes | Add import |
| _debounce_timer unused | No search debounce | Wire timer or remove |

### 10.4 Unimplemented Features

| Feature | Required By | Status |
|---------|-------------|--------|
| Provider auto-registration | M124 Copilot | Missing |
| AIRouter fallback chaining | M123 Reasoning | Missing |
| TTL enforcement | M125 Timeline | Missing |
| Embedding computation | M122 Knowledge | Missing (storage only) |
| Auth on WebSocket | M131 API | Missing |
| Desktop unit tests | All | Missing |
| Desktop plugin management | M132 AgentOS | Missing |
| Task graph UI | M128 Projects | Missing |
| EventStore SQLite reads | M125 Timeline | Missing (dual-write but never read) |

---

## 11. Pre-Phase 0 Unknown Capabilities (Hidden Features Found)

The archaeology discovered several capabilities that were not documented or known before this reverse engineering:

1. **91 BrainEntityTypes** — a rich domain model that no production code uses
2. **GraphV2 full analytics/compression/federation/indexing** — a complete graph processing pipeline, test-verified, never wired
3. **6 sync adapters** (brain/sync.py) that can convert between BrainEntity and multiple graph formats
4. **5 embedding kinds** already defined in storage (just no computation)
4. **AgentScheduler** with deferred/recurring task scheduling (fabric/agents.py)
5. **TaskGraphBuilder** with hierarchical task creation (fabric/tasks.py)
6. **22 role prompts** already defined for agent roles (fabric/execution.py)
7. **`ProviderCapability.STRUCTURED_OUTPUT`** and **`REASONING`** already in the enum
8. **Full `SchemaManager`** with migration infrastructure (storage.py)
9. **`KernelState.DEGRADED`** enum value ready for health degradation tracking
10. **`KernelStats.messages_dropped`** field ready for QoS monitoring
11. **`EventPriority.DEBUG/LOW`** and **`EventSeverity.TRACE/DEBUG`** ready for richer event semantics
12. **`EngineeringEvent.causation_id`**, **`repository_id`**, **`confidence`**, **`ttl_secs`** — all defined, never populated

These hidden capabilities represent opportunities for M121-M132 — the schema and type systems are ready; the wiring is what's missing.

---

## 12. Phase 0 Findings → Mission Mapping

| Finding | Directly Enables | Mission |
|---------|-----------------|---------|
| 91 BrainEntityTypes, sync adapters | Rich Engineering Object model already partially defined | M121 |
| Event schema with causation_id, repository_id, confidence, TTL | Engineering Object universal ID and timeline ready | M121, M125 |
| 6 sync adapters, 5 embedding kinds | Knowledge Engine already has storage backbone | M122 |
| Event+audit+conversation rendering code duplicated 3× | Need unified viewer that Knowledge Engine provides | M122 |
| Cognitive architecture unused, ReasoningEngine exists but disconnected | Can wire evidence-based reasoning from existing code | M123 |
| 22 role prompts, AgentExecutionEngine, AIRouter | Copilot has execution backbone, needs context awareness | M124 |
| Event schema already has timestamps, causation chain | One unified timeline already partially defined | M125 |
| Dead-letter queue exists but never drained | Engineering Decisions can include retry/rollback semantics | M126 |
| GraphV2 analytics, traversal, federation ready | Live Knowledge Graph processing already built | M127 |
| TaskGraphBuilder, Summary with critical path | Project health/velocity already measurable | M128 |
| ContinuousEngineering class exists | Autonomous Review can extend existing watcher system | M129 |
| Brain integration stubs (2 of 7 handlers) | Continuous Learning needs to wire these stubs | M130 |
| FastAPI 21 endpoints ready, no consumers | Public API can stabilize existing endpoints | M131 |
| PluginManager canonical but not desktop-connected | AgentOS needs PluginManager → desktop connection | M132 |

---

## Appendix A: Source Lines of Code by Subsystem

| Subsystem | Files | Lines | Production-Tested? |
|-----------|-------|-------|-------------------|
| genesis/brain/cognition/ | 10 | 2,340 | No (test-only) |
| genesis/desktop/ | 4 | 2,576 | No (0 tests) |
| genesis/fabric/ | 16 | ~2,500 | Partial (events/agents/kernel only) |
| genesis/graph_v2/ | 12 | 1,765 | No (test-only features) |
| genesis/brain/ (core) | 6 | ~1,200 | Yes (entity CRUD, graph, sync) |
| genesis/ai/ | 6 | ~1,000 | Partial |
| genesis/plugin/ | 4 | ~500 | Yes (PluginManager via platform) |
| genesis/server.py | 1 | 350 | No (zero consumers) |
| brain_v4.py | 1 | 738 | No (deprecated but instantiated) |
| genesis/kernel/ | 5 | ~400 | Legacy (tested but deprecated) |

## Appendix B: File:Line Reference Index

| Finding | File | Line(s) |
|---------|------|---------|
| Hooks dead | fabric/kernel.py | 85, 212-220 |
| _emit() never called | fabric/kernel.py | 215 |
| EventStore indexes unused by query | fabric/events.py | 94-155 |
| TTL never enforced | fabric/events.py | 59-61, 51 |
| Dead letter never drained | fabric/events.py | 199, 222-223 |
| DEGRADED never set | fabric/kernel.py | 32 |
| messages_dropped never populated | fabric/kernel.py | 40, 318-335 |
| Dual event storage (memory + SQLite) | fabric/kernel.py | 234-238 |
| 8 storage query methods never called | fabric/storage.py | 388-952 |
| 7 exception types never raised | core/exceptions.py | 14-51 |
| RuntimeError shadows built-in | core/exceptions.py | 42 |
| ServiceProvider.get() never called | di/container.py | 117 |
| 3 pub-sub systems | fabric/kernel.py | 76-77, 85 |
| 3 DI systems | di/container.py, fabric/kernel.py, kernel/di_kernel.py | various |
| 3 graph systems | graph_v2/core.py, metamodel/graph.py, brain/graph.py | various |
| 3 plugin systems | plugin/manager.py, plugin/registry.py, kernel/plugin_loader.py | various |
| 2 API routing systems | server.py, api/router.py | various |
| 2 security systems | kernel/security_manager.py, security/validator.py | various |
| MemoryExplorer vs TimelineScreen duplicate | desktop/screens.py | 491-601 vs 806-874 |
| Missing defaultdict import | desktop/screens.py | 317 |
| ActivityBar orphaned | desktop/widgets.py | 191-219 |
| ContextSidebar orphaned | desktop/widgets.py | 222-235 |
| MetricsTimeline orphaned | desktop/widgets.py | 450-483 |
| 5 dead CSS selectors | desktop/app.py | 86, 139, 157-158, 178 |
| action_go_events unbound | desktop/app.py | 273 |
| _debounce_timer unused | desktop/palette.py | 169 |
| Screen cache never read | desktop/app.py | 243 |
| Conftest in wrong directory | tests/conftest.py vs genesis/tests/ | — |
| Zero desktop/auth/WS/plugin tests | tests/ | — |
| Cognitive architecture never used | brain/cognition/ (10 files) | all |
| brain_v4 deprecated but instantiated | brain_v4.py | 14-18, platform.py:375 |
| Embedding storage only | brain/embeddings.py | 9-12 |
| 2 stub event handlers | brain/integration.py | 137-143 |
| GraphV2 features untested in production | graph_v2/adapter.py, analytics.py, etc. | all |
| 21 server endpoints no consumers | server.py | 105-347 |
| WS queue never drained | server.py | 39-46, 67 |
| Providers never auto-registered | ai/__init__.py, ai/registry.py | — |
| Router fallback unused | ai/router.py | 121-139 |
| summarize() missing "available" key | ai/registry.py | 76-88 |
| SecurityValidator always passes | security/validator.py | 40-59 |
