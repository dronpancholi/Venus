# Template: Post-Decision Review (PDR)

## 1. Document Control
*   **Project Name**: [Project Name]
*   **Decision ID**: DEC-[UUID]
*   **Review Date**: [Date]
*   **Review Owner**: [Name]

---

## 2. Projection vs. Actual Performance Delta

| Comparison Metric | Projected Target | Actual Result (30-day Avg) | Deviation Delta (%) | Verdict |
|---|---|---|---|---|
| **API Latency (p99)** | <= 5ms | 2.8ms | -44% | **EXCEEDED TARGET** |
| **Monthly Server Cost**| <= $200 / mo | $350 / mo | +75% | **OVER BUDGET** |
| **Developer Build Hours**| 40 hours | 35 hours | -12.5% | **EXCEEDED TARGET** |

---

## 3. Operations Regret & Retro Details
*Analyze root causes of any overruns or failed targets.*

*   *Cost Overrun Explanation*: The Redis instance size was selected based on default templates without auto-scaling enabled, causing idle compute costs.
*   *Remediation Plan*: Enable horizontal auto-scaling and configure Redis cache TTL eviction policy to lower cache node storage size.
*   *Historical Update*: Telemetry registered in **Module 21 (Institutional Memory)**.
