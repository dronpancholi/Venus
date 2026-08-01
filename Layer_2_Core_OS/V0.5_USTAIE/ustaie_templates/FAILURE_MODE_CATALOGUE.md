# Template: Failure Mode Catalogue

## 1. Document Control
*   **Project Name**: [Project Name]
*   **Catalogue ID**: FML-CAT-[UUID]

---

## 2. Failure Modes Directory
*Audit potential failure scenarios, assigning Risk Priority Numbers (RPN).*

| Scenario ID | Failure Mode Description | Affected Subsystem | Probability (1-5) | Impact (1-5) | Detectability (1-5) | RPN |
|---|---|---|---|---|---|---|
| **FML-01** | Database deadlock under high write load | PostgreSQL DB | 3 | 5 | 2 | **30** |
| **FML-02** | Redis cache OOM eviction | Redis Cache | 4 | 3 | 4 | **48** |
| **FML-03** | Stripe API payment callback drops | API Gateway | 2 | 5 | 1 | **10** |

---

## 3. Automated Detection & Alerting
*   **FML-01 (DB Deadlock)**:
    *   *Alert Trigger*: Sentry PostgreSQL query execution timeouts.
    *   *Mitigation Action*: Automated query retries with exponential backoff.
*   **FML-02 (Redis OOM)**:
    *   *Alert Trigger*: Prometheus `redis_memory_used_bytes` > 90%.
    *   *Mitigation Action*: Eviction policy configured to volatile-lru.
