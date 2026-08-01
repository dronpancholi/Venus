# M151 — Engineering Decision Intelligence

## File
`genesis/decisions/engine.py`, `genesis/decisions/__init__.py`

## Purpose
Operational engineering decisions with full context, alternatives, reasoning, supporting evidence, counterarguments, architecture diagrams, affected Engineering Objects, reports, timeline, implementation, validation, outcome, and lessons learned.

## Key Components

### DecisionRecord
- `id`, `title`, `problem`, `context`, `alternatives`, `reasoning`
- `supporting_evidence`, `counterarguments`, `affected_objects`, `reports`
- `implementation`, `validation`, `outcome`, `lessons_learned`
- `status` (proposed → decided → implemented)

### EngineeringDecisionIntelligence
- `propose(...)` — create a new decision record
- `decide(id, reasoning, outcome, implementation, validation)` — record decision
- `get(id)`, `search(query, status)`, `stats()`

## Integration
- **kernel.decision_intelligence** — lazy-loaded, auto-booted
- **EngineeringState** — stores decision counts
- **EngineeringRegistry** — decisions registered as DECISION objects
- **Events** — emits decision.proposed, decision.made
