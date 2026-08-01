# Cycle 016 — Technical Debt Delta

## Carried Forward from Cycle 015

| ID | Description | Location | Age | Effort | Priority |
|----|-------------|----------|-----|--------|----------|
| TDR-001 | 30+ bare `except: pass` blocks | Across codebase | 15 cycles | 3d | P0 |
| TDR-004 | 16+ unsafe `storage` accesses without None guard | screens.py, widgets.py | 15 cycles | 1d | P0 |

## New Findings (Cycle 016)

### P0 — Must fix this cycle

| ID | Description | Location | Effort |
|----|-------------|----------|--------|
| TDR-016-01 | `navigate_to` pops screen before push — empty stack on Escape | `app.py:230-233` | 1h |
| TDR-016-02 | WebSocket double delivery — broadcast + per-connection handler | `server.py:53+335` | 2h |
| TDR-016-03 | No `_refresh()` in any screen's `on_mount` — 30s blank screen | All screens | 0.5d |
| TDR-016-04 | Settings entirely read-only — violates user expectation | `screens.py:1344-1395` | 0.5d |
| TDR-016-05 | KnowledgeGraph has no graph — most misleading screen | `screens.py:876-1063` | 2d |
| TDR-016-06 | Provider list in AI screen doesn't respond to clicks | `screens.py:1128-1133` | 2h |
| TDR-016-07 | `_refresh_stats` is a no-op — home screen never updates | `screens.py:192-207` | 1h |
| TDR-016-08 | Watch Mode is cosmetic only — text toggle | `screens.py:1258-1261` | 1h |
| TDR-016-09 | Timer poll destroys scroll/selection on every refresh | `widgets.py:67` (all screens) | 1d |
| TDR-016-10 | Service not-found returns 200 with error body | `server.py:179` | 1h |
| TDR-016-11 | 7 endpoints silently degrade on ImportError | `server.py:182-293` | 1d |
| TDR-016-12 | SearchEverywhere has 2 non-functional buttons | `palette.py:149-152` | 0.5d |
| TDR-016-13 | Keyboard hint "Tab Filter" but Tab not bound | `palette.py:162` | 10m |
| TDR-016-14 | `[R]eports` in subtitle but binding uses `p` | `screens.py:430,440` | 10m |
| TDR-016-15 | No auth on WebSocket | `server.py:326` | 1d |
| TDR-016-16 | Token auth uses unsigned SHA256 — no HMAC | `security_manager.py:84-91` | 1d |

### P1 — Should fix this cycle

| ID | Description | Location | Effort |
|----|-------------|----------|--------|
| TDR-016-17 | Sessions view accesses `kernel._contexts` (private) | `screens.py:136` | 1h |
| TDR-016-18 | 10+ private member accesses across screens | Various screens.py | 0.5d |
| TDR-016-19 | `_message_to_dict` in wrong module (nvidia.py) | `ai/providers/nvidia.py:217` | 1h |
| TDR-016-20 | Ollama `tool_call()` silently drops tools | `ai/providers/ollama.py:145` | 2h |
| TDR-016-21 | Streaming reads one byte at a time | All 3 providers | 1d |
| TDR-016-22 | `count_tokens` is naive space-split | `ai/__init__.py:167` | 1h |
| TDR-016-23 | Plugin Sandbox.validate_module never called | `plugin/manager.py:80` | 2h |
| TDR-016-24 | No circular dependency detection in PluginManager | `plugin/manager.py:141-148` | 1d |
| TDR-016-25 | Deny policies parsed but not enforced | `security_manager.py:56-82` | 1d |
| TDR-016-26 | `summary()` roles count broken | `security_manager.py:116-123` | 1h |
| TDR-016-27 | `RuntimeError` name collision | `core/exceptions.py:42` | 2h |
| TDR-016-28 | `from_dict()` shallow copies — shared mutable state | `events.py:82-86` | 1h |
| TDR-016-29 | Storage `_write()` silently returns None | `storage.py:304-308` | 1d |
| TDR-016-30 | No migration logic — SCHEMA_VERSION recorded only | `storage.py:271` | 2d |
| TDR-016-31 | Event store indexes unused by query() — O(n) scan | `events.py:94-98,124-155` | 1d |
| TDR-016-32 | Event TTL (`expired`) never enforced | `events.py:60-61` | 1h |
| TDR-016-33 | Reports truncated to 5 lines × 120 chars | `screens.py:1313-1334` | 0.5d |
| TDR-016-34 | Last scan shown as Unix timestamp | `screens.py:1219` | 10m |
| TDR-016-35 | Search history stored but never displayed | `palette.py:166` | 0.5d |
| TDR-016-36 | Repository screen has no git integration | `screens.py:613-735` | 2d |
| TDR-016-37 | Event age in seconds (not human-readable) | `screens.py:86` | 10m |
| TDR-016-38 | ActivityBar defined but never composed | `widgets.py:191-220` | 1h |
| TDR-016-39 | ContextSidebar defined but never used | `widgets.py:222-236` | 1h |
| TDR-016-40 | Reports path hardcoded as `Path.cwd() / "Reports"` | `screens.py:544` | 1h |
| TDR-016-41 | Ctrl+Q has no confirmation | `app.py:207` | 1h |
| TDR-016-42 | No `on_unmount` handler — kernel shutdown not called | `app.py:220-228` | 1h |
| TDR-016-43 | TimelineScreen ~80% duplicated from MemoryExplorer | `screens.py:741-869` | 2d |
| TDR-016-44 | Reports filesystem scanning logic duplicated | `screens.py + palette.py` | 1d |

## Debt Summary

| Priority | Count | Estimated Effort |
|----------|-------|------------------|
| P0 (Critical) | 16 | ~11 days |
| P1 (Major) | 28 | ~21 days |
| **Total** | **44** | **~32 days** |

## TDR-001 Analysis (Bare except: pass)

30+ locations including:
- `screens.py:127,151,207,304,385,407,516,568,670,793,807,823,843,936,942,948,952`
- `widgets.py:64,354,389,516`
- `kernel.py:218-220,237-238`
- `server.py:76,332`
- `storage.py:304-308,935-937`
- `events.py:219-222`

## TODO vs Resolved Trend

| Cycle | New TDRs | Resolved | Net |
|-------|----------|----------|-----|
| 014 | 55 | 0 | +55 |
| 015 | 49 | 4 | +45 |
| 016 | 44 | — | +44 |
