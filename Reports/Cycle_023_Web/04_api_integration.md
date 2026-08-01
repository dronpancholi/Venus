# API Integration

## REST Endpoints (18 consumed)
All 18 GET endpoints are consumed via `src/lib/api.ts` using `fetch`:

| Endpoint | Hook | Page |
|----------|------|------|
| `/v1/health` | `useQuery` | Home, Dashboard, StatusBar, Timeline |
| `/v1/kernel/stats` | `useQuery` | Home |
| `/v1/events` | `useQuery` | Timeline, Knowledge, Project |
| `/v1/services` | `useQuery` | Dashboard |
| `/v1/agents` | `useQuery` | Dashboard, Copilot |
| `/v1/tasks` | `useQuery` | Home, Dashboard, Project |
| `/v1/conversations` | `useQuery` | Dashboard, Copilot |
| `/v1/metrics` | `useQuery` | Dashboard |
| `/v1/audit` | `useQuery` | Timeline |
| `/v1/search` | `useQuery` | SearchDialog, SearchPage, Knowledge |
| `/v1/providers` | `useQuery` | Copilot |
| `/v1/storage` | `useQuery` | Dashboard |
| `/v1/execution` | `useQuery` | Dashboard |
| `/v1/repository` | `useQuery` | Home, Dashboard, Knowledge, Project |
| `/v1/auth/status` | `useQuery` | Settings (via StatusBar) |

## WebSocket Integration
- Client: `src/lib/websocket.ts` — custom client with auto-reconnect and ping/keepalive
- Connection: Established on app mount, maintained for session lifetime
- Events: Real-time engineering events pushed to all connected clients
- Status: WS connection status shown in StatusBar (green/red indicator)
- Broadcast: Server subscribes to `"*"` events via `_ws_broadcast_handler`

## Data Flow
1. Pages use `useQuery` with automatic caching and background refetch
2. StatusBar polls `/v1/health` every 5 seconds
3. Timeline polls `/v1/events` every 10 seconds
4. All other data refreshes on stale time (10 seconds default)
5. WebSocket provides push-based updates for immediate UI updates
