# Cycle 015 — Persistence Architecture (M105)

## Current State

**3 competing storage systems:**

| System | File | Lines | Backend | Tables | Primary Use |
|--------|------|-------|---------|--------|-------------|
| StorageEngine | `fabric/storage.py` | 957 | SQLite (WAL) | 10 | Fabric events, agents, tasks, conversations, audit, metrics, services |
| Persistence Stores | `persistence/sqlite_store.py` | 572 | SQLite (WAL) | 6 | Platform knowledge graph, metadata, compilation cache, execution history, memory |
| StorageManager | `kernel/storage_manager.py` | 93 | In-memory | 0 | Abstract volume tracking (unused) |

## Schema Comparison

### StorageEngine Tables (10)
| Table | Purpose | Rows |
|-------|---------|------|
| events | EngineeringEvent persistence | Unlimited |
| agents | Agent state snapshots | Per agent |
| agent_tasks | Agent task assignments | Per task |
| agent_messages | Agent communication | Per message |
| task_graph_nodes | TaskGraph node persistence | Per node |
| conversations | Conversation metadata | Per conversation |
| conversation_messages | Individual messages | Per message |
| audit_entries | Immutable audit trail | Unlimited |
| metric_points | Metric point time series | Unlimited |
| services | Registered service state | Per service |

### Persistence Stores Tables (6)
| Store | Table | Purpose |
|-------|-------|---------|
| MetadataStore | metadata_records | Entity metadata |
| KnowledgeStore | graph_nodes, graph_edges | Knowledge graph |
| HistoryStore | execution_history | Execution history |
| ArtifactStore | compilation_cache | Content-addressed cache |
| CheckpointStore | File system (JSON) | Platform state |
| MemoryStore | memory_store | Key-value memory |

## Consolidation Plan

```
Target Architecture:

BaseStore (shared connection management)
  ├── FabricStore (extends StorageEngine) — events, agents, tasks, conversations, audit, metrics
  └── PlatformStore (extends SQLiteStore) — knowledge graph, metadata, compilation, history, memory
```

### Connection Management (Unified)
Both use SQLite with WAL mode, NORMAL synchronous, foreign keys. Extract shared:
- `connect()` / `disconnect()` lifecycle
- Schema auto-creation and migration
- Vacuum and optimization
- Stats collection (read/write counts)

### Changes Required
1. Extract `BaseStore` class with shared SQLite connection logic
2. Have `StorageEngine` and `SQLiteStore` both extend `BaseStore`
3. Delete `StorageManager` (kernel/storage_manager.py) — no real consumers
4. Update fabric Store/query/store patterns to use same `BaseStore` connection

### Migration Path
1. Create `genesis/persistence/base.py` with `BaseStore`
2. Refactor `StorageEngine` to extend `BaseStore`
3. Refactor `SQLiteStore` family to extend `BaseStore`
4. Delete `StorageManager`
5. Verify all tests pass with refactored hierarchy
