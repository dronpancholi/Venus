# Module 5 — Assumption Discovery

## 1. Context & Strategy

### 1.1 Purpose
Unproven assumptions are the primary drivers of technical debt and product failure. The Assumption Discovery Engine extracts, classifies, and scores every unverified assertion in the project scope, preventing the organization from coding until critical assumptions have been verified with evidence.

### 1.2 Philosophy
Every unverified statement is a liability. We catalog, score, and track assumptions as living debts that must be paid down via active research or benchmarking.

---

## 2. Assumption Taxonomy & Scoring

### 2.1 Taxonomy
We classify assumptions across ten categories:
*   **Explicit**: Clearly stated assumptions (e.g. "We assume Ahrefs API is active").
*   **Implicit**: Unstated but required constraints (e.g. "The database has <50ms read latency").
*   **Hidden**: Underlying dependencies that are taken for granted.
*   **Dangerous**: Assumptions which, if wrong, invalidate the entire system design.
*   **Market**: Assumptions about customer demand, willingness-to-pay, and scale.
*   **Engineering**: Assumptions about language performance, library stability, or server capacity.
*   **AI**: Assumptions about LLM capabilities, accuracy, token bounds, and drift.
*   **Security**: Assumptions about user privileges, firewall configurations, and isolation rules.
*   **Financial**: Assumptions about compute costs, API fees, and operating margins.
*   **Organizational**: Assumptions about development timelines and engineer availability.

### 2.2 Assumption Scoring Model
Each entry in the register is evaluated on a 1-5 scale across three vectors to calculate an **Assumption Risk Score (ARS)**:

\[ARS = Probability\_of\_Failure \times Impact \times Validation\_Cost\]

Where:
*   *Probability of Failure (1-5)*: 1: Highly likely to be correct. 5: Speculative / unproven.
*   *Impact (1-5)*: 1: Trivial. 5: If incorrect, requires a complete system re-architecture or business model pivot.
*   *Validation Cost (1-5)*: 1: Trivial (minutes of code test). 5: Requires months of customer discovery or high-cost prototyping.

---

## 3. Inputs & Outputs

### 3.1 Inputs
*   Initial Intake Record (from Module 1).
*   System Map (from Stage 3).
*   Engineering and product strategy documents.

### 3.2 Outputs
*   **Assumption Register**: Comprehensive table tracking all unproven core assertions.
*   **Validation Plan**: Concrete engineering tasks designed to verify high-risk assumptions.

---

## 4. Reusable Checklists & Templates

### 4.1 Assumption Discovery Checklist
*   [ ] Extracted all explicit assumptions from the project brief.
*   [ ] Checked backend schemas for implicit scaling assumptions.
*   [ ] Vetted AI dependencies for accuracy and latency assumptions.
*   [ ] Calculated the ARS for every entry.
*   [ ] Assigned validation tasks to engineers.

### 4.2 Template: Assumption Register Entry
```markdown
### 1. Assumption Profile: ASM-[UUID]
*   **Assertion**: "[e.g., The Ahrefs API will return domain relevance metrics in under 500ms]"
*   **Classification**: Explicit / Engineering / Dangerous
*   *Probability of Failure*: 3 | *Impact*: 5 | *Validation Cost*: 1
*   **Calculated ARS**: 15 (High Risk - Validate immediately)

### 2. Validation Plan
*   **Methodology**: Run a local curl script querying the Ahrefs sandbox API 100 times under concurrent load, logging latency.
*   **Target Date**: [Date] | **Status**: *Pending*
```

---

## 5. SRE, AI-Agent, & Safety Parameters

### 5.1 AI-Agent Execution Instructions
1.  **Read**: Review all project scopes, database schemas, and prompt designs.
2.  **Extract**: Identify statements containing words like "should", "will", "expects", or "assumes".
3.  **Evaluate**: Run the ARS calculation. Flag any item with an ARS > 12 for immediate prototyping.

### 5.2 Common Anti-patterns
*   **The Implicit Leak**: Writing code based on unstated assumptions (e.g. assuming the cloud environment has constant internet connectivity, failing to handle offline states).
*   **Delayed Validation**: Postponing the testing of dangerous assumptions until the end of the development cycle.

### 5.3 Exit Criteria
*   Assumption Register generated with **all high-risk assumptions (ARS > 12) assigned to validation tasks**.
*   Proceed to **Module 6: Unknown Discovery Engine**.
