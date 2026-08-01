# Engine: Growth Product Systems

## 1. Context & Strategy

### 1.1 Purpose
The Growth Product Systems Engine tracks and optimizes onboarding completion rates, pricing grid conversion metrics, usage quota indicators, and viral sharing mechanics to maximize user activation and customer lifetime value (LTV).

### 1.2 Philosophy
Growth loops are mathematical operations. We optimize onboarding and pricing structures by identifying drop-off points, removing design friction, and simplifying checkouts.

---

## 2. Ingest Parameters & Taxonomy

### 2.1 Inputs & Outputs
*   **Inputs**: User journey navigation events, step completion timestamps, invite data, pricing card click metrics, account quota volumes as defined in [Part 15](file:///Users/dronpancholi/Developer/01_Strategic/Venus/upuxios_parts/PART_15_GROWTH_PRODUCT_SYSTEMS.md).
*   **Outputs**: Growth Funnel Audit Report, including Viral Coefficient ($K$) stats, onboarding completion charts, and paywall trigger counts.

### 2.2 Auditing Pipeline
```
               [Ingest User Cohort Event Data]
                              │
                 [Calculate Time-To-Value]
                └── Log duration to activation
                              │
                [Viral Coefficient Calculator]
                └── Compute invite conversion rates
                              │
               [Pricing Grid & Checkouts Audit]
                └── Check annual/monthly selection
                              │
                [Paywall & Quota Trigger Audit]
```

---

## 3. Algorithmic Checks & Optimization Metrics

### 3.1 Time-to-Value (TTV) Analyzer
The engine computes the average time elapsed ($TTV$) from a user's first log-in ($T_{start}$) to their first successful completion of a key action ($T_{act}$, e.g. creating their first dashboard):

$$TTV = \frac{1}{N} \sum_{i=1}^{N} \left( T_{act, i} - T_{start, i} \right)$$

If average $TTV$ exceeds 5 minutes, the engine flags the onboarding flow as a conversion blocker.

### 3.2 Virality Coefficient ($K$-Factor) Monitor
The engine tracks sharing virality:

$$K = \frac{\text{Total Invites Sent}}{\text{Active Users}} \times \frac{\text{New Users Signed Up via Invites}}{\text{Total Invites Sent}}$$

If $K < 0.5$, the engine triggers a recommendation to place social invite controls in user success pathways.

### 3.3 Quota Warning Audits
*   **Progressive Warnings**: Verifies that when a user reaches 80% usage capacity of their current tier, a warning banner appears.
*   **Gating Action**: Checks that at 100% usage capacity, write actions are blocked and a contextual upgrade modal is shown.

---

## 4. Reusable Checklist & Exit Criteria
*   [ ] Checked that onboarding contains $\le 3$ setup steps.
*   [ ] Verified average $TTV$ falls within the targeted benchmark ($<5$ mins).
*   [ ] Confirmed the viral coefficient ($K$) is active and tracked.
*   [ ] Checked pricing grids for annual pricing discount tags and visual highlights.
*   [ ] Audited warning gates to ensure they fire at $80\%$ and $100\%$ usage limits.
*   *Exit Criteria*: Growth funnel audits complete and recommendations updated in the strategy board.
