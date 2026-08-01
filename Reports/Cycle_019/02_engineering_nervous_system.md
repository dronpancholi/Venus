# M146 — Engineering Nervous System

## File
`genesis/nervous/engine.py`, `genesis/nervous/__init__.py`

## Purpose
Continuous engineering signal propagation. Every subsystem emits state signals that propagate automatically through Fabric. No manual refresh, no polling, no explicit synchronization.

## Key Components

### EngineeringNervousSystem
- `emit_signal(source, domain, key, value)` — injects a signal into the state engine
- `on_signal(pattern, callback)` — subscribe to signal patterns
- `signal_history(domain, limit)` — replayable signal log
- `_wire_subsystem_signals()` — bridges state engine changes to signal listeners

### Signal Flow
```
Subsystem → state.set() → state._notify() → nervous_system._on_state_change()
  → signal dispatch to listeners → signal_history append
```

## Integration
- **kernel.nervous_system** — lazy-loaded, auto-booted
- **EngineeringState** — all signals flow through canonical state
- **EngineeringRegistry** — registered as NERVOUS_SYSTEM object
