# Phase 0 Delta: Agent System

**File:** `genesis/fabric/agents.py` — 424 lines  
**Tests:** Via `test_kernel.py`

## Architecture

```
AgentRuntime (orchestrator)
  ├── _agents: dict[str, AgentInstance]
  ├── _contexts: dict[str, AgentContext]
  └── _inboxes / _outboxes: dict[str, list[AgentMessage]]
        │
        ├── AgentInstance (spec, status, handler, task management)
        │     └── AgentContext (thread-safe key-value memory + workspace)
        │
        └── AgentScheduler (periodic/delayed task scheduling)
```

## AgentRole (18 roles)

`CHIEF_ENGINEER`, `PRINCIPAL_ARCHITECT`, `REPOSITORY_SCIENTIST`, `ENGINEERING_RESEARCHER`, `PLANNER`, `PRODUCT_MANAGER`, `BACKEND_ENGINEER`, `FRONTEND_ENGINEER`, `KNOWLEDGE_ENGINEER`, `DOCUMENTATION_ENGINEER`, `SECURITY_ENGINEER`, `PERFORMANCE_ENGINEER`, `QUALITY_ENGINEER`, `TESTING_ENGINEER`, `GOVERNANCE_AUDITOR`, `MIGRATION_SPECIALIST`, `SIMULATION_SCIENTIST`, `ECONOMICS_ANALYST`, `REVIEWER`, `RELEASE_ENGINEER`

## AgentStatus

`IDLE`, `RUNNING`, `WAITING`, `BLOCKED`, `ERROR`, `TERMINATED`

## Agent Lifecycle

```
AgentRuntime.spawn(spec)
  → AgentInstance created (IDLE)
  → AgentContext created (thread-safe memory)
  → "agent.spawned" event emitted

AgentInstance.assign_task(objective, context)
  → AgentTask created (RUNNING)
  → "agent.task.assigned" event emitted

AgentInstance.complete_task(task, result)
  → status → IDLE
  → "agent.task.completed" event emitted

AgentRuntime.terminate(agent_id)
  → status → TERMINATED
  → removed from agent/context dicts
  → "agent.terminated" event emitted
```

## Messaging

`AgentMessage`: id, sender_id, recipient_id, content, message_type (text/request/response/debate/vote/approval), correlation_id, timestamp

`AgentRuntime.send_message()` → delivers to recipient inbox, stores in sender outbox, emits event, persists

## Findings

1. **No agent persistence recovery** — agents are in-memory only; restart loses all agents
2. **No task timeout** — `AgentTask` has no deadline; a stuck agent blocks its role forever
3. **No agent persistence schema in StorageEngine** — `store_agent()`/`delete_agent()` exist but are one-way (no `query_agents()` with filter)
4. **AgentScheduler.tick() never called** — designed for external loop but no current code calls it
5. **No agent communication constraints** — any agent can message any other agent, no permission checks
6. **18 roles but only 6 used** — `_sc()` and color maps only handle 6 statuses, 12 others fall to default

## Recommendations

1. Persist agent state to StorageEngine on spawn/terminate for crash recovery
2. Add `ttl_seconds` to `AgentTask` with auto-timeout → FAILED
3. Add filterable `query_agents()` to StorageEngine
4. Wire AgentScheduler.tick() into TaskExecutor._tick() loop
5. Add agent-level messaging permissions (who can message whom)
6. Extend color maps + status marks to cover all agent statuses
