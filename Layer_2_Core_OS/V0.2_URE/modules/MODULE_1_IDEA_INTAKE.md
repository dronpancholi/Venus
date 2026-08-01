# Module 1 — Idea Intake Engine

## 1. Context & Strategy

### 1.1 Purpose
The Idea Intake Engine acts as the entry point for all concepts, feature requests, startup ideas, customer complaints, and strategic visions. It standardizes unstructured inputs, preventing raw, unvetted ideas from directly influencing architecture or development cycles.

### 1.2 Philosophy
Every idea is a hypothesis, not a mandate. An idea should be treated with skepticism until it is classified, measured for uncertainty, and scored for initial feasibility. 

---

## 2. Ingestion & Classification Parameters

### 2.1 The Classification Dimensions
When an idea is submitted, the engine classifies it across eight axes:
1.  **Domain**: [e.g., Vertical SaaS, Infrastructure, Distributed Systems, ML Pipeline]
2.  **Industry**: [e.g., AdTech, Healthcare, FinTech, Developer Tools]
3.  **Primary Stakeholder Group**: [e.g., System Admins, Marketing Agencies, Financial Officers]
4.  **Uncertainty Level**: [Low (1) to High (5)]
5.  **Novelty Level**: [Commodity (1) to High Moat (5)]
6.  **Complexity**: [Low (1) to High (5)]
7.  **Business Impact**: [Minor (1) to Strategic Shift (5)]
8.  **Technical Impact**: [Trivial (1) to Core Engine Change (5)]

### 2.2 The Ingestion Flow
```
[Unstructured Input] ──► [Extraction Matrix] ──► [8-Dimensional Classification] ──► [Confidence Score Calculation]
                                                                                               │
                                                                                               ▼
                                                                                   [Intake Record Created]
```

---

## 3. Inputs & Outputs

### 3.1 Inputs
*   Unstructured text input (one-line idea, customer support ticket, slack copy, or strategic pitch).
*   Target geography or regional scope.

### 3.2 Outputs
*   **Structured Ingestion Record**: Categorized metadata representation.
*   **Initial Confidence Score (ICS)**: A mathematical index (0.0 to 1.0) indicating source reliability and validation depth.

---

## 4. Operational Algorithm & Scoring

### 4.1 Initial Confidence Score (ICS) Calculation
The ICS is calculated by scoring the source input quality:

\[ICS = \frac{(Source\_Credibility \times 0.4) + (Evidence\_Level \times 0.4) + (Clarity\_Index \times 0.2)}{5.0}\]

Where:
*   **Source Credibility (1-5)**: 1: Anonymous forum post. 3: Support ticket from customer. 5: Proven transactional failure log.
*   **Evidence Level (1-5)**: 1: Personal opinion. 3: Mapped workflow spreadsheet. 5: Validated API logs and video recordings of user failure.
*   **Clarity Index (1-5)**: 1: Vague concept ("Make it faster"). 5: Concrete defect trace.

---

## 5. Reusable Templates & Checklists

### 5.1 Idea Intake Checklist
*   [ ] Captured unstructured raw input text.
*   [ ] Extracted domain and target industry.
*   [ ] Assigned scores for complexity, novelty, and impacts.
*   [ ] Calculated the Initial Confidence Score (ICS).
*   [ ] Created the permanent intake ID in the database.

### 5.2 Template: Structured Intake Record
```markdown
### 1. Raw Input Context
*   **Intake ID**: INT-[UUID]
*   **Source**: [e.g., Executive Vision / Client Ticket #2910]
*   **Raw Input**: "[Paste raw text here]"

### 2. Auto-Classification Metadata
*   **Domain**: [Domain name] | **Industry**: [Industry name]
*   **Complexity**: [1-5] | **Novelty**: [1-5]
*   **Business Impact**: [1-5] | **Technical Impact**: [1-5]

### 3. Confidence Metrics
*   *Source Credibility*: [1-5]
*   *Evidence Level*: [1-5]
*   *Clarity Index*: [1-5]
*   **Calculated ICS**: [0.0 - 1.0]
```

---

## 6. SRE, AI-Agent, & Safety Parameters

### 6.1 AI-Agent Execution Instructions
1.  **Extract**: Read raw input and extract entities using json schema tags.
2.  **Verify**: Perform vector search against existing intake logs to detect duplicate ideas.
3.  **Classify**: Score complexity and impact matrices. If ICS < 0.4, flag for immediate human review.

### 6.2 Common Anti-patterns
*   **The "HiPPO" Trap**: Scoring executive vision ideas with high confidence (ICS = 1.0) without requiring underlying evidence. *Mitigation*: Enforce objective evidence score weights regardless of submitter role.
*   **Premature Solution Injection**: Ingesting feature requests that specify code stacks (e.g. "We need a DynamoDB table for outreach data") instead of isolating the underlying data problem.

### 6.3 Exit Criteria
*   Structured Intake Record successfully populated with **ICS calculated** and registered in database.
*   Proceed to **Module 2: Problem Classification Engine**.
