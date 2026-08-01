# M161: System Health Engine

**Status:** Implemented
**Files:** `genesis/health/engine.py`, `genesis/health/__init__.py`
**Integration:** FabricKernel.health_engine, 5 default collectors

---

## Design

### Health Dimensions

| Dimension | Weight | Description |
|-----------|--------|-------------|
| availability | 3.0 | Is the subsystem responding? |
| latency | 1.5 | Response time |
| errors | 2.0 | Error rate |
| memory | 1.0 | Memory consumption |
| queue_depth | 1.0 | Backlog depth |
| state_freshness | 1.5 | How current is state data |
| knowledge_freshness | 1.0 | Knowledge staleness |
| ai_provider_health | 2.0 | AI provider reachability |
| workflow_health | 1.5 | Workflow execution status |
| workspace_health | 1.0 | Workspace integrity |
| graph_health | 1.5 | Graph consistency |
| thread_health | 1.0 | Background thread status |
| boot_health | 2.0 | Boot sequence status |
| event_bus_health | 1.5 | Event bus status |

### Architecture

```
SystemHealthEngine
  ├── register_collector(subsystem, fn)  → HealthCollector
  ├── unregister_collector(subsystem)
  ├── snapshot()                         → HealthSnapshot (immediate poll)
  ├── score()                            → EngineeringHealthScore
  ├── history(subsystem, dimension)      → list[HealthSnapshot]
  ├── get_trend(subsystem, dimension)    → HealthTrend
  └── health_by_dimension()              → dict[str, float]

HealthCollector
  └── collect()                          → HealthEntry

HealthEntry
  ├── subsystem: str
  ├── metrics: list[HealthMetric]
  └── score: float                       # Weighted average of metrics

HealthSnapshot
  ├── timestamp
  ├── entries: dict[str, HealthEntry]
  └── overall_score: float               # System-wide health
```

### Default Collectors

| Collector | Metrics | Source |
|-----------|---------|--------|
| kernel | availability, thread_health | KernelState, thread list |
| boot | boot_health, availability | BootReport |
| event_bus | event_bus_health, queue_depth | MessageBus |
| state | state_freshness, availability | StateEngine |
| ai | ai_provider_health | AI engine provider list |

### Trend Analysis

- Stores history of all metrics
- Calculates trend direction (improving/declining/stable) based on last 10 vs last 5 samples
- Health score tracks improving vs declining trends across all subsystems

## API

```python
kernel.health_engine                  # SystemHealthEngine
kernel.health_engine.snapshot()       # Poll all collectors
kernel.health_engine.score()          # EngineeringHealthScore
kernel.health_engine.history()        # Last N snapshots
he.health_by_dimension()              # Health by dimension
```

## Results

| Metric | Value |
|--------|-------|
| Health dimensions | 14 |
| Default collectors | 5 |
| Max snapshots retained | 100,000 |
| Snapshot creation | On-demand (eventual auto-collection) |
| Trend window | 10 samples |

## Future Improvements

1. **Auto-snapshot timer** — periodic health collection on a configurable interval
2. **Alert thresholds** — warn when subsystem score drops below threshold
3. **Health decay** — stale health entries decay over time
4. **Dashboard widget** — health gauge on desktop home screen
5. **Historical persistence** — SQLite storage for health history across restarts
