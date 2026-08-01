# CYCLE 008 — API SERVER REPORT

## Genesis API — REST + WebSocket

**File:** `genesis/server.py`

⸻

## Purpose

The Genesis API exposes the FabricKernel over HTTP and WebSocket, enabling any client
(desktop TUI, web UI, mobile app, CI/CD, IDE plugin) to interact with Genesis.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/v1/health` | Server status, uptime, event count, watcher count |
| GET | `/v1/events` | List events (limit, offset) |
| GET | `/v1/events/query` | Query events by type/severity/source/tags |
| POST | `/v1/events` | Emit a new event |
| GET | `/v1/events/replay` | Replay events (stream) |
| GET | `/v1/agents` | List agents (live + dead) |
| POST | `/v1/agents` | Create an agent instance |
| GET | `/v1/tasks` | List task graph nodes |
| GET | `/v1/conversations` | List conversations |
| GET | `/v1/providers` | List AI providers |
| GET | `/v1/watch` | Watcher status |
| GET | `/v1/services` | Service listing |
| GET | `/v1/audit` | Audit log |
| GET | `/v1/metrics` | Platform metrics |
| WS | `/v1/ws` | WebSocket — live events |

### WebSocket Protocol

```
→ {"type": "subscribe", "channels": ["events", "agents"]}
← {"type": "event", "data": {"event_type": "change", ...}}
← {"type": "heartbeat", "timestamp": ...}
```

Channels: `events` (live events), `agents` (agent state changes)

## Architecture

```
Client (TUI/Web) ←→ HTTP/WS ←→ GenesisAPI → FabricKernel
                                          ├── event_store
                                          ├── scheduler
                                          └── watchers
```

- Uses FastAPI with `@app.on_event("startup")`/`"shutdown"` lifecycle
- Runs on port 8377 (`GENESIS` on phone dial)
- WebSocket supports multi-client subscriptions
- Thread-safe through FabricKernel's sync interface

## Future Plans

- **Authentication** — API keys, JWT
- **Event streaming** — Server-Sent Events as alternative to WS
- **File API** — Read/write workspace files
- **Agent RPC** — Call agents through API
- **SDK clients** — Python, TypeScript, Rust SDKs
