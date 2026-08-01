# Stage 7 — Economic Research

## 1. Governance & Rationale

### 1.1 Why It Exists
Architectures that are technically outstanding but economically irrational cause business failure. Stage 7 mandates the creation of a complete, bottom-up economic cost model that maps infrastructure configuration (compute, storage, network ingress/egress, third-party API queries) directly to business metrics (CAC, LTV, pricing tiers, gross margins).

### 1.2 What Questions It Answers
*   What is the exact infrastructure and compute cost to support a single user session?
*   How do API call frequencies and model inference tokens scale as database records increase?
*   What are our projected gross margins across different customer subscription tiers?
*   At what user count does the system reach financial break-even?

### 1.3 What Decisions Depend on It
*   **Pricing Strategy**: Consumption-based billing vs. flat-rate subscription models.
*   **Infrastructure Design**: Selecting multi-tenant shared databases (lower cost) vs. dedicated database clusters (higher cost).
*   **Caching Strategy**: Implementing caching layers to avoid repeated expensive LLM or data provider queries.

### 1.4 What Happens if It Is Skipped
Skipping Stage 7 results in **Negative Unit Economics**. The company might price its subscription at $99/month while a user's API consumption and LLM token usage cost $150/month. Without visibility into these cost vectors, scaling the user base merely accelerates capital depletion.

### 1.5 What Evidence Is Required Before Proceeding
*   Bottom-up infrastructure cost spreadsheet listing all cloud resources.
*   Estimated Lifetime Value (LTV) and Customer Acquisition Cost (CAC) projection.
*   Signed-off pricing tier model.

---

## 2. Operational Methodology

### 2.1 Connecting Architecture to Operating Margins
To ensure profitability, we map every architectural component to its direct operational cost:

```
┌────────────────────────────────────────────────────────┐
│  ARCHITECTURAL COMPONENT                               │
│  "PostgreSQL database query execution"                 │
└───────────────────────────┬────────────────────────────┘
                            │ (Generates)
                            ▼
┌────────────────────────────────────────────────────────┐
│  OPERATIONAL COST VECTOR                               │
│  - DB instance size: $150/month                        │
│  - Disk IOPS: $50/month                                │
│  - Read replicas: $100/month                           │
└───────────────────────────┬────────────────────────────┘
                            │ (Calculates)
                            ▼
┌────────────────────────────────────────────────────────┐
│  UNIT ECONOMICS                                        │
│  - Infrastructure cost per tenant: $3.00/month         │
│  - Gross Margin at $99 pricing: 96.9%                  │
└────────────────────────────────────────────────────────┘
```

### 2.2 Cost Breakdown Parameters

#### 2.2.1 Compute & Storage Forecasts
*   *Database pricing*: Scaling storage costs for time-series and log databases.
*   *Caching offsets*: Calculating how much database/API cost is avoided by implementing Redis caches.

#### 2.2.2 Third-Party API & Inference Overhead
*   *Token cost modeling*: Input vs. Output token scaling across user cohorts.
*   *API dependencies*: Direct costs for data providers (e.g., Ahrefs, DataForSEO cost per 1,000 queries).

---

## 3. Inputs & Outputs

### 3.1 Inputs
*   Tech Stack Specification (from Stage 5).
*   AI Model Selection (from Stage 6).
*   Target SOM (from Stage 2).

### 3.2 Outputs
*   **Bottom-Up Unit Economic Model**: Comprehensive cost spreadsheet.
*   **Pricing Blueprint**: Validated tier structures.
*   **Cost Control Strategy**: Policies for caching and rate limiting.

---

## 4. Reusable Checklists & Templates

### 4.1 Economic Research Checklist
*   [ ] Listed every cloud resource and calculated its monthly base cost.
*   [ ] Modeled user API usage frequency to project variable costs.
*   [ ] Calculated expected LLM token usage per user transaction.
*   [ ] Verified gross margin targets exceed 80% on all tiers.
*   [ ] Modeled break-even thresholds (number of paying tenants required).

### 4.2 Template: Tenant Unit Cost Calculation
```markdown
### 1. Fixed Infrastructure Costs
*   PostgreSQL: $[Base Cost]/mo
*   Redis: $[Base Cost]/mo
*   Temporal Worker Hosts: $[Base Cost]/mo
*   *Fixed Total*: $[Total]/mo

### 2. Variable Cost per Tenant Transaction
*   LLM Input tokens (Average: [Count]): $[Cost]
*   LLM Output tokens (Average: [Count]): $[Cost]
*   Third-party API calls (Average: [Count]): $[Cost]
*   *Variable Total*: $[Total] per transaction

### 3. Margin Projection
*   Target Price Tier: $[Pricing]/mo
*   Average Transactions/Tenant/mo: [Count]
*   *Projected Gross Margin*: [Percentage]%
```

---

## 5. Scoring & Decision Gates

### 5.1 Scorecard: Economic Viability Score (EVS)
Evaluate the economic model on a 1-5 scale:

| Vector | Scoring Criteria | Score (1-5) |
|---|---|---|
| **Gross Margin** | 1: Margins < 50%. 5: Margins > 85% at scale. | |
| **LTV / CAC Ratio** | 1: Ratio < 1.5x. 5: Projected Ratio > 3.0x. | |
| **Payback Period** | 1: > 18 months. 5: < 6 months payback. | |
| **Infrastructure Overhead** | 1: Base cost > $2K/mo. 5: Base cost < $200/mo. | |

### 5.2 Decision Gate
*   **Exit Criteria**: Economic Viability Score **≥ 15 / 20**, with no single vector scoring below 3.
*   **Pass**: Proceed to **Stage 8: Legal & Compliance Research**.
*   **Fail**: Adjust pricing structure or optimize system architecture to reduce compute/API costs.
