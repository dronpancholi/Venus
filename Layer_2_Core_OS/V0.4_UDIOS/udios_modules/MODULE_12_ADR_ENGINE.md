# Module 12 — ADR Engine

## 1. Context & Strategy

### 1.1 Purpose
The Architecture Decision Record (ADR) Engine automates the documentation of technical, operational, and database design choices. It links decisions directly to verification logs and active constraints.

### 1.2 Philosophy
If a decision is not documented, it did not happen. ADRs must capture the complete context, trade-offs, and rejected options to prevent team alignment failures and future code regression.

---

## 2. Ingest Parameters & Schema

### 2.1 Inputs & Outputs
*   **Inputs**: DIR, trade-off matrix, build vs. buy result, consensus verdict.
*   **Outputs**: Standardized `.md` ADR file registered in the repository's `docs/adr/` directory.

### 2.2 Standard ADR Schema
Every ADR must include:
*   **Status**: Proposed / Accepted / Deprecated.
*   **Context**: The underlying technical problem or constraint.
*   **Decision**: The selected action/technology.
*   **Consequences**: The downstream trade-offs (e.g. higher latency, database maintenance overhead).

---

## 3. Operational Algorithm & Decision Tree

### 3.1 The ADR Engine Pipeline
```
                    [Consensus Verdict Received]
                                 │
                     [Compile Decision Context]
                                 │
                     [Generate ADR Markdown File]
                                 │
                 [Register in Repository docs/adr/]
```

### 3.2 Verification Check
Every ADR is tagged with a unique hash mapping back to the inputs of **Module 05 (Evidence Quality)** and **Module 22 (Decision Confidence)**.

---

## 4. Reusable Templates & Checklists

### 4.1 Template: Architecture Decision Record (ADR)
```markdown
# ADR-001: Migrate Session Store to Redis

*   **Status**: Accepted
*   **Intake ID**: DEC-[UUID]
*   **Date**: YYYY-MM-DD

## 1. Context & Problem Statement
Our application workers are exceeding memory limits under high traffic because sessions are stored in memory.

## 2. Decision & Action
We will move session storage to a dedicated Redis cluster node.

## 3. Consequences & Trade-offs
*   *Positive*: Memory usage on app workers drops by ~40%.
*   *Negative*: Session fetch latency increases by ~2ms (network cost).
```

### 4.2 Checklist
*   [ ] Populated context statement.
*   [ ] Listed direct positive consequences.
*   [ ] Documented negative trade-offs.
*   [ ] Assigned correct status flag.

---

## 5. SRE, AI-Agent, & Safety Parameters

### 5.1 AI-Agent Execution Instructions
1.  **Format**: Generate standard markdown matching the ADR schema.
2.  **Verify**: Ensure no template placeholders are left in the output.

### 5.2 Common Anti-patterns
*   *The Retroactive ADR*: Writing an ADR months after the code has been written and deployed, turning documentation into post-hoc justification rather than design guidance.

### 5.3 Exit Criteria
*   ADR generated and saved in `docs/adr/` directory.
*   Proceed to **Module 13: Decision Debate**.
