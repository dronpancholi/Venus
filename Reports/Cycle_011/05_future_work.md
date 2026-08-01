# CYCLE 011 — FUTURE WORK

## Priorities for Cycle 012+

---

| Priority | Area | Description | Effort |
|----------|------|-------------|--------|
| 🔴 P0 | WebSocket push | Replace polling with event-driven UI updates | Medium |
| 🔴 P0 | API auth | Token-based auth before production exposure | Medium |
| 🟡 P1 | Tabbed layout | Multiple tabs per screen, split views | Medium |
| 🟡 P1 | Window persistence | Save/restore layout, recent projects | Medium |
| 🟡 P1 | Knowledge graph viz | GraphViz/ASCII graph rendering in KG screen | Large |
| 🟡 P1 | Agent reasoning timeline | Show live reasoning steps for running agents | Medium |
| 🟡 P1 | Conversation screen | Full conversation viewer with message detail | Medium |
| 🟢 P2 | File click action | Click file in tree → show purpose/dependencies | Medium |
| 🟢 P2 | Theme toggle | Dark/light mode switch | Small |
| 🟢 P2 | Help overlay | In-app help for all keyboard bindings | Small |
| 🟢 P2 | Startup screen | Boot animation / loading indicator | Small |
| 🔵 P3 | Clickable report content | Read full reports in-app instead of first 5 lines | Small |
| 🔵 P3 | Multi-workspace | RepositoryScreen handles multiple workspace dirs | Medium |

## ARCHITECTURAL DEBT

1. **Polling overhead** — all screens poll independently (2-10s intervals). On a slow system, 5 concurrent timers is wasteful. A single event-driven bus would be more efficient.
2. **CSS in app.py** — the WORKSPACE_CSS string in app.py is ~200 lines. For larger UI systems, extract to `genesis/desktop/css.py` or a `.tcss` file.
3. **Screen registration** — new screens require updates to `SCREENS` dict, keyboard bindings, and Activity Bar. A plugin-based registration system would be cleaner.
4. **Test coverage for desktop** — no unit tests exist for the desktop package yet. All screens are tested only through the full test suite (which doesn't test UI).
