# Cycle 016 — Unified Engineering Workspace (M111)

## Historical Context
Previous cycles built 11 independent screens, each with its own compose/refresh/lifecycle. Navigation destroyed screen state on every switch. Escape after navigation left an empty screen stack, crashing the app (P0-1).

## Design Philosophy
The workspace should feel like a single environment, not a collection of tabs. All panels stay alive. Keyboard shortcuts switch instantly. Escape always goes back.

## Implementation

### Screen Caching (`app.py`)
- `_screen_cache: dict[str, tuple[Screen, str | None]]` stores instantiated screens
- `navigate_to(target)` caches current screen, pushes new one
- `action_go_home()` pops all screens back to home
- `action_back()` pops one level

### Screen Identity
Each screen class has a `screen_id` class attribute:
```python
class GenesisHome(Screen):
    screen_id = "home"
```
Used by `navigate_to` for back-navigation tracking.

### Keyboard Shortcuts
Single-key navigation: `h` Home, `i` Inspector, `a` Agents, `m` Memory, `t` Timeline, `g` Graph, `r` Repo, `p` AI, `c` CE. Escape pops back. All 9 panels reachable with one keypress.

### State Persistence
Screens stay alive on the stack until explicitly popped. Scroll position, selection, and timer state persist across navigations.

## Files Changed
- `genesis/desktop/app.py` — `navigate_to` uses push/cache instead of pop/switch; added escape, h-t-c bindings
- `genesis/desktop/screens.py` — added `screen_id` to all 11 screen classes

## Key Decisions
- **Push over Switch**: `push_screen` preserves state; `switch_screen` destroys. Push is preferred for stateful panels.
- **Screen IDs**: Class-level attribute ensures every screen instance knows its identity without runtime detection.
- **No ActivityBar yet**: Keeping the activity bar as a future enhancement; current focus is on keyboard speed.
