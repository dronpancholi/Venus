# Engine: Valuation

## 1. Context & Strategy

### 1.1 Purpose
The Valuation Engine computes comparable transaction multiples, discounted cash flows (DCF), and IP asset valuations to calculate project value.

### 1.2 Philosophy
Understand value creation. We model DCF values and apply prevailing market ARR multiples based on revenue growth targets.

---

## 2. Multiple-Based Valuation Algorithm
Valuation is calculated using current ARR and growth multiplier rates:

\[Valuation = ARR \times ARR\_Multiple\]

Where:
*   *ARR Multiple*: Based on Year-over-Year (YoY) revenue growth rate:
    *   YoY Growth > 100%: 15x - 20x ARR multiple.
    *   YoY Growth 50% - 100%: 10x - 15x ARR multiple.
    *   YoY Growth < 50%: 5x - 10x ARR multiple.

---

## 3. Valuation Checklist & Exit Criteria
*   [ ] Run comparable transaction reviews.
*   [ ] Checked discounted cash flow metrics.
*   *Exit Criteria*: Valuation Report completed and certified.
