# Web Server Validation

## Verified

- `GenesisAPI` creates a FastAPI application successfully
- 23 REST endpoints registered (via FastAPI route inspection)
- WebSocket endpoint registered at `/ws`
- Server starts with `genesis serve`

## API Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/v1/health` | Health check |
| GET | `/v1/kernel/stats` | Kernel statistics |
| GET | `/v1/events` | Query events |
| POST | `/v1/events/emit` | Emit event |
| GET | `/v1/search` | Search everything |
| GET | `/v1/agents` | List agents |
| GET | `/v1/providers` | List AI providers |
| GET | `/v1/services` | List services |
| GET | `/v1/services/{instance_id}` | Service detail |
| GET | `/v1/tasks` | List tasks |
| GET | `/v1/storage` | Storage stats |
| GET | `/v1/repository` | Repository info |
| GET | `/v1/metrics` | Performance metrics |
| GET | `/v1/audit` | Audit log |
| GET | `/v1/conversations` | Conversations |
| GET | `/v1/conversations/{id}/messages` | Conversation messages |
| GET | `/v1/execution` | Execution status |
| GET | `/v1/watch` | Watch status |
| GET | `/v1/auth/status` | Auth status |
| GET | `/docs` | Swagger UI |
| GET | `/redoc` | ReDoc UI |
| GET | `/openapi.json` | OpenAPI schema |
| GET | `/docs/oauth2-redirect` | OAuth2 redirect |

## Start Command
```bash
genesis serve
```

Default: `http://localhost:8080`

Configurable via:
- `GENESIS_HOST` environment variable
- `GENESIS_PORT` environment variable
- `genesis/config/settings.py` → `api_host`, `api_port`

## What Does NOT Exist
- **No frontend** — no HTML/CSS/JS is served. Only Swagger UI and ReDoc
  are available at `/docs` and `/redoc`.
- **No authentication** — `require_auth=False` by default.
- The "Desktop" URL (http://localhost:8080/desktop) mentioned in startup
  banner exists only as a placeholder.

## Server Boot Flow
```
genesis serve
  → _ensure_config()
  → _auto_setup_if_needed()
  → FabricKernel.instance().boot()
  → GenesisAPI(kernel).create_app()
  → uvicorn.run(app, host, port)
```
