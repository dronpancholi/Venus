# CYCLE 011 — USER EXPERIENCE REPORT

## The Keyboard-First Engineering Workspace

---

## NAVIGATION ARCHITECTURE

```
┌─────┬───────────────────────────────────────────────────────┐
│     │                                                       │
│ Act │  Genesis — Mission Control                           │
│ iv  │  System Health | Agent Activity | Live Events         │
│ ity ├──────────────────┬────────────────────────────────────┤
│     │  Quick Stats     │  Live Events                       │
│ Bar │  State: running  │  [kernel.booted] fabric: {...}     │
│     │  Events: 142     │  [service.registered] fabric:...   │
│     │  Services: 3     │  [session.begun] fabric: {...}     │
│     │  Uptime: 340s    │                                    │
│     ├──────────────────┤                                    │
│     │  Active Agents   │                                    │
│     │  ● alpha (idle)  │                                    │
│     │  ▶ beta (run)    │                                    │
│     ├──────────────────┤                                    │
│     │  Task Graph      │                                    │
│     │  12 nodes, 3 rdy │                                    │
├─────┴──────────────────┴────────────────────────────────────┤
│  Genesis │ State: running │ Events: 142 │ Uptime: 340s ...  │
└──────────────────────────────────────────────────────────────┘
```

## KEYBOARD REFERENCE

| Key | Action | Context |
|-----|--------|---------|
| Ctrl+K | Command Palette | Anywhere |
| Ctrl+P | Search Everywhere | Anywhere |
| Ctrl+H | Home / Mission Control | Anywhere |
| Ctrl+E | Events stream | Anywhere |
| Ctrl+G | Knowledge Graph | Anywhere |
| Ctrl+T | Engineering Timeline | Anywhere |
| Ctrl+1 | Agent Operations | Anywhere |
| Ctrl+2 | AI Command Center | Anywhere |
| Ctrl+3 | Continuous Engineering | Anywhere |
| Ctrl+R | Refresh current view | Anywhere |
| Ctrl+Q | Quit | Anywhere |
| Escape | Go back / Close modal | Screens + Modals |
| E | Show Events | Timeline screen |
| A | Show Audit | Timeline screen |
| C | Show Conversations | Timeline screen |
| T | Show Tasks | Timeline screen |
| P | Pause agent | Agent Ops screen |
| S | Resume agent | Agent Ops screen |
| T | Terminate agent | Agent Ops screen |
| F | File Tree mode | Repository screen |
| A | Architecture mode | Repository screen |
| N | Show graph nodes | Knowledge Graph |
| E | Show graph edges | Knowledge Graph |
| Y | Show graph types | Knowledge Graph |
| / | Filter timeline | Timeline screen |

## COMMAND PALETTE (21 commands)

Every command accessible without leaving the keyboard:
1. Home — Go to Home screen
2. Agent Operations — Open Agent Operations Center
3. Repository Explorer — Open Repository Intelligence
4. Engineering Timeline — Open Engineering Timeline
5. Knowledge Graph — Open Live Knowledge Graph
6. AI Command Center — Manage AI providers
7. Continuous Engineering — Start/stop watchers
8. Reports — View engineering reports
9. Settings — Workspace settings
10. Search Everywhere — Search across all subsystems
11. Refresh — Force refresh current view
12. Command Palette — Show this palette
13. Quit — Exit Genesis
14. Start CE Watchers — Start Continuous Engineering watchers
15. Stop CE Watchers — Stop all watchers
16. Boot Kernel — Ensure FabricKernel is booted
17. Kernel Stats — Show kernel statistics
18. Emit Test Event — Emit a test event through the fabric
19. Start Task Executor — Start the background task executor
20. Stop Task Executor — Stop the task executor
21. New Session — Begin a new engineering session

## SEARCH EVERYWHERE (7 data sources)

One search box spanning: Events, Agents, Tasks, Services, Audit, Conversations, Commands.

Filter by source type (tab buttons), results rendered with type-specific coloring.

## ERROR HANDLING PHILOSOPHY

- **Silent degradation:** if a data source is unavailable, the screen shows "[dim]Not available[/]" rather than crashing
- **Actionable notifications:** errors that can be fixed (e.g., "CE not started") include hints about the fix
- **No uncaught exceptions:** every fabric access is wrapped in try/except
- **Loading tolerance:** screens handle the case where kernel hasn't fully booted yet
