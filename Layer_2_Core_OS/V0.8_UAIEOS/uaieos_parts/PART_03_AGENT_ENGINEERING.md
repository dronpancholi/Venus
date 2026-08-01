# UAIEOS Part 03: Agent Engineering Manual

This manual defines the design patterns, architectural structures, execution loops, and coordination protocols for autonomous agents and multi-agent systems (swarms) operating within the UAIEOS. It standardizes plan representations, consensus algorithms, and state lifecycles to ensure reliable task completion.

---

## 1. Single Agent Architecture & Execution Loops

A single agent is an autonomous entity that cycles through observation, planning, action selection, and execution phases.

```
       ┌───────────────────[Observation]◄──────────────────┐
       │                                                   │
       ▼                                                   │
   [Planning] (ReAct / Plan-and-Solve)                     │ (Environment Feedback)
       │                                                   │
       ▼                                                   │
   [Action Selection] (Tool call / Thought)                │
       │                                                   │
       ▼                                                   │
   [Execution] (API execution / State modification) ───────┘
```

### 1.1 The ReAct Loop (Reason + Action)
ReAct interleaves reasoning traces and task-specific actions. The execution sequence is structured as:
1.  **Thought:** The agent reasons about the current state and goal.
2.  **Action:** The agent calls a tool with specific parameters.
3.  **Observation:** The system returns the tool output, which is appended to the agent's context.

### 1.2 The Plan-and-Solve Loop
For complex tasks, ReAct loops can drift. UAIEOS mandates the Plan-and-Solve model for multi-step tasks:
1.  **Planning Phase:** The agent decomposes the goal into a structured plan (a list of sub-tasks).
2.  **Execution Phase:** The agent executes sub-tasks sequentially.
3.  **Re-planning Phase:** After each action, the agent evaluates progress and updates the plan.

---

## 2. Multi-Agent Systems & Swarms

Complex problems require splitting labor across specialized agents. UAIEOS implements a message-driven, actor-like swarm architecture.

### 2.1 Debate and Consensus Cycles
To solve ambiguous tasks or verify outputs, agents participate in structured debate cycles. Let $E_k(x)$ be the evaluation function of agent $k$ on a candidate completion $x$. The consensus score $S(x)$ is calculated across $K$ agents:

$$S(x) = \frac{1}{K} \sum_{k=1}^{K} w_k \cdot E_k(x)$$

Where $w_k$ is the authority weight of agent $k$ on the task domain. If $S(x) < \theta$ (consensus threshold, e.g., $0.85$), the system triggers another debate round, passing the feedback of the dissenting agents back to the generation queue.

### 2.2 Swarm Communication
Agents do not share memory directly; they communicate by publishing events to an event-broker. Communication envelopes are structured to prevent prompt injection and guarantee type-safety.

---

## 3. Planners & Plan Representation

Planners translate high-level goals into executable action graphs.

### 3.1 Hierarchical Planning Sequences
A plan is represented mathematically as a sequence of states, actions, and goals:

$$P = (S_0, a_1, S_1, a_2, \ldots, S_{n-1}, a_n, S_n)$$

Where:
*   $S_0$ is the initial system state.
*   $a_i$ is an action (or tool call) mapped to step $i$.
*   $S_i$ is the expected state transition: $S_i = \delta(S_{i-1}, a_i)$.
*   $g_i$ is a sub-goal representing a validation assertion that must hold true at state $S_i$.

### 3.2 Plan Representation Schema
Plans are structured as Directed Acyclic Graphs (DAGs) using JSON schemas:

```json
{
  "plan_id": "plan-refactor-9912",
  "root_goal": "Refactor codebase to replace legacy logger.",
  "nodes": [
    {
      "id": "step_1_locate",
      "description": "Locate all legacy logger imports.",
      "dependencies": [],
      "action_type": "TOOL_EXECUTION",
      "action_ref": "workspace_search",
      "args": { "query": "import legacy_logger" },
      "assertion": "matches_found >= 0"
    },
    {
      "id": "step_2_replace",
      "description": "Generate refactoring patch.",
      "dependencies": ["step_1_locate"],
      "action_type": "AGENT_DELEGATION",
      "action_ref": "agent_coder",
      "args": { "files": "$.step_1_locate.output.files" },
      "assertion": "ast_compiles == true"
    }
  ]
}
```

---

## 4. Agent Lifecycles

All agent threads in the UAIEOS run within a strict lifecycle container managed by the Agent Orchestration Engine.

```
       [Init] ──► [Ready] ──► [Executing] ──► [Completed]
                                  │
                                  ├─► [Waiting (Tool/HITL)] ─► [Executing]
                                  │
                                  └─► [Failed] ──► [Recovery / Retry] ──► [Executing]
```

### 4.1 Lifecycle States
1.  **Initialize (INIT):** Instantiates agent configuration, registers system prompts, allocates thread memory buffers, and generates a unique `agent_session_id`.
2.  **Ready (READY):** Agent is queued and waiting for initial state triggers.
3.  **Executing (EXECUTING):** Model processing, reasoning, or tool-calling loop is active.
4.  **Waiting (WAITING):** Thread execution is suspended, waiting for external events (e.g., tool execution, human-in-the-loop validation). The agent state is serialized to persistent storage to free up runtime thread pools.
5.  **Recovery (RECOVERY):** Triggered on error. The system resets the local context window and executes recovery prompts.
6.  **Completed (COMPLETED):** Task completed, assertions pass, resources are de-allocated, and final artifacts are written to the database.
7.  **Failed (FAILED):** Recovery failed, budget exhausted, or critical violation detected. The system halts execution and issues a system alert.

---

## 5. System Cross-References
*   For the orchestration code managing agent execution queues and planning states, see [ENGINE_AGENT_ORCHESTRATION.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/uaieos_parts/ENGINE_AGENT_ORCHESTRATION.md).
*   To see how agents interact with external resources via the Model Context Protocol, refer to [PART_04_MCP_ENGINEERING.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/uaieos_parts/PART_04_MCP_ENGINEERING.md).
*   For event-driven state machines, message brokers, and error recovery schemas, refer to [PART_09_WORKFLOW_ORCHESTRATION.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/uaieos_parts/PART_09_WORKFLOW_ORCHESTRATION.md).
