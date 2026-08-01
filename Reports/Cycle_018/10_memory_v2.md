# M138 — Engineering Memory V2

## File
`genesis/memory_v2/engine.py`, `genesis/memory_v2/__init__.py`

## Purpose
Multi-layer memory system with working, short-term, long-term, and ephemeral layers. Entries automatically promote from working → short-term → long-term over time. Ephemeral entries auto-expire.

## Key Components

### Memory Layers
| Layer | Capacity | TTL | Promotion |
|---|---|---|---|
| WORKING | 100 entries | 5 min | → SHORT_TERM |
| SHORT_TERM | Unlimited | 1 hour | → LONG_TERM |
| LONG_TERM | Unlimited | None | — |
| EPHEMERAL | Unlimited | Configurable | Deleted on expiry |

### EngineeringMemoryV2
- `store(key, content, layer, tags, source, ttl)` — store with optional auto-expiry
- `recall(key, layer=None)` — retrieve from any layer (with TTL check)
- `search(query, limit)` — cross-layer text search
- `promote(key, target)` — manually move to another layer
- `consolidate()` — automatic promotion: working → short → long, ephemeral cleanup
- `stats()` — entry counts per layer

## Integration
- **FabricKernel.memory_v2** — lazy-loaded, auto-booted
- **EngineeringRegistry** — registered as SERVICE object
- **AutomationEngine** — can schedule periodic consolidation
