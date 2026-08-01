# CYCLE 007 — REPORT 01: ENGINEERING FABRIC

## Universal Communication Layer for the Engineering Operating System

⸻

## VISION

The Engineering Fabric is the central nervous system of Genesis. Every subsystem,
agent, service, and user interaction flows through it. No subsystem knows another
subsystem directly — they communicate through the Fabric.

This eliminates:
- Point-to-point coupling between subsystems
- Manual coordination logic
- Hidden dependencies
- Scattered communication patterns

⸻

## PROBLEM STATEMENT

Before Cycle 007, Genesis had multiple communication mechanisms:
- `genesis/events/bus.py` — a simple EventBus
- `genesis/fabric/bus.py` — MessageBus with topics
- `genesis/kernel/event_router.py` — Kernel-level event routing
- `genesis/platform_v2.py` — Platform-level EventRouter
- `genesis/di/interfaces.py` — EventBus protocol
- Direct method calls between subsystems

Each had different APIs, different semantics, and no interoperability. Subsystems
that needed to communicate had to know each other's APIs directly.

⸻

## HISTORICAL CONTEXT

Cycle 003-004 focused on building individual subsystems (orchestrator, service kernel,
governance, autonomous engineering). Cycle 005 focused on decomposing the platform
god-object. Cycle 006 added the AI provider layer and MCP. Each cycle added more
subsystems without unifying how they communicate.

By the end of Cycle 006, the cost of point-to-point integration was becoming visible:
- Adding a new consumer required modifying the producer
- Cross-subsystem workflows were fragile
- No global event history existed
- Debugging required tracing through multiple files

⸻

## PREVIOUS ARCHITECTURE

```
Subsystem A ──calls──→ Subsystem B.method()
Subsystem C ──imports──→ Subsystem D.API
Subsystem E ──EventBus.emit()──→ Subsystem F (different EventBus!)
```

Each arrow was a different mechanism. No single view of communication existed.

⸻

## NEW ARCHITECTURE

```
Any subsystem ──FabricKernel.emit()──→ EventRouter ──→ Subscribers
              ──FabricKernel.send()──→ MessageBus ──→ Topic subscribers
              ──AgentRuntime.send()──→ Agent inboxes
              ──TaskGraph.add_node()──→ Task graph
              ──ConversationEngine.add_message()──→ Conversation
```

All communication uses the Fabric. The Fabric provides:
- **Events** — structured, typed, replayable (new)
- **Messages** — topic-based, prioritized, TTL (existing)
- **Agent messaging** — direct agent-to-agent (new)
- **Task graph** — dependency-aware work tracking (new)
- **Conversations** — structured discussions (new)

⸻

## DESIGN PHILOSOPHY

1. **One Fabric, multiple patterns** — Events for broadcast, messages for point-to-point,
   agent inboxes for directed communication, task graph for structured work.
2. **Observability by default** — Every Fabric action is audited, metered, and traceable.
3. **Thread-safe** — All Fabric operations use RLock for safe concurrent access.
4. **Bounded resources** — Event store has configurable max capacity (default 50K).
5. **No external dependencies** — Fabric uses only Python stdlib.

⸻

## INTERNAL COMPONENTS

### FabricKernel (`kernel.py`)
- Singleton (thread-safe)
- Composes: MessageBus, EventRouter, ServiceRegistry, Scheduler, Policy, Metrics, Audit
- State machine: BOOTING → RUNNING → DEGRADED → SHUTDOWN
- Public API: boot(), shutdown(), emit(), on_event(), send(), subscribe(), register_service()

### EventRouter (`events.py`)
- Manages EventSubscription list
- Synchronous delivery to matched subscribers
- Dead letter queue for failed deliveries
- Subscriber filtering by event type + optional predicate

### EventStore (`events.py`)
- Thread-safe ring buffer (default 50K events)
- Indexed by: type, origin, session, repository, tags
- Query with: type, origin, tags, time range, confidence threshold, limit
- Replay: returns all events matching criteria for replay

⸻

## PUBLIC APIS

### FabricKernel
```python
kernel = FabricKernel.instance()
kernel.boot()
kernel.emit("event.type", {"key": "value"}, origin="module")
kernel.on_event("event.type", handler, filter_fn=None)
kernel.query_events(event_type="...", since=..., limit=100)
kernel.register_service("name", "1.0", ["capability"])
```

### EventRouter
```python
router = EventRouter()
router.subscribe("event.type", handler, filter_fn)
router.unsubscribe(handler)
router.emit(event)
router.emit_raw("type", payload, origin="...", ...)
```

### EventStore
```python
store = EventStore(max_events=10000)
store.append(event)
store.query(event_type="...", tags=[...], limit=100)
store.replay(event_type="...", since=...)
store.count_by_type()
```

⸻

## ALGORITHMS

### Event Matching
1. Get subscription list
2. For each subscription, check if `event_type == sub.event_type or sub.event_type == "*"`
3. If `filter_fn` exists, apply predicate
4. If matched, execute handler

### Event Store Pruning
When `len(events) > max_events`, remove oldest event from front of list
and from all indexes. O(1) for list pop(0), O(n) for index removal.

⸻

## STATE MACHINES

### FabricKernel
```
BOOTING → RUNNING → DEGRADED → SHUTDOWN
              ↑          │
              └──────────┘   (recovery)
```

### AgentInstance
```
IDLE → RUNNING → IDLE  (task complete)
IDLE → RUNNING → ERROR → IDLE  (task fail, manual recover)
Any → TERMINATED  (forced termination)
```

### TaskNode
```
PENDING → READY → RUNNING → COMPLETED
                            → FAILED
                            → ROLLED_BACK
                            → SKIPPED
```

⸻

## THREADING MODEL

All Fabric operations are thread-safe:
- `threading.RLock` for mutable state (reentrant, per-thread)
- Synchronous event delivery (subscribers run in caller's thread)
- Future: AsyncEventRouter for asyncio consumers

⸻

## FAILURE MODES

| Failure | Effect | Recovery |
|---------|--------|----------|
| Subscriber crashes | Event goes to dead letter | Retry on next emit |
| Event store full | Oldest event evicted | Configurable capacity |
| No subscribers for event | Event stored but not delivered | Queryable, replayable |
| Fabric uninitialized | RuntimeError on access | Check kernel state |

⸻

## FUTURE EXTENSIONS

- **Persistence** — EventStore backed by SQLite or file
- **Async delivery** — AsyncEventRouter for non-blocking dispatch
- **Priority queues** — Separate queues per priority level
- **Event sourcing** — Full event sourcing for subsystem state
- **Distributed fabric** — Multi-process FabricKernel with shared event bus
