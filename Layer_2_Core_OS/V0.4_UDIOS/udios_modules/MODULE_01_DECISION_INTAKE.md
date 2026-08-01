# Module 01 — Decision Intake Engine

## 1. Context & Strategy

### 1.1 Purpose
The Decision Intake Engine standardizes and normalizes every proposed engineering, architectural, product, security, and financial decision. It acts as the intake gate, translating raw concepts into structured Decision Intake Records (DIR).

### 1.2 Philosophy
A decision cannot be made until it is defined. Intake must isolate the proposed action from the problem statement, enforcing clear boundary conditions before evaluating solutions.

---

## 2. Ingest Parameters & Taxonomy

### 2.1 Inputs & Outputs
*   **Inputs**: Unstructured text proposals, PR summaries, technical briefs, email/Slack requests.
*   **Outputs**: Normalized Decision Intake Record (DIR) with assigned Decision UUID.

### 2.2 Taxonomy Schema
Every DIR must identify:
*   **Proposer**: Role/Team.
*   **Proposed Change**: Clear declaration of action.
*   **Target Scope**: Impacted sub-systems.
*   **Time Horizon**: Urgency status.

---

## 3. Operational Algorithm & Decision Tree

### 3.1 The Intake Decision Tree
```
                     [Raw Proposal Received]
                                │
                                ▼
                   [Contains Actionable Change?]
                     ├── NO  ──► [Reject Intake: Insufficient Data]
                     └── YES ──► [Expose Boundary Conditions]
                                        │
                                        ▼
                           [Define Target Subsystems]
                                        │
                                        ▼
                           [Assign Unique Decision ID]
```

### 3.2 Confidence & Scoring System
Intake assigns a **Metadata Completeness Index (MCI)**:

\[MCI = \frac{Actionable\_Fields\_Populated}{Total\_Required\_Fields}\]

If MCI < 0.8, the intake record is flagged as **BLOCKED** and returned to the proposer.

---

## 4. Reusable Templates & Checklists

### 4.1 Template: Decision Intake Record (DIR)
```markdown
### 1. Intake Identification
*   **Decision ID**: DEC-[UUID]
*   **Proposer**: [Name / Title]
*   **Timestamp**: YYYY-MM-DD HH:MM:SS UTC

### 2. Proposed Action
*   *Action*: [e.g., Migrate key-value cache from memory to Redis cluster]
*   *Justification*: [e.g., Reduce memory load on application workers]

### 3. Target Scope
*   *Impacted Services*: [e.g., worker-api, worker-crawler]
*   *Database Affected*: [e.g., redis-cache-01]
```

### 4.2 Intake Checklist
*   [ ] Captured raw proposal string.
*   [ ] Populated proposed change vector.
*   [ ] Defined target scope.
*   [ ] Calculated MCI score (MCI >= 0.8).
*   [ ] Generated Decision ID DEC-[UUID].

---

## 5. SRE, AI-Agent, & Safety Parameters

### 5.1 AI-Agent Execution Instructions
1.  **Extract**: Identify entities in unstructured proposal using json parser.
2.  **Verify**: Ensure MCI meets 0.8 threshold.
3.  **Route**: Generate DEC-[UUID] and trigger **Module 02: Decision Classification**.

### 5.2 Anti-patterns & Common Mistakes
*   *The "Do It Now" Trap*: Ingesting a decision without defining target sub-systems.
*   *Premature Coding*: Allocating developers to start branch commits before DIR approval.

### 5.3 Exit Criteria
*   DIR successfully populated and registered.
*   Proceed to **Module 02: Decision Classification**.
