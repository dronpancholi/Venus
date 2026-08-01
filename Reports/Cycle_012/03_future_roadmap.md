# CYCLE 012 — FUTURE ROADMAP

---

## P0 — Immediate Next Cycle

| Priority | Mission | Description | Effort |
|----------|---------|-------------|--------|
| 🔴 P0 | Event-driven UI | Replace polling with EventRouter subscriptions — screens receive push events instead of polling every 1-10s | Large |
| 🔴 P0 | API Auth | Token-based auth for Genesis API server | Medium |
| 🔴 P0 | WebSocket push | Broadcast fabric events via WebSocket for real-time external clients | Medium |

## P1 — Near Term (Cycle 013-014)

| Priority | Mission | Description | Effort |
|----------|---------|-------------|--------|
| 🟡 P1 | Tabbed layouts | Multiple tabs within screens, split views, drag-to-reorder | Medium |
| 🟡 P1 | Plugin screens | Plugin system for external screens, widgets, commands | Large |
| 🟡 P1 | Conversation viewer | Full screen for reading/writing conversations with participants | Medium |
| 🟡 P1 | Graph visualization | ASCII/Unicode graph rendering in Knowledge Graph screen | Large |
| 🟡 P1 | File click actions | Click a file in Repository → show purpose, dependencies, related reports | Medium |

## P2 — Medium Term

| Priority | Mission | Description | Effort |
|----------|---------|-------------|--------|
| 🟢 P2 | Theme toggle | Dark/light mode, configurable accent colors | Small |
| 🟢 P2 | Help overlay | In-app keyboard reference | Small |
| 🟢 P2 | Startup animation | Boot sequence visualization | Small |
| 🟢 P2 | Desktop unit tests | pytest tests for all screens and widgets | Medium |
| 🟢 P2 | Multi-workspace | RepositoryScreen handles multiple workspace directories | Medium |

## P3 — Long Term

| Priority | Mission | Description | Effort |
|----------|---------|-------------|--------|
| 🔵 P3 | Distributed kernel | Multi-process FabricKernel with shared storage | Very Large |
| 🔵 P3 | Execution replay | Full step-by-step replay of agent execution, tasks, conversations | Large |
| 🔵 P3 | Knowledge graph layout | Force-directed graph rendering in terminal | Very Large |

## ARCHITECTURAL DEBT

1. **Polling overhead**: 10+ concurrent timers (1-10s intervals) across all screens. A single event bus subscription would be more efficient.
2. **CSS in app.py**: ~280 lines inline; should extract to `.tcss` file for modularity.
3. **Screen registration**: Manual updates to SCREENS dict, keyboard bindings, and Activity Bar needed for each new screen.
4. **No desktop unit tests**: All 14 screens tested only through the full test suite (which doesn't test UI).
5. **Late import patterns**: Several screens use `try: from genesis.watch import ...` patterns that should be module-level.
