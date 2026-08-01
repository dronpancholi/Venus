# Module 8 — Opportunity Discovery

## 1. Context & Strategy

### 1.1 Purpose
Problem solving shouldn't be defensive. The Opportunity Discovery Engine systematically scans verified problems and constraints to identify hidden strategic leverage points (e.g. platform opportunities, workflow simplifications, automation routes, IP generation) that increase commercial value.

### 1.2 Philosophy
Inside every hard operational constraint lies a platform opportunity. Our objective is to design systems that turn compliance and technical complexity into high-margin competitive advantages.

---

## 2. Opportunity Ingestion Framework

We search for opportunities across six primary vectors:
1.  **Automation & AI**: Where can non-deterministic logic replace manual human data entry?
2.  **Cost Reduction**: Where can caching, data pruning, or query optimization lower infrastructure costs?
3.  **Workflow Simplification**: Can we eliminate steps from the operator journey?
4.  **Platformization**: Can we extract a reusable backend module (e.g., our Temporal campaign saga queue) to serve other product domains?
5.  **IP Creation**: Can we write a proprietary scoring model or data compression format?
6.  **Strategic Advantage**: How does our technical superiority directly enable commercial sales?

---

## 3. Inputs & Outputs

### 3.1 Inputs
*   User Journey Map and High-Friction Steps (from Stage 3).
*   Constraint Dependency Graph (from Module 7).
*   Raw compute logs (from Stage 7).

### 3.2 Outputs
*   **Opportunity Matrix**: Plotted grid tracking potential improvements.
*   **IP Capture Document**: Outlined proprietary algorithms for patent filing.

---

## 4. Operational Methodology & Prioritization

### 4.1 Opportunity Prioritization Matrix
Opportunities are mapped on a 2x2 grid based on **Value Impact** vs. **Engineering Effort**:

```
                  VALUE IMPACT
                1: Low  ...  5: High
             ┌─────────────────────────────────┐
           1 │ Tier 3 (Quick Win) ...  Tier 1   │
           │                                   │
  EFFORT     │                                   │
           5 │ Tier 4 (Decline)   ...  Tier 2   │
             └─────────────────────────────────┘
```

| Tier | Priority | Engineering Mandate |
|---|---|---|
| **Tier 1** (High Value, Low Effort) | **Immediate** | Build into the core product specification. |
| **Tier 2** (High Value, High Effort) | **Strategic Plan** | Schedule for phase 2 release. |
| **Tier 3** (Low Value, Low Effort) | **Backlog** | Optional; implement to improve usability. |
| **Tier 4** (Low Value, High Effort) | **Reject** | Do not build. |

---

## 5. Reusable Checklists & Templates

### 5.1 Opportunity Discovery Checklist
*   [ ] Checked the User Journey for steps with high cognitive load.
*   [ ] Analyzed database queries for caching opportunities.
*   [ ] Evaluated whether any backend service can be modularized as a standalone platform.
*   [ ] Plotted all candidates in the 2x2 Opportunity Matrix.
*   [ ] Drafted IP outlines for proprietary scoring models.

### 5.2 Template: Opportunity Matrix Entry
```markdown
### 1. Opportunity Profile: OPP-[UUID]
*   **Description**: [e.g., Generalize the Temporal campaign saga queue to cover PR and Content scheduling]
*   **Category**: Platformization / Market Expansion
*   *Expected Value*: 5 | *Engineering Effort*: 3
*   **Target Tier**: Tier 1 (Highly Strategic)

### 2. Implementation Outline
*   *Concept*: Modularize `backlink_campaign.py` into a core `orchestration_saga` service that accepts generic activity registries.
*   *Strategic Leverage*: Increases our addressable TAM from $30M (SEO agencies) to $300M (Marketing/PR platforms).
```

---

## 6. SRE, AI-Agent, & Safety Parameters

### 6.1 AI-Agent Execution Instructions
1.  **Scan**: Review all database schemas, API interfaces, and user workflows.
2.  **Compare**: Look for repeated code patterns or data structures that can be simplified.
3.  **Propose**: Generate modularization strategies for repeated code segments.

### 6.2 Common Anti-patterns
*   **The Feature Chase**: Building Tier 3/4 opportunities simply because they are technically interesting, distracting from Tier 1 core work.
*   **Premature Platformization**: Attempting to extract APIs and libraries before the underlying system has been validated by real pilot users.

### 6.3 Exit Criteria
*   Opportunity Matrix compiled and **Tier 1 improvements integrated into the product spec**.
*   Proceed to **Module 9: Failure Prediction**.
