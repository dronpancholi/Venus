# Template: Valuation Report

## 1. Document Control
*   **Project Name**: [Project Name]
*   **Valuation ID**: VAL-REP-[UUID]

---

## 2. Valuation Summary

| Valuation Methodology | Projected Value | Key Assumptions |
|---|---|---|
| **Multiple-Based (15x ARR)**| [e.g., $15,000,000] | Based on ARR target of $1M at Month 12 + 100% YoY growth |
| **Discounted Cash Flow (DCF)**| [e.g., $12,400,000] | Based on WACC of 12% and 5-year free cash flows |
| **Asset-Based Value** | [e.g., $1,500,000] | Replacement cost of custom code + IP patent valuations |

---

## 3. ARR Multiples Valuation Algorithm
Calculations are updated dynamically based on YoY growth rates:

\[Valuation = Current\_ARR \times ARR\_Multiple\]

Enforced baseline multiple: **10x ARR** for standard growth; **15x ARR** for hyper-growth (YoY growth > 100%).
