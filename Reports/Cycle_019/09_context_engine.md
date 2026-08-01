# M153 — Context Engine

## File
`genesis/context/engine.py`, `genesis/context/__init__.py`

## Purpose
Automatic context assembly for every interaction. Every request automatically receives context from all subsystems — no manual context building required.

## Key Components

### EngineeringContext
- `query`, `workspace`, `project`, `repository`, `architecture`, `timeline`
- `knowledge`, `memory`, `decisions`, `plans`, `workflows`, `ai`, `agents`
- `insights`, `recent_events`, `related_objects`, `errors`, `timestamp`

### ContextEngine
- `build(query, project, object_id, depth)` — assembles context from all subsystems
- `summarize(ctx, max_lines)` — produces human-readable context summary

### Data Sources
DigitalTwin (repository), KnowledgeEngine (knowledge), MemoryV2 (memory), UniversalTimeline (timeline), TaskGraph (workflows), AIOrchestrationEngine (AI), AgentRuntime (agents), EngineeringRegistry (related objects), EventStore (events)

## Integration
- **kernel.context_engine** — lazy-loaded, auto-booted
- **EngineeringRegistry** — registered as SERVICE object
- **Every subsystem** — feeds into context assembly
