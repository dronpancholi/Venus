# Template: Failure Prediction Report

## 1. Meta Control
*   **Project Name**: [Project Name]
*   **Intake ID**: INT-[UUID]
*   **Report ID**: FAIL-[UUID]
*   **Analysis Date**: [Date]
*   **Facilitator**: [Name]

---

## 2. Failure Mode and Effects Analysis (FMEA)
*A systemic process for identifying potential design or execution failures. This table catalogs failure modes across the entire system lifecycle.*

| Scenario ID | Failure Scenario | Failure Category | Probability (1-5) | Impact (1-5) | Detectability (1-5) | RPN | Mitigation Effort (1-5) |
|---|---|---|---|---|---|---|---|
| **FML-SYS-01** | Database deadlocks under write load | System Infrastructure | 3 | 5 | 2 | 30 | 3 |
| **FML-API-01** | Vendor API returns 502 / deprecation | External Dependencies | 4 | 4 | 5 | 80 | 2 |
| **FML-SEC-01** | Session token hijack via XSS | Security | 2 | 5 | 1 | 10 | 4 |
| **FML-OPS-01** | Operator misconfigures outreach filters| Human Operations | 4 | 3 | 4 | 48 | 1 |
| **FML-DATA-01**| Database records corrupted on write | Data Integrity | 1 | 5 | 3 | 15 | 4 |

---

## 3. RPN Scoring & Prioritization
The Risk Priority Number (RPN) is calculated to identify the most dangerous failure modes:

\[RPN = Probability \times Impact \times Detectability\]

*   **Probability (1-5)**: 1: Extremely rare. 5: Guaranteed to happen regularly.
*   **Impact (1-5)**: 1: Trivial UI anomaly. 5: Total data loss / system downtime / lawsuit.
*   **Detectability (1-5)**: 1: Instant alerting (e.g. Sentry/PagerDuty). 5: Silent failure (goes unnoticed for months).

*Prioritization Strategy:*
*   **RPN >= 50**: Critical Threat. Must implement automated prevention policies prior to build.
*   **RPN 20 - 49**: Moderate Threat. Implement monitoring alerts and manual playbooks.
*   **RPN < 20**: Accept risk, monitor periodically.

---

## 4. High-Priority Prevention & Recovery Plans

### FML-API-01: Vendor API returns 502 or changes schema
*   **Failure Scenario Description**: *The third-party indexing API changes its schema or goes down, causing all crawler jobs to crash.*
*   **Prevention Plan (Before Build)**:
    *   Build an API adapter layer that isolates the API contract from the application logic.
    *   Implement schema validation (using Pydantic/Zod) at the boundary.
*   **Recovery Plan (After Failure)**:
    *   Gracefully catch validation errors, store raw payload in a queue for manual retry, and alert developers.
    *   Fallback to offline database cache if API is offline.
*   **Verification Command**: `npm run test:api-mock-failure` or `pytest tests/integration/test_api_fallback.py`

### FML-SYS-01: Database deadlocks under write load
*   **Failure Scenario Description**: *Concurrent writes from multiple indexing workers cause transaction lock contention on the target tables.*
*   **Prevention Plan (Before Build)**:
    *   Implement bulk insertion batches instead of row-by-row updates.
    *   Implement queue-based serialization of write operations.
*   **Recovery Plan (After Failure)**:
    *   Implement automatic query retry with jittered exponential backoff.
*   **Verification Command**: `k6 run load_tests/db_stress_test.js`

---

## 5. The Top 100 Failure Scenarios Register
*Enforce the listing of potential errors across the system. The analyzing agent or team must enumerate scenarios matching their specific domain.*

1.  **FML-001**: [Description] | *Category*: [System/API/Security/Human/Data] | *RPN*: [Score]
2.  **FML-002**: [Description] | *Category*: [System/API/Security/Human/Data] | *RPN*: [Score]
...
100. **FML-100**: [Description] | *Category*: [System/API/Security/Human/Data] | *RPN*: [Score]
