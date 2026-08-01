# Cycle 015 — API Reference

## REST API (`/v1/`)

### Health
`GET /v1/health` → `{status, uptime_seconds, services, messages, sessions}`

### Kernel
`GET /v1/kernel/stats` → Full `KernelStats.__dict__`

### Events
`GET /v1/events?event_type=&origin=&limit=` → `{events: [...], count}`
`POST /v1/events/emit` → `{event_type, payload, origin, tags}` → `{id, type, timestamp}`

### Services
`GET /v1/services` → `{count, services}`
`GET /v1/services/{id}` → Service instance detail

### Agents
`GET /v1/agents` → Agent runtime summary

### Tasks
`GET /v1/tasks?status=` → Task graph summary or filtered tasks

### Conversations
`GET /v1/conversations?query=&limit=` → Conversation list
`GET /v1/conversations/{id}/messages?limit=` → Messages

### Metrics
`GET /v1/metrics` → Metrics snapshot + histogram details

### Audit
`GET /v1/audit?action=&actor=&limit=` → `{entries, count, total}`

### Watch
`GET /v1/watch` → CE watcher states

### Providers
`GET /v1/providers` → AI provider registry summary

### Storage
`GET /v1/storage` → Storage engine stats + table sizes

### Execution
`GET /v1/execution` → Agent execution engine stats

### Auth
`GET /v1/auth/status` → `{auth: bool}`
`POST /v1/auth/token` → `{identity, ttl}` → `{token, identity, expires_in}`
`POST /v1/auth/revoke` → `{token}` → `{revoked: bool}`

## WebSocket API

### Connect
`ws://host:port/v1/ws`

### Client Messages
| Type | Payload | Response |
|------|---------|----------|
| `ping` | `{}` | `{"type": "pong"}` |
| `subscribe` | `{"event_type": "*"}` | Server pushes events |
| `query_events` | `{"filters": {...}}` | `{"type": "events", "events": [...]}` |

### Server Messages
| Type | Payload | Trigger |
|------|---------|---------|
| `event` | `{"type": "event", "event": {...}}` | Any kernel event |
