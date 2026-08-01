# Module 11 — Vendor Evaluation

## 1. Context & Strategy

### 1.1 Purpose
The Vendor Evaluation module establishes standard validation metrics for evaluating third-party SaaS, API, and cloud providers (e.g., Stripe, Auth0, Cloudflare).

### 1.2 Philosophy
Vendor selection creates system dependencies. We audit vendor security compliance, operational SLA history, API stability, and developer ergonomics before routing company traffic or business data through their infrastructure.

---

## 2. Ingest Parameters & Taxonomy

### 2.1 Inputs & Outputs
*   **Inputs**: Vendor proposal, SLA documentation, SOC2 Type II reports, pricing matrices.
*   **Outputs**: Vendor Suitability Scorecard and approved SLA contract terms.

### 2.2 Audited Vectors
*   **Security (SOC2/GDPR)**: Compliance status.
*   **Availability SLA**: Contractual uptime commitments (e.g., 99.9% uptime).
*   **API Stability**: History of breaking changes, API versioning policy.
*   **Financial Cost**: Standard pricing tier structure and hidden usage overage fees.

---

## 3. Operational Algorithm & Decision Tree

### 3.1 Vendor Scorecard Model
Vendors are evaluated across 4 metrics (scored 1-5):

\[Vendor\_Score = (Security\_Score \times 0.3) + (SLA\_Score \times 0.3) + (Cost\_Score \times 0.2) + (API\_Score \times 0.2)\]

### 3.2 Decision Tree logic
```
                          [Evaluate Vendor]
                                 │
                   [Breaches SOC2/GDPR Standards?]
                     ├── YES ──► [Reject Vendor: Compliance Failure]
                     └── NO  ──► [Verify Vendor Score >= 4.0]
                                       ├── PASS ──► [Approve Vendor]
                                       └── FAIL ──► [Halt; Seek Alternatives]
```

---

## 4. Reusable Templates & Checklists

### 4.1 Template: Vendor Suitability Scorecard
```markdown
### 1. Vendor Profile: VEN-[UUID]
*   **Vendor Name**: [Name]
*   **SOC2 Type II Status**: [Yes / No]
*   **Availability SLA**: [e.g., 99.95%]
*   **Calculated Score**: [0.0 - 5.0]
```

### 4.2 Checklist
*   [ ] Requested SOC2 compliance documentation.
*   [ ] Checked API documentation for SDK availability.
*   [ ] Audited vendor's public status history page.
*   [ ] Calculated total operational cost at 10x current scale.

---

## 5. SRE, AI-Agent, & Safety Parameters

### 5.1 AI-Agent Execution Instructions
1.  **Parse**: Read vendor contract texts and SLA targets.
2.  **Verify**: Search public security breach directories for recent vendor hacks.

### 5.2 Common Anti-patterns
*   *The Hype Contract*: Selecting a vendor because "everyone uses them" without verifying if they support regional data residency constraints.

### 5.3 Exit Criteria
*   Vendor Suitability Scorecard populated and **security audit certified**.
*   Proceed to **Module 12: ADR Engine**.
