# Cycle 015 — Operations Manual

## Deployment

Genesis runs as a single process. Two modes can run independently or together:

### Desktop Mode
```bash
genesis desktop
```
No external dependencies (beyond Python packages). Uses Textual for TUI. Data is in-memory by default, persisted to SQLite when `enable_persistence=True`.

### Server Mode
```bash
genesis server
```
Launches FastAPI on `127.0.0.1:8377`. Environment variables:
- `GENESIS_HOST` (default: `127.0.0.1`)
- `GENESIS_PORT` (default: `8377`)
- `GENESIS_AUTH` (any value → enables token auth)
- `GENESIS_STORAGE_PATH` (default: `~/.genesis/data`)

### Watch Mode
```bash
genesis watch
```
File watcher + auto-restart. Useful during development.

## Health Monitoring

### Endpoint
`GET /v1/health` returns:
```json
{
  "status": "healthy",
  "uptime_seconds": 3600,
  "services": {"count": 3},
  "messages": {"total": 42},
  "sessions": {"active_count": 1}
}
```

### Health Checks
- Kernel: `FabricKernel.instance().health()` → `KernelHealth` namedtuple
  - `alive`, `booted`, `event_router`, `service_registry`
  - Runtime health: `healthy`, `uptime_seconds`

### Metrics
`GET /v1/metrics` returns:
```json
{
  "total_events": 1234,
  "events_by_type": {"system_boot": 1, ...},
  "active_services": 3,
  "total_messages": 42,
  "active_sessions": 1,
  "events_per_second": 0.5,
  "histogram_details": {...}
}
```

## Backup & Recovery

Data stored at `~/.genesis/data/genesis.db` (SQLite):
- Events table: last 50,000 events
- Conversations and messages
- Audit log
- Metrics points
- Service registrations

Backup: `cp ~/.genesis/data/genesis.db ~/.genesis/data/genesis.db.bak`

## Logging

Server outputs structured JSON logs to stdout. Redirect to file:
```bash
genesis server 2>&1 | tee genesis.log
```

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| "No module named genesis" | Package not installed | `pip install -e .` |
| Desktop is blank | No data sources running | Events will appear as activity happens |
| Server won't start | Port in use | `lsof -i :8377` → kill conflicting process |
| Auth errors | Token expired | `POST /v1/auth/token` with valid identity |
| WS disconnects | Server restart | Client auto-reconnect (not yet implemented) |
