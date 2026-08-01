# Engine: User Intelligence

## 1. Context & Strategy

### 1.1 Purpose
The User Intelligence Engine maps incoming user attributes, client environment data, and behavioral inputs against the project's Ideal Customer Profile (ICP) specifications. It calculates user profile compatibility to ensure that design and technical deliverables fit target user capabilities.

### 1.2 Philosophy
Understand the user's operational reality. A software design optimized for a multi-monitor desktop administrator is broken if rendered on a low-bandwidth cellular link for a field technician. The engine checks user profile bounds to identify layout mismatch risks.

---

## 2. Ingest Parameters & Taxonomy

### 2.1 Inputs & Outputs
*   **Inputs**:
    *   `Domain_Match`: Value ($0.0 - 1.0$) indicating role alignment with compliance/regulatory expertise requirements.
    *   `Technical_Match`: Value ($0.0 - 1.0$) indicating proficiency with systems management interfaces.
    *   `Environment_Match`: Value ($0.0 - 1.0$) representing network speed, system screen resolution, and computing hardware compatibility.
*   **Outputs**:
    *   `Profile Match Index (PMI)`: Float score ($0.0 - 1.0$).
    *   `Classification`: `Match Approved`, `Match Warning`, or `Match Critical Failure`.

### 2.2 Calculations Pipeline
The engine executes a weighted scoring matrix:

$$\text{PMI} = (w_1 \times \text{Domain\_Match}) + (w_2 \times \text{Technical\_Match}) + (w_3 \times \text{Environment\_Match})$$

Where:
*   $w_1$: Domain weight (Default = $0.40$).
*   $w_2$: Technical capacity weight (Default = $0.30$).
*   $w_3$: Hardware/Environmental environment weight (Default = $0.30$).

Note: The weights must satisfy $\sum w_i = 1.0$.

```
                      [Ingest User Profile Parameters]
                                     │
                        [Apply Weighted Coefficient]
                                     │
                         [Calculate Final PMI Score]
                         /           │             \
          (PMI >= 0.75) /            │             \ (PMI < 0.50)
                       ▼             ▼              ▼
           [Match Approved]   [Match Warning]   [Match Critical Failure]
```

### 2.3 Threshold Levels
*   **Match Approved ($\text{PMI} \ge 0.75$)**: User characteristics align with core system capabilities. Safe for standard layouts.
*   **Match Warning ($0.50 \le \text{PMI} < 0.75$)**: Potential mismatch (e.g., user is a domain expert but lacks technical environment capacity). Layouts must offer guided assistance screens.
*   **Match Critical Failure ($\text{PMI} < 0.50$)**: Severe mismatch. Block standard GUI deployment; route user to dedicated setup wizards or terminal help paths.

---

## 3. Reusable Checklist & Exit Criteria
*   [ ] Checked that profile metadata is compiled from real user sessions.
*   [ ] Confirmed weight coefficients match current product release priorities.
*   [ ] Verified network bandwidth tests are included in the environment evaluation.
*   *Exit Criteria*: User profile validation passes with a PMI $\ge 0.75$, or secondary support documentation is generated.
