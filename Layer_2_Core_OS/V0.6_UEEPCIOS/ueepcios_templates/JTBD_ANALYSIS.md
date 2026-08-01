# Template: Jobs-to-be-Done Analysis

## 1. Document Control
*   **Project Name**: [Project Name]
*   **JTBD ID**: JTB-[UUID]

---

## 2. The Core Customer Jobs (JTBD Statement)
*Formulate the user's core motivation using the JTBD schema:*

```
"When I am [Context/Situation], I want to [Action/Workaround], so that I can [Target Outcome/Benefit]."
```

*   **Job 1 (Enterprise SRE)**:
    *   *Statement*: When I am diagnosing database deadlocks, I want to trace query blocks across subnets, so that I can reduce MTTR to under 15 minutes.
*   **Job 2 (Product Lead)**:
    *   *Statement*: When I am launching a new billing tier, I want to route checkouts via Stripe, so that I can minimize integration dev cycles.

---

## 3. Job Outcomes & Success Metrics
*   *Success Metric (Job 1)*: Time to locate blocking query reduced from 4 hours to 5 minutes.
*   *Success Metric (Job 2)*: New payment checkout deployed within 2 hours of billing changes.
