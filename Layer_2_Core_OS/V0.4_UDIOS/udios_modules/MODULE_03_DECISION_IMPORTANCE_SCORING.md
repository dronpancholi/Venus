# Module 03 — Decision Importance Scoring

## 1. Context & Strategy

### 1.1 Purpose
Decision Importance Scoring calculates the systemic blast radius, reversibility, and financial priority of a proposal. This score determines the validation depth and approval routing required for the decision.

### 1.2 Philosophy
Decisions are asymmetric. Some are low cost and easily reversible (Type II), while others are high cost and irreversible (Type I). The system must scale its review overhead to match the decision importance.

---

## 2. Ingest Parameters & Taxonomy

### 2.1 Inputs & Outputs
*   **Inputs**: Classified Decision Intake Record (DIR).
*   **Outputs**: Importance Scorecard, Reversibility Classification (Type I / Type II), and required approval routing pathway.

### 2.2 Reversibility Taxonomy
*   **Type I (Irreversible)**: High exit cost, structural lock-in (e.g., migrating core cloud provider, proprietary DB engine migration).
*   **Type II (Reversible)**: Low exit cost, modular (e.g., swapping front-end packages, changing CDN cache rules).

---

## 3. Operational Algorithm & Decision Tree

### 3.1 Importance Score (IS) Calculation
The importance score is calculated by scoring the impact across five dimensions:

\[IS = \frac{(Blast\_Radius \times 0.3) + (Exit\_Cost \times 0.3) + (Financial\_Cost \times 0.2) + (Time\_Urgency \times 0.2)}{5.0}\]

Where:
*   **Blast Radius (1-5)**: 1: Single dev sandbox. 3: Tenant dashboard. 5: Core database / auth service.
*   **Exit Cost (1-5)**: 1: Swapped in minutes. 3: Swapped in weeks. 5: Complete structural rebuild (>3 months).
*   **Financial Cost (1-5)**: 1: <$100/mo. 3: <$5K/mo. 5: >$20K/mo.
*   **Time Urgency (1-5)**: 1: Backlog feature. 3: Standard roadmap milestone. 5: Active production outage / security vulnerability.

### 3.2 Decision Routing Tree
```
                         [Calculate IS Score]
                                  │
                  ┌───────────────┴───────────────┐
              IS >= 0.7                       IS < 0.7
                  │                               │
                  ▼                               ▼
       [Classify: Type I]              [Classify: Type II]
   *Requires full debate (M13)     *Requires simple peer validation*
     and Executive Approval*
```

---

## 4. Reusable Templates & Checklists

### 4.1 Template: Importance Scorecard
```markdown
### 1. Scoring Summary
*   **Decision ID**: DEC-[UUID]
*   **Blast Radius Score**: [1-5]
*   **Exit Cost Score**: [1-5]
*   **Financial Cost Score**: [1-5]
*   **Time Urgency Score**: [1-5]
*   **Calculated IS Index**: [0.0 - 1.0]

### 2. Validation Pathway
*   *Reversibility*: Type I (Irreversible) / Type II (Reversible)
*   *Required Approvers*: [Role Names]
```

### 4.2 Checklist
*   [ ] Checked blast radius dependencies.
*   [ ] Checked developer hours and cash spend estimates.
*   [ ] Assigned correct Reversibility Class.
*   [ ] Populated Importance Scorecard.

---

## 5. SRE, AI-Agent, & Safety Parameters

### 5.1 AI-Agent Execution Instructions
1.  **Calculate**: Parse budget estimates and directory scopes, then execute the IS algorithm.
2.  **Verify**: If a proposal changes an auth file or base database configuration, automatically override Blast Radius to 5.

### 5.2 Common Anti-patterns
*   *The "Quick Script" Bypass*: Labeling a DB migration script as Type II to bypass review, resulting in data loss.

### 5.3 Exit Criteria
*   Importance Scorecard calculated and **Reversibility Class assigned**.
*   Proceed to **Module 04: Evidence Collection**.
