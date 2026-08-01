# Part 09 — Financial Intelligence

## 1. Context & Strategy
Financial Intelligence models ARR/MRR forecasts, monthly cash flows, runway limits, burn rates, and growth scenarios using Monte Carlo simulations.

---

## 2. Standard Financial Calculations
*   **Annual Recurring Revenue (ARR)**: Monthly Recurring Revenue (MRR) * 12.
*   **Net Burn Rate**: Total cash spend per month - monthly recurring revenue.
*   **Runway**: Current Cash Balance / Net Burn Rate.
    *   *Enforced Target*: Enforce minimum runway target of **18 months**.

---

## 3. Financial Projections Modeling

| Projections Horizon | Month 12 | Month 24 | Month 36 |
|---|---|---|---|
| **Best Case ARR** | [e.g., $1.2M] | [e.g., $4.5M] | [e.g., $12M] |
| **Expected ARR** | [e.g., $800K] | [e.g., $2.5M] | [e.g., $7M] |
| **Worst Case ARR** | [e.g., $300K] | [e.g., $1.0M] | [e.g., $2.5M] |

---

## 4. Financial Intelligence Checklist
*   [ ] Created ARR and cash flow projection sheets.
*   [ ] Checked monthly net burn rates.
*   [ ] Verified runway limits >= 18 months.
*   [ ] Executed sensitivity analysis under worst-case churn.
