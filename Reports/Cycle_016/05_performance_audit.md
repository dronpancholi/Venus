# Cycle 016 — Performance Audit

## Desktop Startup Performance

| Phase | Current | Target | Bottleneck |
|-------|---------|--------|------------|
| CLI dispatch | ~10ms | <5ms | Import genesis.desktop |
| Kernel boot | ~50ms | ~30ms | Lazy imports via `__import__` |
| App creation | ~100ms | ~50ms | CSS parsing (300+ lines inline) |
| First render | 30s (first timer tick) | <1s | No `_refresh()` on mount |
| Full data load | 30-60s | <5s | Polling at 30s interval |

**Critical issue:** First render shows empty widgets. No `_refresh()` call exists in any screen's `on_mount` method. The user stares at a blank terminal for 30 seconds.

## Runtime Performance

### Screen Navigation
| Operation | Current | Target | Notes |
|-----------|---------|--------|-------|
| Screen switch | ~100ms | <50ms | navigate_to destroys + recreates |
| Command Palette | ~20ms | <10ms | Live filter on 25 items |
| Search Everywhere | ~50ms | <30ms | 10 sources, 30 result cap |

### Event System
| Operation | Current | Max | Notes |
|-----------|---------|-----|-------|
| Event emission | ~1μs | - | In-memory write |
| Event delivery | ~50μs | - | Synchronous handler calls |
| Event query (50K) | O(n) scan | <5ms with index | Indexes exist but unused by query() |
| Event pruning | O(n) | - | Flawed index maintenance |

### Storage
| Operation | Current | Target | Notes |
|-----------|---------|--------|-------|
| SQLite write | ~100μs | <50μs | WAL mode, synchronous=NORMAL |
| SQLite read (indexed) | ~50μs | ~30μs | 17 indexes |
| SQLite read (LIKE) | ~5ms | <1ms | JSON array columns force LIKE search |

### API
| Operation | Current | Target | Notes |
|-----------|---------|--------|-------|
| `/v1/health` | ~5ms | <3ms | Lightweight |
| `/v1/events` | ~10ms | <5ms | O(n) scan over in-memory store |
| `/v1/events/emit` | ~200μs | ~100μs | In-memory + optional SQLite |
| `/v1/kernel/stats` | ~5ms | ~3ms | Aggregates from multiple subsystems |

## Memory Analysis

| Component | Current Max | Safe Limit | Risk |
|-----------|-------------|------------|------|
| EventStore | 50,000 events × ~1KB = ~50MB | 100MB | OK |
| EventStore (peak) | ~50MB | 100MB | FIFO eviction keeps bound |
| Session contexts | 1KB per session | Unbounded | No cleanup for expired sessions |
| Agent runtimes | ~10KB each | 10 agents = 100KB | Negligible |
| Working memory | 7 items (Miller's Law) | Fixed | Bounded by design |
| Episodic memory | Unbounded | Configurable | No pruning strategy |
| SQLite connection | Single connection | Single | Safe with WAL |
| Thread count | ~5 (kernel + server + CE) | 10 | Low |

## Network Performance

| Operation | Current | Notes |
|-----------|---------|-------|
| WebSocket latency | ~1-5ms | Localhost only |
| REST latency | ~5-15ms | Localhost only |
| AI provider call | ~500ms-10s | Depends on model/provider |
| Streaming throughput | ~1 byte/syscall | `resp.read(1)` is extremely inefficient |

## Performance Score: 4/10

| Dimension | Score | Key Issues |
|-----------|-------|------------|
| Startup Time | 2/10 | 30-second blank screen, no loading |
| Screen Navigation | 5/10 | 100ms switches, context destroy |
| Data Refresh | 3/10 | 30s polling, no event-driven priority |
| Event Query | 3/10 | O(n) scan with unused indexes |
| Storage I/O | 6/10 | Decent with WAL, but LIKE on JSON cols |
| Streaming | 2/10 | Byte-at-a-time, no async |
| Memory Management | 5/10 | Bounded for events, unbounded for sessions/episodic |
| API Response Times | 5/10 | Consistent <15ms, no caching |

## Recommendations

1. **Fix first-render blank screen** — add `_refresh()` call before `set_interval` in every screen's `on_mount`
2. **Reduce poll interval** — from 30s to 5s as interim, migrate to event-driven as primary
3. **Use event indexes in query()** — replace O(n) scan with index lookups
4. **Buffer SSE streaming** — replace `resp.read(1)` with `resp.readline()` or buffered reader
5. **Add LRU eviction to EventStore** — enforce TTL property that currently does nothing
6. **Add session timeout** — prune expired contexts from kernel._contexts
7. **Move from polling to event-driven** — make EventRouter the primary update mechanism and timer the fallback
