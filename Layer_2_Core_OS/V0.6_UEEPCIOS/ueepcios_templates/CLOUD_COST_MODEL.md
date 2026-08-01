# Template: Cloud Cost Model

## 1. Document Control
*   **Project Name**: [Project Name]
*   **Model ID**: CLD-[UUID]
*   **Target Scale**: [e.g., Tier 4 (100,000 users)]

---

## 2. Infrastructure Resource Budgets

| Service Component | Cloud Resource Type | Pricing Unit | Monthly Units | Projected Cost |
|---|---|---|---|---|
| **api-gateway** | AWS Fargate (0.5 vCPU) | $0.04048 / hr | 730 hours | $29.55 |
| **primary-db** | Amazon Aurora pg.r6g | $0.29000 / hr | 730 hours | $211.70 |
| **caching** | ElastiCache Redis cache | $0.06800 / hr | 730 hours | $49.64 |
| **data-egress** | AWS Network Bandwidth | $0.09000 / GB | 500 GB | $45.00 |
| **Total Cloud MIC** | | | | **$335.89** |

---

## 3. Scale-Up Financial Projections
*   *Month 12 Cloud Cost*: [$0.00 / month]
*   *Month 36 Cloud Cost*: [$0.00 / month]
*   *Autoscaling Cost Ceiling*: Enforce maximum budget cap alert of $1,000/mo.
