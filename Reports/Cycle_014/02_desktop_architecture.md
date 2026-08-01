# Phase 0 Delta: Desktop Architecture

**Directory:** `genesis/desktop/` — 5 files, 2,486 lines  
**Tests:** 0  
**Maturity:** 0.52

## Architecture

```
app.py (GenesisDesktop App)
  ├── WORKSPACE_CSS  (180 lines of CSS)
  ├── SCREENS dict   (11 named screens → classes)
  ├── BINDINGS       (13 app-level keyboard bindings)
  ├── navigate_to()  (pop + push screen)
  └── action_go_*    (9 navigation methods)
      │
      ├── screens.py  (11 Screen classes, 1,395 lines)
      ├── palette.py  (2 ModalScreen classes, 281 lines)
      └── widgets.py  (14 custom widgets, 516 lines)
```

## Key Architectural Decisions

| Decision | Current Approach |
|----------|-----------------|
| **Data access** | Every screen reads from `FabricKernel.instance()` — no duplication |
| **Refresh model** | `_DRIVEN_INTERVAL` (30s) polling + `_subscribe_events()` event-driven refresh |
| **Navigation** | `pop_screen()` + `push_screen(target)` — destroys and recreates screens |
| **CSS** | Single `WORKSPACE_CSS` string in `app.py` — no per-screen CSS splitting |
| **Screen lifecycle** | `on_mount` subscribes events, `on_unmount` unsubscribes |

## Event-Driven Architecture

Every data-displaying screen uses `_subscribe_events()` which calls `FabricKernel.on_event()` and schedules `call_from_thread(refresh_method)`. A 30s `set_interval` fallback ensures stale data doesn't persist.

**Thread safety:** `call_from_thread()` posts refresh to Textual's main thread — handlers run in event router thread (non-Textual thread).

## Findings

1. **No state persistence** — `navigate_to()` destroys and recreates every screen on every nav. Scroll position, filter state, and selection are all lost.
2. **30+ `except Exception: pass`** blocks across all screens — silent failure hides real issues
3. **Zero loading indicators** — no `LoadingIndicator` or skeleton screens during data fetch
4. **Zero error notifications** — failed data accesses show `[dim]Not available[/]` with no toast/reason
5. **CSS in Python string** — `WORKSPACE_CSS` is a raw string, no syntax validation, no editor support
6. **No desktop tests** — 0 unit tests for screens, widgets, palette, or app
7. **Memory/KnowledgeGraph share ~85% code** — both have near-identical filter/search/detail patterns
8. **Unsafe `call_from_thread`** — some screens don't guard against stale widget references during rapid navigation

## Recommendations

1. Persist screen state in `SCREENS` dict or a `_screen_state` dict keyed by tab name
2. Add `_handle_error(msg)` helper wrapping `self.app.notify()` for all data access
3. Add `LoadingIndicator` widget that shows during `on_mount` before first `_refresh`
4. Extract per-screen CSS into class-level `CSS` variables or separate `.tcss` files
5. Create `test_desktop.py` with Textual `pilot` tests for navigation and screen render
6. Merge Memory/KnowledgeGraph into a shared `FilteredDetailScreen` base class
7. Guard all `call_from_thread` with `try: self.app.call_from_thread(...)` retry on `NoneError`
