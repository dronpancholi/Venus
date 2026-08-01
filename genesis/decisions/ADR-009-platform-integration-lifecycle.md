# ADR-009: Platform Integration Lifecycle

**Status:** Accepted
**Date:** 2026-06-26

## Context

The Venus platform had 8 domain services (Compiler, KnowledgeGraphEngine, ExecutionEngine, MetadataEngine, Diagnostics, RepositoryIndexer, PluginManager, CapabilityRegistry), 5 persistence stores (VPS §10.1), an EventBus, and a DI container — but no unified entry point. Each service was created manually; there was no lifecycle that:

1. Initializes all services with their dependencies injected
2. Runs VRIP intelligence automatically on startup
3. Provides graceful shutdown with checkpoint persistence
4. Produces a platform-wide health summary

VPS §5.7 requires a defined platform lifecycle (bootstrap/initialize/run/shutdown).

## Decision

Create `genesis/platform.py` with `VenusPlatform` class implementing the full lifecycle:

1. **bootstrap()**: Creates the DI ServiceProvider via `di.bootstrap()`, registers all 5 persistence stores + EventBus
2. **boot()**: Creates all 8 domain services with store + EventBus injection, registers them in DI, runs VRIP intelligence, emits `platform.boot.completed` event
3. **shutdown()**: Saves VRIP checkpoint, emits `platform.shutdown` event, closes all SQLite connections
4. **CLI entry**: `python -m genesis.platform [boot|status|vrip|cli]`

### Design Decisions

- `VenusPlatform` is the single entry point. Domain services are accessed via `platform.compiler`, `platform.graph`, etc.
- VRIP runs automatically on boot — every platform start updates the knowledge graph
- All services follow the established `event_bus: EventBus | None = None` constructor pattern
- The `RegisterIntelligence` instance survives the full platform lifecycle and saves checkpoint on shutdown

## Specification Mapping

- VPS §5.7 (Platform Lifecycle): bootstrap/boot/shutdown now implemented
- VPS §5.6 (Observation Model): platform.boot.completed and platform.shutdown events emitted
- VPS §10.1 (Storage Providers): All 5 stores wired and lifecycle-managed

## Files Modified

| File | Change |
|---|---|
| `genesis/platform.py` | New — VenusPlatform class with full lifecycle |
| `genesis/tests/test_architecture.py` | Added genesis.platform to LAYER_5_MODULES |

## Alternatives Considered

- **Each service booted independently**: Would violate VPS §5.7 lifecycle requirement. No central health check possible.
- **ServiceProvider as the entry point**: The DI container is infrastructure, not a lifecycle manager. VenusPlatform wraps it with domain-specific wiring.
- **VRIP as a separate process**: Running VRIP in-process on every boot ensures intelligence is always current. Async offload can be added later.
