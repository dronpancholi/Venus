# M147 — Engineering State Engine

## File
`genesis/state/engine.py`, `genesis/state/__init__.py`

## Purpose
Unified canonical engineering state. Every subsystem observes and contributes to the same state. Every mutation produces events. Every transition is recorded and replayable.

## Key Components

### EngineeringState (Singleton)
- `set(domain, key, value)` — atomic state mutation with transition recording
- `get(domain, key)` — read from canonical state
- `get_domain(domain)` — entire domain snapshot
- `update_domain(domain, values)` — batch update
- `observe(domain_pattern, callback)` — subscribe to domain changes
- `transitions(domain, limit)` — replayable history
- `snapshot()` — complete state dump
- `replay(domain)` — full transition history
- `domains()` — list all active domains

### Data Structures
- **StateTransition** — timestamp, domain, key, old/new value, event
- **StateEvent** — event_type, domain, key, value, timestamp, origin

## State Domains Created (auto)
nervous, workflows, decisions, knowledge_v2, proactive_copilot, playbooks, app_platform, command_center, + dynamic domains

## Integration
- **kernel.state_engine** — lazy-loaded singleton, auto-booted
- **EngineeringRegistry** — registered as STATE object
- **NervousSystem** — observes all state changes
- **Every new subsystem** — stores state in state engine
