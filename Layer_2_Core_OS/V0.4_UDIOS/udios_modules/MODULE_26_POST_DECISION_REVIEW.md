# Module 26 — Post-Decision Review

## 1. Context & Strategy

### 1.1 Purpose
The Post-Decision Review triggers ongoing performance tracking post-implementation, verifying actual system behavior against the baseline expectations documented in the ADR.

### 1.2 Philosophy
Decisions are hypotheses; implementation is the experiment. We measure results 30 days after deployment to confirm that the chosen solution met its performance and cost targets.

---

## 2. Ingest Parameters & Schema

### 2.1 Inputs & Outputs
*   **Inputs**: Original ADR, Sentry/Datadog metric snapshots, cloud billing invoices.
*   **Outputs**: Post-Decision Review Report (PDR) detailing performance deltas.

### 2.2 Metric Comparison Mappings
Every PDR compares:
*   *Projected Latency* vs. *Actual Latency*.
*   *Projected Monthly Cost* vs. *Actual Monthly Cost*.
*   *Projected Developer Setup Hours* vs. *Actual Developer Setup Hours*.

---

## 3. Operational Algorithm & Feedback Loop

### 3.1 The Review Timeline
```
                       [Decision Deployed to Prod]
                                    │
                         [Wait 30 Days Telemetry]
                                    │
                        [Generate Actual Metrics]
                                    │
                     [Calculate Performance Delta]
                                    │
                  [Update Institutional Memory (M21)]
```

### 3.2 Failure / Regret Flag Trigger
If the actual metrics exceed projected values by > 20% on any vector, the decision is flagged as a **REGRET**, triggering an immediate review spike.

---

## 4. Reusable Templates & Checklists

### 4.1 Template: Post-Decision Review (PDR)
```markdown
### 1. Review Summary
*   **Decision ID**: DEC-[UUID]
*   **Deployment Date**: YYYY-MM-DD
*   **Review Date**: YYYY-MM-DD

### 2. Metric Projections vs. Actuals
*   *Latency (Target)*: < 5ms | *Actual*: 2.8ms (Success)
*   *Monthly Cost (Target)*: < $200 | *Actual*: $350 (Failed - 75% overrun)
*   **Verdict**: **REGRET** (Triggers cost-optimization review)
```

### 4.2 Checklist
*   [ ] Captured 30-day telemetry logs.
*   [ ] Checked cloud provider billing ledgers.
*   [ ] Calculated deltas.
*   [ ] Updated memory registers.

---

## 5. SRE, AI-Agent, & Safety Parameters

### 5.1 AI-Agent Execution Instructions
1.  **Parse**: Read Prometheus or Datadog APIs to pull latency targets.
2.  **Alert**: If actual memory limits exceed 90% of constraints, create warning tickets.

### 5.2 Common Anti-patterns
*   *The "Ignore the Bill" Habit*: Checking latency and speed metrics but ignoring cloud cost overruns until the quarterly invoice arrives.

### 5.3 Exit Criteria
*   PDR Report compiled and **memory registers updated**.
*   Proceed to **Module 27: Decision Knowledge Graph**.
