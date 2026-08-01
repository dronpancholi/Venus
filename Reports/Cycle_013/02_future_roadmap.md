# CYCLE 013 — FUTURE ROADMAP

---

## P0 — Immediate Next Cycle

| Priority | Mission | Description | Effort |
|----------|---------|-------------|--------|
| 🔴 P0 | Tabbed layouts | Multiple tabs within screens, split views, drag-to-reorder | Medium |
| 🔴 P0 | Plugin screens | Plugin system for external screens, widgets, commands | Large |

## P1 — Near Term (Cycle 014-015)

| Priority | Mission | Description | Effort |
|----------|---------|-------------|--------|
| 🟡 P1 | Graph visualization | ASCII/Unicode graph rendering in Knowledge Graph screen | Large |
| 🟡 P1 | Conversation viewer | Full screen for reading/writing conversations with participants | Medium |
| 🟡 P1 | File click actions | Click a file in Repository → show purpose, dependencies, related reports | Medium |
| 🟡 P1 | Desktop unit tests | pytest tests for all screens and widgets | Medium |
| 🟡 P1 | Multi-workspace | RepositoryScreen handles multiple workspace directories | Medium |

## P2 — Medium Term

| Priority | Mission | Description | Effort |
|----------|---------|-------------|--------|
| 🟢 P2 | Theme toggle | Dark/light mode, configurable accent colors | Small |
| 🟢 P2 | Startup animation | Boot sequence visualization | Small |
| 🟢 P2 | Execution replay | Full step-by-step replay of agent execution | Large |

## P3 — Long Term

| Priority | Mission | Description | Effort |
|----------|---------|-------------|--------|
| 🔵 P3 | Distributed kernel | Multi-process FabricKernel with shared storage | Very Large |
| 🔵 P3 | Force-directed graph | Knowledge graph layout in terminal | Very Large |

## ARCHITECTURAL DEBT

1. **CSS in app.py**: ~280 lines inline; should extract to `.tcss` file.
2. **Screen registration**: Manual updates to SCREENS dict, keyboard bindings, and Activity Bar needed for each new screen.
3. **No desktop unit tests**: All 14 screens tested only through the full test suite (no UI tests).
4. **Late import patterns**: Several screens use `try: from genesis.watch import ...` patterns.
