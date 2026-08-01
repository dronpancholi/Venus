# CYCLE 009 — STORAGE ENGINE REPORT

## SQLite Persistence Layer (Mission 71)

---

## Overview

The StorageEngine is Genesis's first persistence layer. Every Fabric subsystem
now optionally persists state to SQLite. The engine uses WAL mode for concurrent
read/write performance, auto-creates all tables on first connection, and supports
a repository pattern for all 10 entity types.

## Architecture

```
StorageEngine
  ├── SchemaManager        (auto-create tables, indexes, migration)
  ├── connect/disconnect   (WAL mode, foreign keys)
  │
  ├── Event Repository     (store, query, purge, count)
  ├── Agent Repository     (store, query, delete)
  ├── AgentTask Repository (store, query by agent/status)
  ├── Message Repository   (store, query by agent)
  ├── TaskNode Repository  (store, query by status/type/parent)
  ├── Conversation Repo    (store, query by title/participant)
  ├── ConvMessage Repo     (store, query by conversation)
  ├── Audit Repository     (store, query by action/actor)
  ├── Metric Repository    (store, query by name/since)
  └── Service Repository   (store, query, delete)
```

## Schema

11 tables with 19 indexes:

| Table | Purpose | Columns |
|-------|---------|---------|
| `events` | Engineering events | 15 columns — type, timestamp, origin, payload (JSON), tags, confidence, etc. |
| `agents` | Agent instances | 13 columns — role, name, capabilities, status, task counts |
| `agent_tasks` | Tasks assigned to agents | 10 columns — objective, context, status, result |
| `agent_messages` | Inter-agent messages | 8 columns — sender, recipient, content, type |
| `task_graph_nodes` | Task graph nodes | 24 columns — type, title, deps, blocking, progress, evidence |
| `conversations` | Engineering conversations | 13 columns — title, participants, decisions, links |
| `conversation_messages` | Conversation messages | 8 columns — role, content, citations, links |
| `audit_entries` | Audit trail | 9 columns — action, actor, detail, severity |
| `metric_points` | Time-series metrics | 6 columns — name, value, tags, host |
| `services` | Service registry | 8 columns — name, version, capabilities, heartbeat |
| `schema_version` | Migration tracking | 2 columns — version, applied_at |

## Thread Safety

All operations use `threading.RLock` for thread-safe concurrent access.
WAL mode enables concurrent readers without writer blocking.

## Integration Points

| Fabric Component | Persistence Mechanism |
|-----------------|----------------------|
| FabricKernel.emit() | Auto-store event to SQLite |
| AgentRuntime.spawn() | Auto-store agent to SQLite |
| AgentInstance.assign/complet/fail | Auto-store agent task to SQLite |
| AgentRuntime.send_message | Auto-store message to SQLite |
| TaskGraph.add_node/update_status | Auto-store task node to SQLite |
| ConversationEngine.create | Auto-store conversation to SQLite |
| ConversationEngine.add_message | Auto-store message to SQLite |
| AuditLog.log | Auto-store audit entry to SQLite |
| FabricMetrics.record | Auto-store metric point to SQLite |
| FabricKernel.register_service | Auto-store service to SQLite |

## Usage

```python
from genesis.fabric.storage import StorageEngine

# Default path: ~/.genesis/fabric.db
engine = StorageEngine()
engine.connect()

# Custom path
engine = StorageEngine("/path/to/custom.db")
engine.connect()

# Query persisted events
events = engine.query_events(event_type="kernel.booted")
print(f"Found {len(events)} boot events")

# Get table sizes
sizes = engine.get_table_sizes()
for table, count in sizes.items():
    print(f"{table}: {count} records")

engine.disconnect()
```

## Configuration

Storage is enabled by default in FabricKernel. To disable:
```python
kernel = FabricKernel.instance(enable_persistence=False)
```

Custom storage path:
```python
kernel = FabricKernel.instance(storage_path="/custom/path/fabric.db")
```
