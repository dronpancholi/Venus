# M150 — Engineering Insight Engine

## File
`genesis/insight/engine.py`, `genesis/insight/__init__.py`

## Purpose
Evidence-backed engineering insights with root cause, historical trend, confidence, affected objects, architecture impact, knowledge impact, timeline references, suggested actions, estimated engineering effort, expected engineering value, potential risks, and related reports/decisions/plans.

## Key Components

### Insight
- `title`, `summary`, `evidence`, `confidence`, `category`, `severity`
- `affected_objects`, `architecture_impact`, `knowledge_refs`, `timeline_refs`
- `suggested_actions`, `estimated_effort`, `estimated_value`, `risks`
- `related_reports`, `related_decisions`, `related_plans`, `source`

### EngineeringInsightEngine
- `create(...)` — full-insight constructor with all metadata
- `list(category, severity, min_confidence)` — filtered queries
- `stats()` — by category/severity distribution
- `_auto_generate()` — automatically creates insights from ReasoningEngine findings

## Integration
- **kernel.insight_engine** — lazy-loaded, auto-booted
- **EngineeringState** — stores insight totals
- **EngineeringRegistry** — registered as INSIGHT object, each insight as RECOMMENDATION
- **ReasoningEngine** — source of auto-generated insights
