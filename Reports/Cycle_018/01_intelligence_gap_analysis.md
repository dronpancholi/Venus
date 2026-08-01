# Phase 0: Genesis Intelligence Gap Analysis

> Cycle 018 — Project Odyssey
> Complete repository re-evaluation: discovering disconnected intelligence, manual workflows, and automation opportunities

---

## Executive Summary

Genesis has rich intelligence in three independent layers (Fabric events/core, AI provider/router, EngineeringRegistry objects) but **zero integration points** between them. The desktop displays data but never helps users make decisions. AI providers exist but are never auto-registered. The server is fully functional but has no consumers. 15 critical integration gaps prevent the platform from operating as an autonomous engineering environment.

This analysis identifies **42 gaps** across 5 categories, each backed by repository evidence. Every gap maps to one or more Cycle 018 missions.

---

## 1. Disconnected Intelligence (12 gaps)

Capabilities that are fully implemented but not consumed by any other system.

| # | Gap | Evidence | Owners | Severity |
|---|-----|----------|--------|----------|
| G1 | AI providers never auto-registered | `registry.py:17`, `test_ai_platform.py:94-227` (tests only); `ai/providers/__init__.py` missing | M141 | **Critical** |
| G2 | `AIRouter.routing_decision()` never called | `router.py:121-140` — fallback chain built but `chat()` never tries it; `screens.py:1161` prints "active" only | M141 | High |
| G3 | `ProviderRegistry.summarize()` missing `"available"` key | `registry.py:76-88` vs `screens.py:1130` — desktop renders empty list forever | M141 | High |
| G4 | WebSocket queue never drained | `server.py:39` — `_ws_queue` written via `put_nowait` but never consumed by any background task | M142 | High |
| G5 | Server endpoints have no consumers | `desktop/app.py:225-227` bypasses server; `run_server()` uncalled in production | M145 | Medium |
| G6 | No screen uses `EngineeringRegistry` for live data | All 11 screens call `FabricKernel.instance()` directly — no registry abstraction | M135, M143 | High |
| G7 | No screen uses `CopilotEngine` | Zero references to copilot in any screen — no proactive suggestions | M135 | **Critical** |
| G8 | No screen uses `UniversalTimeline` | `TimelineScreen` queries `kernel.query_events()` directly, not timeline | M134 | High |
| G9 | No screen uses `AutonomousReview` | Zero references — no review results visible anywhere | M142 | Medium |
| G10 | `SearchEverywhere` uses legacy `UniversalMemorySystem` | `palette.py:269-277` imports old `memory_system`, not `KnowledgeEngine` | M136 | **Critical** |
| G11 | `KnowledgeEngine` findings not stored as EngineeringObjects | `reasoning.py` findings returned but not registered in registry | M133 | Medium |
| G12 | Timeline requires explicit `refresh()` | `timeline.py:43` — no auto-refresh on kernel events | M134 | Medium |

---

## 2. Manual Workflows (10 gaps)

Operations that still require manual intervention instead of being event-driven.

| # | Gap | Evidence | Owners | Severity |
|---|-----|----------|--------|----------|
| G13 | Universal 30-second polling | `widgets.py:67` — `_DRIVEN_INTERVAL = 30`; every screen uses `set_interval` instead of event push | M143 | **Critical** |
| G14 | Event subscription redundant with polling | `widgets.py:51-56` — handler calls same `_refresh` as timer, no filtering by event type | M143 | High |
| G15 | ReportsScreen reads filesystem directly | `screens.py:1318` — `Path.cwd() / "Reports"` bypasses knowledge systems | M135 | High |
| G16 | No auto-refresh after mutation | Screens don't refresh after agent pause/resume/terminate — wait 30s | M143 | Medium |
| G17 | Navigation is manual between screens | `app.py:234-244` — no contextual linking, no "follow-the-chain" | M135 | High |
| G18 | Provider registration requires manual code | Zero `register()` calls in production; no config-file or plugin-based registration | M141 | **Critical** |
| G19 | AI routing requires manual setup | Kernel has no `_ai` or `_ai_router`; `execution.py:150` creates its own | M141 | High |
| G20 | Server must be started manually | `server.py:353` — `run_server()` has no entry point, no lifecycle management | M145 | Medium |
| G21 | KnowledgeEngine requires explicit `index_reports()` | `engine.py:35` — no auto-index on boot or file change | M133 | High |
| G22 | No auto-discovery of available providers | `registry.py:69-73` — `healthy_providers()` never auto-populated | M141 | High |

---

## 3. Missing Abstractions (7 gaps)

Components that still expose implementation details instead of clean interfaces.

| # | Gap | Evidence | Owners | Severity |
|---|-----|----------|--------|----------|
| G23 | `EventStore._store` accessed as private | `kernel.py:113` — `return self._event_router._store`; `kernel.py:329` — direct `.query()` passthrough | M133 | High |
| G24 | `FabricKernel._contexts` is private dict | `kernel.py:84` — no `list_sessions()`, `session_count()`, `active_session_ids()` | M133 | Medium |
| G25 | `query_events()` is unvalidated pass-through | `kernel.py:328-329` — arbitrary kwargs passed straight to `EventStore.query()` | M133 | Medium |
| G26 | `FabricKernel.lookup()` accesses private stores | `kernel.py:211` — `self._event_router._store` private access even in kernel | M133 | Medium |
| G27 | No clean query facade for intelligence layer | No pagination, cursor-based iteration, or projection support on any query method | M133 | Medium |
| G28 | `AgentRuntime._contexts` is private dict | `agents.py:159` — same pattern as kernel, no query API | M138 | Medium |
| G29 | 18 role prompts hardcoded as flat dict | `execution.py:30-132` — no storage, no versioning, no registry link | M141 | High |

