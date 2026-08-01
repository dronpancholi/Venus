# Cycle 016 — Architecture Delta

## Changes vs Cycle 015

### App Architecture
| Concern | Before (C015) | After (C016) | Rationale |
|---------|--------------|-------------|-----------|
| Screen navigation | `pop_screen() + push_screen()` | `push_screen() + cache` | Escape crash bug fix |
| Screen identity | None | `screen_id` class attribute | Back-navigation tracking |
| Keyboard shortcuts | 13 Ctrl+Shift+letter bindings | 9 single-key bindings + escape | Speed, VSCode muscle memory |
| Home screen refresh | No-op (`_refresh_stats`) | 7 widget refresh calls | P0 bug fix |

### Server Architecture
| Concern | Before (C015) | After (C016) | Rationale |
|---------|--------------|-------------|-----------|
| WS event delivery | Broadcast + per-connection handler | Broadcast only | Double delivery fix |
| WS handler lifecycle | Never unsubscribed | Auto-removed on disconnect | Memory leak fix |

### Visual Architecture
| Concern | Before (C015) | After (C016) | Rationale |
|---------|--------------|-------------|-----------|
| Knowledge Graph | ListView + hardcoded text | Tree widget + real data | Most misleading screen fixed |
| Entity browsing | None (statistics only) | Hierarchical tree with details | Actual graph-like experience |

## Unchanged Architecture
- 6-layer architecture (Foundation → Kernel → Domain → Intellect → Platform → Plugin) — unchanged
- FabricKernel singleton — unchanged
- EventRouter event system — unchanged
- StorageEngine/SQLite — unchanged
- 3 AI providers — unchanged
- Plugin system — unchanged
- 3,274 tests — all pass

## New Technical Debt
| Item | Severity | Created By |
|------|----------|------------|
| Tree widget in KG screen may be slow on large datasets | Low | M113 |
| Screen caching increases memory usage (11 screens alive) | Low | M111 |
| Search history in memory only (no persistence) | Low | M112 |
