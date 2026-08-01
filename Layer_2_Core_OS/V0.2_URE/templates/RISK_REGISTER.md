# Template: Risk Register

## 1. Document Context
*   **Project Name**: [Project Name]
*   **Target Scope**: [e.g., Technical, Compliance, Financial]
*   **Date Compiled**: [Date]

---

## 2. Risk Mitigation Logs

| Risk ID | Category | Threat Description | Probability (1-5) | Impact (1-5) | Exposure (P×I) | Active Mitigation | Contingency Action |
|---|---|---|---|---|---|---|---|
| **RISK-TEC-01** | Technical | Database scaling bottleneck | [Score] | [Score] | [Total] | Add dynamic caching | Scale read replicas |
| **RISK-SEC-02** | Security | Cross-tenant data leakage | [Score] | [Score] | [Total] | PostgreSQL RLS | Immediate session tear-down |
| **RISK-FIN-03** | Financial | API invoice overrun | [Score] | [Score] | [Total] | Redis rate limits | Terminate workflow execution |

---

## 3. Telemetry Alert Metrics
*   *Alert Rule 1*: If CPU > 85% for 5 mins, alert SRE.
*   *Alert Rule 2*: If API 5xx errors > 5% of traffic, route to fallback provider.
*   *Alert Rule 3*: If tenant invoice spends > 120% of limit, trigger account block.
