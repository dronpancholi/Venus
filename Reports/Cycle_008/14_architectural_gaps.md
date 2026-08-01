# CYCLE 008 — ARCHITECTURAL GAPS REPORT

## What's Still Missing

⸻

## Gaps

### Critical

- **No authentication** — API server is completely open
- **No persistence** — Events, agents, tasks are in-memory only
- **No error recovery** — Server crash loses all state

### High

- **No WebSocket reconnect** — Desktop disconnects silently
- **No multi-workspace support** — Each watcher monitors one repo
- **No event replay for new clients** — WebSocket only sends new events

### Medium

- **No file change buffering** — Rapid changes flood event store
- **No watcher persistence** — Configuration lost on restart
- **No provider status UI** — Desktop shows no provider info
- **No dark/light theme toggle UI** — Only hardcoded dark
- **No task execution** — TaskGraph is a DAG but not executed
- **No agent scheduling** — Agents exist but aren't started

### Low

- **No search** — Event log is not searchable
- **No filtering** — WebSocket supports no per-client filters
- **No metrics persistence** — Metrics reset on restart
- **No integration tests** — API tests use mocks, not real server
- **No documentation** — Reports exist, but no user-facing docs

## Gap Closure Roadmap

| Cycle | Gaps Closed |
|-------|-------------|
| 009 | Auth, WS reconnect, error recovery, task execution |
| 010 | Persistence (SQLite), multi-workspace, theme toggle |
| 011 | Search, filtering, provider UI, event buffering |
| 012 | Integration tests, documentation, metrics persistence |
