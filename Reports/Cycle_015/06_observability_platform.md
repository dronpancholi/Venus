# Cycle 015 — Observability Platform (M103)

## Current State

| Feature | Status | Implementation |
|---------|--------|----------------|
| Event metrics | ✅ | FabricKernel.metrics — counters, gauges, histograms |
| Audit log | ✅ | FabricKernel.audit — immutable audit trail |
| Health endpoint | ✅ | `/v1/health` — uptime, services, sessions |
| Kernel stats | ✅ | `/v1/kernel/stats` — full telemetry |
| Storage metrics | ✅ | Read/write counts, table sizes |
| Performance metrics | ❌ | No per-operation timing |
| Tracing | ❌ | No distributed tracing |
| Memory profiling | ❌ | No memory usage tracking |
| CPU profiling | ❌ | No CPU usage tracking |
| Event throughput | ⚠️ | FabricTrafficLight shows events/s (desktop only) |
| Failure tracking | ❌ | No centralized error log |
| Slow operations | ❌ | No operation duration tracking |

## What Exists

### FabricMetrics (`genesis/fabric/metrics.py` — 98 lines)
- Counters: increment named counters
- Gauges: set named gauge values
- Histograms: record values for percentile computation
- `snapshot()` returns all current metrics
- `histogram(name)` returns p50/p95/p99/last

### AuditLog (`genesis/fabric/audit.py` — 116 lines)
- `record(action, actor, resource, detail, severity)` → Entry
- `query(action, actor, limit)` → filtered entries
- `count()` → total entries

### FabricTrafficLight (desktop widget)
- Samples event delta per second (10s rolling average)
- Green >5/s, Yellow >1/s, Dim otherwise

## Target Architecture

```
┌─────────────────────────────────────────────┐
│             Observability Layer              │
├──────────────────┬──────────────────────────┤
│  MetricsService  │  TraceService             │
│  ─ counters      │  ─ span collection        │
│  ─ gauges        │  ─ trace context          │
│  ─ histograms    │  ─ TraceEvent integration │
│  ─ snapshots     │                           │
├──────────────────┴──────────────────────────┤
│  DiagnosticsEngine                          │
│  ─ slow operation detection (>1s)           │
│  ─ failure tracking                         │
│  ─ performance budget enforcement           │
├─────────────────────────────────────────────┤
│  Desktop Observability Screen               │
│  ─ real-time metrics dashboard              │
│  ─ per-screen render timing                 │
│  ─ operation waterfall                      │
│  ─ error log                                │
└─────────────────────────────────────────────┘
```

## Recommendations

1. **Add operation timing** to FabricKernel — wrap all public methods with `_record_duration()`
2. **Add trace context** — extend `TransactionSpan` with parent/child spans
3. **Add ObservabilityScreen** — desktop screen showing real-time metrics, event throughput, audit log
4. **Add `/_ops` endpoint** to server — list slow operations, recent failures
5. **Add performance budgets** — `_DRIVEN_INTERVAL` (30s) should warn if actual refresh >10s
