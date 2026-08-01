# Cycle 016 — Live Engineering Design (M116)

## Current State
All screens poll every 30 seconds via `_DRIVEN_INTERVAL`. Event subscription exists (`_subscribe_events`) but is secondary — the timer is the primary update mechanism. Widgets clear and re-render on every refresh, losing scroll position.

## Target Architecture
Event-driven updates with timer fallback:
```
Event Emission → EventRouter → EventStore
                                  ↓ (event subscription)
                            Widget.update(new data)
                                  ↓ (delta only, no full re-render)
                            Scroll position preserved
                            Selection state preserved
```

## Implementation Plan

### Phase 1 (Current — Cycle 016)
- ✅ Event subscription for all screens and widgets
- ✅ `call_from_thread(refresh_method)` for thread-safe updates
- ✅ WS broadcast for remote event distribution
- ⬜ Widgets update via delta (append new events, don't clear)

### Phase 2 (Cycle 017)
- Make event subscription the primary update path
- Timer only fires if no events received in 30s
- Change widget pattern from `clear() + write(all)` to `write(new only)`
- Preserve scroll position on refresh
- Add "last updated" timestamp to each widget

## Key Challenge
Widgets currently use `clear()` + full re-render. Changing to delta updates requires per-widget refactoring:
- `EventLog` → append new events only (not re-render all)
- `LiveActivityFeed` → append new entries only
- `AgentListView` → update agent status without rebuilding list
- TaskSummary → update counts without rebuilding

Deferred to Cycle 017.
