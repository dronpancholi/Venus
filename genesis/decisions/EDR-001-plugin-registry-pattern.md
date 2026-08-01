# EDR-001: ModulePluginRegistry for Engine Decoupling

**Status:** Implemented
**Date:** 2025-06-28
**Author:** Venus Chief Systems Architect (Autonomous Session)

## Problem

OmegaLoop directly imported from 6 engine modules at the module level
(reasoning, repository_scientist, repository_engineer, repository_economics,
digital_civilization, reverse_engineer) plus 3 core modules (ontology,
meta_model, mathematics). This created a star-shaped import graph where
any change to any engine potentially required modifying OmegaLoop's
import section. There was no programmatic way to enumerate available
engines, check if an engine was registered, or add a new engine without
touching OmegaLoop's top-level code.

## Context

The existing `genesis.plugin` package contained `PluginManager` (236 lines)
designed for external plugins with YAML manifests, sandboxing, and hot
reload. Using `PluginManager` for internal engine registration would require
every engine to have a manifest file. The system needed a simpler registry
for internal engine discovery.

At the time of decision, OmegaLoop had 21 `from genesis.*` references to
engine modules across 5 methods, plus 6 at module level. All engines were
lazily initialized (created in method bodies, not at `__init__` time).

## Evidence

- 6 module-level engine imports acting as coupling points
- 21 total `from genesis.*` references to engine modules
- `from __future__ import annotations` already active — type annotations
  are lazy strings and don't require runtime imports
- `PluginManager` already existed but was designed for external plugins

## Alternatives Considered

### Alternative A: Message Bus Pattern
Engines communicate through a typed message bus. OmegaLoop subscribes
to engine events rather than importing engines.
**Rejected**: Overengineered for single-process execution. Genesis engines
need synchronous API access, not async event-driven communication.

### Alternative B: Dependency Injection Container
A DI container manages engine lifecycle and wiring. OmegaLoop receives
engines through constructor injection.
**Rejected**: Genesis engines have complex mutual dependencies (reasoning
depends on ontology, scientist depends on reasoning, engineer depends on
both). A DI container would introduce configuration that is harder to
understand than the current lazy initialization.

### Alternative C: Full PluginManager Adoption
Make every genesis engine a full PluginManager-compatible plugin.
**Rejected**: As Atlas's Stage 7 design analysis noted, "Plugins maintain
the duplication problem." PluginManager is for third-party plugins.

### Alternative D: Canonical Namespace Pattern
All engines export through a single `genesis.engines` namespace.
**Rejected**: Just moves coupling to a different file. The fundamental issue
is module-level import coupling, not the number of import statements.

## Chosen Solution

Create `ModulePluginRegistry` (110 lines) in `genesis/plugin/registry.py`:
- Dict-based mapping of string name → EnginePlugin
- Supports eager (instance) and lazy (factory) registration
- `to_dict()` provides complete snapshot of all registered engines
- `get_by_type()` enables type-based discovery
- Rejects duplicate registrations with KeyError

OmegaLoop uses the registry via `_register_plugins()` and routes all
engine initialization through `registry.register(name, "engine",
instance=engine)`.

## Migration Impact

- **Positive**: 6 module-level engine imports → 0. Engine imports now lazy
  in method bodies. Registry provides programmatic discovery.
- **Negative**: Method-level import duplication (21 `from genesis.*`
  references across 5 methods instead of 6 at module level).
- **Zero**: All existing `self.reasoning` etc. attribute references
  continue to work. No consumer code changes needed.

Files modified:
- `genesis/plugin/registry.py` — CREATED (110 lines)
- `genesis/plugin/__init__.py` — Updated exports
- `genesis/omega_loop.py` — Refactored imports, added `_register_plugins()`
- `genesis/atlas.py` — Removed unused imports, Stage 9 updated

## Rejected Designs

- **Message Bus**: Would require rewriting engine communication patterns.
- **DI Container**: Would require configuration files or decorators.
- **Full PluginManager**: Would require manifests for every engine.

## Expected Lifetime

Indefinite. The registry pattern is foundational. It may be extended with
lifecycle hooks, health checks, and version resolution but the core
(name → instance mapping) should remain stable.

## Review Schedule

Review after 6 months. Evaluate:
1. Are all engine registrations still going through the registry?
2. Has `to_dict()` been useful for discovery?
3. Should lifecycle hooks be added?

## Future Reconsideration Conditions

- If the system moves to a microservices architecture, the registry must
  be replaced with a service discovery mechanism.
- If PluginManager is ever extended to support internal plugins natively,
  ModulePluginRegistry could be deprecated in its favor.
