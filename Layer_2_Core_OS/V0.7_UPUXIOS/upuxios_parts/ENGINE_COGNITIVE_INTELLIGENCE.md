# Engine: Cognitive Intelligence

## 1. Context & Strategy

### 1.1 Purpose
The Cognitive Intelligence Engine audits interface designs and screens to detect cognitive overload. By quantifying layout complexity, choice density, and visual noise, the engine provides objective feedback to design teams to optimize screen ergonomics prior to frontend code selection.

### 1.2 Philosophy
Human attention is the ultimate bottleneck. Interfaces must adapt to human working memory limits ($7 \pm 2$ chunks) and decision speeds, never the other way around. If a layout exceeds the cognitive thresholds, it represents a usability risk and must be simplified.

---

## 2. Ingest Parameters & Taxonomy

### 2.1 Inputs & Outputs
*   **Inputs**:
    *   `N_elements`: Total count of visual nodes (text lines, inputs, icons, controls) visible in the viewport.
    *   `N_decisions`: Total number of distinct click/touch target endpoints.
    *   `N_colors`: Count of distinct semantic colors visible simultaneously.
    *   `Friction_Factor`: Modifier score ($0.0 - 2.0$) based on visual proximity errors, font hierarchy issues, or missing labels.
*   **Outputs**:
    *   `Cognitive Load Score (CLS)`: Float value ($0.0 - 10.0$).
    *   `Audit Classification`: `Optimal`, `Moderate`, or `Overloaded`.

### 2.2 Calculations Pipeline
The engine runs the following logic:

$$\text{CLS} = (N_{\text{elements}} \times 0.15) + (N_{\text{decisions}} \times 0.40) + (N_{\text{colors}} \times 0.30) + \text{Friction\_Factor}$$

```
                           [Ingest Screen Model]
                                     │
                       [Evaluate Complexity Metrics]
                                     │
                     [Calculate Cognitive Load Score]
                                     │
                         [Apply Gateway Threshold]
                         /                       \
        (CLS <= 6.0)   /                           \ (CLS > 6.0)
                     ▼                               ▼
             [Gate: APPROVED]                [Gate: REJECTED]
```

### 2.3 Threshold Levels
*   **Optimal ($\text{CLS} \le 3.0$)**: High clarity, minimal effort. Target for transaction pages.
*   **Moderate ($3.0 < \text{CLS} \le 6.0$)**: Acceptable for complex data environments like dashboards.
*   **Overloaded ($\text{CLS} > 6.0$)**: Interactive elements and visual styles are too dense. Blocked from production release.

---

## 3. Reusable Checklist & Exit Criteria
*   [ ] Checked that `N_decisions` is calculated at the viewport level.
*   [ ] Audited visual layout to ensure `Friction_Factor` evaluates spacing and alignment errors.
*   [ ] Verified contrast ratio of elements before computing final scores.
*   *Exit Criteria*: A signed Cognitive Load Audit report with a CLS $\le 6.0$ is registered in the release dossier.
