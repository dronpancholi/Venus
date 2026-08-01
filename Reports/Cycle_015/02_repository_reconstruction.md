# Cycle 015 — Repository Reconstruction (Phase 0)

## Fresh Metrics (Do Not Trust Previous Reports)

| Metric | Cycle 014 Claimed | Actual (Fresh) |
|--------|------------------|----------------|
| Total Python files | ~390 | **464** |
| Total lines of Python | ~40,000 | **111,820** |
| Total packages | 73 | **73** |
| ABC interfaces | 9 | **9** |
| Protocol classes | 14 | **17** |
| Dataclass definitions | ~192 | **192** |
| Test count | 3,274 (baseline) | 3,274 (verified) / ~10,709 (census) |

## Package Inventory

### Core Infrastructure (14 packages)
- `genesis/core/` — EngineBase, GenesisException, MetadataStore, UIRType
- `genesis/config/` — PlatformConfig (45 lines)
- `genesis/di/` — ServiceProvider DI container
- `genesis/events/` — Legacy EventBus (97 lines, to be deprecated)
- `genesis/utils/` — Graph algorithms, identity, serialization
- `genesis/fabric/` — FabricKernel + all Fabric subsystems (16 files, ~4,000 lines)

### Platform (7 packages)
- `genesis/desktop/` — TUI application (5 files, 2,486 lines)
- `genesis/server.py` — FastAPI REST + WebSocket (367 lines)
- `genesis/cli/` — CLI commands
- `genesis/watch/` — File/Git provider watchers
- `genesis/plugin/` — Plugin system (3 files, 476 lines)
- `genesis/package/` — Package management (63 lines)
- `genesis/project/` — Project management (62 lines)

### Intelligence (8 packages)
- `genesis/brain/` — EngineeringBrain + cognition (7 files, ~2,000 lines)
- `genesis/intelligence/` — Analysis, metrics, planning, reports (14 files, ~2,000 lines)
- `genesis/planning/` — Strategic/architectural/research planning
- `genesis/reasoning.py` — Reasoning engine (364 lines)
- `genesis/reverse_engineer.py` — Reverse engineering (910 lines)
- `genesis/repository_scientist.py` — Repository analysis (247 lines)
- `genesis/repository_engineer.py` — Repository engineering (221 lines)
- `genesis/repository_graph.py` — Repository graph (241 lines)

### Knowledge (7 packages)
- `genesis/knowledge_graph.py` — Knowledge graph (320 lines)
- `genesis/hypergraph.py` — Hypergraph knowledge core (648 lines)
- `genesis/graph/` — Graph engine (310 lines)
- `genesis/graph_v2/` — Unified graph (9 files, ~1,815 lines)
- `genesis/graphdb/` — Persistent graph DB (835 lines)
- `genesis/ontology.py` — Ontology engine (1,398 lines)
- `genesis/meta_model.py` — Meta model (711 lines)

### Memory (5 packages)
- `genesis/memory/` — Engineering + institutional memory (5 files, ~1,220 lines)
- `genesis/memory_system.py` — Universal memory system (413 lines)
- `genesis/datalake/` — Data lake (492 lines)
- `genesis/temporal/` — Time series + snapshots (546 lines)
- `genesis/memory_system.py` — Legacy memory types

### Agents & Execution (5 packages)
- `genesis/fabric/agents.py` — Agent runtime (424 lines)
- `genesis/fabric/execution.py` — Execution engine (473 lines)
- `genesis/fabric/tasks.py` — Task graph (312 lines)
- `genesis/execution/` — General execution engine (7 files, ~823 lines)
- `genesis/runtime/` — Runtime executor (266 lines)

### AI (2 packages)
- `genesis/ai/` — AI provider interface + router + registry (3 files, 401 lines)
- `genesis/ai/providers/` — NVIDIA, Ollama, OpenAI-compat (3 files, 593 lines)

### Platform Programs (17 root files)
- `genesis/platform.py` (725), `platform_v2.py` (512), `platform_adapter.py` (728)
- `genesis/engineering_os.py` (331), `service_kernel.py` (637)
- `genesis/brain_v4.py` (738), `omega_loop.py` (6,575!) 
- `genesis/ontology.py` (1,398), `mathematics.py` (800), `mathematics_v2.py` (669)
- And 7 more (atlas, discovery, economics, evolution, governance, hypergraph, etc.)

## Technical Debt Hotspots

### By File Size
| File | Lines | Issue |
|------|-------|-------|
| `omega_loop.py` | 6,575 | God file — needs decomposition |
| `ontology.py` | 1,398 | God file — ontology + entities + temporal |
| `atlas.py` | 1,297 | God file — self-analysis + evolution |
| `reverse_engineer.py` | 910 | Core reverse engineering logic |

### By Package Maturity (lowest)
| Package | Maturity | Lines | Issue |
|---------|----------|-------|-------|
| `autonomous/` | 0.33 | 330 | No tests, low maturity |
| `certification/` | 0.33 | 65 | No tests |
| `package/` | 0.33 | 65 | No tests |
| `project/` | 0.33 | 64 | No tests |
| `security/` | 0.33 | 64 | No tests |
| `execution/` | 0.40 | 848 | Execution consolidation needed |
| `desktop/` | 0.52 | 2,486 | 0 tests |
| `plugin/` | 0.58 | 476 | 0 plugin-specific tests |

## Key Files Referenced in This Report

| Path | Purpose |
|------|---------|
| `genesis/fabric/kernel.py` | Canonical kernel |
| `genesis/fabric/events.py` | Canonical event system |
| `genesis/fabric/storage.py` | Fabric storage engine |
| `genesis/graph_v2/core.py` | Canonical graph |
| `genesis/memory_system.py` | Canonical memory system |
| `genesis/plugin/manager.py` | Canonical plugin system |
| `genesis/di/container.py` | Canonical DI container |
| `genesis/persistence/sqlite_store.py` | Platform storage stores |
| `genesis/desktop/app.py` | Desktop TUI application |
| `genesis/server.py` | API + WebSocket server |
| `genesis/__main__.py` | CLI entry point |
| `tests/conftest.py` | Shared test fixtures (NEW) |
| `pytest.ini` | Pytest configuration (NEW) |
