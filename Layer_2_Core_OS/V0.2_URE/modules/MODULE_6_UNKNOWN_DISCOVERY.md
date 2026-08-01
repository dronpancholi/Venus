# Module 6 — Unknown Discovery Engine

## 1. Context & Strategy

### 1.1 Purpose
The Unknown Discovery Engine maps the boundary of the organization's knowledge. By classifying information into structured quadrants of certainty and identifying hidden "Unknown Unknowns" (systemic blindsides), it defines the research priorities required to secure the engineering baseline.

### 1.2 Philosophy
Risk resides in what we don't know, but catastrophe resides in what we don't know we don't know. The objective of Module 6 is to systematically convert Unknown Unknowns into Known Unknowns, and then resolve them.

---

## 2. Uncertainty Mapping Framework

We classify information across the Johari-style Knowledge Matrix:

```
                      KNOWN TO US            UNKNOWN TO US
                 ┌──────────────────────┬──────────────────────┐
    KNOWN IN     │     Known Knowns     │    Known Unknowns    │
  REALITY/MARKET │ (Facts & Benchmarks) │  (Defined Queries)   │
                 ├──────────────────────┼──────────────────────┤
   UNKNOWN IN    │   Unknown Knowns     │   Unknown Unknowns   │
  REALITY/MARKET │  (Tribal Knowledge)  │ (Blind Spots / Risk) │
                 └──────────────────────┴──────────────────────┘
```

*   **Known Knowns**: Verified facts, benchmarked latencies, and documented legal requirements.
*   **Known Unknowns**: Explicit questions we know we must answer (e.g. "What is the cost of NIM token calls under concurrency?").
*   **Unknown Unknowns**: Hidden assumptions or market conditions we have not yet considered (e.g., a competitor filing a patent covering our exact workflow pattern).
*   **Critical Unknowns**: High-impact queries that directly block architecture decisions.

---

## 3. Inputs & Outputs

### 3.1 Inputs
*   Assumption Register (from Module 5).
*   Technology Evaluation Matrix (from Stage 5).
*   Regulatory Compliance Registry (from Stage 8).

### 3.2 Outputs
*   **Uncertainty Map**: Matrix of categorized knowledge domains.
*   **Critical Unknowns Register**: Ranked list of high-priority research queries.

---

## 4. Operational Methodology & Prioritization

### 4.1 Prioritization Algorithm for Unknowns
Known Unknowns are ranked for research priority using a **Priority Value (PV)**:

\[PV = Impact\_Scope \times Severity \times Cost\_to\_Uncover\]

Where:
*   *Impact Scope (1-5)*: 1: Impacts one feature. 5: Impacts entire database schema and deployment host.
*   *Severity (1-5)*: 1: Trivial. 5: Complete project termination risk.
*   *Cost to Uncover (1-5)*: 1: High cost (requires full prototype). 5: Low cost (requires reading a doc).

*Note*: Higher PV indicates queries that must be resolved immediately due to high impact and low verification cost.

---

## 5. Reusable Checklists & Templates

### 5.1 Unknown Discovery Checklist
*   [ ] Categorized all logged assumptions into the Knowledge Matrix.
*   [ ] Surveyed engineers for hidden technical uncertainties.
*   [ ] Checked compliance docs for unmapped regulatory boundaries.
*   [ ] Calculated the Priority Value (PV) for all Known Unknowns.
*   [ ] Created research briefs for all Critical Unknowns.

### 5.2 Template: Unknown Register Entry
```markdown
### 1. Unknown Profile: UNK-[UUID]
*   **The Query**: "[e.g., Will the local Llama-3 model maintain structured JSON formatting under 100 concurrent requests?]"
*   **Classification**: Known Unknown / Critical Unknown
*   *Impact Scope*: 5 | *Severity*: 5 | *Verification Cost*: 2 (Requires local python benchmark script)
*   **Calculated PV**: 50 (High Priority)

### 2. Resolution Action
*   **Assigned Task**: [e.g., Create local Llama-3 docker instance and execute concurrency test script]
*   **Verification Target**: [Date] | **Status**: *Active*
```

---

## 6. SRE, AI-Agent, & Safety Parameters

### 6.1 AI-Agent Execution Instructions
1.  **Analyze**: Review the project configuration files, DB connection pool setups, and RLS configurations.
2.  **Compare**: Scan external CVE security registries, patent databases, and packages registries.
3.  **Identify**: Highlight any missing dependencies or unverified versions, entering them as Known Unknowns in the register.

### 6.2 Common Anti-patterns
*   **The Ignorance Bias**: Pretending that unproven assumptions are verified facts to accelerate development.
*   **Research Paralysis**: Spending months trying to resolve low-impact Unknown Unknowns instead of building a minimal test code loop.

### 6.3 Exit Criteria
*   Uncertainty Map compiled with **all Critical Unknowns assigned to active research tasks**.
*   Proceed to **Module 7: Constraint Discovery**.
