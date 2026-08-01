# Feature Prioritization Matrix (RICE & MoSCoW)

## 1. Document Overview
This document outlines the prioritization framework for features and initiatives. By combining the qualitative prioritization of **MoSCoW** with the quantitative rigor of **RICE**, we ensure that resources are allocated to features that deliver the highest user impact with the lowest engineering effort.

---

## 2. MoSCoW Categorization Framework
The MoSCoW method groups features into four categories to establish a baseline of launch expectations.

```
  [ MUST HAVE ] -----------------------> Non-negotiable launch requirements.
  [ SHOULD HAVE ] ---------------------> Important but not critical; workaround exists.
  [ COULD HAVE ] ----------------------> Nice-to-have; low impact if omitted.
  [ WON'T HAVE ] ----------------------> Out of scope for this release cycle.
```

1.  **Must Have (M):** Non-negotiable requirements without which the product cannot launch. There is no manual workaround (e.g., *User authentication for a banking app*).
2.  **Should Have (S):** Important but not vital for launch. A manual workaround exists, or it can be delayed to a future patch (e.g., *One-click CSV export*).
3.  **Could Have (C):** Nice-to-have features that would improve the experience but have low business impact if excluded (e.g., *Dark mode interface*).
4.  **Won't Have (W):** Explicitly out of scope for the current release cycle. These are stored in the product backlog for future consideration.

---

## 3. RICE Scoring Methodology
To rank items within MoSCoW categories, we apply the RICE formula:

$$\text{RICE Score} = \frac{\text{Reach} \times \text{Impact} \times \text{Confidence}}{\text{Effort}}$$

### 3.1. RICE Inputs Scoring Key

*   **Reach ($R$):** Estimated number of users impacted per month (e.g., `12,000` users).
*   **Impact ($I$):** Emotional or functional impact on the user:
    *   $3$ = Massive Impact
    *   $2$ = High Impact
    *   $1$ = Medium Impact
    *   $0.5$ = Low Impact
    *   $0.25$ = Minimal Impact
*   **Confidence ($C$):** Percentage of certainty about our estimates (based on user tests, data):
    *   $1.0$ ($100\%$) = High Confidence (validated with users/data)
    *   $0.8$ ($80\%$) = Medium Confidence (proxy metrics, team consensus)
    *   $0.5$ ($50\%$) = Low Confidence (gut feeling, unvalidated idea)
*   **Effort ($E$):** Estimated engineering and design time in person-months (e.g., `2.5` months. Minimum is `0.5`).

---

## 4. Prioritization Matrix
Evaluate and rank your backlog using this combined prioritization table.

| Feature Name / ID | MoSCoW | Reach ($R$) | Impact ($I$) | Confidence ($C$) | Effort ($E$) | RICE Score | Priority Rank |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| *e.g., SSO Login* | *Must* | *10,000* | *2.0* | *100%* | *1.0* | **20,000** | **1** |
| *e.g., Custom Theme* | *Could* | *2,000* | *0.5* | *80%* | *2.0* | **400** | **4** |
| | | | | | | | |
| | | | | | | | |
| | | | | | | | |

---

## 5. Kano Model Satisfaction Check (Optional)
To validate the RICE scores against user delight, classify high-scoring features into Kano categories:

```
  SATISFACTION
      High ^
           |                                     . [ Delighter / Attractive ]
           |                                  .
           |                               .
           |   . . . . . . . . . . . . . . [ Linear / Performance ]
           | .
       Low |-------------------------------------------------------->
           | . . . . . . . . . . . . . . . [ Must-Be / Basic Need ]
       Low |
           |                                     EXPECTATION / EXECUTION High
```

1.  **Must-Be Features:** Expected features. Their presence doesn't delight, but their absence causes massive frustration (e.g., app stability).
2.  **Linear / Performance Features:** Customer satisfaction is directly proportional to how well these features perform (e.g., page loading speed, database limits).
3.  **Attractive / Delighters:** Unexpected features that surprise and delight users. Their absence causes no dissatisfaction (e.g., custom animations, easter eggs).

---

## 6. Revision History
*   **V1.0 (2026-06-26):** Initial creation of prioritization framework template.
