# Module 17 — Risk Decision Engine

## 1. Context & Strategy

### 1.1 Purpose
The Risk Decision Engine identifies, scores, and mitigates architectural, infrastructure, compliance, and security risks introduced by a proposed decision.

### 1.2 Philosophy
Every decision creates risk. Risk cannot be eliminated entirely, but it must be quantified, monitored, and capped within the organization's risk tolerance limits.

---

## 2. Ingest Parameters & Scoring Taxonomy

### 2.1 Inputs & Outputs
*   **Inputs**: DIR, classification tags, trade-off matrix.
*   **Outputs**: Risk Register Entry and designated Rollback Playbook.

### 2.2 Risk Indicators
*   **Probability (P)**: Chance of occurrence (1: Rare, 5: Daily).
*   **Impact (I)**: Systemic damage severity (1: Cosmetic, 5: Critical data loss/lawsuit).
*   **Recoverability (R)**: Ease of roll back (1: Immediate auto-rollback, 5: Manual DB recovery).

---

## 3. Operational Algorithm & Scoring

### 3.1 Risk Score (RS) Formula
The overall risk score is calculated as:

\[RS = \frac{P \times I \times R}{5.0}\]

### 3.2 Gate Thresholds
*   **RS >= 8.0**: Critical Risk. Banned. Requires immediate architectural changes to isolate blast radius before proceeding.
*   **RS < 8.0**: Acceptable risk, requires automated rollback script verification.

---

## 4. Reusable Templates & Checklists

### 4.1 Template: Risk Register Entry
```markdown
### 1. Risk Profile
*   **Decision ID**: DEC-[UUID]
*   **Risk Vector**: [e.g., Data corruption due to bulk upload schema failures]
*   **Calculated RS**: [0.0 - 25.0]

### 2. Mitigation Strategy
*   *Rollback Playbook*: `playbooks/rollback_bulk_upload.sh`
*   *Detection System*: Sentry alerting on schema validation errors.
```

### 4.2 Checklist
*   [ ] Checked database recovery options.
*   [ ] Verified data consistency backups.
*   [ ] Written automated rollback scripts.
*   [ ] Configured real-time system alerts.

---

## 5. SRE, AI-Agent, & Safety Parameters

### 5.1 AI-Agent Execution Instructions
1.  **Parse**: Audit configuration files for security keys and API endpoints.
2.  **Verify**: Ensure all DB migrations have a reverse/down script recorded in the codebase.

### 5.2 Common Anti-patterns
*   *The One-Way Migration*: Deploying a schema change that alters column names without keeping old names deprecated but functional, making rollbacks impossible.

### 5.3 Exit Criteria
*   Risk Score calculated and **Rollback Playbook verified**.
*   Proceed to **Module 18: Complexity Budget**.
