# Template: Compliance Gap Analysis

## 1. Document Control
*   **Project Name**: [Project Name]
*   **Analysis ID**: CMP-GAP-[UUID]

---

## 2. Compliance Gap Register

| Target Regulation | Identified Gap | Severity | Remediation Strategy | Target Date |
|---|---|---|---|---|
| **GDPR** | Inbound log dumps contain user emails | High | Implement regex log cleaners | YYYY-MM-DD |
| **HIPAA** | Cache DB is not encrypted at rest | Critical | Update redis config parameter | YYYY-MM-DD |
| **SOC2** | No employee background check policy | Medium | Implement standard employee check | YYYY-MM-DD |

---

## 3. Verification Check
*   [ ] Checked Sentry logs for user PII.
*   [ ] Verified Cloud configuration settings for AWS/GCP resources.
