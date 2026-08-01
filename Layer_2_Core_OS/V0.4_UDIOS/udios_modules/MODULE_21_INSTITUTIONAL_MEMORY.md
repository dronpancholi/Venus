# Module 21 — Institutional Memory Engine

## 1. Context & Strategy

### 1.1 Purpose
The Institutional Memory Engine logs post-decision outcomes, incidents, and regrets. It feeds this telemetry back into Module 01 (Intake) to adjust weighting parameters for future proposals.

### 1.2 Philosophy
History repeats itself when it is forgotten. By cataloging past architectural failures and comparing them to the original decision parameters, we prevent the organization from repeating known mistakes.

---

## 2. Ingest Parameters & Schema

### 2.1 Inputs & Outputs
*   **Inputs**: Post-decision review logs, Sentry incidents, developer feedback entries.
*   **Outputs**: Adjusted weights database and updated historical regret registry.

### 2.2 Telemetry Schema
Every memory record logs:
*   **Original DEC-ID**: DEC-[UUID].
*   **Outcome Type**: Success / Neutral / Failure (Regret).
*   **Root Deviation**: Difference between projected and actual metrics (e.g. latency projected 5ms, actual 20ms).
*   **Root Cause Category**: Code bug, vendor SLA failure, scaling bottleneck.

---

## 3. Operational Algorithm & Feedback Loop

### 3.1 Weight Adjuster Pipeline
```
                          [Incident Registered]
                                    │
                         [Resolve to DEC-[UUID]]
                                    │
                  [Calculate Deviation Delta (D)]
                                    │
                  [Adjust Source Weight Multiplier]
```

### 3.2 Adjustment Formula
The multiplier adjustment is calculated as:

\[Weight_{New} = Weight_{Old} \times (1 - \alpha \times Deviation\_Delta)\]

Where:
*   \(\alpha\): Learning rate constant (e.g., 0.1).
*   \(Deviation\_Delta\): Normalized difference between projected and actual values (0.0 to 1.0).

---

## 4. Reusable Templates & Checklists

### 4.1 Template: Historical Regret Log
```markdown
### 1. Memory Profile: MEM-[UUID]
*   **Target Decision**: DEC-001 (Migrate Session Store to Local Memory)
*   **Outcome**: Failure
*   *Actual Deviation*: Memory load exceeded limits at 50 concurrent users (projected limit was 10,000).
*   *Adjustment*: Decreased source credibility score of the original proposer by 20%.
```

### 4.2 Checklist
*   [ ] Linked incident to original DEC-ID.
*   [ ] Quantified deviation metric.
*   [ ] Checked database configuration.
*   [ ] Saved memory record.

---

## 5. SRE, AI-Agent, & Safety Parameters

### 5.1 AI-Agent Execution Instructions
1.  **Parse**: Read incident logs to identify references to software name inputs.
2.  **Verify**: If a name matches a historical failure entity, inject warning notes into new intake flows.

### 5.2 Common Anti-patterns
*   *The Memory Void*: Deleting incident logs or failing to link outage root causes to past design choices, enabling repeat mistakes.

### 5.3 Exit Criteria
*   Historical Regret Log entry recorded and **weight adjuster coefficients updated**.
*   Proceed to **Module 22: Decision Confidence**.
