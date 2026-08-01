# Template: Unknown Register

## 1. Meta Control
*   **Project Name**: [Project Name]
*   **Intake ID**: INT-[UUID]
*   **Register ID**: UNK-[UUID]
*   **Last Updated**: [Date]
*   **Lead Researcher**: [Name]

---

## 2. Uncertainty Classification Matrix
*Categorize the system's operational parameters based on availability of information and certainty of knowledge.*

```
             +───────────────────────────────────+───────────────────────────────────+
             |         KNOWN KNOWNS              |         KNOWN UNKNOWNS            |
             |  - Database version limits        |  - Target API performance limits  |
   KNOWABILITY|  - Team development velocity      |  - User conversion rates          |
             |                                   |                                   |
             +───────────────────────────────────+───────────────────────────────────+
             |         UNKNOWN KNOWNS            |         UNKNOWN UNKNOWNS          |
             |  - Legacy code hidden behaviors   |  - Third-party platform policy    |
             |  - Institutional tribal knowledge |    changes, sudden library deprecations|
             |                                   |                                   |
             +───────────────────────────────────+───────────────────────────────────+
                             KNOWN                           UNKNOWN
                                       INFORMATION STATE
```

---

## 3. Active Unknowns Registry
*Track and prioritize identified unknowns based on their potential system impact.*

| Unknown ID | Description | Impact Vector | Risk Class | Validation Complexity (1-5) | Owner | Target Resolution Date |
|---|---|---|---|---|---|---|
| **UNK-01** | [e.g., Will target API change billing rules?] | Business / Cost | Critical | 3 | [Name] | YYYY-MM-DD |
| **UNK-02** | [e.g., Maximum DB write rate under stress] | Technical | High | 4 | [Name] | YYYY-MM-DD |
| **UNK-03** | [e.g., Latency impact of third-party DNS] | Performance | Medium | 2 | [Name] | YYYY-MM-DD |
| **UNK-04** | [e.g., Legal status of scraping in Germany] | Regulatory | High | 5 | [Name] | YYYY-MM-DD |

---

## 4. Unknowns Prioritization Queue
*Unknowns are ranked by their Risk Score. Critical and High risk unknowns must have active validation spikes before engineering begins.*

### 4.1 Prioritization Formula
Uncertainty Score is calculated as:

\[Uncertainty\_Score = Impact\_Class \times Validation\_Complexity\]

*   **Impact Class**: 5: Critical/Showstopper. 3: Significant restructure. 1: Minor tweak.
*   **Validation Complexity**: 1: Simple web search. 3: Multi-day test spike. 5: External legal audit / production load test.

### 4.2 Spikes & Research Tasks
*   **Spike ID**: SPK-UNK-01 (targeting UNK-02)
    *   *Description*: *Build simulated load client to push 5,000 mock transactions/second to postgres instance.*
    *   *Assigned Researcher*: [Name]
    *   *Verification Command*: `pytest tests/performance/test_max_write_rate.py`
    *   *Resolution Criteria*: Identify the system saturation throughput limit and log memory usage profiles.
    *   *Resolution Summary*: [To be filled after Spike completes]
