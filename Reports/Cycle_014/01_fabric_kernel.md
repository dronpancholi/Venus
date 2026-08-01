# Phase 0 Delta: FabricKernel

**File:** `genesis/fabric/kernel.py` — 354 lines  
**Maturity:** 0.82  
**Tests:** 159 (via `test_kernel.py`)

## Architecture

`FabricKernel` is a **singleton** central communications hub. Design principle: *"All communication flows through the Fabric."*

**State machine:** `BOOTING` → `RUNNING` → `DEGRADED` → `SHUTDOWN`

**Internal components created at `__init__`:**
- `MessageBus` — topic-based pub/sub
- `EventRouter` — structured `EngineeringEvent` routing
- `ServiceRegistry` — service discovery and health
- `DistributedScheduler` — recurring task scheduling
- `PolicyEngine` — access/execution policy
- `FabricMetrics` — metric collection
- `AuditLog` — immutable audit trail
- `Context dict` — active session contexts
- `Hook dict` — simple callback system
- `StorageEngine` — optional SQLite persistence

## Boot Sequence

```
FabricKernel.boot()
  1. State → RUNNING
  2. MessageBus.start()
  3. Scheduler.start()
  4. StorageEngine.connect()
  5. Lazy-import: AgentRuntime, TaskGraph, AgentExecutionEngine, TaskExecutor
  6. TaskExecutor.start() (2s poll loop)
  7. Emit "kernel.booted"
```

## Key Methods

| Method | Signature | Purpose |
|--------|-----------|---------|
| `instance()` | `(storage_path, enable_persistence)` | Singleton accessor |
| `boot()` | `() -> None` | Start all subsystems |
| `emit()` | `(event_type, payload, ...) -> EngineeringEvent` | Route structured event |
| `on_event()` | `(event_type, handler, filter_fn)` | Subscribe typed handler |
| `query_events()` | `(**kwargs) -> list[EngineeringEvent]` | Query event store |
| `begin_session()` | `(type, metadata) -> Context` | Start tracked session |
| `end_session()` | `(session_id)` | End session |
| `health()` | `() -> ServiceHealth` | Uptime/services/sessions |
| `stats()` | `() -> KernelStats` | Full telemetry |
| `shutdown()` | `() -> None` | Graceful shutdown |

## Findings

1. `boot()` uses `__import__` for lazy loading — breaks static analysis and IDE tooling
2. No error recovery if lazy imports fail mid-boot — kernel enters unknown state
3. `begin_session()` doesn't expire stale sessions — memory leak over time
4. No `get_service()` public method — `registry` attribute is the only access path
5. `storage` can be `None` — every access must check, but callers forget (16+ unsafe accesses)
6. `stats().executor_running` can be stale immediately after boot (async start race)

## Recommendations

1. Replace `__import__` with `importlib.import_module()` for proper error context
2. Add session TTL/expiry with periodic cleanup
3. Add `get_service(instance_id)` convenience method
4. Wrap storage access in a safe helper that returns `"[not connected]"` instead of crashing
5. Make `TaskExecutor.start()` synchronous by polling until thread is alive
6. Add `KernelState.DEGRADED` recovery path with partial restart capability
