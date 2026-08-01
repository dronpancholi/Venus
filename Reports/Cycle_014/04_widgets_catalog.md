# Phase 0 Delta: Widgets Catalog

**File:** `genesis/desktop/widgets.py` — 516 lines, 14 widgets  
**Tests:** 0

## Widget Inventory

| Widget | Parent | Lines | Purpose |
|--------|--------|-------|---------|
| `StatusBar` | `Widget` | 34 | Bottom bar: kernel state, events, services, uptime, keyboard hint |
| `EventLog` | `RichLog` | 25 | Live filtered event stream (last 120s, colored by severity) |
| `AgentListView` | `ListView` | 28 | Agent list with status markers, role badges, task counts |
| `TaskSummary` | `Widget` | 25 | Task graph summary: total nodes, per-status breakdown, critical path |
| `ActivityBar` | `Widget` | 29 | Left sidebar with 11 icon buttons → `app.navigate_to()` |
| `ContextSidebar` | `Widget` | 14 | Right sidebar with title + RichLog (UNUSED — dead code) |
| `SectionTitle` | `Static` | 5 | Bold section title |
| `DataPanel` | `Widget` | 22 | Reusable panel: SectionTitle + RichLog |
| `AttentionWidget` | `Widget` | 61 | Requires attention: agents in error, failed tasks, recent errors |
| `LiveActivityFeed` | `RichLog` | 24 | Recent events (<30s) with severity coloring |
| `FabricTrafficLight` | `Widget` | 32 | Event traffic indicator: green >5/s, yellow >1/s, dim otherwise |
| `AgentCollaborationGraph` | `Widget` | 56 | Agent hierarchy, task ownership, messaging activity |
| `MetricsTimeline` | `Widget` | 34 | Events/s, uptime, services, sessions, executor runs, DB stats |
| `SessionTimeline` | `Widget` | 31 | Active session IDs, types, ages |

## Shared Color Maps

```python
AGENT_STATUS_COLOR      # idle→green, running→cyan, error→red, ...
AGENT_STATUS_MARK       # idle→●, running→▶, error→✗, ...
EVENT_SEVERITY_COLOR    # info→green, warning→yellow, error→red, ...
TASK_STATUS_COLOR       # pending→dim, completed→green, failed→red, ...
CONNECTION_STATUS_COLOR # connected→green, disconnected→red, error→red
```

## Data Access Pattern

Every widget in `on_mount`:
1. `kernel = FabricKernel.instance()`
2. Read data from kernel attributes
3. Write to widget display via `.write()`, `.clear()`, etc.
4. All wrapped in `try/except Exception: pass`

## Findings

1. **`ContextSidebar` is dead code** — defined at line 222, never instantiated or used by any screen
2. **`DataPanel` generates dynamic IDs** — `.log` property creates IDs CSS can't target
3. **Color maps were duplicated 5×** — now centralized in `widgets.py` (bug fix in this cycle)
4. **No compose-time validation** — widgets assume kernel data exists; silent fail if not booted
5. **Widgets don't emit events** — no mechanism for widgets to signal state changes back to screens

## Recommendations

1. Remove `ContextSidebar` class if unused after Cycle 014
2. Add static `id_prefix` to DataPanel so CSS can style child widgets
3. Add `on_data_error` callback mechanism for widgets to notify parent screens
