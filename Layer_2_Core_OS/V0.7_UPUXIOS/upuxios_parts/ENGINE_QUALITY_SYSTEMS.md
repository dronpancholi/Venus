# Engine: Quality Systems

## 1. Context & Strategy

### 1.1 Purpose
The Quality Systems Engine aggregates heuristic ratings, usability review metrics, and cognitive walkthrough tables to calculate the unified UX Quality Score (UXQS). It prevents low-quality interface deployments by acting as an automated compliance gateway.

### 1.2 Philosophy
Do not rely on subjective design reviews. Screen usability, step-by-step cognitive loops, and task completion metrics must be tracked, scored, and audited against strict quantitative limits.

---

## 2. Ingest Parameters & Taxonomy

### 2.1 Inputs & Outputs
*   **Inputs**: Auditor heuristic sheets, cognitive walkthrough logs, task completion metrics (TSR, ToT), SUS questionnaires as defined in [Part 17](file:///Users/dronpancholi/Developer/01_Strategic/Venus/upuxios_parts/PART_17_QUALITY_SYSTEMS.md).
*   **Outputs**: Unified UX Quality Scorecard, listing heuristic failures, cognitive walkthrough gaps, and overall usability ratings.

### 2.2 Auditing Pipeline
```
                 [Ingest Auditor Evaluation Sheets]
                                 │
                   [Heuristic Weighted Aggregation]
                    └── Calculate overall UXQS
                                 │
                  [Walkthrough Question Analyzer]
                    └── Verify 4 cognitive questions
                                 │
                   [Usability KPI Calculator]
                    └── Process TSR, ToT, and SUS
                                 │
                     [Release Threshold Gate]
```

---

## 3. Algorithmic Checks & Scoring Calculations

### 3.1 UX Quality Score (UXQS) Aggregation
The engine compiles individual heuristic evaluation ratings into the final UXQS:

$$\text{UXQS} = 100 - \sum_{i=1}^{10} w_i \times \text{Severity}_i$$

Where:
*   $\text{Severity}_i$ is the average severity score ($0-4$) logged by auditors.
*   $w_i$ is the weight parameter (assigned to prioritize user friction areas, such as $w = 2.5$ for Error Prevention).

If the resulting score falls below the mandatory gate ($\text{UXQS} < 85$), the system flags the view and prevents build integration.

### 3.2 Usability Metrics Analyzer
The engine parses usability review logs to calculate:
*   **Task Success Rate (TSR)**:
    $$\text{TSR} = \frac{\text{Completed Tasks}}{\text{Total Attempted Tasks}} \times 100$$
    *Required Gate*: $\text{TSR} \ge 90\%$ for primary onboarding and checkout workflows.
*   **System Usability Scale (SUS)**: Compiles the standard 10-question Likert-scale responses.
    *Required Gate*: $\text{SUS} \ge 80$.

---

## 4. Reusable Checklist & Exit Criteria
*   [ ] Checked that auditor logs cover all 10 usability heuristics.
*   [ ] Calculated the final UXQS and verified it meets the $\ge 85$ gating requirement.
*   [ ] Audited cognitive walkthrough tables to ensure zero unresolved action failures.
*   [ ] Verified that Usability Review cohorts meet sizing standards (minimum 5 users).
*   [ ] Confirmed TSR, ToT, and SUS scores meet the target benchmarks.
*   *Exit Criteria*: UX Quality Scorecard finalized and approved for production release.
