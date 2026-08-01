# Phase 0 Delta: Data Storage

**Files:** `genesis/fabric/storage.py` (957 lines), `genesis/persistence/` (767 lines)  
**Tests:** Via `test_kernel.py` (StorageEngine tests)

## Three Storage Subsystems

### 1. Fabric StorageEngine (957 lines)

**Technology:** SQLite via `sqlite3`  
**Tables:** 10 (events, agents, agent_tasks, agent_messages, task_graph_nodes, conversations, conversation_messages, audit_entries, metric_points, services)  
**Indexes:** 15+ B-tree indexes  
**Features:** WAL mode, auto-schema migration via `SchemaManager`, read/write counting

### 2. Genesis-II Persistence Layer (767 lines)

**5 Normative Stores:**
| Store | Table | Purpose |
|-------|-------|---------|
| `MetadataStore` | metadata_records | Entity metadata CRUD |
| `KnowledgeStore` | graph_nodes, graph_edges | Knowledge graph persistence |
| `HistoryStore` | execution_history | Append-only execution history |
| `ArtifactStore` | compilation_cache | Content-addressed cache |
| `CheckpointStore` | File system (JSON) | Platform state snapshots |
| `MemoryStore` | memory_store | Namespace/key/value memory |

**Repository Pattern:** Abstract `Repository[T]` interface with `InMemoryRepository[T]` default

### 3. UniversalKernel StorageManager (93 lines)

Abstract volume manager — NOT a real database. Tracks storage classes (HOT, WARM, COLD, ARCHIVE).

## Findings

1. **StorageEngine path is relative** — default `_path = "venus.db"` resolves to `Path.cwd()` which breaks outside project root
2. **No connection pooling** — synchronous `sqlite3`, single connection, no retry logic
3. **Schema migration is lineage-only** — `SchemaManager` tracks version but can't downgrade, and version changes are manual
4. **No query pagination** — `query_events()` returns all matching rows (can be 50K+)
5. **Persistence is optional but unchecked** — `if self._kernel.storage and self._kernel.storage.connected` pattern is inconsistent across callers
6. **Three storage layers** — fabric StorageEngine, persistence stores, and storage managers all solve overlapping problems
7. **MemoryStore vs StorageEngine** — both persist conversations and messages, leading to data duplication

## Recommendations

1. Make storage path absolute or resolve relative to `venus_brain/` directory
2. Add connection pooling or at minimum retry with exponential backoff
3. Add migration rollback support (store down-migration scripts)
4. Add `LIMIT/OFFSET` pagination to all query methods
5. Create `_safe_storage()` helper that returns `None` and centralizes the "is connected" check
6. Consolidate fabric StorageEngine with persistence stores — pick one pattern
7. Deduplicate conversation storage (pick MemoryStore or StorageEngine, not both)
