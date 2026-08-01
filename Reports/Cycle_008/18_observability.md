# CYCLE 008 — OBSERVABILITY REPORT

## Can You See What's Happening?

⸻

## Current Observability

| Capability | Status | Details |
|------------|--------|---------|
| Health check | ✅ | GET /v1/health — status, uptime, counts |
| Event log | ✅ | GET /v1/events — query by type/severity/source |
| Agent status | ✅ | GET /v1/agents — list live agents |
| Task graph | ✅ | GET /v1/tasks — list task nodes |
| Watcher status | ✅ | GET /v1/watch — per-watcher state |
| Provider status | ✅ | GET /v1/providers — health check |
| Live events | ✅ | WS /v1/ws — real-time event stream |
| Audit log | ✅ | GET /v1/audit — recent audit entries |
| Metrics | ✅ | GET /v1/metrics — platform metrics |
| Memory | ✅ (backend) | Engineering memory accessible via kernel |
| Knowledge graph | ✅ (backend) | Graph accessible via kernel |
| CLI | ✅ | `genesis --help` |
| Desktop dashboards | ✅ | Home, Agents, Events screens |
| File change detection | ✅ | Watcher events in event log |
| Error visibility | ⬜ | No structured error reporting |
| Performance metrics | ⬜ | No latency histograms |
| Health history | ⬜ | No uptime tracking |
| Distributed tracing | ⬜ | Single process — not yet needed |

## Key Observability Flows

```
File change → Watcher → Fabric Event → EventStore
                                       → WebSocket → Desktop TUI
                                       → API query → curl
                                       → (future) → notification
```

## Metrics Exported

| Metric | Source |
|--------|--------|
| `event_count` | EventStore |
| `uptime_seconds` | GenesisAPI |
| `watcher_count` | ContinuousEngineering |
| `agent_count` | AgentScheduler |
| `provider_count` | ProviderRegistry |

## Future Observability (Cycle 009)

- Structured logging (JSON logs)
- Event latency histograms
- Agent execution traces
- Memory/knowledge query logging
- File change rate metrics
