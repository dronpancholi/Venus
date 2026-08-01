# CYCLE 015 — PROJECT ECLIPSE: THE CONSOLIDATION CYCLE

**Theme:** Stop adding systems. Make the current ones exceptional.
**Core Objective:** Transform Genesis from "a powerful engineering application" into "a professional engineering platform."
**Constitution:** Every change must simplify, remove duplication, reduce maintenance cost, improve DX/UX/extensibility/observability/performance, and make architectural sense five years from now.

---

## PHASE 0: REPOSITORY RECONSTRUCTION

| Metric | Value |
|--------|-------|
| Total Python files | 464 |
| Total lines of Python | 111,820 |
| Total packages | 73 |
| Total ABC/protocol interfaces | 9 ABC + 17 protocols |
| Total dataclasses | ~192 |
| Total tests (census) | ~10,709 (3,274 baseline verified) |
| Modules with tests | 139/390 (35.6%) |
| Average module maturity | 0.679 |

## CONSOLIDATION MATRIX (M99)

| Area | Competing Impls | Canonical | Migration Priority |
|------|----------------|-----------|-------------------|
| Kernels | 7 | `fabric/kernel.py` → FabricKernel | HIGH |
| Event Systems | 4 | `fabric/events.py` → EventRouter | HIGH |
| Graph Systems | 5 | `graph_v2/core.py` → UnifiedGraph | HIGH |
| Storage Systems | 4 | `persistence/sqlite_store.py` + `fabric/storage.py` | MEDIUM |
| Execution Engines | 4 | `fabric/execution.py` (AI) + `execution/engine.py` (general) | MEDIUM |
| Memory Systems | 7 | `memory_system.py` → UniversalMemorySystem | MEDIUM |
| Plugin Systems | 3 | `plugin/manager.py` → PluginManager | LOW |
| DI Containers | 2 | `di/container.py` → ServiceProvider | MEDIUM |
| Watcher Systems | 2 | `watch/__init__.py` → Watcher | LOW |

## BUG FIXES APPLIED (from TDR P0+P1)

| TDR | Description | Status |
|-----|-------------|--------|
| TDR-003 | Missing `run_server()` — CLI broken | FIXED |
| TDR-002 | `asyncio.run()` in sync thread for WS broadcast | FIXED |
| TDR-042 | Dead `run_desktop()` in `__main__.py` | FIXED |
| TDR-043 | `broadcast_event()` also used unsafe `asyncio.run()` | FIXED |

## REPORTS GENERATED

| # | Report | Status |
|---|--------|--------|
| 1 | Master Report | THIS FILE |
| 2 | Consolidation Matrix | `01_consolidation_matrix.md` |
| 3 | Architecture Delta | `03_architecture_delta.md` |
| 4 | Technical Debt Resolution | `12_technical_debt_resolution.md` |
| 5-24 | Remaining reports | IN PROGRESS |

## ARCHITECTURAL DECISIONS (CYCLE 015)

1. **One Kernel**: FabricKernel is the canonical runtime kernel. UniversalKernel, ServiceKernel, VenusPlatform, PlatformV2, EngineeringOS are deprecated for runtime use.
2. **One Event System**: Fabric EventRouter with EngineeringEvent is canonical. EventBus (legacy) and Kernel EventRouter are deprecated.
3. **One Graph**: UnifiedGraph (graph_v2) is canonical. KnowledgeGraphEngine, PersistentGraphDB, Hypergraph adapt to UnifiedGraph.
4. **One Memory**: UniversalMemorySystem is canonical. Legacy memory/types.py is replaced.
5. **One Plugin System**: PluginManager is canonical. PluginLoader (kernel) is deprecated.
6. **One DI Container**: ServiceProvider (di/container.py) is canonical. DIKernel is deprecated.
