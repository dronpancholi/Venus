# Module 18 — Complexity Budget

## 1. Context & Strategy

### 1.1 Purpose
The Complexity Budget module enforces simplicity in system design. It assigns a numerical complexity index to proposed architectures, blocking solutions that introduce unnecessary layers or technology choices.

### 1.2 Philosophy
Complexity is a debt that incurs interest every day in the form of slower developer velocity, harder debugging, and higher infrastructure bills. We design for simplicity first, adding complex layers only when scale (Module 16) mandates it.

---

## 2. Ingest Parameters & Scoring Taxonomy

### 2.1 Inputs & Outputs
*   **Inputs**: DIR and target architecture diagram/description.
*   **Outputs**: Complexity scorecard and budget validation status.

### 2.2 Complexity Metrics
We calculate complexity across four axes:
*   **Number of distinct tools (x0.3)**: Database types, cache layers, external services.
*   **Dependency depth (x0.3)**: Number of package requirements, API connections.
*   **Logical layers (x0.2)**: Adapters, middlewares, wrapper microservices.
*   **Operational interfaces (x0.2)**: Distinct UI layouts, API endpoints.

---

## 3. Operational Algorithm & Scoring

### 3.1 Complexity Index (CI) Formula
\[CI = (Distinct\_Tools \times 1.5) + (Dependency\_Depth \times 1.0) + (Logical\_Layers \times 2.0)\]

### 3.2 Gate Thresholds
*   **CI <= 15.0**: Simple design. Approved.
*   **CI > 15.0**: Over-engineered design. Blocked. Requires consolidation of tools or removal of unnecessary adapter wrappers.

---

## 4. Reusable Templates & Checklists

### 4.1 Template: Complexity Scorecard
```markdown
### 1. Architecture Complexity Profile
*   **Decision ID**: DEC-[UUID]
*   **Distinct Tools**: [e.g., 3: Postgres, Redis, S3]
*   **Dependency Depth**: [e.g., 5 packages]
*   **Logical Layers**: [e.g., 2: API, Database Adapter]
*   **Calculated CI**: **13.5** (Approved)
```

### 4.2 Checklist
*   [ ] Checked dependency count in locks.
*   [ ] Checked database types.
*   [ ] Verified code line count estimations.
*   [ ] Audited system interfaces.

---

## 5. SRE, AI-Agent, & Safety Parameters

### 5.1 AI-Agent Execution Instructions
1.  **Parse**: Read import statements and package dependencies.
2.  **Verify**: Count database connections. If a single microservice requires 3 different database types (e.g. Postgres, Dynamo, and Elasticsearch) to run a single user flow, block PR.

### 5.2 Common Anti-patterns
*   *The Microservice Mania*: Splitting simple monolithic functions into 15 distinct containerized services, inflating local setup complexity.

### 5.3 Exit Criteria
*   Complexity Scorecard completed and **Complexity Index verified <= 15.0**.
*   Proceed to **Module 19: Opportunity Cost**.
