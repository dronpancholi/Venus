# Module 02 — Decision Classification Engine

## 1. Context & Strategy

### 1.1 Purpose
The Decision Classification Engine routes proposals into their correct technical, operational, financial, and strategic tracks. This classification ensures that decisions undergo appropriate scoring matrices.

### 1.2 Philosophy
Classifying a decision correctly prevents process mismatches. A minor UI change should not trigger a weeks-long Vendor evaluation, nor should a core database migration bypass compliance checks.

---

## 2. Ingest Parameters & Taxonomy

### 2.1 Inputs & Outputs
*   **Inputs**: Approved Decision Intake Record (DIR).
*   **Outputs**: Multi-vector classification tag mapping.

### 2.2 Classification Mappings
Every decision is mapped across eleven axes:
1.  **Strategic**: Impacting high-level vision, pricing tiers, or acquisitions.
2.  **Product**: Adding, modifying, or removing core features.
3.  **Architecture**: Changing software design, database schemas, or communication protocols.
4.  **Infrastructure**: Modifying cloud resources, subnets, clusters, or CDN providers.
5.  **AI**: Integrating ML/LLMs, changing models, or agent structures.
6.  **Security**: Altering cryptography, auth flows, firewalls, or compliance boundaries.
7.  **Hiring**: Staff allocations, team reorganizations.
8.  **Financial**: Exceeding baseline budgets, new vendor contracts.
9.  **Legal**: Modifying OSS licenses, privacy policy, or regulatory exposure.
10. **Operational**: Altering CI/CD, deploy rules, on-call schedules, or metrics dashboards.
11. **Commercial**: Pricing metrics, GTM channel allocations.

---

## 3. Operational Algorithm & Decision Tree

### 3.1 The Classification Logic
Decisions are scanned for keywords and domain entities:

```
                            [DIR Received]
                                  │
                       [Scan Keyword Dictionary]
                                  │
         ┌────────────────────────┼────────────────────────┐
         ▼                        ▼                        ▼
[Security / Compliance]  [DB Schemas / Ports]     [Cloud Spends / Contracts]
         │                        │                        │
         ▼                        ▼                        ▼
  Tag: Security           Tag: Architecture          Tag: Financial
```

### 3.2 Required Evidence
Classification matches classification dictionaries:
*   *Security*: Authentication, JWT, HTTPS, firewall, vault.
*   *Architecture*: Schema, REST, GraphQL, thread, cache.

---

## 4. Reusable Templates & Checklists

### 4.1 Template: Classification Record
```markdown
### 1. Classification Overview
*   **Decision ID**: DEC-[UUID]
*   **Target Tags**: [e.g., Architecture, Financial]

### 2. Regulatory Flags
*   *HIPAA Exposure*: [Yes / No]
*   *GDPR Data Residency Impact*: [Yes / No]
```

### 4.2 Checklist
*   [ ] Checked proposal against key dictionary lists.
*   [ ] Checked security/compliance flags.
*   [ ] Assigned correct tags.

---

## 5. SRE, AI-Agent, & Safety Parameters

### 5.1 AI-Agent Execution Instructions
1.  **Tag**: Extract classifications using zero-shot semantic matching.
2.  **Verify**: If "Security" keywords appear, force the Security classification tag regardless of primary proposer categorization.

### 5.2 Common Anti-patterns
*   *The Legacy Bypass*: Classifying database schema alterations as "Operational" fixes to skip architectural reviews.

### 5.3 Exit Criteria
*   Classification vectors successfully tagged.
*   Proceed to **Module 03: Decision Importance Scoring**.
