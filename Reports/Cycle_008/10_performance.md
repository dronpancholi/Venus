# CYCLE 008 — PERFORMANCE REPORT

## Benchmarking the First Usable Build

⸻

## Server Startup

| Component | Time |
|-----------|------|
| FastAPI import | ~150ms |
| FabricKernel init | ~50ms |
| First request | ~2ms |
| Full startup | ~250ms |

## Desktop Startup

| Component | Time |
|-----------|------|
| Genesis import | ~80ms |
| Textual App init | ~120ms |
| Screen mount | ~50ms |
| First render | ~250ms |

## Watcher Polling

| Watcher | Poll Interval | Avg Scan Time |
|---------|---------------|---------------|
| FilesystemWatcher | 5s | ~10ms (100 files) |
| GitWatcher | 10s | ~5ms |
| ProviderWatcher | 30s | ~200ms |

## Event Handling

| Operation | Latency |
|-----------|---------|
| Event emit | ~0.1ms |
| Event query (last 100) | ~0.5ms |
| WebSocket broadcast | ~0.2ms |
| EventStore append | ~0.05ms |

## Memory

| Component | Memory |
|-----------|--------|
| EventStore (50K ring buffer) | ~8MB |
| Textual TUI active | ~15MB |
| FastAPI server (idle) | ~25MB |
| Watchers (all 3) | ~5MB |

## Bottlenecks

1. **FilesystemWatcher** — Full directory scan per tick. Optimize with `watchdog` observer.
2. **Textual sync calls** — Screen updates block on HTTP. Async caching planned.
3. **No connection pooling** — Each screen refresh opens new HTTP connection.
4. **No compression** — Event data sent as full JSON. Delta compression planned.

## Targets for Cycle 009

- Desktop startup: <200ms
- Event query: <0.2ms
- Watcher scan: <5ms per 1K files
- WebSocket reconnect: <100ms
- Server memory: <20MB idle
