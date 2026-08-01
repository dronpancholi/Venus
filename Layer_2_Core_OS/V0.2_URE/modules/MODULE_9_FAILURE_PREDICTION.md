# Module 9 — Failure Prediction

## 1. Context & Strategy

### 1.1 Purpose
Failure Prediction uses structured pre-mortem analysis to identify and mitigate failure scenarios before engineering begins. By cataloging and ranking potential failure points, we ensure the system architecture is resilient to runtime anomalies, scaling issues, and security threats.

### 1.2 Philosophy
Excellence is not the absence of failure; it is the prediction and containment of failure. We assume our code, third-party APIs, and hosting providers will fail in production. We engineer safety loops to handle these failures.

---

## 2. Failure Mode and Effects Analysis (FMEA)

The engine ranks failure modes using a **Risk Priority Number (RPN)**:

\[RPN = Probability \times Impact \times Detectability\]

Where:
*   **Probability (1-5)**: Likelihood of the failure occurring.
*   **Impact (1-5)**: Severity of the failure to the business or customer data.
*   **Detectability (1-5)**: Ease of detecting the failure via automated telemetry (1: Immediately visible via SRE alerts. 5: Silent data corruption).

---

## 3. Inputs & Outputs

### 3.1 Inputs
*   Tech Stack Specification (from Stage 5).
*   Constraint Dependency Graph (from Module 7).
*   System telemetry setups.

### 3.2 Outputs
*   **Top Failure Scenarios Log**: Fully populated threat matrix.
*   **Automated System Fail-Safe Protocols**: Coded instructions for system recovery.

---

## 4. Operational Methodology & Failure Directory

### 4.1 The Top 10 High-Risk Failure Paths (Reference Directory)

| ID | Failure Mode | Trigger | RPN | Prevention Strategy | Contingency Action |
|---|---|---|---|---|---|
| **FAIL-01** | Database RLS bypass | Connection pool misconfiguration | 12 | Connection listeners enforce session variables | Raise boot error and halt server |
| **FAIL-02** | Temporal loop memory leak | High workflow history size | 16 | Enforce ContinueAsNew iterations | Purge old workflow runs |
| **FAIL-03** | Third-party rate limit lock | Concurrent outbound queries | 20 | Redis-backed sliding window rate limits | Temporal backoff and retry |
| **FAIL-04** | LLM Grounding Leak | Prompt injection payload | 15 | Input parsing validation layers | Block request; log IP |
| **FAIL-05** | Silent data corruption | Undetected database script errors | 10 | Strict type checks and DB constraints | Rollback transaction; page SRE |
| **FAIL-06** | Ingress endpoint attack | Direct open port calls | 12 | Bind internal ports to 127.0.0.1 | Firewall blocks IP |
| **FAIL-07** | Client data leak | Incorrect tenant SQL joins | 15 | Enforced RLS policy on all tables | Terminate connection |
| **FAIL-08** | Storage exhaustion | Unbounded snapshot growth | 8 | Automatic weekly database truncation | Archive to S3 storage |
| **FAIL-09** | Email Reader crash | Connection drops to IMAP server | 12 | Register retry policies on worker | Reconnect in 60s |
| **FAIL-10** | Auth token expiration | Key rotation script failure | 10 | Vault-managed keys rotation | Fallback to secondary cert |

---

## 5. Reusable Checklists & Templates

### 5.1 Failure Prediction Checklist
*   [ ] Conducted a project pre-mortem meeting.
*   [ ] Cataloged all high-probability failure points.
*   [ ] Calculated the RPN for all candidates.
*   [ ] Structured automated alerts for all silent failures.
*   [ ] Documented recovery playbooks.

### 5.2 Template: Pre-Mortem Scenario Sheet
```markdown
### 1. Failure Scenario: FAIL-[UUID]
*   **Description**: [e.g., Unbounded database growth from time-series logs causes disk exhaustion]
*   *Probability*: 4 | *Impact*: 4 | *Detectability*: 2
*   **Calculated RPN**: 32 (High Risk - Requires automated prevention)

### 2. Prevention & Recovery Blueprint
*   *System Prevention*: Execute a database partition cron task that automatically drops log tables older than 30 days.
*   *SRE Alert*: Alert triggers warning when disk volume exceeds 80% capacity.
```

---

## 6. SRE, AI-Agent, & Safety Parameters

### 6.1 AI-Agent Execution Instructions
1.  **Read**: Review database definitions, infrastructure Dockerfiles, and task queues.
2.  **Model**: Simulating high-traffic events, calculate resource load curves.
3.  **Identify**: Highlight where bottlenecks occur (e.g. database locks), entering them in the failure log.

### 6.2 Common Anti-patterns
*   **The Happy-Path Bias**: Assuming that because code passes unit tests locally, it will operate without issues under real-world network latency.
*   **Silent Failures**: Writing try-except blocks that catch errors but suppress logs, masking failures.

### 6.3 Exit Criteria
*   Top Failure Scenarios Log compiled and **SRE alert thresholds validated**.
*   Proceed to **Module 10: Systems Context**.
