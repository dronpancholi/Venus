# Engine: Interaction Design

## 1. Context & Strategy

### 1.1 Purpose
The Interaction Design Engine validates widget physical layouts, keyboard accessibility paths, and state completeness against ergonomic laws (Fitts' Law, Hick's Law). It ensures that all GUI controls remain easy to target, rapid to evaluate, and highly responsive.

### 1.2 Philosophy
Interactions must be predictable and responsive. Every button, input field, and menu item must communicate its state immediately, provide keyboard accessibility, and minimize target search times.

---

## 2. Ingest Parameters & Taxonomy

### 2.1 Inputs & Outputs
*   **Inputs**:
    *   `D_distance`: Pixels from the cursor starting point to the target center.
    *   `W_width`: Target dimension (pixels) along the axis of motion.
    *   `Choice_Count (n)`: Number of choices presented at a decision junction.
    *   `States_Defined`: Array of state strings defined for the widget (`Default`, `Hover`, `Active`, `Focus`, `Disabled`, `Loading`, `Selected`).
*   **Outputs**:
    *   `Fitts_Target_Score (FTS)`: Float value.
    *   `Hick_Decision_Time (T_Hick)`: Seconds estimate.
    *   `State_Completeness (ISC)`: Float ($0.0 - 1.0$).
    *   `Interaction Status`: `Approved` or `Rejected`.

### 2.2 Calculations Pipeline

#### Fitts' Law Target Score
The engine calculates the index of difficulty for target selection:

$$\text{FTS} = \log_2\left(\frac{2 \times \text{D\_distance}}{\text{W\_width}}\right)$$

#### Hick's Law Decision Time
The engine models user selection latency (assuming a baseline cognitive processing speed coefficient $b = 0.50$):

$$\text{T\_Hick} = 0.50 \times \log_2(n + 1)$$

#### State Completeness
The engine verifies that all $7$ operational widget states are explicitly styled:

$$\text{ISC} = \frac{\text{Count of styled states in States\_Defined}}{7}$$

```
                       [Ingest Widget Dimensions & n]
                                     │
                        [Calculate FTS, T_Hick, ISC]
                                     │
                        {Verify Ergonomic Limits}
                         /                      \
          (FTS <= 5.0 & /                        \ (Violations)
           T_Hick <= 1.5 &                       ▼
           ISC == 1.0)  ▼                    [Rejected]
                     [Approved]
```

### 2.3 Threshold Rules
*   **Approved**: $\text{FTS} \le 5.0$, $\text{T\_Hick} \le 1.5\text{s}$, and $\text{ISC} = 1.00$. Interactive targets are highly accessible.
*   **Rejected**: $\text{FTS} > 5.0$ (target too small or distant), $\text{T\_Hick} > 1.5\text{s}$ (too many choices), or $\text{ISC} < 1.00$ (missing states).

---

## 3. Reusable Checklist & Exit Criteria
*   [ ] Checked that touch targets are $\ge 48\text{px} \times 48\text{px}$ on mobile responsive views.
*   [ ] Confirmed keyboard shortcuts are mapped to primary workspace actions.
*   [ ] Verified global command palette returns autocomplete results within $80\text{ms}$.
*   *Exit Criteria*: Interaction Design score sheet yields an Approved status.
