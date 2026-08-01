# CYCLE 010 — NEXT INITIATIVES

## Priorities for Cycle 011+

---

| Priority | Mission | Description | Track | Effort |
|----------|---------|-------------|-------|--------|
| 🔴 P0 | **API Auth** (Mission 55 gap) | Add token-based auth to HTTP API before production exposure | B | Medium |
| 🔴 P0 | **WebSocket Reconnect** (Mission 55 gap) | Exponential backoff reconnection in desktop client | B | Medium |
| 🟡 P1 | **Multi-workspace** | RepositoryScreen supports multiple workspace directories | B | Medium |
| 🟡 P1 | **Live File Tree** | Wire ContinuousEngineering watchers into RepositoryScreen | B | Small |
| 🟢 P2 | **Theme toggle** | Dark/light mode for desktop | B | Small |
| 🟢 P2 | **Conversation persistence** | Save/load engineering sessions to disk | A | Medium |
| 🟢 P2 | **TaskGraph visualization** | Desktop screen for TaskGraph DAG with status colors | B | Large |
| 🔵 P3 | **Plugin system** | External agent/event plugins via entry points | A | Large |
| 🔵 P3 | **Distributed kernel** | Multi-process FabricKernel with shared storage | A | Very Large |

## TRACK A (Kernel/Execution) — Next Steps

1. **ConversationEngine multi-turn sessions** — currently single-message;
   wire up sequential agent communication
2. **TaskGraph prioritization** — support priority-sorted polling in
   TaskExecutor (currently FIFO across ready tasks)
3. **Agent pre-emption** — allow higher-priority tasks to interrupt running
   agents

## TRACK B (Product/Desktop/API) — Next Steps

1. **API Auth** — simple bearer token with configurable secret
2. **WebSocket reconnection** — exponential backoff, jitter, max-retry limit
3. **RepositoryScreen enhancements** — multi-workspace, live file tree,
   git status overlay

## PRE-EXISTING BUGS

| Bug | File | Status |
|-----|------|--------|
| `uptime_seconds=0` after `record_start` | `test_service_kernel.py` | Pre-existing, not fixed |
| `entry`→`task_data` parameter name | `test_storage.py` | ✅ Fixed in Cycle 010 |
