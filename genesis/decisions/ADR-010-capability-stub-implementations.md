# ADR-010: Capability Stub Implementations

**Status:** Accepted
**Date:** 2026-06-26

## Context

The CapabilityRegistry registered 18 capabilities (VPS §9.3), but 5 had zero implementation:

- `package_manager` — VenusPM package management
- `memory_engine` — Institutional memory management
- `project_manager` — Project lifecycle management
- `certification` — Artifact certification
- `security` — Security validation and policies

These capabilities appeared in dependency graphs and API contracts but had no executing code. Any service depending on them (e.g., `studio_backend` depending on `security`) would fail at runtime.

## Decision

Create minimal stub implementations for each capability following the established EventBus-integrated pattern:

1. **PackageManager** (`genesis/package/manager.py`): Wraps PluginManager; manages package install/uninstall/list with EventBus events
2. **MemoryEngine** (`genesis/memory/engine.py`): Namespace-based key/value store for institutional memory across sessions with EventBus events
3. **ProjectManager** (`genesis/project/manager.py`): Manages project create/close/list lifecycle with EventBus events
4. **CertificationEngine** (`genesis/certification/engine.py`): Manages artifact certification state (bronze/silver/gold/platinum) with EventBus events
5. **SecurityValidator** (`genesis/security/validator.py`): Policy-based validation engine with audit log and EventBus events

All stubs:
- Accept `event_bus: EventBus | None = None` (backward compatible)
- Implement `_emit()` for EventBus integration
- Provide meaningful operations that can be extended
- Register in the VenusPlatform DI container
- Return concrete types (not `NotImplementedError`)

## Specification Mapping

- VPS §9.3 (Capability Resolution): All 18 capabilities now have implementing code
- VPS §5.6 (Observation Model): package.*, memory.*, project.*, artifact.*, security.* events added to event catalog

## Files Modified

| File | Change |
|---|---|
| `genesis/package/manager.py` | New — PackageManager stub |
| `genesis/memory/engine.py` | New — MemoryEngine stub |
| `genesis/project/manager.py` | New — ProjectManager stub |
| `genesis/certification/engine.py` | New — CertificationEngine stub |
| `genesis/security/validator.py` | New — SecurityValidator stub |
| `genesis/platform.py` | All 5 new services wired into boot lifecycle |
| `genesis/tests/test_architecture.py` | Added 5 new modules to LAYER_4 |

## Future

These stubs represent minimal implementations. Full implementations should:
- Wire persistence stores (PackageDB, MemoryStore, CertificationStore)
- Add storage-backed operation patterns
- Integrate with VRIP intelligence gathering
