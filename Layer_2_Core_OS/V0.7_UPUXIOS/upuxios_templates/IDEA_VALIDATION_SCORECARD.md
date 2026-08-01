# Idea Validation Scorecard

## 1. Document Overview
This scorecard is used to evaluate, rank, and validate new product features, product offerings, or startup ideas before allocating significant engineering resources. It helps avoid building products nobody wants by relying on empirical data and structured prioritization.

---

## 2. Hypothesis Formulation
Before evaluating the idea, formulate the core hypothesis:

*   **We believe that:** [Describe target user segment]
*   **Will perform this action:** [Describe target behavior / solution usage]
*   **Because of this value proposition:** [Describe problem solved / motivation]
*   **We will know this is true when we see:** [Measurable metric, e.g., 20% conversion rate on smoke test]

---

## 3. Quantitative Scorecard Matrix
Score the idea across the following five dimensions. Use the scoring guidelines below the matrix.

| Evaluation Dimension | Weight | Score (1-5) | Weighted Score | Evidence / Validation Source |
| :--- | :--- | :--- | :--- | :--- |
| **1. Problem Urgency & Intensity** | 25% | | | |
| **2. Reach & Market Addressability** | 20% | | | |
| **3. Execution Feasibility** | 20% | | | |
| **4. Strategic Business Alignment** | 15% | | | |
| **5. Willingness to Pay / Invest** | 20% | | | |
| **TOTAL SCORE** | **100%** | | **[Sum Weighted]**| |

### Scoring Guidelines (1 to 5 Scale)
*   **Problem Urgency:**
    *   *5 (Critical):* User actively searches for solutions; experiences immediate loss (time/money).
    *   *1 (Nice-to-Have):* Mild inconvenience; user works around it without stress.
*   **Reach & Market Addressability:**
    *   *5 (Broad):* Applies to $\ge 80\%$ of target customer segments.
    *   *1 (Niche):* Applies to $< 5\%$ of a specific user sub-segment.
*   **Execution Feasibility:**
    *   *5 (Simple):* Can be built by current team in $< 2$ weeks; no new technology stack needed.
    *   *1 (Highly Complex):* Requires custom research, infrastructure changes, or $> 3$ months.
*   **Strategic Business Alignment:**
    *   *5 (Direct):* Core to achieving current company Objectives & Key Results (OKRs).
    *   *1 (Distraction):* Interesting idea, but strays away from core vision.
*   **Willingness to Pay / Invest:**
    *   *5 (Validated):* Users have pre-ordered, paid deposits, or agreed in writing.
    *   *1 (Unproven):* Users say they "might" use it, but no financial/time commitment is demonstrated.

---

## 4. Prioritization Index: RICE Framework
To cross-reference this idea against other validated ideas, compute the RICE Score:

$$\text{RICE Score} = \frac{\text{Reach} \times \text{Impact} \times \text{Confidence}}{\text{Effort}}$$

### Input Definitions:
1.  **Reach (Monthly Users):** How many users will this feature impact in a 30-day period?
2.  **Impact Score:**
    *   $3.0$ = Massive Impact
    *   $2.0$ = High Impact
    *   $1.0$ = Medium Impact
    *   $0.5$ = Low Impact
    *   $0.25$ = Minimal Impact
3.  **Confidence (%):** How confident are you in your estimates (based on user testing, data)?
    *   $100\%$ = High Confidence (data/customer quotes)
    *   $80\%$ = Medium Confidence (proxy metrics)
    *   $50\%$ = Low Confidence (gut feeling)
4.  **Effort (Person-Months):** Number of months it will take one person to build it (minimum of $0.5$).

### RICE Calculation:
*   **Reach:** `______`
*   **Impact:** `______`
*   **Confidence (%):** `______`
*   **Effort:** `______`
*   **RICE Score Result:** `______`

---

## 5. Validation Experiments Tracker
Define the validation experiments to test the riskiest assumptions.

```
       UNVALIDATED  [ Smoke Test / Landing Page ] ---> Measure Click-Through
            |
            v
       SEMI-VALIDATED  [ Concierge / Wizard of Oz ] -> Measure Time/Work Effort
            |
            v
        VALIDATED   [ High-Fi Prototype / Pre-Sales ] -> Measure Financial Transaction
```

| Risk Level | Experiment Type | Execution Details | Target Metric for Success | Actual Result | Status (Pass/Fail) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **High** | *Smoke Test (e.g., Landing Page)* | *Create a landing page with a CTA button "Join Waitlist".* | *Conversion rate $\ge 15\%$* | | |
| **Medium** | *Wizard of Oz / Concierge* | *Deliver the service manually behind the scenes.* | *Retention rate $\ge 50\%$ after 2 weeks* | | |
| **Low** | *Interactive Prototype* | *Run remote usability testing sessions.* | *System Usability Scale (SUS) $\ge 80$* | | |

---

## 6. Revision History
*   **V1.0 (2026-06-26):** Created comprehensive idea validation scorecard.
