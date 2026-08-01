# Heuristic Usability Review Template

## 1. Document Overview
This template provides guidelines, evaluation metrics, scoring rules, and prioritization frameworks to conduct heuristic usability audits.

---

## 2. Evaluation Methodology & Heuristics
Reviews are based on **Jakob Nielsen's 10 Usability Heuristics**. Assess each issue and score its severity from 0 to 4:

| Severity Rating | Definition | Action Timeline |
| :--- | :--- | :--- |
| **0 - No Issue** | Usability is good; no problems detected. | None. |
| **1 - Cosmetic** | Minor aesthetic issue; does not affect tasks. | Fix if time permits. |
| **2 - Minor** | Low-priority issue; users can easily find workarounds. | Address in next minor release. |
| **3 - Major** | Important issue; makes tasks difficult. High friction. | Priority fix in upcoming sprint. |
| **4 - Catastrophe** | Critical issue; blocks tasks. Causes data loss. | Block release; fix immediately. |

---

## 3. Heuristic Evaluation Matrix
Use this table to record and analyze usability issues during reviews:

| Heuristic Area | Screen / View | Issue Description | Severity | Suggested Action |
| :--- | :--- | :--- | :--- | :--- |
| **H1: System Status** | Checkout Page | No loading spinner during payment processing. | 3 | Add spinner and lock submit button. |
| **H2: Match System/Real World** | Team Dashboard | Uses technical database keys instead of names. | 2 | Display user names in list columns. |
| **H5: Error Prevention** | Delete Project | Clicking delete executes immediately without confirmation. | 4 | Add confirmation dialog and double-check prompt. |
| **H7: Flexibility & Efficiency**| Document Edit | Lacks keyboard shortcuts for saving drafts. | 2 | Add `Ctrl + S` shortcut and show in tooltips. |

---

## 4. Review Session Protocol
*   **Auditor Role:** Walk through user scenarios systematically.
*   **Device Checks:** Run tests across Chrome, Safari, and mobile views.
*   **Documentation:** Record screen recordings and screenshots of issues.

---

## 5. Prioritization Matrix (RICE Score)
Prioritize fixing identified issues using the RICE scoring model:

$$\text{RICE Score} = \frac{\text{Reach} \times \text{Impact} \times \text{Confidence}}{\text{Effort}}$$

Where:
*   $\text{Reach}$: Number of users affected per month.
*   $\text{Impact}$: Severity impact of the fix ($3$ for critical, $0.25$ for minimal).
*   $\text{Confidence}$: Reviewer certainty score ($50\%$ to $100\%$).
*   $\text{Effort}$: Developer time required (measured in person-weeks).

---

## 6. Verification Checklist
- [ ] Rate every usability issue using the severity scale.
- [ ] Calculate RICE scores to prioritize fixes.
- [ ] Confirm recommendations include design improvements.
- [ ] Share reports with both design and development teams.

---

## 7. Revision History
*   **V1.0 (2026-06-26):** Initial Heuristic Usability Review template.\n