# Cycle 016 — Consistency Audit

## Naming Consistency

### Screen Names
| Screen | Composed Name | Docstring Claim | Reality |
|--------|--------------|-----------------|---------|
| EngineeringCommandCenter | `"home"` | Mission control | Dashboard with dead refresh |
| FabricInspectorScreen | `"inspector"` | Kernel internals | Event/metric/session viewer |
| AgentCollaborationScreen | `"agents"` | Collaboration | Agent list + text tree |
| EngineeringMemoryExplorer | `"memory"` | Memory exploration | Multi-source data browser |
| EngineeringTimelineScreen | `"timeline"` | Filtering, replay, inspection | Simplified memory explorer |
| KnowledgeGraphScreen | `"graph"` | Interactive knowledge graph | System statistics browser |
| AIOrchestrationCenter | `"ai"` | Provider management | Read-only provider stats |
| ContinuousEngineeringScreen | `"ce"` | Auto-detection, recommendations | Watcher start/stop |

### Key Inconsistencies
1. `KnowledgeGraphScreen` — docstring says "Interactive knowledge graph with search, filtering, relationship explorer, overlays" — zero of these exist.
2. `Settings` — read-only system info, not settings.
3. `EngineeringTimelineScreen` — docstring promises "filtering, replay, and inspection" — replay and inspection do not exist.
4. `[R]eports` binding label vs actual `p` key — mismatch between subtitle and bindings.

## Response Shape Consistency

### API Inconsistencies
| Endpoint | Response Shape | Pattern |
|----------|---------------|---------|
| `/v1/health` | `{"status": ..., "uptime_seconds": ..., ...}` | Flat dict |
| `/v1/kernel/stats` | KernelStats `__dict__` | Dataclass dump |
| `/v1/events` | `{"count": N, "events": [...]}` | Wrapped |
| `/v1/services` | `{"count": N, "services": [...]}` | Wrapped |
| `/v1/metrics` | `{"total_events": N, ...}` | Flat dict (no count) |
| `/v1/services/{id}` (missing) | `{"error": "not found"}` with status 200 | 200 with error |
| All import failures | `[]` or `{"active": False}` | Silent degradation |

### Error Response Inconsistencies
| Scenario | Status | Body |
|----------|--------|------|
| Auth missing | 401 | `{"error": "missing authorization"}` |
| Auth expired | 401 | `{"error": "invalid or expired token"}` |
| Service not found | 200 | `{"error": "not found"}` |
| ImportError | 200 | `[]` or `{"active": False}` |

## Keyboard Binding Consistency

| Screen | Binding Pattern | Issue |
|--------|----------------|-------|
| Inspector | `E/M/S` for views, `R` for refresh | Clean |
| Memory Explorer | `1-6` for views, `R` for refresh | Clean |
| Timeline | `1-4` for views, `R` for refresh | Clean |
| Agents | `P/S/T/D/C` — all single letters | Pause/Start/Terminate — no mnemonics |
| CE | `S/X/W` — Start/Stop/Watch | Watch does nothing |
| AI | Only Escape + `R` | No view switching |
| Settings | Only Escape | No interaction possible |

## Error Handling Consistency

| Pattern | Locations | Assessment |
|---------|-----------|------------|
| `except Exception: pass` | 30+ locations | Silent failure — worst pattern |
| `except ImportError: return empty` | 7 server endpoints | OK for optional deps, but no HTTP signal |
| `try: ... except: show dim message` | 10+ screen locations | Better — user sees something |
| `try: ... except: notify user` | Palette | Best — user is informed |
| `no try at all` | Settings, KnowledgeGraph hardcoded | Worst — crashes on error |

## Code Style Consistency

| Concern | Assessment |
|---------|------------|
| Typing | Good — most functions typed, dataclasses used |
| Import style | Inconsistent — `from X import Y` and `import X.Y.Z` both used |
| Private member access | 10+ accesses to `_` prefixed attrs across class boundaries |
| Docstrings | Good — most classes/screens have docstrings |
| Error handling | Poor — 3 different patterns with no guidance |
| Commit strategy | Inconsistent in storage — some commit, most don't |

## Consistency Score: 4/10

| Dimension | Score | Key Issues |
|-----------|-------|------------|
| Screen Naming | 3/10 | Misleading names, docstring/reality gaps |
| API Responses | 3/10 | 3+ response shapes, 200 for errors |
| Keyboard Bindings | 5/10 | Inconsistent patterns across screens |
| Error Handling | 3/10 | 4 patterns with no consistency rule |
| Code Style | 5/10 | Good typing, poor private access, mixed imports |
