# Cycle 016 — Phase 0: Complete Product Audit

## Historical Context

Genesis has evolved through 15 cycles from a proof-of-concept engineering framework into a 73-package, 464-file, 112K-line platform. Each cycle added screens, subsystems, and capabilities. The result is a platform with world-class architectural ambition but uneven execution quality — some components (EventRouter, EngineeringBrain) are well-architected; others (SettingsScreen, KnowledgeGraph screen, Auth) are clearly prototype-grade.

This is the first audit performed from a **pure user perspective** — no assumptions about internal architecture, no deference to historical decisions.

## Audit Methodology

All 464 Python files were examined. Every screen was tested for: loading state, error state, empty state, data freshness, keyboard navigation, visual consistency. Every API endpoint was reviewed for: response shape, error handling, auth, performance. Every plugin and AI provider was audited for: completeness, DX, error handling.

## Key Findings by Severity

### Critical (Users will notice immediately)

| ID | Finding | Location | Impact |
|----|---------|----------|--------|
| P0-1 | `navigate_to` pops screen then pushes — Escape leaves empty stack | `app.py:230-233` | App crash on back navigation |
| P0-2 | WebSocket double delivery — every event sent twice per client | `server.py:53+335` | Duplicate events, double bandwidth |
| P0-3 | SettingsScreen is entirely read-only — no settings can be changed | `screens.py:1344-1395` | Misnamed, frustrating dead end |
| P0-4 | KnowledgeGraph screen has NO graph visualization — just stats | `screens.py:876-1063` | Most misleading screen name |
| P0-5 | Provider list in AIOrchestrationCenter does not respond to clicks | `screens.py:1128-1133` | UI element is decorative, not functional |
| P0-6 | `_refresh_stats` in Command Center is a no-op — fetches data, does nothing | `screens.py:192-207` | Home screen never updates |
| P0-7 | "Watch Mode" button in CE screen is cosmetic only (toggles text) | `screens.py:1258-1261` | Placeholder masquerading as feature |

### High (Impairs daily use)

| ID | Finding | Location |
|----|---------|----------|
| P0-8 | 30s timer poll destroys scroll/selection on every refresh (ALL screens) | `widgets.py:67` |
| P0-9 | No loading indicators anywhere — every screen is blank until first timer tick | All screens |
| P0-10 | `try/except Exception: pass` in 30+ locations — systemic silent failure | Across codebase |
| P0-11 | No auth on WebSocket endpoint | `server.py:326` |
| P0-12 | Service not-found returns HTTP 200 with error body, not 404 | `server.py:179` |
| P0-13 | 7 API endpoints silently degrade on ImportError with no HTTP status change | `server.py:182-293` |
| P0-14 | SearchEverywhere has 2 non-functional source buttons (Files, Knowledge) | `palette.py:149-152` |
| P0-15 | Keyboard hint "Tab Filter" in SearchEverywhere but Tab is not bound | `palette.py:162` |
| P0-16 | `memory` screen subtitle says `[R]eports` but binding uses `p` | `screens.py:430,440` |
| P0-17 | `has_permission` and `check_policy` in SecurityManager are never called from API | `server.py` |
| P0-18 | Token auth uses unsigned SHA256 — no HMAC, no signing key | `security_manager.py:84-91` |
| P0-19 | Sessions view accesses `kernel._contexts` (private attribute) | `screens.py:136` |
| P0-20 | 10+ accesses to private `_` members across screens | Across `screens.py` |

### Medium (Quality of life)

| ID | Finding | Location |
|----|---------|----------|
| P0-21 | `"All systems normal"` in AttentionWidget is misleading — only checks agent/task status | `widgets.py:328-329` |
| P0-22 | Agent Collaboration "Graph" is a text tree, not a visual graph | `widgets.py:407-447` |
| P0-23 | Reports screen truncates to 5 lines × 120 chars — cannot read full reports | `screens.py:1313-1334` |
| P0-24 | Last scan time in CE screen is Unix timestamp, not human-readable | `screens.py:1219` |
| P0-25 | No `SearchEverywhere` — search history is stored but never displayed | `palette.py:166` |
| P0-26 | Repository screen has no git integration — it's a plain file explorer | `screens.py:613-735` |
| P0-27 | Event age shown in seconds (e.g. "5432s ago") instead of human format | `screens.py:86` |
| P0-28 | `DataPanel` uses `id(self)` in compose — unstable across re-compose | `widgets.py:245-267` |
| P0-29 | TimelineScreen is 80% code-duplicated from MemoryExplorer | `screens.py:741-869` |
| P0-30 | SettingsScreen data loads once on mount — never updates | `screens.py:1363-1364` |

