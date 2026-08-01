# M149 — Live Project Command Center

## File
`genesis/command_center/engine.py`, `genesis/command_center/__init__.py`

## Purpose
Live project command center with real-time dashboards. Every project dashboard continuously displays architecture, knowledge, timeline, memory, risk, velocity, open decisions, technical debt, engineering health, agent activity, AI conversations, pending plans, running workflows, recent reports, and repository evolution.

## Key Components

### LiveCommandCenter
- `get_dashboard(name)` — project dashboard with panels
- `refresh_panel(dashboard, panel)` — live data fetch for one panel
- `refresh_all(dashboard)` — refresh all panels
- `snapshot()` — dashboard overview

### DashboardPanel
- `title`, `data_source`, `refresh_interval`, `last_data`, `last_refresh`

### Data Sources (14 panels)
architecture, knowledge, timeline, memory_v2, reasoning, observatory, decisions, insight, planner, workflows, ai, agents, health, reports

## Integration
- **kernel.command_center** — lazy-loaded, auto-booted
- **EngineeringState** — stores dashboard count
- **EngineeringRegistry** — registered as WORKSPACE object
- **All subsystems** — feed data into panels
