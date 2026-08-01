# Template: Root Cause Report

## 1. Meta Control
*   **Project Name**: [Project Name]
*   **Intake ID**: INT-[UUID]
*   **Root Cause ID**: RC-[UUID]
*   **Analysis Date**: [Date]
*   **Lead Analyst**: [Name]

---

## 2. Executive Root Cause Summary
*Provide a concise summary of the verified root cause and the evidence that supports it.*

---

## 3. The Five Whys Deep-Dive
*Trace the path from the primary symptom down to the systemic or latent root cause.*

*   **Symptom / Starting Point**: [Describe the visible operational or technical failure]
    *   *Why?* (Why does this symptom occur?)
        *   **Answer**: [Description]
    *   *Why?* (Why does the immediate cause occur?)
        *   **Answer**: [Description]
    *   *Why?* (Why does the underlying cause occur?)
        *   **Answer**: [Description]
    *   *Why?* (Why does that process or system behavior occur?)
        *   **Answer**: [Description]
    *   *Why?* (What is the final, root cause/policy/architecture that forces this?)
        *   **Answer**: [Validated Root Cause]

---

## 4. Fishbone (Ishikawa) Analysis Mapping
Categorize the contributing causes to the core issue:

```
  People                      Process                      Technology
    │                           │                            │
    ├─ [Inadequate training]    ├─ [Unclear SLA standards]   ├─ [Database lock contention]
    │                           │                            │
    ▼                           ▼                            ▼
 ───────────────────────────────────────────────────────────────► [PRIMARY SYMPTOM]
    ▲                           ▲                            ▲
    │                           │                            │
    ├─ [Outdated runbooks]      ├─ [Manual approvals]        ├─ [Legacy API rate limits]
    │                           │                            │
  Materials / Data            Environment                  Infrastructure / Tools
```

### 4.1 Detailed Contributors
*   **People / Skills**: [e.g., Team lacked specialized performance tuning capability]
*   **Process / Methodology**: [e.g., Deployments run without pre-prod scaling tests]
*   **Technology / Systems**: [e.g., Deadlocks in high-throughput transactional flows]
*   **Materials / Data Quality**: [e.g., Upstream webhook formats change without schema enforcement]
*   **Environment**: [e.g., Local dev setup does not mirror concurrency behaviors of prod]
*   **Infrastructure / Tools**: [e.g., Log aggregation lacks transaction tracing across workers]

---

## 5. Fault Tree Analysis (FTA)
Represent the logical combinations of failures that lead to the primary system failure:

```
                  +----------------------------------------+
                  |  [T] Primary System Failure (Symptom)  |
                  +----------------------------------------+
                                      │
                                     AND
                                      ├─── (G1) Concurrency Overrun
                                      └─── (G2) Lack of Fallback Cache
                                      
                  +-------------------+      +-------------------+
                  | (G1) Concurrency  |      |  (G2) No Cache    |
                  +-------------------+      +-------------------+
                            │                          │
                           OR                         AND
                            ├── (E1) Batch size overflow├─ (E3) Redis out of memory
                            └── (E2) CPU throttling    └─ (E4) Config misaligned
```

*   **Top Event (T)**: [Primary Symptom Name]
*   **Gate 1 (G1)**: [Contributing Intermediate Failure] | **Logic**: [AND/OR]
    *   *Event E1*: [Basic Failure Event] | *Probability*: [e.g., 0.05]
    *   *Event E2*: [Basic Failure Event] | *Probability*: [e.g., 0.12]
*   **Gate 2 (G2)**: [Contributing Intermediate Failure] | **Logic**: [AND/OR]
    *   *Event E3*: [Basic Failure Event] | *Probability*: [e.g., 0.02]
    *   *Event E4*: [Basic Failure Event] | *Probability*: [e.g., 0.08]

---

## 6. Causal Loop Diagram (Systems Context)
Describe the reinforcing (R) or balancing (B) feedback loops causing the issue:

```
[System Load] ────(+)────► [Database Latency] ────(+)────► [Retry Loops]
      ▲                                                           │
      │                                                           │
      └──────────────────────────(+)──────────────────────────────┘
                          (R1: Reinforcing Retry Storm)
```

*   **Loop R1 (Reinforcing Retry Storm)**:
    *   *Mechanism*: Higher system load causes database latency to spike, triggering client-side retry loops, which further increases system load.
    *   *Leverage Point*: Implement exponential backoff, client jitters, or a circuit breaker to break the loop.

---

## 7. Root Cause Categorization Matrix

| Cause Type | Identified Item | Verification Evidence |
|---|---|---|
| **Direct Cause** | [Immediate physical/digital cause] | [e.g., Sentry event ID #4928] |
| **Systemic Cause** | [Procedural or architectural failure] | [e.g., No auto-scaling policies on DB node] |
| **Latent Cause** | [Dormant bug or structural configuration] | [e.g., Maximum thread pool limits set to 10] |
| **External Cause** | [Third-party API or provider constraint] | [e.g., Cloudflare rate limiting webhook IPs] |
| **Organizational Cause** | [Policy, budget, or training block] | [e.g., Security policy mandates synchronous audits] |

---

## 8. Resolution Guidance & Leverage Points
*   **High-Leverage Remediation**: [Define the single, highest-yield change that eliminates the root cause permanently]
*   **Effort vs. Impact**:
    *   *Estimated Implementation Effort*: [High / Medium / Low]
    *   *Expected Root Cause Reduction*: [e.g., 100% mitigation of retry storm failures]
