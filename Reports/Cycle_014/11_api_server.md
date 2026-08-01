# Phase 0 Delta: API Server

**File:** `genesis/server.py` — 342 lines  
**Tests:** 10 (via `test_server.py`)

## Architecture

```python
GenesisAPI(kernel: FabricKernel, require_auth: bool = False)
  ├── create_app() -> FastAPI
  │     ├── lifespan: kernel.boot() + subscribe event broadcast
  │     ├── auth middleware (optional Bearer token check)
  │     ├── 18 REST routes
  │     └── WebSocket endpoint /v1/ws
```

## REST Routes

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/v1/health` | Kernel health |
| GET | `/v1/kernel/stats` | Full telemetry |
| GET | `/v1/events` | Filtered event list |
| POST | `/v1/events/emit` | Create event |
| GET | `/v1/services` | Service list |
| GET | `/v1/services/{id}` | Service detail |
| GET | `/v1/agents` | Agent summary |
| GET | `/v1/tasks` | Task graph |
| GET | `/v1/conversations` | Conversation list |
| GET | `/v1/metrics` | Metrics snapshot |
| GET | `/v1/audit` | Audit log |
| GET | `/v1/watch` | CE watcher states |
| GET | `/v1/providers` | AI providers |
| GET | `/v1/storage` | Storage stats |
| GET | `/v1/execution` | Execution stats |
| GET | `/v1/conversations/{id}/messages` | Conversation messages |
| GET/POST | `/v1/auth/*` | Token management |

## WebSocket (`/v1/ws`)

- On connect: register client in `_websocket_clients` list
- Received messages: `ping` → pong, `subscribe` → event listener, `query_events` → event store query
- Server push: all kernel events broadcast to all clients via wildcard handler

## Legacy API (`genesis/api/router.py`)

- Non-FastAPI custom router with 32 defined routes
- Only 1 handler registered (health) — everything else returns 501
- No test coverage
- Effectively dead code superseded by `server.py`

## Findings

1. **`run_server` function is missing** — `__main__.py` imports `run_server` from `genesis.server` but no such function exists. CLI `genesis server` crashes with ImportError
2. **WebSocket broadcast uses `asyncio.run()` inside synchronous thread** — can cause "event loop already running" errors in production
3. **No CORS middleware** — not configured, browser clients will be blocked
4. **No rate limiting** — event emission endpoint can be spammed
5. **No request logging** — no middleware for request/response logging
6. **Lazy imports in route handlers** — 10+ routes call `__import__()` inside handler, each call blocks the request thread
7. **Legacy API router is dead code** — 32 routes defined, only `/health` implemented

## Recommendations

1. Add `run_server()` function with uvicorn launcher to `server.py`
2. Replace `asyncio.run()` with proper async handler or thread-safe queue + async consumer
3. Add CORS middleware (allow all origins for dev, configurable for prod)
4. Add rate limiting middleware (e.g., `slowapi` or custom token bucket)
5. Add request logging middleware
6. Move lazy imports to module level inside route registration, not handler execution
7. Deprecate and remove `genesis/api/router.py`
