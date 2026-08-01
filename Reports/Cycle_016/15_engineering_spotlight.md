# Cycle 016 — Engineering Spotlight (M112)

## Historical Context
`SearchEverywhere` had 10 source buttons, 2 of which (Files, Knowledge) were non-functional. The footer incorrectly claimed Tab was bound for filtering. Search history was stored but never displayed.

## Design
Spotlight is the primary navigation mechanism. Search 10+ sources simultaneously. Tab cycles through sources. History shows recent queries when input is empty.

## Implementation

### Enhanced `SearchEverywhere` (`palette.py`)

**New Features:**
1. **Files source**: Searches `genesis/` directory for `.py` files matching query
2. **Knowledge source**: Queries `UniversalMemorySystem` for matching entries
3. **Tab cycling**: `Tab` cycles through all sources in order (all → events → agents → ... → commands)
4. **Search history**: Stored in `_search_history` (max 50 entries), displayed when input is empty or < 2 chars
5. **Footer text corrected**: Shows "↵ Open ↑↓ Tab Cycle Source Esc Close"
6. **Source button counts**: Results grouped by source type (future enhancement)

### Bug Fixes
1. **Non-functional buttons**: Files and Knowledge now have real query logic
2. **Wrong keyboard hint**: Tab is now actually bound to `action_cycle_source`
3. **Conversation search**: Fixed to use `search(query=q, ...)` instead of just `search(limit=10)`

### Data Flow
```
User types query (≥2 chars)
  → on_input_changed
    → _perform_search(query)
      → kernel.query_events (Events)
      → kernel.agent_runtime.list_agents (Agents)
      → kernel.task_graph.list_nodes (Tasks)
      → kernel.registry.list (Services)
      → kernel.audit.query (Audit)
      → kernel._conversation_engine.search (Conversations)
      → COMMANDS iteration (Commands)
      → Filesystem glob (Files, Reports)
      → UniversalMemorySystem.query (Knowledge)
    → Results sorted by relevance, capped at 30
    → Displayed in ListView
    → Added to search_history
```

## Files Changed
- `genesis/desktop/palette.py` — full rewrite of `_perform_search`, added `action_cycle_source`, `_show_history`, fixed bindings

## Key Decisions
- **No debounce**: Replaced by immediate search on ≥2 chars (simpler, and search is fast enough)
- **30 result cap**: Prevents overwhelming the terminal with results
- **Tab cycles through all sources**: All → Events → Agents → ... → Commands → back to All
- **History in memory only**: Not persisted to disk (future enhancement)
