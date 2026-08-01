# Engine: Product Discovery

## 1. Context & Strategy

### 1.1 Purpose
The Product Discovery Engine ingests opportunity ratings, customer survey data, and technical assessments to calculate discovery priority values. By comparing user demand against feasibility, the engine prevents team focus from shifting to low-yield or technically unviable features.

### 1.2 Philosophy
Value is validation. We do not build things because they sound interesting; we build them when there is a documented, under-served customer need paired with a clear path to engineering feasibility.

---

## 2. Ingest Parameters & Taxonomy

### 2.1 Inputs & Outputs
*   **Inputs**:
    *   `Importance (I)`: Value from $1.0 - 10.0$ based on user research surveys.
    *   `Satisfaction (S)`: Value from $1.0 - 10.0$ based on satisfaction with current workarounds.
    *   `Feasibility_Index (FI)`: Integer from $1 - 5$ ($1$: multi-quarter research, $5$: standard off-the-shelf solution).
    *   `Viability_Index (VI)`: Integer from $1 - 5$ ($1$: negative unit economics, $5$: high strategic/commercial yield).
*   **Outputs**:
    *   `Opportunity Score (OS)`: Value from $1.0 - 20.0$.
    *   `Discovery Priority Index (DPI)`: Score from $1.0 - 500.0$.
    *   `Discovery Category`: `Fast-Track`, `Backlog`, or `Archive`.

### 2.2 Calculations Pipeline
The engine processes inputs using the following equations:

$$\text{OS} = I + \max(I - S, 0)$$

$$\text{DPI} = \text{OS} \times \text{FI} \times \text{VI}$$

```
                          [Ingest Survey & Tech Data]
                                      │
                         [Calculate OS & DPI Metrics]
                                      │
                        [Classify Priority Boundaries]
```

### 2.3 Threshold Levels
*   **Fast-Track ($\text{DPI} \ge 250$)**: High importance, low current satisfaction, easy to implement, commercially viable. Queue immediately for strategy maps.
*   **Backlog ($100 \le \text{DPI} < 250$)**: Good potential. Refine concept or reduce engineering complexity to boost feasibility.
*   **Archive ($\text{DPI} < 100$)**: Over-served needs, hyper-difficult build paths, or commercially unviable concepts.

---

## 3. Reusable Checklist & Exit Criteria
*   [ ] Checked that survey sample size ($N$) is $\ge 15$ responses before running calculator.
*   [ ] Verified Feasibility Index rating is signed off by Engineering Architecture lead.
*   [ ] Audited Viability Index against the Business Model selectors (V0.6).
*   *Exit Criteria*: Discovery Priority report saved to the product catalog with a status of Fast-Track or Backlog.
