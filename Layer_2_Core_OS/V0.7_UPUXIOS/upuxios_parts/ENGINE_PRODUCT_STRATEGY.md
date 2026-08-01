# Engine: Product Strategy & Prioritization

## 1. Context & Strategy

### 1.1 Purpose
The Product Strategy Engine automates feature prioritization by compiling RICE variables and Kano satisfaction coefficients. By calculating a unified Adjusted Priority Score (APS), it removes emotional bias from release planning and aligns engineering resources with high-yield business outcomes.

### 1.2 Philosophy
Maximize outcome per unit of effort. Prioritization is a mathematical optimization problem where we seek to deliver the greatest user impact while respecting developer capacity and cost constraints.

---

## 2. Ingest Parameters & Taxonomy

### 2.1 Inputs & Outputs
*   **Inputs**:
    *   `Reach (R)`: Numeric value representing quarterly active user volume.
    *   `Impact (I)`: Value ($0.25$ to $3.0$) mapping to expected user value.
    *   `Confidence (C)`: Float ($0.2$ to $1.0$) representing data certainty.
    *   `Effort (E)`: Float ($0.5$ to $12.0$) representing developer-months.
    *   `Kano_Category`: String enum (`Must-Be`, `One-Dimensional`, `Attractive`, `Indifferent`, `Reverse`).
*   **Outputs**:
    *   `RICE_Score`: Float value.
    *   `Adjusted Priority Score (APS)`: Unified priority value.
    *   `Strategy Decision`: `Build Now`, `Schedule Next`, `Defer`, or `Drop`.

### 2.2 Calculations Pipeline
The engine runs the primary RICE equation:

$$\text{RICE Score} = \frac{\text{Reach} \times \text{Impact} \times \text{Confidence}}{\text{Effort}}$$

Then, it applies a **Kano Adjustment Modifier ($\beta$)** to compute the final APS:

$$\text{APS} = \text{RICE Score} \times \beta$$

#### Kano Adjustment Coefficients ($\beta$):
*   `Must-Be`: $\beta = 1.50$ (Crucial base expectations; must build).
*   `One-Dimensional`: $\beta = 1.25$ (Linear value creator).
*   `Attractive`: $\beta = 1.10$ (High delighter potential).
*   `Indifferent`: $\beta = 0.25$ (Waste of engineering effort).
*   `Reverse`: $\beta = -1.00$ (Causes active user frustration; reject).

```
                      [Ingest RICE & Kano Attributes]
                                     │
                         [Compute Base RICE Score]
                                     │
                        [Apply Kano Multiplier Beta]
                                     │
                          [Generate Sorted APS List]
```

### 2.3 Priority Thresholds
*   **Build Now ($\text{APS} \ge 1500$)**: Immediate deployment in the current sprint.
*   **Schedule Next ($500 \le \text{APS} < 1500$)**: Schedule for the subsequent release phase.
*   **Defer ($100 \le \text{APS} < 500$)**: Keep in product backlog; monitor variables.
*   **Drop ($\text{APS} < 100$ or $\beta < 0$)**: Archival of requirement.

---

## 3. Reusable Checklist & Exit Criteria
*   [ ] Confirmed Effort estimation is backed by standard agile sizing.
*   [ ] Checked that Reach figures are derived from database analytics.
*   [ ] Verified Kano survey mappings are configured for the target ICP segment.
*   *Exit Criteria*: Prioritized feature list sorted by APS score generated and stored.
