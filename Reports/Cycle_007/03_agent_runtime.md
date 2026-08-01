# CYCLE 007 — REPORT 03: REAL AGENT RUNTIME

## Living, Observable, Collaborative Agents

⸻

## VISION

Agents in Genesis are not static definitions. They are living computational entities
that run in a managed runtime with lifecycle, messaging, state, and observability.
Users can watch agents work, inspect their state, communicate with them, and observe
their decision-making process.

⸻

## PROBLEM STATEMENT

Before Cycle 007, "agents" existed only as static definitions in the autonomous
engineering pipeline (`genesis/autonomous/analyzer.py`, `planner.py`, `codegen.py`).
These were function calls, not agents:
- No lifecycle management
- No inter-agent communication
- No agent state or memory
- No observability into agent activity
- No parallel execution
- No error recovery
- No task assignment

⸻

## ARCHITECTURE

```
Agent Runtime
  ├── AgentInstance (living agent)
  │     ├── AgentSpec (identity, role, capabilities)
  │     ├── AgentContext (private memory, workspace)
  │     ├── Inbox (messages from other agents)
  │     ├── Outbox (messages sent)
  │     └── Status (state machine)
  ├── AgentScheduler
  │     └── Scheduled tasks (one-shot, recurring)
  └── FabricKernel (events, messaging, audit)
```

⸻

## AGENT ROLES (20 defined)

`AgentRole` enum covers: ChiefEngineer, PrincipalArchitect, RepositoryScientist,
EngineeringResearcher, Planner, ProductManager, BackendEngineer, FrontendEngineer,
KnowledgeEngineer, DocumentationEngineer, SecurityEngineer, PerformanceEngineer,
QualityEngineer, TestingEngineer, GovernanceAuditor, MigrationSpecialist,
SimulationScientist, EconomicsAnalyst, Reviewer, ReleaseEngineer.

⸻

## AGENT LIFECYCLE

```
spawn() → AgentSpec → AgentInstance(status=IDLE)
  assign_task() → status=RUNNING
    complete_task() → status=IDLE
    fail_task() → status=ERROR
  terminate() → status=TERMINATED
```

## AGENT TASK LIFECYCLE

```
AgentTask(status=pending)
  → assign_task() → started_at=now, status=running
  → complete_task() → completed_at=now, status=completed, result=...
  → fail_task() → completed_at=now, status=failed, error=...
```

⸻

## AGENT MESSAGING

Agents communicate through a built-in message system:

```python
# Send a message
runtime.send_message("agent_a", "agent_b", "Review this plan", 
                     message_type="request")

# Read inbox
messages = runtime.read_inbox("agent_b")

# Agent instance shorthand
agent.send("agent_b", "Please review")
messages = agent.read_messages()
```

Message types: `text`, `request`, `response`, `debate`, `vote`, `approval`

⸻

## AGENT CONTEXT

Each agent has private memory and workspace:

```python
ctx = runtime.get_context("agent_id")
ctx.remember("key", "value")          # long-term memory
ctx.recall("key")                     # retrieve
ctx.store_workspace("file", data)     # working files
ctx.read_workspace("file")            # retrieve working file
```

⸻

## AGENT SCHEDULER

Supports one-shot and recurring tasks:

```python
scheduler = AgentScheduler(runtime)
tid = scheduler.schedule_task("agent_id", "Do something", 
                              delay_secs=0, interval_secs=300)
scheduler.cancel_task(tid)
scheduler.tick()  # run due tasks
```

⸻

## OBSERVABILITY

Every agent action emits structured events:

```
agent.spawned         agent.terminated
agent.task.assigned   agent.task.completed
agent.task.failed     agent.message.sent
```

Debug info available per agent:
```python
info = runtime.get_debug_info("agent_id")
# AgentDebugInfo: status, current_task, task_count, completed_count,
#                 failed_count, uptime, inbox_count, memory_size
```

⸻

## FUTURE EXTENSIONS

- Agent handler registration (actual AI-powered execution)
- Debate protocol between agents
- Voting and consensus mechanisms
- Agent spawning child agents
- Checkpoint/recovery for long-running tasks
- Agent benchmarks and performance history
