# UAIEOS Part 09: Workflow Orchestration Manual

This document defines the architectural patterns, state machine protocols, and routing algorithms for orchestration within the Unified AI Enterprise Operating System (UAIEOS). It covers the transition from simple Directed Acyclic Graph (DAG) structures to dynamic, autonomous multi-agent state machines, ensuring deterministic reliability under non-deterministic workloads.

---

## 1. Orchestration Paradigms

UAIEOS supports two primary orchestration models, which can be nested hierarchically:

### 1.1 Directed Acyclic Graphs (DAGs)
For structured, predictable, and audit-compliant processes (e.g., ETL pipelines, standardized compliance checks), workflows are defined as static DAGs.
*   **Determinism:** Execution paths are computed ahead of time.
*   **Parallelism:** Independent nodes execute concurrently.
*   **Error Boundaries:** Upstream failures halt downstream execution or trigger explicit failover nodes.

### 1.2 Autonomous Multi-Agent State Machines
For non-deterministic, open-ended problem solving (e.g., software engineering, research, complex system debugging), workflows are orchestrated via reactive state machines.
*   **Dynamism:** State transitions are determined at runtime based on agent outputs.
*   **Message Broker:** Agents communicate asynchronously via a shared event-bus using validated JSON schemas.
*   **Convergence Controls:** State loops are bounded by strict counter limits and convergence metrics to prevent infinite execution patterns.

---

## 2. State Serialization, Recovery, and Transition Matrices

To guarantee high availability and disaster recovery, all state machines must serialize their context to a persistent datastore (e.g., Redis or Spanner) at every transition edge.

### 2.1 State Serialization Schema
```json
{
  "trace_id": "tx-98172-abc",
  "workflow_id": "wf-agentic-refactor-09",
  "current_state": "VERIFYING_CODE",
  "state_version": 14,
  "timestamp_utc": "2026-06-26T03:06:06Z",
  "shared_context": {
    "target_repository": "git://github.com/enterprise/core-runtime.git",
    "active_branch": "patch-11",
    "generation_attempts": 3,
    "last_error": null
  },
  "agent_registry": {
    "architect": "agent_architect_v2",
    "coder": "agent_coder_v3",
    "tester": "agent_tester_v2"
  },
  "execution_history": [
    {
      "step": 1,
      "from_state": "INIT",
      "to_state": "ARCHITECTING",
      "actioned_by": "agent_architect_v2",
      "tokens_consumed": 4096,
      "latency_ms": 1240
    }
  ]
}
```

### 2.2 Transition Matrix and Probability Evaluation
Transitions are governed by a state transition matrix $T_{ij}$, representing the valid path from State $i$ to State $j$. In autonomous modes, the next state is selected using a soft-max over evaluation metrics or deterministic classifiers.

| Source State | Destination State | Trigger Condition | Fallback Action |
| :--- | :--- | :--- | :--- |
| `INIT` | `PLANNING` | Workflow initialized | Terminate with error |
| `PLANNING` | `EXECUTING` | Plan generated & validated | Return to `PLANNING` (Max 3) |
| `EXECUTING` | `VERIFYING` | Execution artifacts produced | Route to `RECOVERY` |
| `VERIFYING` | `COMPLETED` | All test suites pass | Route to `DEBUGGING` |
| `DEBUGGING` | `EXECUTING` | Error analyzed & patch proposed | Route to `HUMAN_IN_THE_LOOP` |
| `RECOVERY` | `PLANNING` | Context reset & budget active | Terminate (Budget exhausted) |

---

## 3. Dynamic Routing and Budget Constraints

Routing decisions use a cost-performance optimization function. For any candidate path $P$, the system evaluates the expected path utility $U(P)$ against token and time budgets.

### 3.1 Routing Utility Formula
$$U(P) = \alpha \cdot \text{Similarity}(C, T_P) - \beta \cdot \text{ExpectedCost}(P) - \gamma \cdot \text{ExpectedLatency}(P)$$

Where:
*   $C$ is the current execution context embedding.
*   $T_P$ is the target profile embedding of the path.
*   $\text{Similarity}(C, T_P) = \frac{C \cdot T_P}{\|C\| \|T_P\|}$ (Cosine Similarity).
*   $\alpha, \beta, \gamma$ are weights configured at the runtime level.

### 3.2 Z-Score Evaluation for Routing Pathways
When comparing two agent cohorts (e.g., Code Generator A vs. Code Generator B) to determine dynamic routing rules under A/B test patterns, the system calculates the Z-score of success rates:

$$Z = \frac{p_1 - p_2}{\sqrt{p(1-p)\left(\frac{1}{n_1} + \frac{1}{n_2}\right)}}$$

Where:
*   $p_1, p_2$ are the success rates of Cohort 1 and Cohort 2 respectively.
*   $n_1, n_2$ are the sample sizes (executions) of each cohort.
*   $p$ is the pooled success rate: $p = \frac{x_1 + x_2}{n_1 + n_2}$ (with $x_i$ being the total successful executions).
*   If $|Z| > 1.96$, the performance difference is statistically significant at the $95\%$ confidence level, triggering an automated update to the routing weights.

---

## 4. Multi-Agent Communication Protocol

Agents communicate via structured envelopes. Direct prompt injection is mitigated by isolating system commands from user payloads inside the envelope.

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "AgentMessageEnvelope",
  "type": "object",
  "properties": {
    "message_id": { "type": "string", "format": "uuid" },
    "parent_id": { "type": ["string", "null"] },
    "sender": { "type": "string" },
    "recipient": { "type": "string" },
    "timestamp": { "type": "string", "format": "date-time" },
    "intent": { "type": "string", "enum": ["REQUEST", "RESPONSE", "BROADCAST", "ERROR"] },
    "payload": {
      "type": "object",
      "properties": {
        "content": { "type": "string" },
        "structured_data": { "type": "object" },
        "error_code": { "type": ["string", "null"] }
      },
      "required": ["content"]
    },
    "security_token": { "type": "string" }
  },
  "required": ["message_id", "sender", "recipient", "timestamp", "intent", "payload"]
}
```

---

## 5. System Cross-References
*   To examine the engine implementation of this orchestrator, see [ENGINE_WORKFLOW_ORCHESTRATION.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/uaieos_parts/ENGINE_WORKFLOW_ORCHESTRATION.md).
*   For the cost management and optimization controls, refer to [PART_13_AI_ECONOMICS.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/uaieos_parts/PART_13_AI_ECONOMICS.md).
*   For self-healing runtimes, refer to [PART_14_AUTONOMOUS_AI_OPERATIONS.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/uaieos_parts/PART_14_AUTONOMOUS_AI_OPERATIONS.md).
