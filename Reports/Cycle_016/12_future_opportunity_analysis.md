# Cycle 016 — Future Opportunity Analysis

## High-Impact Opportunities

### 1. Desktop as Primary Interface (M110-M111)
**Current**: 11 screens, each independently built, with `navigate_to` crash bug.
**Opportunity**: A single unified workspace with dockable panels, persistent layouts, and state persistence would make Genesis feel like a professional product rather than a collection of screens.
**Impact**: Transformative. Every user interaction improves.

### 2. Engineering Spotlight as Navigation Hub (M112)
**Current**: SearchEverywhere in palette.py has 10 sources, 2 non-functional, no semantic search.
**Opportunity**: Make search the PRIMARY way to navigate Genesis. Everything searchable. AI-assisted ranking. Inline preview. Saved searches.
**Impact**: Eliminates the need to remember which screen has which data.

### 3. Visual Engineering (M113)
**Current**: KnowledgeGraph screen has no graph. Agent "graph" is a text tree. No visualizations anywhere.
**Opportunity**: Replace text dumps with real visualizations using Textual's Tree, DataTable, and Rich renderables.
**Impact**: Makes Genesis immediately more approachable and professional.

### 4. Persistent AI Workspaces (M114)
**Current**: No persistence. No workspace recovery. No conversation history across sessions.
**Opportunity**: AI workspaces with persistent context, memory, and conversation history attached to repositories.
**Impact**: Genesis becomes an AI-native engineering environment rather than a monitoring dashboard.

### 5. Production Hardening (M119)
**Current**: Silent `except: pass` everywhere, unsigned tokens, no crash recovery, no graceful shutdown.
**Opportunity**: Structured error handling, HMAC-signed JWTs, session recovery, and graceful shutdown would make Genesis production-ready.
**Impact**: Trustworthiness. Users can rely on Genesis for daily work.

## Medium-Impact Opportunities

### 6. Plugin SDK (M118)
Developers can extend Genesis with plugins, themes, widgets, and AI providers. Currently possible but undocumented, untemplated, and unenforced.

### 7. Multi-Agent Orchestration (M115)
10 specialized agents with memory, goals, and permissions. Currently the cognitive architecture exists (EngineeringBrain) but is not wired into the desktop or AI pipeline.

### 8. Live Engineering (M116)
All data updates through Fabric events. Currently timer-driven with 30s polling. Event subscription exists but is not the primary mechanism.

## Low-Impact Opportunities (Defer)

### 9. AI Pipeline (M117)
14-stage pipeline (Planner → Retriever → Memory → Context → Router → Model → Verifier → Critic → Reflector → Writer → Generator → Timeline → User).
**Why defer**: Requires multi-agent system first. The stages are well-defined but the infrastructure doesn't exist yet.

### 10. Foundation for AgentOS (M120)
Versioned APIs for all subsystems. Important long-term but premature until the current APIs stabilize.

## Quick Wins (Within First 30% of Cycle)

| Opportunity | Effort | Impact | Why Now |
|-------------|--------|--------|---------|
| Fix `navigate_to` crash | 1h | Critical | Blocks all navigation |
| Add `_refresh()` to all `on_mount` | 0.5d | Critical | 30s blank screen fixed |
| Fix double WebSocket delivery | 2h | High | Data integrity |
| Fix knowledge graph screen | 2d | High | Most misleading screen becomes functional |
| Fix Settings screen | 0.5d | High | Misnomer resolved |
| Fix provider list interactivity | 2h | High | Broken UI fixed |
| Fix search source buttons | 0.5d | High | Non-functional UI fixed |
| Fix Watch Mode placebo | 1h | Medium | Facade removed |
| Fix keyboard binding doc | 30m | Medium | Consistency |
| Fix timestamp formatting | 30m | Low | Human-readable |

## Strategic Bets

| Bet | Investment | Potential Return | Risk |
|-----|-----------|-----------------|------|
| Unified Workspace (M111) | 5-7d | Transformative UX | High — layout persistence is complex |
| Spotlight (M112) | 3-5d | Best nav mechanism | Medium — 20+ source integration |
| Auth Hardening (M119) | 3-5d | Production readiness | Low — well-understood problem |
| Visual Engineering (M113) | 4-6d | Professional polish | Medium — terminal viz limits |
