# Phase 0 Delta: Screens Deep Dive

**File:** `genesis/desktop/screens.py` — 1,395 lines, 11 screens  
**Tests:** 0

## Screen Inventory

| Key | Class | Lines | Description | Keyboard |
|-----|-------|-------|-------------|----------|
| `home` | `EngineeringCommandCenter` | 175 | Command Center — attention, activity, agents, tasks, events | ctrl+h |
| `inspector` | `FabricInspectorScreen` | 120 | Real-time event flow, traffic light, metrics | ctrl+shift+f |
| `agents` | `AgentCollaborationScreen` | 193 | Agent hierarchy graph, list, detail panel | ctrl+shift+a |
| `memory` | `EngineeringMemoryExplorer` | 157 | Events, audit, conversations, tasks, reports, decisions | ctrl+shift+m |
| `repository` | `RepositoryScreen` | 128 | File tree, architecture, health | ctrl+t |
| `timeline` | `EngineeringTimelineScreen` | 135 | Canonical history — events, audit, conversations, tasks | ctrl+e |
| `graph` | `KnowledgeGraphScreen` | 194 | Nodes, edges, types, dependencies, agents overlay | ctrl+g |
| `ai` | `AIOrchestrationCenter` | 97 | Provider list, detail, routing info | ctrl+1 |
| `ce` | `ContinuousEngineeringScreen` | 99 | Watcher log, event log, start/stop | ctrl+2 |
| `reports` | `ReportsScreen` | 73 | Cycle report browser | none |
| `settings` | `SettingsScreen` | 54 | General, kernel, persistence, AI provider info | none |

## Common Patterns

Every screen follows this template:
```python
class XScreen(Screen):
    BINDINGS = [Binding(...)]
    def compose(self) -> ComposeResult: ...
    def on_mount(self): self.set_interval(_DRIVEN_INTERVAL, self._refresh)
    def on_unmount(self): _unsubscribe_events(...)
    def _refresh(self): ...  # read kernel data, write to widgets
```

## Findings

1. **No state sharing** — screens can't communicate (e.g., "open agent x in inspector" from agent screen)
2. **`_refresh` never called once on mount** — first render shows empty data for 30s until interval fires
3. **Memory/Timeline ~85% identical** — both have filter, events/audit/conversations/tasks views, RichLog display
4. **Settings is a glorified debug panel** — exposes raw internal state, no actual settings UI
5. **ReportsScreen loads files from disk** — assumes `Path.cwd() / "Reports"` exists, crashes silently elsewhere
6. **No screen-level error boundaries** — one widget's failure in compose can crash the entire screen
7. **`_selected_agent: Any = None`** — pervasive use of `Any` types breaks type checking

## Recommendations

1. Add `post_mount` hook that calls `_refresh` once before first interval
2. Refactor Memory/Timeline into shared `FilteredDetailScreen(Generic[T])` base
3. Convert Settings to real control panel: toggle auth, change poll interval, set AI provider default
4. Add missing keyboard bindings for Reports/Settings (or remove from SCREENS if unreachable)
5. Use `Path(__file__).parent` instead of `Path.cwd()` for report loading
6. Replace `Any` with proper type annotations
