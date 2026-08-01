# M148 — Engineering Workflow Engine

## File
`genesis/workflows/engine.py`, `genesis/workflows/models.py`, `genesis/workflows/__init__.py`

## Purpose
Real executable engineering workflows with goals, stages, dependencies, conditions, retries, rollback, parallel execution, approvals, agent/AI/human participation, timeouts, observability, metrics, execution history, knowledge generation, and decision recording.

## Key Components

### WorkflowDef
- `name`, `description`, `stages`, `goals`, `timeout`, `auto_rollback`, `tags`

### WorkflowExecution
- `id`, `workflow_name`, `status`, `current_stage`, `history`, `artifacts`
- Statuses: PENDING → RUNNING → COMPLETED/FAILED/ROLLED_BACK
- Stages: INIT → PREPARE → EXECUTE → VALIDATE → COMPLETE → ROLLBACK

### EngineeringWorkflowEngine
- `register(wf_def)` — register a workflow definition
- `run(name, inputs)` — execute workflow asynchronously
- `get_execution(id)` — query execution status
- `list_executions(status)` — filter by status

### Built-in Workflows
1. **refactor_module** — analyze → backup → refactor → test → validate (5 stages)
2. **analyze_repository** — scan → reason → extract → report (4 stages)
3. **deploy_provider** — register → benchmark → route → validate (4 stages)

## Integration
- **kernel.workflow_engine** — lazy-loaded, auto-booted
- **EngineeringState** — stores workflow definitions and executions
- **EngineeringRegistry** — workflows registered as WORKFLOW objects
- **Events** — emits workflow.stage.started, workflow.completed
