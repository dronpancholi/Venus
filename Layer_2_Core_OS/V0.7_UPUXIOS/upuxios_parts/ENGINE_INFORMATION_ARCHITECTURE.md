# Engine: Information Architecture

## 1. Context & Strategy

### 1.1 Purpose
The Information Architecture Engine evaluates the depth, navigability, and taxonomic efficiency of application menu systems and resource metadata. It quantifies navigation paths and processes tree testing datasets to guarantee that users locate target data without getting lost in deep menus.

### 1.2 Philosophy
Keep structure flat. Every layer of menu hierarchy represents a cognitive fork where users can choose the wrong path. We optimize for flat structures supported by robust search taxonomy and filtering sidebars.

---

## 2. Ingest Parameters & Taxonomy

### 2.1 Inputs & Outputs
*   **Inputs**:
    *   `D_array`: Array containing the navigation depth levels ($1, 2, 3, \dots$) for all terminal resources.
    *   `N_direct_finds`: Number of users who navigate straight to the target in a tree test without backtracking.
    *   `N_indirect_finds`: Number of users who locate the target but backtracked at least once.
    *   `N_total_runs`: Total number of user tests executed.
*   **Outputs**:
    *   `Navigation Depth Score (NDS)`: Float score.
    *   `Findability Index (FI)`: Float value ($0.0 - 1.0$).
    *   `IA Status`: `Pass` or `Fail`.

### 2.2 Calculations Pipeline

#### Navigation Depth Score
The engine calculates the average depth across all resource endpoints:

$$\text{NDS} = \frac{\sum_{i=1}^{n} D_i}{n}$$

Where $D_i$ is the depth level of endpoint $i$, and $n$ is the total number of resource endpoints.

#### Findability Index
The engine evaluates navigation success:

$$\text{FI} = \frac{\text{N\_direct\_finds} + (0.5 \times \text{N\_indirect\_finds})}{\text{N\_total\_runs}}$$

```
                        [Ingest IA Tree & Testing Logs]
                                      │
                         [Calculate NDS & FI Metrics]
                                      │
                        {Verify Architectural Limits}
                         /                         \
         (NDS <= 3.0 & /                             \ (Violations)
           FI >= 0.85) ▼                               ▼
                    [Pass]                           [Fail]
```

### 2.3 Threshold Rules
*   **Pass**: $\text{NDS} \le 3.0$ and $\text{FI} \ge 0.85$. The taxonomy is highly intuitive and maintains flat hierarchy constraints.
*   **Fail**: $\text{NDS} > 3.0$ or $\text{FI} < 0.85$. The structure is too deep or confusing; navigation must be refactored before release.

---

## 3. Reusable Checklist & Exit Criteria
*   [ ] Checked that no menu branch exceeds a nesting depth of $3$ levels.
*   [ ] Verified that search query suggestions display within the $150\text{ms}$ latency budget.
*   [ ] Checked that all resource metadata tags conform to the `Namespace:Type:Owner` structure.
*   *Exit Criteria*: Information Architecture audit report registered with a Pass status.
