# CYCLE 008 — DESKTOP TUI REPORT

## Genesis Desktop — Textual Application

**File:** `genesis/desktop.py`

⸻

## Purpose

The Desktop TUI is Genesis's primary user interface. Built with Textual, it provides
a rich terminal experience with zero build step, zero dependencies beyond Python,
and instant startup.

## Screens

### HomeScreen

- Displays a live dashboard with agent status, recent events, and task overview
- Refreshes periodically via `set_interval`
- Shows uptime, agent count, event count
- Minimalist layout: Header, 3-column body (Agents | Events | Tasks), StatusBar

### AgentScreen

- Lists all agents with name, role, status, last active
- Color-coded by status (active=green, idle=yellow, dead=red)
- Auto-refresh

### EventsScreen

- Lists recent EngineeringEvents ordered by timestamp
- Type, severity, source, summary per event
- Color-coded by severity (info=blue, warning=yellow, error=red, critical=magenta)

### CommandPalette

- `Ctrl+K` triggers command palette
- Commands: `View Home`, `View Agents`, `View Events`, `Toggle Dark Mode`, `Quit`
- Filterable with live search

### StatusBar

- Shows app name, connection status, event count, current time

## Architecture

```
GenesisDesktop (Textual App)
├── HomeScreen        — dashboard
├── AgentScreen       — agent list
├── EventsScreen      — event log
├── CommandPalette    — command input
└── StatusBar         — status indicators
     │
     └── GenesisClient (async HTTP + WS client)
              └── FastAPI Server → FabricKernel
```

## Design Notes

- Uses `run_async` + `asyncio.run` for non-blocking API calls
- WebSocket connected on mount; reconnects on disconnect
- Design tokens from `genesis/ui/tokens.css` are hardcoded here (Textual uses its own CSS)
- Future: dynamic token loading
- No heavy animation — first render in <500ms

## Future Enhancements

- **Repository Screen** — browse workspace tree, file content
- **Knowledge Graph Screen** — visual graph browser
- **Engineering Memory Timeline** — history browser
- **Settings Screen** — configure providers, watchers, themes
- **Native desktop** — Tauri/Electron wrapper around FastAPI backend
