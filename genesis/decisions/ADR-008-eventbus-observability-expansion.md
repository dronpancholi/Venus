# ADR-008: EventBus Observability Expansion

**Status:** Accepted
**Date:** 2026-06-26

## Context

VPS §5.6 (Observation Model) mandates that all platform operations must be observable. The EventBus was initially wired into 5 of 9 domain services (Compiler, Graph, Executor, Metadata, Diagnostics). Three services operated without event visibility:

- **RepositoryIndexer**: Scans entire repository silently
- **PluginManager**: Plugin lifecycle (registration, activation, deactivation) invisible
- **CapabilityRegistry**: Capability registration and validation invisible

## Decision

Wire EventBus into the remaining 3 domain services using the established pattern:

1. **Optional constructor injection**: `event_bus: EventBus | None = None` — backward compatible
2. **Private `_emit()` helper**: Centralizes the null-check pattern
3. **Lifecycle events**: Each service emits events at its key lifecycle transitions

### Event Catalog (new)

| Service | Events |
|---|---|
| RepositoryIndexer | `indexer.scan.started`, `indexer.scan.completed`, `indexer.dead_files.detected` |
| PluginManager | `plugin.registered`, `plugin.activated`, `plugin.deactivated` |
| CapabilityRegistry | `capability.registered`, `capability.validation.completed`, `capability.registry.cleared` |

### Existing Event Catalog (already wired)

| Service | Events |
|---|---|
| Compiler | `compiler.compile.started`, `compiler.compile.completed`, `compiler.compile.error`, `compiler.generate.started`, `compiler.generate.completed` |
| KnowledgeGraphEngine | `knowledge.node.added`, `knowledge.edge.added` |
| ExecutionEngine | `workflow.created`, `workflow.planned`, `workflow.completed`, `workflow.failed`, `task.running`, `task.completed`, `task.failed`, `task.blocked` |
| MetadataEngine | `metadata.record.created`, `metadata.record.updated`, `metadata.record.deleted` |
| Diagnostics | `diagnostics.run.started`, `diagnostics.run.completed` |

## Specification Mapping

- VPS §5.6 (Observation Model): All 8 domain services now observable
- VPS Principle 7: "No operation may execute silently" — now satisfied

## Files Modified

| File | Change |
|---|---|
| `genesis/indexer/indexer.py` | Added `event_bus` param + emit events |
| `genesis/plugin/manager.py` | Added `event_bus` param + emit events |
| `genesis/capability/registry.py` | Added `event_bus` param + emit events |

## Design Consistency

All 8 services follow the identical pattern: optional constructor injection, `_emit()` helper, `self._bus is not None` guard. This ensures uniform observability posture across the platform and makes the EventBus swappable (Redis/RabbitMQ in Genesis-III) without per-service changes.
