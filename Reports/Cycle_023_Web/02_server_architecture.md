# Server Architecture

## Before
```
genesis serve → __main__.cmd_serve()
  └─ Banner: lies about /desktop, /api, /ws routes
  └─ run_server(host, port)
      └─ GenesisAPI() → create_app()
          └─ 18 REST endpoints under /v1/*
          └─ WebSocket at /v1/ws
          └─ No static files
          └─ No root route → 404
```

## After
```
genesis serve → __main__.cmd_serve()
  └─ Banner: shows real routes, checks frontend build, shows kernel status
  └─ run_server(host, port, frontend_dir)
      └─ GenesisAPI(frontend_dir=...) → create_app()
          └─ 18 REST endpoints under /v1/*
          └─ WebSocket at /v1/ws
          └─ Static files at /assets/{path}
          └─ Static root files: /favicon.svg, /manifest.json
          └─ SPA root: /, /desktop, /app → index.html
          └─ SPA fallback: /{path} → index.html (client-side routing)
          └─ API docs: /docs, /redoc
```

## Frontend Detection
- Server auto-detects `web/dist/` relative to package root
- If missing: serves API-only mode with correct banner
- If present: serves SPA with correct banner

## Key Design Decisions
1. **Served by FastAPI, not a separate web server**: Simplifies deployment, single port
2. **SPA catch-all after API routes**: Ensures `/v1/*` takes priority over `/{path:path}`
3. **Client-side routing**: React Router handles all navigation, server only serves index.html
