# CYCLE 007 — REPORT 02: UNIVERSAL EVENT SYSTEM

## Structured, Replayable, Queryable Engineering Events

⸻

## VISION

Every important engineering action in Genesis emits a structured event. Events are
not transient messages — they are permanent records with identity, lineage, and
engineering context. Events can be queried, replayed, and analyzed.

⸻

## PROBLEM STATEMENT

Before Cycle 007, Genesis had no standard event format. Different subsystems emitted
different data structures through different channels. There was no way to:
- Ask "what happened in the last hour?"
- Trace the causal chain of an engineering action
- Replay events to reconstruct system state
- Query events by type, origin, or tag
- Correlate events across subsystems

⸻

## EVENT STRUCTURE

Every `EngineeringEvent` contains:

| Field | Type | Description |
|-------|------|-------------|
| `id` | str | Unique identity (ven:evt:{random}) |
| `type` | str | Event type (e.g., "repository.indexed") |
| `timestamp` | float | When the event occurred |
| `origin` | str | Subsystem that created the event |
| `correlation_id` | str | Links related events in a flow |
| `causation_id` | str | ID of the event that caused this one |
| `session_id` | str | Engineering session |
| `repository_id` | str | Target repository |
| `priority` | EventPriority | DEBUG (-1) to CRITICAL (3) |
| `severity` | EventSeverity | TRACE to CRITICAL |
| `payload` | dict | Event-specific data |
| `metadata` | dict | Additional context |
| `tags` | list[str] | Categorical labels |
| `confidence` | float | 0.0 to 1.0 |
| `ttl_secs` | float | Time-to-live (default 24h) |

⸻

## BUILT-IN EVENT TYPES

The Fabric emits these event types automatically:

```
kernel.booted              service.registered
service.unregistered       message.sent
session.begun              session.ended
agent.spawned              agent.terminated
agent.task.assigned        agent.task.completed
agent.task.failed          agent.message.sent
agent.scheduled            agent.scheduled.cancelled
task_graph.node.added      task_graph.node.status
conversation.created       conversation.message.added
```

Subsystems emit their own event types using the same `FabricKernel.emit()` API.

⸻

## EVENT FLOW

```
1. Any code calls FabricKernel.emit(type, payload, ...)
2. FabricKernel creates EngineeringEvent with auto-generated id + timestamp
3. EventRouter receives the event
4. EventStore appends to ring buffer (queryable storage)
5. All matching subscribers receive the event synchronously
6. Failed deliveries go to dead letter queue
7. Metrics recorded, audit logged
```

⸻

## EVENT STORE QUERYING

```python
# All events of a type
kernel.query_events(event_type="agent.task.completed")

# Events with tags
kernel.query_events(tags=["critical", "security"])

# Events in a time range
kernel.query_events(since=time.time() - 3600, until=time.time())

# Events by origin
kernel.query_events(origin="agent_runtime")

# Combined
kernel.query_events(event_type="agent.*", tags=["migration"], limit=50)
```

⸻

## TRADEOFFS

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Storage | In-memory ring buffer | No persistence dependency, fast, bounded |
| Delivery | Synchronous | Deterministic, easier debugging |
| Event format | Dataclass | Self-documenting, type-safe |
| Type matching | Exact + wildcard | Simple, sufficient for current needs |
| Query | Linear scan on filtered subset | <50K events, fast enough |
