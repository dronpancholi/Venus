# Stage 8 — Legal & Compliance Research

## 1. Governance & Rationale

### 1.1 Why It Exists
Deploying systems without verifying legal and regulatory compliance exposes the company to extreme liabilities, including data privacy fines (GDPR/CCPA), industry exclusion (SOC 2, HIPAA, PCI DSS), or regulatory bans (EU AI Act). Stage 8 establishes the research methodology to identify compliance requirements and translate them into database design and server layout.

### 1.2 What Questions It Answers
*   What privacy laws (GDPR, CCPA) govern user data in our target regions?
*   Do our customers require SOC 2 Type II or ISO 27001 certifications before purchase?
*   Does our platform process protected information (HIPAA, PCI DSS)?
*   Are there restrictions on our software architecture due to export controls or AI regulatory acts?

### 1.3 What Decisions Depend on It
*   **Database Schema & Archival Policy**: Deletion cascades, audit logging, and encryption at rest.
*   **Infrastructure Hosting Locations**: Data residency requirements (e.g., EU-only hosts).
*   **Authentication & Session Rules**: Password complexity, 2FA, session timeouts, and access logging.

### 1.4 What Happens if It Is Skipped
Skipping Stage 8 leads to **Compliance Invalidation**. An enterprise buyer’s security team will immediately block deployment during due diligence because the system lacks audit logs, handles PII incorrectly, or hosts database instances in non-compliant regions.

### 1.5 What Evidence Is Required Before Proceeding
*   Completed compliance checklist covering target markets.
*   Documented data processing map illustrating where PII is stored.
*   Vetted software license matrix confirming all packages are cleared.

---

## 2. Operational Methodology

### 2.1 Compliance-to-Architecture Requirements
To keep compliance research actionable, we map legal requirements directly to database and code rules:

```
┌────────────────────────────────────────────────────────┐
│  REGULATORY REQUIREMENT                                │
│  "GDPR Right to be Forgotten (Article 17)"             │
└───────────────────────────┬────────────────────────────┘
                            │ (Generates)
                            ▼
┌────────────────────────────────────────────────────────┐
│  DATABASE SCHEMAS RULES                                │
│  - Cascade delete keys on client UUID                  │
│  - Clean purging of soft-deleted records in 30 days    │
│  - No backup persistence of deleted UUIDs              │
└────────────────────────────────────────────────────────┘
```

### 2.2 Standard Regulatory Protocols

#### 2.2.1 Data Privacy (GDPR, CCPA)
*   *PII Isolation*: Encrypting and separating email addresses and contact names from operational metrics.
*   *Consent Tracking*: Storing explicit logs verifying when and how user consent was captured.

#### 2.2.2 Security Certifications (SOC 2, ISO 27001)
*   *Access Audits*: Recording who accessed which database rows (essential for Postgres RLS logs).
*   *Change Management*: Version controlling migrations and CI approvals.

---

## 3. Inputs & Outputs

### 3.1 Inputs
*   Geographic targets (from Stage 2).
*   User data profile description (from Stage 3).
*   External package inventory (from Stage 5).

### 3.2 Outputs
*   **Regulatory Compliance Blueprint**: Documented list of database rules.
*   **Data Processing Diagram**: Visual map of PII lifecycle.
*   **Licensing Clearance Dossier**: Vetted list of open-source components.

---

## 4. Reusable Checklists & Templates

### 4.1 Legal & Compliance Checklist
*   [ ] Mapped all geographic jurisdictions for target users.
*   [ ] Checked database designs for compatibility with GDPR Article 17 (Deletion).
*   [ ] Confirmed no health data (HIPAA) or credit card details (PCI DSS) are stored on our servers.
*   [ ] Verified all third-party libraries use permissible licenses (MIT, Apache, BSD).
*   [ ] Documented encryption-at-rest policies for all persistent volumes.

### 4.2 Template: Regulatory Constraint Register
```markdown
### 1. Compliance Target: [e.g., SOC 2 Security Trust Criterion]
*   **Requirement**: Enforce audit logging for administrative write actions.
*   **System Action**: Log all inserts and updates to the `credential_vault` to the `audit_logger`.

### 2. PII Data Processing Log
*   *Data Element*: [e.g., Prospect email address]
*   *Storage Location*: `backlink_prospects.email` (PostgreSQL)
*   *Encryption Status*: Encrypted at rest
*   *Purge Policy*: Cascades delete when the parent campaign is removed.
```

---

## 5. Scoring & Decision Gates

### 5.1 Scorecard: Compliance Readiness Score (CRS)
Evaluate compliance readiness on a 1-5 scale:

| Vector | Scoring Criteria | Score (1-5) |
|---|---|---|
| **Privacy Alignment** | 1: Hardcoded PII / no deletion path. 5: Zero PII storage / complete isolation. | |
| **Audit Coverage** | 1: No system logging. 5: Structured audit trails for all operations. | |
| **Licensing Safety** | 1: Unvetted licensing. 5: 100% compliant open-source libraries. | |
| **Geographic Safety** | 1: Violates local residency. 5: Flexible deployment regions. | |

### 5.2 Decision Gate
*   **Exit Criteria**: Compliance Readiness Score **≥ 16 / 20**, with no single vector scoring below 3.
*   **Pass**: Proceed to **Stage 9: Risk Intelligence**.
*   **Fail**: Rearchitect database tables, data privacy paths, or hosting strategies.
