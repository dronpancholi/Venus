# Template: Enterprise Readiness Assessment

## 1. Document Control
*   **Project Name**: [Project Name]
*   **Assessment ID**: ENT-RDY-[UUID]

---

## 2. Compliance Checklist

| Standard | Requirement Details | Current Status | Remediation Plan |
|---|---|---|---|
| **SOC2 Type II** | Continuous system logs audit | **STAGED** | Schedule auditor review in Month 3 |
| **GDPR** | EU localized user data subnets | **COMPLIANT** | Enforce database RLS partition rules |
| **HIPAA** | Business Associate Agreement (BAA) | **PENDING** | Secure BAA sign-offs with AWS/GCP |

---

## 3. SLA Targets & Penalties
*   **Target Availability**: 99.9% uptime SLA.
*   **Downtime Penalty**: Enforce refund credit allocations if monthly availability drops below target.

---

## 4. Verification Check
*   [ ] Checked database encryption parameters.
*   [ ] Checked database deletion scripts.
