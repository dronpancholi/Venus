# Template: Cost Model

## 1. Document Context
*   **Project Name**: [Project Name]
*   **Target SOM Tenant Count**: [e.g., 100 Tenants]
*   **Date Compiled**: [Date]

---

## 2. Infrastructure Cost Projection (Bottom-Up)

### 2.1 Fixed Database & Compute Cost

| Resource | Service / Provider | Monthly Base | Notes |
|---|---|---|---|
| PostgreSQL DB | AWS Aurora Serverless | $[Cost] | Enforces multi-tenant RLS |
| Cache DB | Redis Cloud | $[Cost] | Idempotency and rate limits |
| Orchestration | Temporal Cloud | $[Cost] | Durable execution logs |
| Application Host | AWS ECS (Fargate) | $[Cost] | Horizontal scale backend |
| Frontend Host | Vercel Enterprise | $[Cost] | Web UI routing |
| **Fixed Total** | | **$[Total]** | |

### 2.2 Variable Cost per User Session (Inference & APIs)
*   *Inference Tokens*: $[Cost] per transaction
*   *Third-Party APIs*: $[Cost] per transaction (Ahrefs, Hunter, DataForSEO)
*   *Network Data Out*: $[Cost] per GB
*   **Variable Cost Total**: **$[Total]** per transaction

---

## 3. Unit Economics & Operating Margin

```
╔══════════════════════════════════════════════════════════════╗
║               MARGIN PROJECTION AT SCALE                     ║
╠══════════════════════════════════════════════════════════════╣
║  TARGET SUBSCRIPTION PRICE:  $[Price]/mo                     ║
║  AVERAGE VARIABLE COST:      $[Cost]/mo                      ║
║  AVERAGE FIXED ALLOCATION:   $[Cost]/mo                      ║
║                                                              ║
║  EXPECTED OPERATING MARGIN:   [Percentage]% (Target: >80%)   ║
╚══════════════════════════════════════════════════════════════╝
```
*Break-Even Tenant Count*: [Count] tenants required to cover all fixed costs.
