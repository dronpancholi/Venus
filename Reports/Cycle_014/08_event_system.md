# Phase 0 Delta: Event System

**File:** `genesis/fabric/events.py` — 254 lines  
**Tests:** Via `test_kernel.py` (EventRouter + EventStore tests)

## Architecture

```
EngineeringEvent (dataclass, 18 fields)
  ├── EventStore (bounded 50K, 6 indexes, FIFO eviction)
  └── EventRouter (type-based pub/sub, dead-letter queue)
        └── FabricKernel.on_event() → screen/widget refresh callbacks
```

## Event Types (24+)

| Type | Emitted By |
|------|-----------|
| `kernel.booted` | FabricKernel.boot() |
| `kernel.shutdown` | FabricKernel.shutdown() |
| `service.registered` | FabricKernel.register_service() |
| `service.unregistered` | FabricKernel.unregister_service() |
| `message.sent` | FabricKernel.send() |
| `session.begun` | FabricKernel.begin_session() |
| `session.ended` | FabricKernel.end_session() |
| `agent.spawned` | AgentRuntime.spawn() |
| `agent.terminated` | AgentRuntime.terminate() |
| `agent.task.assigned` | AgentInstance.assign_task() |
| `agent.task.completed` | AgentInstance.complete_task() |
| `agent.task.failed` | AgentInstance.fail_task() |
| `agent.execution.completed` | AgentExecutionEngine.execute() |
| `agent.execution.failed` | AgentExecutionEngine.execute() |
| `conversation.created` | ConversationEngine.create() |
| `conversation.message.added` | ConversationEngine.add_message() |
| `task_graph.node.added` | TaskGraph.add_node() |
| `task_graph.node.status` | TaskGraph.update_status() |
| `task_executor.started` | TaskExecutor.start() |
| `task_executor.stopped` | TaskExecutor.stop() |
| `task_executor.node.completed` | TaskExecutor._execute_node() |
| `platform.boot.completed` | VenusPlatform.boot() |
| `platform.shutdown` | VenusPlatform.shutdown() |
| `brain.ready` | VenusPlatform.boot() |

## EventStore Indexes

6 indexes for query performance: `_by_type`, `_by_origin`, `_by_tag`, `_by_session`, `_by_repository`. Query supports filtering on: type, origin, session, repository, tags, confidence, time range.

## Non-Fabric Event Systems

- **UniversalKernel EventRouter** (`kernel/event_router.py`, 103 lines) — lightweight, priority-sorted subscribers, source filtering
- **Legacy EventBus** (`events/bus.py`, 97 lines) — simple synchronous pub/sub, used by VenusPlatform boot
- **PlatformV2 EventRouter** (`platform_v2.py`) — service-oriented pub/sub with event history

## Findings

1. **24 event types are not enumerated anywhere** — they're magic strings scattered across the codebase
2. **Three independent event systems** — fabric Events, kernel EventRouter, legacy EventBus — all do the same thing
3. **EventStore has no persistence** — 50K events in-memory only, events lost on restart (SQLite mirror exists in StorageEngine but EventStore itself is RAM-only)
4. **Dead-letter queue is mute** — failed handlers are counted but never surfaced or alerted
5. **No event schema registry** — payload structure for each event type is undocumented
6. **Thread safety concern** — desktop subscriptions run in event router thread, use `call_from_thread()` (synchronous dispatch blocks the router)

## Recommendations

1. Create `EventType` enum or `StrEnum` centralizing all 24+ event types
2. Consolidate: deprecate `events/bus.py` and `kernel/event_router.py` in favor of fabric EventRouter
3. Add periodic event store snapshot to SQLite StorageEngine
4. Surface dead-letter queue in a desktop debug panel
5. Add typed event payload dataclasses (one per event type) for IDE autocompletion
6. Add async dispatch path for non-blocking event delivery
