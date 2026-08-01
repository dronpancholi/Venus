# Cycle 016 — Genesis Home Experience (M110)

## Historical Context
The previous home screen (`EngineeringCommandCenter`) had a critical P0 bug: `_refresh_stats` was a no-op. It fetched kernel health and stats but never updated any widget. The 30-second blank screen at startup existed because no `_refresh()` was called before `set_interval`.

## Design
The home screen answers "What should I work on next?" through three columns:
- **Left**: Attention (errors, failures, blocked items) + Recent Activity
- **Center**: Active Agents + Task Summary
- **Right**: Live Events + Active Sessions

## Implementation

### `GenesisHome` Class (`screens.py`)
- Composes 7 widgets: AttentionWidget, LiveActivityFeed, AgentListView, TaskSummary, EventLog, SessionTimeline, StatusBar
- `_greeting()` in `on_mount` shows uptime and keyboard shortcut hints
- `_refresh_home()` triggers refresh on all 6 child widgets
- Event subscription + 30s timer fallback

### P0 Fixes Applied
1. **`_refresh_stats` → `_refresh_home`**: Now calls `refresh()`, `refresh_agents()`, `poll_events()`, `poll()` on each child widget
2. **Initial refresh**: `_refresh_home()` called before `set_interval` — no more blank screen
3. **Each widget guarded**: Every `query_one` call in its own try/except — one widget failure doesn't block others

## CSS (`app.py`)
- `#home-title`, `#home-subtitle`, `#home-left/center/right`, `#home-attention/activity/agents/tasks/events/sessions`
- Same 3-column layout (35/35/30) as previous Command Center
- Title shows "Genesis Home" with uptime subtitle

## Key Decisions
- **Widget isolation**: Each widget refresh in its own try/except — prevents one failure from cascading
- **Keep all existing widgets**: Reuses AttentionWidget, EventLog, AgentListView, etc. — no new widget types needed
- **No recommendations section yet**: The subtitle no longer promises Recommendations, matching reality