---

## 4. Architecture Gaps (8 gaps)

Structural issues that prevent the platform from operating as an autonomous environment.

| # | Gap | Evidence | Owners | Severity |
|---|-----|----------|--------|----------|
| G30 | Desktop + Server are completely independent | `app.py:225` vs `server.py:353` — two parallel access paths, zero coordination | M145 | High |
| G31 | AI layer not a first-class kernel subsystem | Kernel has `knowledge`, `reasoning`, `copilot`, `timeline`, `review` — but no `ai` or `ai_router` | M141 | **Critical** |
| G32 | 18 role prompts disconnected from EngineeringRegistry | `execution.py:30-132` vs `engineering/object.py:11-34` — two type systems for agents | M138 | High |
| G33 | Settings are not configurable | `screens.py:1362-1416` — static text page, no inputs, no toggles, no saves | M143 | High |
| G34 | No cross-screen navigation context | Screens are islands — no shared selection, no "jump to related" | M135 | High |
| G35 | Data rendered in 5+ duplicate formats | Events (6 formats), agents (5), tasks (5), conversations (4), metrics (4) | M143 | Medium |
| G36 | No event-driven architecture despite event system | All screens fall back to 30s polling; event subscriptions are redundant | M142, M143 | **Critical** |
| G37 | No auto-refresh on state change | Screens only update on timer or manual Ctrl+R | M142 | Medium |

---

## 5. Desktop Intelligence Gaps (5 gaps)

Screens that are simple viewers instead of intelligent workspaces.

| # | Screen | Current State | Desired State | Evidence |
|---|--------|--------------|---------------|----------|
| G38 | GenesisHome | "What to work on?" passive dashboard | Actionable triage: restart agents, reprioritize tasks | `screens.py:162-247` |
| G39 | AIOrchestrationCenter | Read-only provider list | Configure, enable/disable, test providers | `screens.py:1085-1176` |
| G40 | SettingsScreen | Static text display | Real configuration with toggles and saves | `screens.py:1362-1416` |
| G41 | KnowledgeGraphScreen | Tree hierarchy (not a graph) | True graph with cross-entity edges | `screens.py:907-1078` |
| G42 | RepositoryScreen | File browser + hardcoded docs | Live architecture + git + dependency analysis | `screens.py:642-765` |

---

## Gap → Mission Mapping

| Mission | Gaps Addressed | Implementation Priority |
|---------|---------------|------------------------|
| M133: Digital Twin | G11, G21, G23, G24, G25, G26, G27 | **P0** — foundation for all others |
| M134: Observatory | G8, G12 | P1 |
| M135: Explorer | G6, G7, G15, G17, G34 | P1 |
| M136: Search V2 | G10 | P1 |
| M137: Autonomous Planner | (all G43-G48, new component) | P2 |
| M138: Memory V2 | G28, G32 | P2 |
| M139: Multi-Project | (new component) | P2 |
| M140: Live Architecture | (new component) | P2 |
| M141: AI Orchestration | G1, G2, G3, G18, G19, G22, G29, G31 | **P0** — core infrastructure |
| M142: Engineering Automation | G4, G9, G36, G37 | P1 |
| M143: Universal Workspace | G13, G14, G16, G33, G35 | **P0** — UX foundation |
| M144: Visual Reasoning | (new component) | P2 |
| M145: AgentOS Foundation | G5, G20, G30 | P2 |

---

## Effort Estimates

| Category | Gaps | Estimated Effort |
|----------|------|-----------------|
| **Critical** (blocks autonomy) | 7 | ~3-4 sessions |
| **High** (significant improvement) | 17 | ~5-7 sessions |
| **Medium** (important polish) | 13 | ~3-4 sessions |
| **Low** (nice to have) | 5 | ~1-2 sessions |

---

## Appendix: Repository Evidence Index

| Finding | File | Line |
|---------|------|------|
| AI providers never registered in production | ai/registry.py, ai/providers/*.py | all |
| routing_decision() never called | ai/router.py | 121-140 |
| summarize() missing "available" | ai/registry.py | 76-88 |
| WS queue never drained | server.py | 39, 55-67 |
| All 11 screens use 30s polling | desktop/screens.py | numerous |
| Event subscription redundant | desktop/widgets.py | 51-56 |
| ReportsScreen reads filesystem | desktop/screens.py | 1318 |
| SearchEverywhere uses old memory | desktop/palette.py | 269-277 |
| No _ai_router in kernel | fabric/kernel.py | 94-98 |
| EventStore._store accessed private | fabric/kernel.py | 113, 329 |
| _contexts is private dict | fabric/kernel.py | 84 |
| query_events unvalidated passthrough | fabric/kernel.py | 328-329 |
| Role prompts hardcoded | fabric/execution.py | 30-132 |
| Desktop bypasses server | desktop/app.py | 225-227 |
