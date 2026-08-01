# Engine: Business Model Selection

## 1. Context & Strategy

### 1.1 Purpose
The Business Model Selection Engine analyzes market competitive density, capital constraints, and target NRR expectations to select the optimal model class (SaaS, Marketplace, Open Core, or API).

### 1.2 Philosophy
Business models dictate company valuation. We prioritize SaaS and Usage-based APIs because their recurring nature and high NRR potential maximize market value and strategic exit multiples.

---

## 2. Selection Routing Tree
```
                         [Check target NRR goal]
                                   │
                   ┌───────────────┴───────────────┐
              Goal >= 120%                    Goal < 120%
                   │                               │
                   ▼                               ▼
       [Select: Usage-Based API]        [Select: SaaS Subscription]
    *Encourages product expansion*    *Ensures cash flow predictability*
```

---

## 3. Selection Checklist & Exit Criteria
*   [ ] Checked target customer segment profiles.
*   [ ] Checked open-source licensing rules for open-core plays.
*   *Exit Criteria*: Business Model Canvas and strategy signed off.
