# Cycle 016 — Roadmap Delta

## Where We Are

Genesis has 464 Python files (112K lines), 73 packages, 11 desktop screens, 16 REST endpoints, WebSocket push, 3 AI providers, 2 plugin systems, 5+ event/pub-sub systems, 10 cognitive subsystems, and 3,274 tests.

The architecture is sound. The ambition is correct. The execution is uneven.

## Where We Need to Go

### Immediate (Cycle 016)
1. **Product Polish**: Fix all P0 UX bugs (navigate_to crash, blank first render, Settings misnomer, Knowledge Graph facade, Watch Mode placebo, non-functional provider list)
2. **Unified Workspace**: Replace 11 separate screens with a dockable, resizable, persistent-layout workspace
3. **Engineering Spotlight**: Universal search that actually searches everything
4. **Visual Intelligence**: Convert text views into actual visualizations (graphs, trees, dashboards)
5. **Production Hardening**: Auth with real tokens, error handling, crash recovery, graceful shutdown

### Near-term (Cycle 017)
1. **AI Pipeline**: 14-stage observable pipeline
2. **Multi-Agent**: 10 specialized agents with memory, goals, permissions
3. **Human+AI Collaboration**: Persistent AI workspaces
4. **Live Engineering**: Event-driven everything, no refresh buttons

### Medium-term (Cycle 018)
1. **Genesis SDK**: Official SDK, plugin templates, developer CLI
2. **AgentOS Foundation**: Stable APIs for all subsystems

## What Changes from Cycle 015

The focus shifts from:
- **Consolidation** (reducing 10 competing systems to 1 each)
  → **Product Excellence** (making every interaction delightful)
- **Adding screens** (11 static screens)
  → **Unified workspace** (one dynamic layout system)
- **Framework thinking** ("Genesis is an engineering framework")
  → **Product thinking** ("Genesis is an engineering operating system")
- **Proof-of-concept** ("this demonstrates the capability")
  → **Production quality** ("this is reliable and polished")

## Goals Not Being Carried Forward

From Cycle 015's targets, the following remain unaddressed:
- Semantic search (embedding-based)
- SDK package extraction (`genesis/sdk/`)
- Consolidation of 9 competing systems (still at designation stage)
- Desktop unit tests (Textual pilot tests)
- Execution platform retry/circuit-breaker implementation

These are subsumed by Cycle 016's missions (Spotlight covers search, SDK covers SDK, Unified Workspace enables desktop testing, AI Pipeline covers execution).

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Scope creep — 11 missions is aggressive | High | High | Phase 0 first, prioritize P0 bugs |
| Workspace rewrite breaks existing screens | Medium | Critical | Incremental migration, no full rewrite |
| Visualizations in terminal are limited | Medium | Medium | Textual's built-in widgets + Rich renderables |
| Auth hardening breaks existing workflows | Medium | Medium | Backward-compatible, opt-in per endpoint |
| 26 reports = significant documentation effort | High | Low | Auto-generate from audit data; quality over quantity |
