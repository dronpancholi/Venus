# Cycle 015 — Performance Analysis

## Desktop Performance

| Operation | Current | Target | Bottleneck |
|-----------|---------|--------|------------|
| Initial render | 30s (first timer tick) | <1s | No `_refresh()` call in `on_mount` |
| Screen navigation | ~100ms | <50ms | `navigate_to()` destroys/recreates |
| Event display | Instant (in-memory) | Instant | EventStore is RAM |
| Agent list refresh | 30s interval | <1s (event-driven) | Timer fallback is default |
| Search response | Per-keystroke | <100ms with 200ms debounce | No debounce |

## Server Performance

| Operation | Current | Target | Bottleneck |
|-----------|---------|--------|------------|
| REST response | ~10ms | <5ms | Lazy imports in route handlers |
| WebSocket broadcast | `asyncio.run()` | Queue-based | Fixed in Cycle 015 |
| Event emission | ~1ms | <1ms | Direct memory write |
| Event query (50K events) | ~5ms | <5ms | Indexed by 6 dimensions |

## Memory Usage

| Component | Current | Notes |
|-----------|---------|-------|
| EventStore | 50K events max | FIFO eviction, ~18KB per event = ~900MB worst case |
| AgentRuntime | Per-agent | ~10KB per agent with context |
| TaskGraph | Per-node | ~2KB per node |
| ConversationEngine | Per-conversation | ~1KB + messages in memory |

## Recommendations

1. Add `_refresh()` call in `on_mount` before `set_interval` — eliminates 30s blank screen
2. Reduce `_DRIVEN_INTERVAL` from 30s to 5s for responsive feel
3. Add LRU eviction to EventStore with max_memory_bytes config
4. Persist EventStore to SQLite periodically to bound RAM growth
5. Move lazy imports in server route handlers to module level
6. Add response time middleware to server for performance tracking
