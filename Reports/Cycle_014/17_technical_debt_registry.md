# Phase 0 Delta: Technical Debt Registry

## Prioritization Key

| Priority | Label | Criteria |
|----------|-------|----------|
| P0 | Critical | Causes crashes, data loss, or blocked workflows |
| P1 | High | Significant performance, maintainability, or UX degradation |
| P2 | Medium | Code quality, duplication, or missing features |
| P3 | Low | Nice-to-have improvements, documentation |

## All Items

| ID | Area | Priority | Description | Impact | Effort |
|----|------|----------|-------------|--------|--------|
| TDR-001 | desktop | P0 | 30+ `except Exception: pass` blocks | Silent failures hide real bugs | 1d |
| TDR-002 | desktop | P0 | `asyncio.run()` in synchronous thread for WS broadcast | Event loop crashes in production | 2h |
| TDR-003 | server | P0 | `run_server()` function missing; CLI crashes | Can't launch server from CLI | 1h |
| TDR-004 | kernel | P0 | 16+ unsafe `storage` accesses without guard | AttributeError when persistence off | 1d |
| TDR-005 | desktop | P1 | No loading indicators on any screen | User sees blank/empty for 30s | 2d |
| TDR-006 | desktop | P1 | No error notifications for data failure | Silent degradation | 1d |
| TDR-007 | desktop | P1 | `navigate_to()` destroys all screen state | Scroll/filter/selection lost on nav | 3d |
| TDR-008 | desktop | P1 | Zero desktop tests | Any change may break UI without detection | 5d |
| TDR-009 | desktop | P1 | Memory ↔ KnowledgeGraph ~85% code duplication | Bug fixes needed in 2 places | 2d |
| TDR-010 | kernel | P1 | 3 competing event systems (fabric, kernel, legacy) | Fragmented observability | 3d |
| TDR-011 | kernel | P1 | 3 competing platform frameworks | Inconsistent service lifecycle | 4d |
| TDR-012 | kernel | P1 | 3 competing plugin systems | No clear extension path | 3d |
| TDR-013 | execution | P1 | TaskExecutor single-thread bottleneck | Sequential execution blocks pipeline | 2d |
| TDR-014 | execution | P1 | No task timeout | Stuck task blocks agent forever | 1d |
| TDR-015 | auth | P1 | 0 auth tests | Token/auth changes have no regression guard | 2d |
| TDR-016 | auth | P1 | Tokens stored in plain dict | Security risk, no persistence | 1d |
| TDR-017 | server | P1 | Lazy imports in route handlers via `__import__` | Each request pays import cost | 1d |
| TDR-018 | storage | P1 | No query pagination (50K+ return) | Memory pressure and latency | 2d |
| TDR-019 | desktop | P2 | CSS in Python string (no syntax validation) | CSS bugs found only at runtime | 1d |
| TDR-020 | desktop | P2 | Palette shortcut mismatches (fixed in this cycle) | User confusion | 2h |
| TDR-021 | desktop | P2 | Color maps duplicated 5× (fixed in this cycle) | Inconsistent colors | 2h |
| TDR-022 | desktop | P2 | `ContextSidebar` dead code | Maintenance burden | 1h |
| TDR-023 | desktop | P2 | Orphaned `EventsScreen` (removed in this cycle) | Dead registration | 1h |
| TDR-024 | desktop | P2 | No debounce on SearchEverywhere keystroke | CPU spike on fast typing | 2h |
| TDR-025 | ai | P2 | No provider health caching | Per-request health check overhead | 1d |
| TDR-026 | ai | P2 | `urllib.request` with no timeout/retry | Network failures hang forever | 1d |
| TDR-027 | kernel | P2 | `boot()` uses `__import__` for lazy loading | Breaks static analysis, no error context | 2h |
| TDR-028 | kernel | P2 | No session TTL/expiry | Memory leak over time | 1d |
| TDR-029 | events | P2 | 24 event types are magic strings | No discoverability, no autocomplete | 1d |
| TDR-030 | events | P2 | EventStore is RAM-only | All events lost on restart | 2d |
| TDR-031 | tests | P2 | No conftest.py (0 shared fixtures) | Massive setup code duplication | 2d |
| TDR-032 | tests | P2 | Singleton reset pattern is fragile | Test ordering dependencies | 1d |
| TDR-033 | tests | P2 | 0 WebSocket tests | WS changes unvalidated | 2d |
| TDR-034 | tests | P2 | 0 auth tests | Security changes unvalidated | 1d |
| TDR-035 | storage | P2 | 3 storage subsystems doing the same thing | Data duplication, confusion | 3d |
| TDR-036 | storage | P2 | StorageEngine path relative to cwd | Breaks when run from other dirs | 1h |
| TDR-037 | agents | P2 | No agent persistence recovery | All agents lost on restart | 2d |
| TDR-038 | agents | P2 | AgentScheduler.tick() never called | Feature is dead code | 1d |
| TDR-039 | execution | P2 | Role prompts in source code | Can't customize without code change | 1d |
| TDR-040 | execution | P2 | No task retry logic | Failed tasks require manual intervention | 2d |
| TDR-041 | conversations | P2 | No LLM integration for summarization | Summarize is metadata-only | 1d |
| TDR-042 | conversations | P2 | Decision extraction uses naive string match | Misses true decisions | 1d |
| TDR-043 | conversations | P2 | No conversation export | Data lock-in | 1d |
| TDR-044 | desktop | P3 | `_selected_agent: Any` — pervasive Any typing | No type safety | 1d |
| TDR-045 | desktop | P3 | `DataPanel` generates dynamic IDs | CSS can't style children | 1d |
| TDR-046 | desktop | P3 | No keyboard for Reports/Settings screens | Mouse-only reachable | 1h |
| TDR-047 | desktop | P3 | ReportsScreen loads from `Path.cwd()` | Breaks outside project dir | 1h |
| TDR-048 | server | P3 | No CORS middleware | Browser clients blocked | 1h |
| TDR-049 | server | P3 | No rate limiting | Event emission can be spammed | 1d |
| TDR-050 | server | P3 | Legacy `api/router.py` is dead code (32 routes, 1 handler) | Maintenance burden | 1d |
| TDR-051 | ai | P3 | No streaming in desktop | All AI responses are synchronous | 2d |
| TDR-052 | kernel | P3 | UniversalKernel has no consumers | Dead code for runtime | 2d |
| TDR-053 | plugin | P3 | No example plugin has ever been created | Plugin API is untested | 3d |
| TDR-054 | plugin | P3 | Sandbox is documentary only (not enforced) | False security guarantee | 1d |
| TDR-055 | plugin | P3 | No semver resolution in dependency check | Version conflicts undetected | 2d |

## Summary

| Priority | Count | Total Effort (est.) |
|----------|-------|-------------------|
| P0 | 4 | ~3 days |
| P1 | 14 | ~30 days |
| P2 | 25 | ~30 days |
| P3 | 12 | ~15 days |
| **Total** | **55** | **~78 days** |

## Top 10 By Impact

1. **TDR-003**: Missing `run_server()` — CLI broken
2. **TDR-002**: `asyncio.run()` in sync thread — production crashes
3. **TDR-004**: Unsafe storage access — crashes when persistence off
4. **TDR-005**: No loading indicators — poor UX
5. **TDR-006**: No error notifications — silent failures
6. **TDR-008**: Zero desktop tests — UI changes untested
7. **TDR-013**: Single-threaded executor — performance bottleneck
8. **TDR-014**: No task timeout — stuck tasks
9. **TDR-015-016**: Auth has no tests + plain token storage
10. **TDR-019**: CSS in Python string — runtime-only validation
