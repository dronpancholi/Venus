# Human-in-the-Loop (HITL) Override UX Spec

## 1. Document Overview
This document specifies workflow gates, verification layouts, approval menus, and override logs for Human-in-the-Loop (HITL) processes. It ensures high-risk AI operations are checked and approved by human operators.

---

## 2. Critical Intercept Criteria
High-risk actions require human verification before execution. Risk is calculated using a standard formula:

$$\text{Risk Score} = \text{Severity} \times \text{Probability}$$

Where:
*   $\text{Severity}$ = Business impact of error (scaled $1$ to $10$).
*   $\text{Probability}$ = Likelihood of model error ($1 - \text{Confidence Score}$).
*   **HITL Threshold:** Actions with a **Risk Score $\ge 2.5$** must be held for review.

| Risk Level | Risk Score | Action Target | Workflow Gate Behavior |
| :--- | :--- | :--- | :--- |
| **High Risk** | $\ge 5.0$ | Bulk database updates, financial transactions $> \$5,000$. | Strict Block. Lock action, send notification to administrator, log event. |
| **Medium Risk** | $2.5 - 4.9$ | Minor permissions shifts, bulk marketing emails. | Warn & Review. Show inline approval panel with change diff. |
| **Low Risk** | $< 2.5$ | Layout updates, minor profile edits. | Auto-approve. Log action, execute immediately. |

---

## 3. Review & Verification Interface
The override screen displays a side-by-side comparison of the AI's proposed action and the user's original request.

```
+--------------------------------------------------------------------------+
|  [Review Required]: High-Risk Transaction Request                        |
+--------------------------------------------------------------------------+
|  Original Request:                      AI Proposed Action:              |
|  "Pay invoice for vendor Acme Corp."    Send $12,500 to Account ...4321  |
|                                         [Warning]: Account mismatch.      |
|                                                                          |
|  [Change Diff View]                                                      |
|  - Vendor Account: ...1111 (Current)                                     |
|  + Vendor Account: ...4321 (Proposed by AI - source: email attachment)   |
+--------------------------------------------------------------------------+
|  [Reject Action]          [Modify Options]          [Approve & Execute]  |
+--------------------------------------------------------------------------+
```

*   **Diff Styling:** Show deletions in red (`--color-error-bg`) and additions in green (`--color-success-bg`).

---

## 4. Escalation & Team Workflows
*   **Routing Rules:** Send reviews to the appropriate team inbox based on the active project or permissions level.
*   **Review Timeouts:** If a review is not completed within $15$ minutes, return the task to the queue and alert supervisor roles.

---

## 5. Conflict Resolution & Logging
Every override action must be logged to keep records complete:
*   **Operator Metadata:** Record the reviewer's ID, timestamp, and decision (Approve, Reject, Modify).
*   **Override Category:** Require operators to choose a category from a dropdown menu (e.g., Incorrect Account, Wrong Amount, Model Error).
*   **Feedback Loop:** Export logs daily to retrain the AI models.

---

## 6. Verification Checklist
- [ ] Test screen reader announcements when a high-risk process is paused for review.
- [ ] Verify that diff views display changes clearly in high-contrast modes.
- [ ] Confirm timeout alerts trigger escalation notifications correctly.
- [ ] Verify that override logs record decisions and metadata accurately.

---

## 7. Revision History
*   **V1.0 (2026-06-26):** Initial HITL Override UX Specification template.\n