### Low (Polish)

| ID | Finding | Location |
|----|---------|----------|
| P0-31 | Ctrl+Q quits immediately — no confirmation, watchers abandoned | `app.py:207` |
| P0-32 | No `on_unmount` handler on App — kernel shutdown never called | `app.py:220-228` |
| P0-33 | ActivityBar widget defined but never composed into any screen | `widgets.py:191-220` |
| P0-34 | ContextSidebar defined but never used | `widgets.py:222-236` |
| P0-35 | Reports directory path hardcoded as `Path.cwd() / "Reports"` | `screens.py:544` |
| P0-36 | Event store indexes built but never used by `query()` — O(n) iteration | `events.py:94-98,124-155` |
| P0-37 | Event TTL (`expired` property) never enforced | `events.py:60-61` |
| P0-38 | `_message_to_dict` lives in nvidia.py, imported by ollama + openai_compat | `ai/providers/nvidia.py:217` |
| P0-39 | Ollama `tool_call()` silently ignores tools — delegates to `chat()` | `ai/providers/ollama.py:145` |
| P0-40 | All streaming reads one byte at a time (`resp.read(1)`) | All 3 providers |
| P0-41 | `count_tokens` is naive space-split — inaccurate for code | `ai/__init__.py:167` |
| P0-42 | Plugin `Sandbox.validate_module` exists but is never called | `plugin/manager.py:80` |
| P0-43 | No circular dependency detection in PluginManager | `plugin/manager.py:141-148` |
| P0-44 | Deny policies parsed but never enforced in SecurityManager | `security_manager.py:56-82` |
| P0-45 | `summary()` roles count is broken (nonsensical list comprehension) | `security_manager.py:116-123` |
| P0-46 | `RuntimeError` name collision — Genesis defines its own, shadowing built-in | `core/exceptions.py:42` |
| P0-47 | `EngineeringEvent.from_dict()` shallow-copies — shared mutable state risk | `events.py:82-86` |
| P0-48 | Storage `_write()` silently returns `None` on error — all callers ignore it | `storage.py:304-308` |
| P0-49 | No migration logic — `SCHEMA_VERSION` recorded but never drives changes | `storage.py:271` |
| P0-50 | Commit strategy inconsistent — some store methods commit, most don't | `storage.py` |

## Product Quality Score: 5.5/10

| Dimension | Score | Why |
|-----------|-------|-----|
| Navigation | 4/10 | navigate_to crash, 30s scroll reset, no back stack |
| Data Freshness | 5/10 | Timer-based, event subscription exists but is secondary |
| Error Handling | 3/10 | 30+ silent `except: pass`, no loading states, no error screen |
| Keyboard UX | 7/10 | Good coverage, some binding inconsistencies |
| Visual Design | 6/10 | Clean CSS, but KnowledgeGraph has no graph, Settings is read-only |
| Onboarding | 2/10 | Blank screen at startup, no first-run experience |
| API Design | 6/10 | Good routes, inconsistent response shapes |
| Auth & Security | 3/10 | Unsigned tokens, no WS auth, no permission enforcement |
| Plugin System | 5/10 | Good foundation, no enforcement, no topological sort |
| AI Providers | 5/10 | Good ABC design, prototype implementations (byte-streaming) |

## What Feels World-Class

- EventRouter + EngineeringEvent model (16-field tracing, dead-letter queue, wildcard subscriptions)
- EngineeringBrain cognitive architecture (10 subsystems with documented integrations)
- PluginManager lifecycle events integrated with EventBus
- FabricKernel shutdown orchestrates all subsystems in reverse order
- Storage schema — 10 well-designed tables with 17 indexes and proper WAL pragmas
- Dark theme CSS with hover states and consistent color palette
- 3,274 passing tests with conftest.py modernization
- Separation of concerns: kernel, events, storage, AI, plugins each in their own modules

## What Feels Prototype

- Silent `except Exception: pass` as error-handling strategy
- No loading states on any screen (blank until first timer tick)
- Auth: unsigned tokens, no credential validation, disabled by default
- Knowledge Graph screen with no graph visualization
- Settings screen that is read-only
- Watch Mode toggle that is cosmetic
- Provider list that doesn't respond to clicks
- Repository screen with no git integration
- Reports truncated to 5 lines
- `navigate_to` that breaks back navigation
- Byte-at-a-time HTTP streaming
- No migration system for storage schema
- Tests at 35.6% module coverage
