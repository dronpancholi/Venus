# Cycle 016 — Architecture Audit

## Six-Layer Architecture Validation

The intended architecture has 6 layers with a strict dependency rule:
```
PLUGIN    Layer 5
PLATFORM  Layer 4
INTELLECT Layer 3
DOMAIN    Layer 2
KERNEL    Layer 1
FOUNDATION Layer 0
```

### Dependency Violations Found

| Violation | Source | Target | Layer |
|-----------|--------|--------|-------|
| `screens.py:136` | `kernel._contexts` | FabricKernel private attr | Platform → Kernel |
| `screens.py:394` | `kernel._conversation_engine` | FabricKernel private attr | Platform → Kernel |
| `screens.py:812` | `kernel._conversation_engine` | FabricKernel private attr | Platform → Kernel |
| `widgets.py:443` | `a._outbox, a._inbox` | AgentRuntime private attrs | Widgets → Agent |
| `widgets.py:508` | `kernel._contexts` | FabricKernel private attr | Widgets → Kernel |
| `palette.py:120` | `kernel._continuous_engineering` | FabricKernel private attr | Palette → Kernel |
| `kernel.py:158` | `__import__("genesis.fabric.agents")` | Circular dep risk | Kernel → Domain |
| `server.py:174` | `from genesis.fabric.kernel import FabricKernel` | Import inside handler | Server → Kernel |

### Architectural Concerns

1. **Singleton coupling**: Everything gets FabricKernel via `FabricKernel.instance()`. No DI, no interface injection, no testing seams. Every test that needs a different kernel state must manipulate globals.

2. **Dual pub-sub systems**: The kernel has `on()/_emit()` (string-keyed hooks) AND `on_event()/emit()` (typed EngineeringEvent system). Both are active. The hook system has 0 visibility into failures.

3. **Dual storage systems**: In-memory EventStore (events.py) AND SQLite StorageEngine (storage.py). The API reads from the in-memory store, not SQLite. SQLite `query_events()` is effectively orphaned.

4. **Dual plugin registries**: PluginManager and ModulePluginRegistry both exist. PluginManager is canonical but not connected to desktop discovery.

5. **No clear boundary between Kernel and Domain**: FabricKernel directly lazy-loads AgentRuntime, ConversationEngine, ContinuousEngineering, etc. via `__import__`. These are Domain-layer concerns, not Kernel.

## Consolidation Candidates Not Yet Consolidated

From Cycle 015's 9-area consolidation matrix, only server bugs and test infrastructure were addressed. No actual consolidation was implemented:

| Area | Competing Systems | Canonical | Status |
|------|------------------|-----------|--------|
| Kernels | FabricKernel, UniversalKernel, ServiceKernel, VenusPlatform, PlatformV2, EngineeringOS, LegacyKernel | FabricKernel | Designated only |
| Events | EventRouter, EventBus, LegacyEventDispatcher, EventManager | EventRouter | Designated only |
| Graphs | UnifiedGraph, PersistentGraphDB, KnowledgeGraphEngine, GraphV1, LegacyGraph | UnifiedGraph | Designated only |
| Storage | StorageEngine, SQLiteStore, StorageManager, FileSystemStore | StorageEngine + SQLiteStore | Designated only |
| Execution | fabric/execution.py, execution/engine.py, TaskExecutor, AgentExecutionEngine | fabric/execution.py | Designated only |
| Memory | UniversalMemorySystem, MemoryManager, WorkingMemory, EpisodicMemory | UniversalMemorySystem | Designated only |
| Plugins | PluginManager, kernel/plugin_loader.py, plugin/registry.py | PluginManager | Designated only |
| DI | ServiceProvider, LegacyInjector | ServiceProvider | Designated only |
| Watchers | gen_watcher.py, LegacyWatcher | gen_watcher.py | Designated only |

## Test Coverage Architecture

- 3,274 verified tests, 139/390 modules (35.6%)
- Desktop tests: 0 (no Textual pilot tests)
- Screen tests: 0
- Widget tests: 0
- Palette tests: 0
- Server tests: minimal
- Plugin tests: minimal
- Brain tests: minimal
- conftest.py enables desktop/server tests but they haven't been written

## Security Architecture

- Auth is opt-in (disabled by default)
- Tokens are unsigned SHA256 hashes (no HMAC)
- WebSocket has no auth
- RBAC exists but is never called from API layer
- Policy engine exists but deny policies are not enforced
- No credential validation — any identity string accepted
- All auth state is in-memory — lost on restart

## Architecture Score: 5/10

| Dimension | Score | Key Issues |
|-----------|-------|------------|
| Layer Compliance | 5/10 | 10+ private attr violations, dual systems, no consolidation done |
| Component Cohesion | 6/10 | Good within modules, poor across layer boundaries |
| Testing Architecture | 4/10 | No desktop/server/plugin tests, 35.6% coverage |
| Security Architecture | 3/10 | Unsigned tokens, no WS auth, RBAC unwired, deny not enforced |
| State Management | 4/10 | Everything in-memory, no persistence strategy for cognitive state |
| Extensibility | 5/10 | Plugin system designed but not enforced, no SDK |
