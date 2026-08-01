# M164: Engineering Command Center

**Status:** Implemented
**Files:** `genesis/command_center/engine.py`
**Integration:** FabricKernel.command_center, 17 panels, 5 action handlers

## Changes

The command center evolved from informational dashboards to operational command centers:

- **17 panels** (up from 14) — added boot, observability, graph
- **Panel capabilities** — OBSERVE, REASON, RECOMMEND, EXECUTE, MONITOR
- **Panel actions** — run health checks, view boot reports, export observability
- **Action handler registry** — register/replace handlers for any panel action
- **Observability integration** — every panel refresh and action execution is recorded
- **Health-aware** — command center snapshot reports panel health

## Architecture

```
LiveCommandCenter
  ├── dashboards["default"]
  │   ├── health (OBSERVE, MONITOR)    → run_health_check
  │   ├── boot (OBSERVE, REASON)       → observe_boot
  │   ├── observability (OBSERVE, EXECUTE) → export_observability
  │   ├── architecture / knowledge / timeline / memory / risk
  │   ├── velocity / decisions / insights / plans / workflows
  │   ├── ai / agents / graph / reports
  └── action_handlers{}
      ├── refresh_architecture
      ├── refresh_health
      ├── run_health_check
      ├── observe_boot
      └── export_observability
```
