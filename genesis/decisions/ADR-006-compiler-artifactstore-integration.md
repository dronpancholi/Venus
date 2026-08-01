# ADR-006: Compiler ArtifactStore Integration

**Status:** Accepted  
**Date:** 2026-06-26

## Context

VPS Part X §10.1.1 defines the Artifact Store for compiled output artifacts. The ArtifactStore existed as a SQLite-backed repository but was not wired into any domain service. The Compiler's `_cache` dict was purely in-memory — all compilation results lost on restart.

Following V9 Platform Evolution Principle *"implement infrastructure before consumers"*, the infrastructure (ArtifactStore) existed; this change integrates it with its first consumer (Compiler).

## Decision

Wire `ArtifactStore` into the `Compiler` as an optional secondary cache layer:

- `Compiler.__init__(artifact_store: ArtifactStore | None = None)` — backward compatible
- `compile()` persists result to ArtifactStore after in-memory cache
- `incremental_compile()` checks ArtifactStore on in-memory miss (cache hierarchy: memory → SQLite → full compile)
- `invalidate_cache()` clears both layers
- `CompilationUnit.from_dict()` added for deserialization

## Specification Mapping

- VPS §10.1.1 (Artifact Store): Implemented — compilation cache now persists
- VPS §10.1.1 §read/write/delete: All normative operations covered

## Files Modified

| File | Change |
|---|---|
| `genesis/compiler/compiler.py` | Added `artifact_store` param, persist on compile, restore on miss |
| `genesis/core/uir.py` | Added `CompilationUnit.from_dict()`, `_set_graph()` |
| `genesis/tests/test_persistence.py` | 38 tests (pre-existing, unchanged) |

## Verification

- 132 tests pass (34 Genesis-I + 48 Phase 0 + 12 Architecture + 38 Persistence)
- Persistence roundtrip verified: compile → restart → restore from SQLite
- Architecture verification: 12/12 (1.00)

## Rollback Strategy

`git revert`. The `artifact_store` parameter defaults to `None` — removal is clean.

## Future Recommendations

1. Wire KnowledgeStore → KnowledgeGraphEngine (next highest leverage)
2. Wire HistoryStore → ExecutionEngine
3. Wire MetadataStore → MetadataEngine
4. Backfill missing ADRs (EventBus pattern, UIR delegation)
