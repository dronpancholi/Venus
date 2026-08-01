# Engine: Dashboard Intelligence

## 1. Context & Strategy

### 1.1 Purpose
The Dashboard Intelligence Engine audits the structure of data dashboards, ensuring widget configurations adhere to the 12-column layout grid and satisfy performance budgets (LCP, CLS, FID). It guarantees high responsiveness and cognitive clarity for enterprise metrics screens.

### 1.2 Philosophy
Data must inform, not confuse. Dashboards must load rapidly, prevent layout shifts during visual rendering, and keep widget configurations aligned to the user's operational needs.

---

## 2. Ingest Parameters & Taxonomy

### 2.1 Inputs & Outputs
*   **Inputs**:
    *   `Grid_Widths`: Array of integers representing widget column spans (must sum to multiples of $12$).
    *   `LCP_sec`: Largest Contentful Paint value in seconds.
    *   `CLS_val`: Cumulative Layout Shift float value.
    *   `FID_ms`: First Input Delay value in milliseconds.
*   **Outputs**:
    *   `Layout Grid Compliance (LGC)`: Float ($0.0 - 1.0$).
    *   `Visual Performance Score (VPS)`: Float ($0.0 - 1.0$).
    *   `Compliance Status`: `Certify` or `Hold`.

### 2.2 Calculations Pipeline

#### Layout Grid Compliance
The engine verifies that all widgets span valid column sizes ($3, 4, 6, 8, \text{ or } 12$ columns) and fit the grid structure:

$$\text{LGC} = \frac{\text{Count of widgets satisfying width rules}}{\text{Total count of widgets}}$$

#### Visual Performance Score
The engine normalizes and scores performance metrics against targets ($LCP \le 1.5\text{s}$, $CLS \le 0.05$, $FID \le 100\text{ms}$):

$$\text{VPS} = (0.40 \times \text{LCP\_score}) + (0.40 \times \text{CLS\_score}) + (0.20 \times \text{FID\_score})$$

Where:
*   $\text{LCP\_score} = \max\left(0, 1 - \frac{\text{LCP\_sec}}{3.0}\right)$
*   $\text{CLS\_score} = \max\left(0, 1 - \frac{\text{CLS\_val}}{0.25}\right)$
*   $\text{FID\_score} = \max\left(0, 1 - \frac{\text{FID\_ms}}{300}\right)$

```
                     [Ingest Layout Grid & Performance Telemetry]
                                         │
                             [Calculate LGC & VPS Scores]
                                         │
                          {Evaluate Performance Gate}
                           /                        \
           (LGC == 1.0 &  /                          \ (Violations)
            VPS >= 0.80) ▼                            ▼
                      [Certify]                     [Hold]
```

### 2.3 Threshold Rules
*   **Certify**: $\text{LGC} = 1.00$ and $\text{VPS} \ge 0.80$. The dashboard complies with layout guidelines and runs efficiently.
*   **Hold**: $\text{LGC} < 1.00$ or $\text{VPS} < 0.80$. The dashboard layout is broken or loads too slowly; release is blocked.

---

## 3. Reusable Checklist & Exit Criteria
*   [ ] Checked that no visual widget is a pie chart.
*   [ ] Confirmed all chart components use fixed aspect-ratio containers.
*   [ ] Verified data table templates support direct CSV/JSON export actions.
*   *Exit Criteria*: Dashboard compliance audit report registered with a status of Certify.
