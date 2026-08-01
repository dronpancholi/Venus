# UAIEOS Engine: Agent Orchestration Engine

This document defines the operational architecture, state management systems, communication queues, and mathematical models for the Agent Orchestration Engine. This engine coordinates multi-agent system (swarm) execution, plans decomposition, and resolves task dependencies.

---

## 1. Engine Overview & Core Functions

The Agent Orchestration Engine manages the lifecycle of individual agent instances and supervises their communication over the shared event bus.

```
                         [Goal Intake Protocol]
                                   │
                                   ▼
                       [Agent Orchestrator Node]
                         ├── Task Dependency Resolver
                         ├── Swarm Event Bus Coordinator
                         └── State Machine Monitor
                                   │
             ┌─────────────────────┼─────────────────────┐
             ▼                     ▼                     ▼
      [Planning Queue]     [Execution Queue]      [Debate Console]
```

### 1.1 Core Functions
1.  **Task Dependency Resolution:** Compiles high-level plans into Directed Acyclic Graphs (DAGs) and maps ready tasks to execution queues.
2.  **State Machine Execution:** Evaluates agent transitions, ensuring safety guardrails and resource budgets are not breached.
3.  **Debate Arbitration:** Manages multi-agent debate cycles, computing consensus values to validate completion artifacts.
4.  **Process Suspension & Deserialization:** Serializes inactive threads to persistent storage while waiting for external inputs.

---

## 2. Technical Architecture & Algorithms

### 2.1 Task Dependency Resolution
Let $G = (V, E)$ be the Directed Acyclic Graph of tasks in a plan, where $V$ represents the set of tasks and $E$ is the set of directed dependency edges. A task $v_j \in V$ is marked as `READY` for execution if and only if all its direct predecessors are marked as `COMPLETED`:

$$\forall v_i \in V, \text{ if } (v_i, v_j) \in E \implies \text{State}(v_i) == \text{COMPLETED}$$

The scheduler runs a topological sort over the graph at initialization. If a cycle is detected ($E$ contains a path from $v_i$ back to $v_i$), the orchestrator halts execution with a cyclic dependency error before resources are allocated.

### 2.2 Consensus Evaluation Algorithm
During debate phases, if consensus is not met (see [PART_03_AGENT_ENGINEERING.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/uaieos_parts/PART_03_AGENT_ENGINEERING.md#L20-L40)), the orchestrator selects the dissenting argument with the highest relevance score to construct the revision prompt.

---

## 3. Data Protocols & Schemas

### 3.1 Swarm Event Message Schema
Agents publish and subscribe to events via a message broker. Every message must match the validation envelope:

```json
{
  "event_id": "evt-8827-09a",
  "correlation_id": "trace-refactor-9912",
  "sender_agent_id": "agent_coder_v3",
  "recipient_topic": "swarm.v1.verification",
  "timestamp_utc": "2026-06-26T03:06:06Z",
  "payload": {
    "artifact_type": "source_code_patch",
    "details": {
      "file_path": "/src/logger.py",
      "lines_modified": 12,
      "diff": "@@ -12,3 +12,3 @@\n-import logging\n+from enterprise_logger import log"
    }
  },
  "signature": "sha256-hash-value"
}
```

### 3.2 Agent Thread State Schema
The execution state is captured to database records for audit and recovery logs:

```json
{
  "agent_session_id": "sess-agent-99218",
  "status": "WAITING",
  "active_step_id": "step_2_replace",
  "current_budget_spent_usd": 0.124,
  "max_budget_limit_usd": 1.50,
  "state_variables": {
    "compilation_retries": 1,
    "last_tool_used": "file_write"
  },
  "execution_history_refs": [
    "evt-8826-08z",
    "evt-8827-09a"
  ]
}
```

---

## 4. Integration & Commands

Administrators manage swarm runtimes using CLI utilities.

### 4.1 Dispatch Swarm Job
```bash
python -m uaieos.engines.agent_orchestrator --action dispatch-plan --plan-path /Users/dronpancholi/Developer/01_Strategic/Venus/problem_templates/PROBLEM_DEFINITION_DOCUMENT.md
```
*Expected Output:*
```json
{
  "session_id": "sess-agent-99218",
  "status": "INITIATED",
  "active_nodes": ["step_1_locate"],
  "allocated_agents": ["agent_architect_v2", "agent_coder_v3"]
}
```

### 4.2 Query Swarm Thread Status
```bash
python -m uaieos.engines.agent_orchestrator --action thread-status --session-id sess-agent-99218
```
*Expected Output:*
```json
{
  "session_id": "sess-agent-99218",
  "status": "EXECUTING",
  "current_step": "step_2_replace",
  "tokens_consumed": 18450,
  "estimated_cost_usd": 0.138
}
```

---

## 5. System Cross-References
*   For the agent design patterns, planning loops, and debate mechanisms, see [PART_03_AGENT_ENGINEERING.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/PART_03_AGENT_ENGINEERING.md).
*   For details on the event-driven workflow engine and transition matrices, see [PART_09_WORKFLOW_ORCHESTRATION.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/uaieos_parts/PART_09_WORKFLOW_ORCHESTRATION.md).
*   For runtime supervision details, refer to [ENGINE_CORE_RUNTIME.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/uaieos_parts/ENGINE_CORE_RUNTIME.md).
