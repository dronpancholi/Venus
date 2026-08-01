# M142 — Engineering Automation Engine

## File
`genesis/automation/engine.py`, `genesis/automation/__init__.py`

## Purpose
Event-driven workflow engine that reacts to engineering events. Links role prompts to EngineeringRegistry. Drains the WebSocket queue in production. Replaces polling with push-based event subscriptions.

## Key Components

### AutomationEngine
- `add_workflow()` / `remove_workflow()` — manage event-driven workflows
- `handle_event()` — dispatches matched workflows on every EngineeringEvent
- `_run_workflow()` — executes step chain with success/failure events
- `start_ws_drainer()` / `stop_ws_drainer()` — drains `_ws_queue` (fixes silent drops)
- `stats()` — workflow counts, total runs, queue drained

### Built-in Workflows
| Workflow | Trigger | Steps |
|---|---|---|
| `twin_file_change_refresh_knowledge` | `twin.files.changed` | Refresh KnowledgeEngine |
| `twin_scan_autoreview` | `twin.scan.completed` | Run AutonomousReview |
| `autoreview_findings` | `review.completed` | Log and broadcast findings |

### Role Prompt Registration
All 20 role prompts from `genesis/fabric/execution.py` are registered as EngineeringObjects with type `PROMPT` on boot. This decouples prompts from hardcoded dictionaries and enables dynamic updates.

## Integration
- **FabricKernel.automation** — lazy-loaded property, auto-booted
- **EventRouter** — subscribed to `*` events via `on_event("*", handler)`
- **EngineeringRegistry** — workflows + prompts registered as objects
- **Server** — WS queue drainer prevents silent event loss

## Critical Gaps Addressed
- ✅ Event subscriptions now drive workflows (no polling)
- ✅ WS queue no longer silently drops events
- ✅ Role prompts linked to EngineeringRegistry
