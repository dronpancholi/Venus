# Template: Vendor Comparison Report

## 1. Document Control
*   **Project Name**: [Project Name]
*   **Decision ID**: DEC-[UUID]
*   **Evaluation Date**: [Date]

---

## 2. Vendor Profiles Summary

| Comparison Vector | Vendor A: [Name] | Vendor B: [Name] |
|---|---|---|
| **Monthly Subscription** | [e.g., $199 / mo] | [e.g., $299 / mo] |
| **SOC2 Compliance** | SOC2 Type II Certified | Self-attested only |
| **Contract SLA Uptime** | 99.9% Uptime SLA | 99.0% Uptime SLA |
| **API Rate Limits** | 100 req / minute | 1,000 req / minute |
| **Suitability Score** | **4.2 / 5.0** (Winner) | **3.1 / 5.0** |

---

## 3. SLA & Financial Risk Assessment
*   **Vendor A Risk**: Lower rate limits might restrict crawler scaling during peaks.
*   **Vendor B Risk**: Lacks SOC2 Type II certification, violating our security constraints.
*   **Selection Recommendation**: Select Vendor A; implement queue scheduling to smooth write volume spikes and respect the 100 req/minute rate limit.
