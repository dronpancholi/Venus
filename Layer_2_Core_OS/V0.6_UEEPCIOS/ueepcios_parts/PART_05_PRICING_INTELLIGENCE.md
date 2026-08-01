# Part 05 — Pricing Intelligence

## 1. Context & Strategy
Pricing Intelligence models target seat, token, usage, enterprise, discount, and tier structures to optimize Average Revenue Per User (ARPU).

---

## 2. Pricing Models Directory
*   **Seat-Based**: Simple, predictable (e.g. $15/user/mo).
*   **Usage / Token-Based**: Directly maps to running cost (e.g. $0.02 / 1K tokens).
*   **Tiered Feature Gate**: Encourages upgrades by gating premium features.
*   **Enterprise / Negotiated**: High ticket contracts with custom SLAs.

---

## 3. Dynamic Pricing Model
When user transaction volume spikes, dynamic pricing parameters scale unit costs to preserve margins:

\[Price_{Unit} = Base\_Cost_{Unit} \times (1 + Volume\_Multiplier)\]

Where:
*   *Volume Multiplier*: Decreases per tier to incentivize higher consumption.

---

## 4. Pricing Checklist
*   [ ] Structured core tier definitions.
*   [ ] Checked token and compute cost margins.
*   [ ] Wrote discount threshold rules.
*   [ ] Defined enterprise negotiation guardrails.
