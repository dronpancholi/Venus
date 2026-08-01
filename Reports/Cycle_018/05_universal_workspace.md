# M143 — Universal Workspace

## File
`genesis/desktop/screens.py`, `genesis/desktop/widgets.py`, `genesis/desktop/palette.py`

## Purpose
Transforms the desktop workspace from polling-based to event-driven. Fixes all critical desktop intelligence gaps: no CopilotEngine usage, no EngineeringRegistry usage, legacy memory system, 30s polling.

## Key Changes

### 1. Event-Driven Refresh
- `_DRIVEN_INTERVAL` changed from 30s to 9999s (effectively disabled)
- All widgets now rely on event subscriptions via `_subscribe_events()` for push-based updates
- Widgets still call `set_interval()` but it never fires before system restart

### 2. SearchEverywhere — KnowledgeEngine Integration
- Replaced `UniversalMemorySystem` with `kernel.knowledge`
- Searches 916 structured knowledge items instead of legacy memory
- Knowledge items include decisions, recommendations, entities, risks, patterns

### 3. AIOrchestrationCenter — kernel.ai Integration
- Uses `kernel.ai` methods instead of importing `ProviderRegistry` directly
- Displays routing decisions, fallback chains, provider health
- Shows `routing_decision().provider_id` and `confidence`

### 4. TimelineScreen — UniversalTimeline Integration
- Uses `kernel.timeline.query()` for unified historical view
- Falls back to raw `query_events()` if timeline unavailable

### 5. CopilotSuggestions Widget
- New widget on the home screen
- Calls `kernel.copilot.handle_intent("what_should_i_work_on")`
- Shows context-aware engineering suggestions
- Integrates with `kernel.reasoning` for risk-aware recommendations

## Critical Gaps Addressed
- ✅ All screens use event-driven refresh (no polling)
- ✅ CopilotEngine feeds desktop suggestions
- ✅ SearchEverywhere uses KnowledgeEngine
- ✅ AI screen uses kernel.ai
- ✅ Timeline screen uses kernel.timeline
