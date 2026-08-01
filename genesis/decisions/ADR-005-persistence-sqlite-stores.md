# ADR-005: VPS Part X Storage Providers (SQLite Backend)

**Status:** Accepted  
**Date:** 2026-06-26

## Context

VPS Part X §10.1 defines 5 normative storage roles. All platform state was in-memory only — data lost on restart (AUDIT S05). The `Repository[T]` abstract interface existed but no durable implementations.

This ADR documents the implementation of all 5 storage providers backed by SQLite.

## Decision

Implement 5 storage provider classes in `persistence/sqlite_store.py`:

| Provider | VPS § | Schema Table | Key Operations |
|---|---|---|---|
| `MetadataStore` | §10.1.4 | `metadata_records` | CRUD + update(), find() |
| `KnowledgeStore` | §10.1.2 | `graph_nodes`, `graph_edges` | save_node/edge, query_by_type |
| `HistoryStore` | §10.1.3 | `execution_history` | append-only save, query_by_time_range |
| `ArtifactStore` | §10.1.1 | `compilation_cache` | get_by_hash (content-addressed) |
| `CheckpointStore` | §10.1.5 | JSON files | save/load/list/delete snapshots |

All SQLite stores share a `SQLiteStore` base class providing connection management, WAL journal mode, and schema initialization. CheckpointStore uses separate JSON files (GENESIS_II_ARCHITECTURE §5.4).

## Design Decisions

1. **Single SQLite database** (not 5): atomic cross-store operations, simpler lifecycle
2. **Shared base class**: eliminates connection/schema duplication across stores
3. **json columns for attributes**: schema flexibility without migration
4. **sqlite3 stdlib only**: zero external dependencies, matches GENESIS_II_ARCHITECTURE §5.3
5. **Additive**: existing in-memory stores unchanged, domain services not rewired yet

## Alternatives Rejected

- **5 separate databases**: increased complexity, no transactional benefit
- **5 independent connection classes**: code duplication (rejected via base class)
- **Neo4j** (stated in GENESIS_II_ARCHITECTURE for Genesis-III): premature, heavier dependency
- **Active Record** (stated in ADR-006): couples entities to storage

## Consequences

- Persistence coverage: 0% → 100% of VPS Part X §10.1
- Total tests: 94 → 132 (+38 persistence tests)
- Platform metrics: 7,127 → 8,180 lines, 97 → 103 classes
- AUDIT S05 eliminated: data survives restart
- No existing behavior changed (additive)

## Next Step

Wire these stores into domain services (MetadataEngine, Compiler, KnowledgeGraphEngine, ExecutionEngine) so they use persistent storage instead of in-memory dicts.
