# Module 19 — Opportunity Cost

## 1. Context & Strategy

### 1.1 Purpose
The Opportunity Cost module models the value, roadmap velocity, and revenue potential sacrificed by selecting a specific option and rejecting alternatives.

### 1.2 Philosophy
Selecting one path means rejecting all others. We must quantify what we are giving up (e.g. delaying a core feature release to build custom database sync adapters) to make informed architectural trade-offs.

---

## 2. Ingest Parameters & Taxonomy

### 2.1 Inputs & Outputs
*   **Inputs**: DIR, trade-off matrix, product roadmap milestones.
*   **Outputs**: Opportunity Cost Register Entry.

### 2.2 Audited Vectors
*   **Roadmap Delay**: Time added to other feature releases.
*   **Revenue Forgone**: Expected income lost due to delayed releases.
*   **Maintenance Overhead**: Future developer hours consumed by the decision that could have been spent building features.

---

## 3. Operational Algorithm & Scoring

### 3.1 Opportunity Cost Index (OCI) Formula
The OCI is calculated to compare the yield of selected vs. rejected paths:

\[OCI = \frac{Value_{Selected} - Value_{Rejected}}{Cost_{Selected}}\]

Where:
*   **Value (Selected/Rejected)**: Revenue / performance yield index.
*   **Cost**: Total financial and resource cost of the selected option.

---

## 4. Reusable Templates & Checklists

### 4.1 Template: Opportunity Cost Record
```markdown
### 1. Cost Profile
*   **Decision ID**: DEC-[UUID]
*   **Selected Option**: [Option Name]
*   **Primary Rejected Option**: [Option Name]
*   **Sacrificed Roadmap Milestone**: [e.g., Q3 Analytics API release delayed by 3 weeks]
*   **Calculated OCI**: [Score]
```

### 4.2 Checklist
*   [ ] Identified all active roadmap items.
*   [ ] Checked developer hours allocations.
*   [ ] Estimated future revenue impacts of delayed features.

---

## 5. SRE, AI-Agent, & Safety Parameters

### 5.1 AI-Agent Execution Instructions
1.  **Parse**: Read project Gantt chart or JIRA milestone backlogs.
2.  **Verify**: If a proposal requires more than 40% of the entire developer team's capacity for a non-core feature, flag for executive review.

### 5.2 Common Anti-patterns
*   *The Tunnel Vision*: Focusing on the technical perfection of a single component while ignoring the fact that the delay blocks the company's product launch.

### 5.3 Exit Criteria
*   Opportunity Cost Record generated and **OCI validated**.
*   Proceed to **Module 20: Future Evolution**.
