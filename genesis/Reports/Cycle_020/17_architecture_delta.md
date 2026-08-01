# Architecture Delta — Cycle 019 → Cycle 020

## New Packages

| Package | Purpose | Files |
|---------|---------|-------|
| `genesis/boot/` | Boot Sequence 2.0 — orchestrated lifecycle | 2 |
| `genesis/health/` | System Health Engine — unified health model | 2 |
| `genesis/observability/` | Universal Observability — every action recorded | 2 |
| `genesis/graph_core/` | Engineering Graph Unification — canonical graph layer | 2 |

## Enhanced Packages

| Package | Changes |
|---------|---------|
| `genesis/fabric/kernel.py` | Boot → phased boot, health engine, observability, graph registry |
| `genesis/command_center/engine.py` | Operational panels, actions, capabilities, 17 panels |
| `genesis/desktop/memory.py` | SessionSnapshot, save/restore, auto-restore context |
| `genesis/watch/__init__.py` | AutonomousTrigger, TwinRefreshTrigger, CopilotTrigger |
| `genesis/ai/router.py` | debate_chat, critique_chat, evaluate_chat |

## Architecture Diagram

```
┌─────────────────────────────────────────────────────┐
│                   Genesis Kernel                      │
│  ┌────────┐ ┌────────┐ ┌──────────┐ ┌────────────┐ │
│  │ Boot   │ │ Health │ │Observab. │ │ Graph      │ │
│  │Engine  │ │Engine  │ │ Engine   │ │ Registry   │ │
│  └────────┘ └────────┘ └──────────┘ └────────────┘ │
│       │            │           │            │         │
│       ▼            ▼           ▼            ▼         │
│  ┌────────┐ ┌────────┐ ┌──────────┐ ┌────────────┐  │
│  │14      │ │5       │ │20 action │ │Canonical   │  │
│  │Phases  │ │Collect.│ │types     │ │Graph +     │  │
│  │34 Steps│ │14 Dims │ │2 formats │ │Adapters    │  │
│  └────────┘ └────────┘ └──────────┘ └────────────┘  │
├─────────────────────────────────────────────────────┤
│  Command Center         Workspace Memory             │
│  17 panels, actions     Session save/restore         │
├─────────────────────────────────────────────────────┤
│  CE Autonomous          AI Collaboration             │
│  Triggers, actions      Debate/Critique/Evaluate     │
└─────────────────────────────────────────────────────┘
```

## Key Architectural Decisions

| Decision | Rationale |
|----------|-----------|
| **Boot as a service** (ADR-020-001) | Every phase is measurable, testable, and replaceable |
| **Health as a service** (ADR-020-002) | Unified health replaces ad-hoc subsystem checks |
| **Observability as a service** (ADR-020-003) | Record everything, query anything, export anytime |
| **Canonical graph facade** (ADR-020-004) | One interface, many implementations, backward compatible |
| **Command centers, not screens** (ADR-020-005) | Panels observe, reason, recommend, execute |
| **Autonomous triggers** (ADR-020-006) | CE reacts without manual intervention |
| **AI collaboration patterns** (ADR-020-007) | Debate/critique/evaluate complement parallel/consensus |
