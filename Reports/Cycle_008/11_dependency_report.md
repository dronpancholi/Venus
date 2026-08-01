# CYCLE 008 — DEPENDENCY REPORT

## What Genesis Depends On

⸻

## Dependency Tree

```
genesis
├── rich            [core]  — terminal formatting
├── textual         [core]  — terminal UI framework
├── fastapi         [server] — REST framework
├── uvicorn         [server] — ASGI server
├── websockets      [server] — WebSocket support
└── watchdog        [watch]  — filesystem monitoring
```

## Dependency Analysis

| Dependency | Purpose | Alternative | Risk |
|------------|---------|-------------|------|
| `rich` | Terminal rendering | None (stdlib lacks tables/panels) | Low — mature, pure Python |
| `textual` | TUI framework | `urwid`, `prompt_toolkit` | Medium — active development |
| `fastapi` | REST API | `flask`, `starlette`, `aiohttp` | Low — mature, ASGI-native |
| `uvicorn` | ASGI server | `gunicorn`, `hypercorn` | Low — standard choice |
| `websockets` | WebSocket | `fastapi` built-in WS | Low — established |
| `watchdog` | File monitoring | `inotify` (Linux), `kqueue` (macOS) | Low — cross-platform |

## Version Constraints

- `rich >= 13.0` — Text fixes, better table API
- `textual >= 0.41` — CSS support, refactored screen lifecycle
- `fastapi >= 0.100` — New event API (`@app.on_event`)
- `uvicorn >= 0.22` — Reliable WebSocket support

## Security Notes

- Genesis core (rich + textual) has **no network access** — safe for air-gapped use
- Server deps (fastapi, uvicorn, websockets) bind to `127.0.0.1` by default
- Watch deps (watchdog) only reads files — no write capability
- No dependencies with known CVEs at time of writing

## Deprecation Strategy

- All dependencies are optional `extras_require` — core install is minimal
- `watchdog` is the riskiest dep (native extensions). Fallback: polling only.
- Textual is the most active dep — follow releases for API changes.
