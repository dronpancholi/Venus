# ADR-004: Capability Dependency Graph

**Status:** Accepted  
**Date:** 2026-06-26

## Context

VPS §9.3 requires capability dependency resolution: all capability dependencies must resolve to registered capabilities and must not contain cycles. The `CapabilityRegistry` had 18 registered capabilities but zero defined dependency edges, leaving §9.3 unenforceable.

## Decision

Add explicit dependency edges between capabilities in `_register_core_capabilities()` using `add_dependency()`, with cycle detection via shared `find_cycles()` from `utils.graph_algorithms`.

18 edges defined across 8 capabilities:
- `compiler` → `parser`
- `graph_exporter` → `knowledge_graph`
- `package_manager` → `plugin_manager`
- `certification` → `metadata_engine`
- `diagnostics` → `capability_registry`, `type_registry`, `knowledge_graph`
- `studio_backend` → `capability_registry`, `compiler`, `type_registry`, `knowledge_graph`, `validator`
- `project_manager` → `capability_registry`, `compiler`, `type_registry`, `knowledge_graph`, `validator`
- `memory_engine` → `knowledge_graph`

## Alternatives Considered

- **Auto-derivation from imports**: Fragile, requires runtime analysis of capability module imports.
- **Config file**: Premature abstraction — no requirement for external configuration yet.

## Consequences

- `validate_all()` now detects unresolved dependencies and circular references.
- `dependency_chain()` returns empty list on cycle detection instead of infinite recursion.
- 10 capabilities remain root nodes (no dependencies), which is valid.

## Verification

- 94 tests pass, zero regressions.
- Architecture checks: 12/12 (1.00 health).
- Zero import cycles introduced.
