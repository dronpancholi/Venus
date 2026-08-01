# Phase 0 Delta: Execution Engine

**File:** `genesis/fabric/execution.py` — 473 lines  
**Tests:** Via `test_kernel.py`

## Architecture

```
AgentExecutionEngine
  └── execute(agent, task, capability, provider_id, model) -> str
        ├── _build_system_prompt(agent, task)  → role prompt + custom + Genesis footer
        ├── AIRouter.chat()                     → auto-select best provider
        └── emit "agent.execution.completed/failed"

TaskExecutor (background daemon thread, 2s poll)
  └── _tick()
        ├── graph.get_ready_tasks()
        ├── _find_agent(node) → idle agent matching required roles
        └── _execute_node(node, agent)
              ├── graph.update_status(RUNNING)
              ├── agent.assign_task()
              ├── engine.execute(agent, task)
              ├── agent.complete_task()
              ├── graph.update_status(COMPLETED)
              └── _propagate_completion() → unblock dependents
```

## TaskGraph (`genesis/fabric/tasks.py` — 312 lines)

| Component | Purpose |
|-----------|---------|
| `TaskNodeType` (11) | GOAL, OBJECTIVE, PROJECT, EPIC, STORY, ENGINEERING_TASK, AGENT_TASK, EXECUTION_UNIT, OPERATION, VALIDATION, EVIDENCE, COMPLETION |
| `TaskStatus` (8) | PENDING, READY, RUNNING, BLOCKED, COMPLETED, FAILED, SKIPPED, ROLLED_BACK |
| `TaskGraph` | Dependency DAG with 4 indexes, critical path analysis |
| `TaskGraphBuilder` | Convenience builder from objectives |

## Role Prompts (18)

Each agent role has a custom system prompt (30-131 lines in execution.py), e.g.:
- Chief Engineer: "oversee all engineering operations, make architectural decisions..."
- Backend Engineer: "write Python code, design APIs, implement business logic..."
- Reviewer: "review pull requests, provide actionable feedback..."

## Findings

1. **TaskExecutor single-threaded bottleneck** — one thread polls, finds agents, and executes tasks sequentially. With 2s poll, a 30s task blocks the entire pipeline
2. **No task result persistence** — `complete_task()` stores result in memory, not StorageEngine
3. **`_find_agent()` has no backpressure** — assigns all ready tasks to all idle agents simultaneously (race condition on agent status)
4. **Role prompts in source code** — 18 prompts embedded in execution.py, no externalization or hot-reload
5. **No task retry logic** — failed tasks stay FAILED, no automatic retry or escalation
6. **No execution timeout** — `provider.chat()` can hang indefinitely, blocking the executor thread

## Recommendations

1. Add thread pool to TaskExecutor for concurrent task execution
2. Persist task results (output, duration, provider used) to StorageEngine
3. Add agent status lock in `_find_agent()` to prevent double-assignment
4. Extract role prompts to YAML files in `genesis/roles/` directory
5. Add retry policy: max_retries, backoff, escalation role
6. Add timeout to `engine.execute()` with `concurrent.futures` or signal-based timeout
