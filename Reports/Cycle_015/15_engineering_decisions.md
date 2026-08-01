# Cycle 015 — Engineering Decisions Record

## ADR-015-001: One Kernel Architecture

**Status:** Approved  
**Context:** 7 competing kernel/platform implementations  
**Decision:** FabricKernel (`genesis/fabric/kernel.py`) is the canonical runtime kernel  
**Consequences:**
- All new runtime code must use FabricKernel
- UniversalKernel, ServiceKernel, VenusPlatform, PlatformV2, EngineeringOS are deprecated for new development
- Migration adapters provided for existing consumers

---

## ADR-015-002: One Event System

**Status:** Approved  
**Context:** 4 competing event routing implementations  
**Decision:** Fabric EventRouter (`genesis/fabric/events.py`) with `EngineeringEvent` is canonical  
**Consequences:**
- 30 EventBus consumers get a compatibility adapter, not full rewrite
- Kernel EventRouter and PlatformV2 EventRouter are deprecated
- Event types become an `StrEnum` (no more magic strings)

---

## ADR-015-003: One Graph Architecture

**Status:** Approved  
**Context:** 5 competing graph implementations  
**Decision:** UnifiedGraph (`genesis/graph_v2/core.py`) is canonical; PersistentGraphDB remains as SQLite backend  
**Consequences:**
- KnowledgeGraphEngine adapters exist and are sufficient
- Hypergraph wrapped as UnifiedGraph layer with hyperedge extension
- KnowledgeGraph/PlanetaryKnowledgeGraph consumers migrate to UnifiedGraph layers

---

## ADR-015-004: Async WebSocket Safety

**Status:** Implemented  
**Context:** `asyncio.run()` called from synchronous EventRouter thread  
**Decision:** Use `asyncio.run_coroutine_threadsafe()` when an event loop exists, fall back to thread-safe queue  
**Implementation:** `server.py` — `_ws_broadcast_handler` detects running loop, dispatches accordingly  
**Verification:** All WS send operations are now non-blocking in the EventRouter thread

---

## ADR-015-005: Server Launcher as First-Class Entry Point

**Status:** Implemented  
**Context:** `__main__.py` imported `run_server` which didn't exist  
**Decision:** Add `run_server()` to `server.py` with uvicorn integration  
**Implementation:** `genesis server` now launches a working FastAPI+WebSocket server on `127.0.0.1:8377`

---

## ADR-015-006: Shared Test Fixtures

**Status:** Implemented  
**Context:** 0 conftest.py, 0 shared fixtures, manual singleton reset in 10+ files  
**Decision:** Create `tests/conftest.py` with 22 fixtures + `pytest.ini` with markers  
**Implementation:** Autouse singleton reset, kernel/server/desktop/provider/agent/WS/security fixtures  
**Migration:** All new tests use fixtures; existing tests migrate incrementally

---

## ADR-015-007: Consolidation Over Feature Addition

**Status:** Active principle  
**Context:** 73 packages, 464 files, 111K+ lines with extensive duplication  
**Decision:** No new subsystems in Cycle 015. All effort goes to consolidating existing ones.  
**Enforcement:** Architectural review gate — every PR must identify which existing system it consolidates
