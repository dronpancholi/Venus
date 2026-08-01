# Template: Risk Decision Register

## 1. Document Control
*   **Project Name**: [Project Name]
*   **Decision ID**: DEC-[UUID]
*   **Date Updated**: [Date]

---

## 2. Risk Registry Entries

| Risk ID | Description of Threat | Probability (1-5) | Impact (1-5) | Recoverability (1-5) | Risk Score | Status |
|---|---|---|---|---|---|---|
| **RSK-DEC-01** | Database locking during migrations | 2 | 5 | 4 | **8.0** | **MITIGATED** |
| **RSK-DEC-02** | Vendor API billing tier change | 3 | 4 | 2 | **4.8** | **MONITORED** |
| **RSK-DEC-03** | Data exposure outside EU boundaries | 1 | 5 | 5 | **5.0** | **MITIGATED** |

---

## 3. Rollback Playbooks & Verification
*Detail rollback actions to resolve incident triggers.*

*   **Risk Mitigation (RSK-DEC-01)**:
    *   *Detection Indicator*: Sentry alert on DB migration script execution crash.
    *   *Rollback Script*: `scripts/db_rollback_v2.sh`
    *   *Verification Code*: Run migration tests in local docker compose prior to production merge.
