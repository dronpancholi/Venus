# Module 2 — Problem Classification Engine

## 1. Context & Strategy

### 1.1 Purpose
Problems are rarely single-dimensional. A technical bug often conceals a workflow constraint or compliance violation. The Problem Classification Engine analyzes the ingestion record, mapping it across multiple concurrent classification vectors to define what layers of the system must participate in resolution.

### 1.2 Philosophy
If you classify a multi-dimensional problem as a simple technical ticket, you will write code to patch a symptom that requires organizational or workflow restructuring. We classify problems across all operational dimensions simultaneously.

---

## 2. Multi-Vector Classification Schema

The engine evaluates and maps the incoming record across seventeen distinct classification tags:

| Vector | Description | Trigger Example |
|---|---|---|
| **Technical** | Pure software logic, API response errors | Code exceptions, data type mismatches |
| **Operational** | DevOps, deployment pipelines, container states | Server memory exhaustion, network drops |
| **Workflow** | Sequence of user actions, process delays | Approvals lagging, manual copypastes |
| **Organizational** | Team structures, communication silos | Lack of ownership on queue components |
| **Compliance** | Legal rules, certifications, residency limits | EU customer data stored in US region |
| **Security** | Access privileges, exposure, encryption | Exposed port bindings, lack of token checks |
| **Performance** | Latency, throughput limits | Database query speed > 500ms |
| **Reliability** | Failovers, data preservation, recovery | Missing database backup validation crons |
| **AI Capability** | Model drift, generation grounding, context size | Hallucinations in generated outreach mail |
| **Human Behavior** | Operator interface errors, user adoption | Manual database inserts bypassing check flows |

---

## 3. Inputs & Outputs

### 3.1 Inputs
*   Structured Ingestion Record (from Module 1).
*   API payload structures or error log outputs.

### 3.2 Outputs
*   **Classification Vector Matrix**: A mapped list of active tags with confidence ratings.
*   **Assigned Engineering Scopes**: A list of departments or engineering teams required for validation.

---

## 4. Operational Algorithm & Scoring

### 4.1 Multi-Tag Scoring Algorithm
Every vector is scored from 0.0 (no match) to 1.0 (exact match) based on keyword frequency, error log analysis, and stakeholder reporting patterns:

\[Score_{Vector} = (Keyword\_Weight \times 0.3) + (Log\_Correlation \times 0.5) + (User\_Tagging \times 0.2)\]

Where:
*   *Keyword Weight*: Presence of domain-specific terms (e.g., "SAML", "auth" triggers Security/Compliance).
*   *Log Correlation*: Connection to container exceptions or slow query logs (triggers Operational/Performance).
*   *User Tagging*: Manual classification from operators.

---

## 5. Reusable Templates & Checklists

### 5.1 Classification Checklist
*   [ ] Checked input logs for system exceptions.
*   [ ] Evaluated compliance boundaries (data privacy checks).
*   [ ] Assessed UI/UX steps to determine if workflow friction is present.
*   [ ] Logged concurrent classifications with respective score tags.
*   [ ] Released work orders to relevant engineering groups.

### 5.2 Template: Classification Vector Matrix
```markdown
### 1. Intake Reference: INT-[UUID]
*   **Active Classifications**:
    1.  **Security** (Score: 0.95) | *Trigger*: Auth bypass detected
    2.  **Compliance** (Score: 0.88) | *Trigger*: Cross-tenant database leak risk
    3.  **Workflow** (Score: 0.70) | *Trigger*: Approval gate lacks timeout

### 2. Affected System Layers
*   **Layer A**: REST API router endpoints (Security)
*   **Layer B**: PostgreSQL connection session listeners (Compliance)
*   **Layer C**: Temporal workflow state definition (Workflow)
```

---

## 6. SRE, AI-Agent, & Safety Parameters

### 6.1 AI-Agent Execution Instructions
1.  **Parse**: Review the structured intake logs and stack traces.
2.  **Evaluate**: Run the multi-tag scoring algorithm across all 17 vectors.
3.  **Verify**: If a Security or Compliance score exceeds 0.75, immediately tag the problem as "CRITICAL EXPOSURE" and alert the Security Architect.

### 6.2 Common Anti-patterns
*   **The Technical Bias**: Classifying every issue as software code failure. *Mitigation*: Force the system to evaluate UI/UX step logs to check if the error is caused by cognitive overload.
*   **Single-Tag Siloing**: Assigning only one label to an intake, masking complex security/workflow crossovers.

### 6.3 Exit Criteria
*   Classification Vector Matrix populated with **all active vectors mapped and scored**.
*   Proceed to **Module 3: Root Cause Discovery**.
