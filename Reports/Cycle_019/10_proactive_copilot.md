# M154 — Proactive Copilot

## File
`genesis/copilot_v2/engine.py`, `genesis/copilot_v2/__init__.py`

## Purpose
Copilot that continuously watches engineering activity and proactively suggests improvements. No longer waits for prompts. Watches for: repository instability, architecture drift, knowledge contradiction, dependency explosion, test quality decline, unhealthy providers, stalled agents, blocked workflows, overdue decisions, accelerating technical debt.

## Key Components

### ProactiveSuggestion
- `title`, `explanation`, `evidence`, `expected_impact`
- `suggested_solution`, `rollback`, `confidence`, `category`, `urgency`

### ProactiveCopilot
- `_watch_loop()` — background thread checks conditions every 30s
- `_check_conditions()` — evaluates DigitalTwin, ReasoningEngine, KnowledgeV2
- `_suggest(...)` — create suggestion, emit copilot.suggestion event
- `suggestions(category, min_urgency, limit)` — query suggestions

### Watch Conditions
1. High function-to-class ratio (>15:1) → architecture warning
2. Critical reasoning findings (>0.7 risk) → critical urgency
3. Knowledge over-clustering (>50 clusters) → consolidation info

## Integration
- **kernel.proactive_copilot** — lazy-loaded, auto-booted
- **EngineeringState** — stores suggestion count
- **EngineeringRegistry** — registered as COPILOT object
- **Events** — emits copilot.suggestion
