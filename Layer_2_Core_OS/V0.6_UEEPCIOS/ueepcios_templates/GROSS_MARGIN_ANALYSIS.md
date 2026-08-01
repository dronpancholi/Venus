# Template: Gross Margin Analysis

## 1. Document Control
*   **Project Name**: [Project Name]
*   **Analysis ID**: MAR-[UUID]

---

## 2. Gross Margin Calculation
Project margins across pricing tiers:

\[Gross\_Margin = \frac{Price_{Tier} - Unit\_Cost_{COGS}}{Price_{Tier}}\]

---

## 3. Margin Projection Matrix

| Product Tier | Price | Unit Cost (COGS) | Gross Profit | Gross Margin % | Status |
|---|---|---|---|---|---|
| **Developer** | $19.00 | $3.50 | $15.50 | **81.5%** | **APPROVED** |
| **Team** | $99.00 | $12.00 | $87.00 | **87.8%** | **APPROVED** |
| **Enterprise**| $499.00 | $55.00 | $444.00 | **88.9%** | **APPROVED** |

---

## 4. Margin Optimization Levers
*   *Lever 1*: Swap cloud LLM to local Ollama nodes for simple categorization, lowering COGS by $1.20/user.
*   *Lever 2*: Enable caching of external API database reads, lowering query egress fees by $0.40/user.
