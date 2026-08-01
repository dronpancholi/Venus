# ADR-007: CheckpointStore Lifecycle Integration

**Status:** Accepted
**Date:** 2026-06-26

## Context

VPS Part X §10.1.5 defines the CheckpointStore for JSON platform state snapshots. Unlike the other 4 VPS Part X stores (MetadataStore, KnowledgeStore, HistoryStore, ArtifactStore), CheckpointStore is file-based (not SQLite) and had no consumer — no service used it to save or restore state.

The VRIP RepositoryIntelligence engine builds a 550+ node knowledge graph on every run but never persisted it between runs. Each invocation started from scratch, losing all accumulated knowledge.

## Decision

Integrate CheckpointStore into the VRIP engine as its persistence backend, and register it in the DI container for general platform use:

1. **VRIP engine auto-save/load**: `RepositoryIntelligence.__init__()` loads the knowledge graph from a `vrip_knowledge_graph` checkpoint. `run_all()` saves the updated graph after completion. Knowledge accumulates across runs.
2. **KnowledgeGraph serialization**: Added `KnowledgeGraph.from_dict()` classmethod to reconstruct the graph from a serialized dict (mirrors existing `to_dict()`).
3. **DI registration**: `bootstrap()` registers CheckpointStore as a singleton under both `CheckpointStore` (concrete) and `CheckpointService` (protocol).
4. **Shutdown hook**: Platform shutdown triggers a final `platform_shutdown` checkpoint.

## Specification Mapping

- VPS §10.1.5 (Checkpoint Store): Now consumed — VRIP engine persists knowledge graph
- VPS §5.7 (Service Lifecycle): Shutdown hooks registered for graceful persistence

## Files Modified

| File | Change |
|---|---|
| `genesis/intelligence/kgraph.py` | Added `from_dict()` classmethod |
| `genesis/intelligence/engine.py` | Auto-save/load KG via CheckpointStore |
| `genesis/di/bootstrap.py` | New module — bootstrap registers all stores + EventBus in DI |
| `genesis/di/interfaces.py` | Added `CheckpointService` protocol |
| `genesis/di/__init__.py` | Export new protocols and bootstrap |

## Alternatives Considered

- **SQLite serialization**: CheckpointStore is intentionally file-based (JSON) for human-readable inspection and git-friendly diffs. SQLite would add no benefit for snapshot metadata.
- **Auto-checkpoint on every mutation**: Adds latency to every operation. Save-on-run fits VRIP's batch-oriented execution model.
