# ENGINE — Cost Optimizer
## V0.9 USEDPOS | Universal Software Engineering, Delivery & Production Operating System

---

## Purpose
Analyzes cloud infrastructure costs across compute, storage, network, and managed services. Identifies waste, right-sizing opportunities, commitment discount opportunities, and architectural changes that reduce cost while maintaining or improving performance and reliability.

---

## Cost Analysis Framework

### Phase 1: Cost Inventory
```
Sources ingested:
  - AWS Cost Explorer / GCP Billing / Azure Cost Management
  - Kubernetes resource utilization (requests vs actual)
  - Database sizing vs utilization
  - Network egress analysis
  - Idle and unused resource detection

Breakdown by:
  - Service / team
  - Environment (dev/staging/prod)
  - Resource type (compute, storage, network, managed services)
  - Region
  - Tag (cost allocation tags)
```

### Phase 2: Waste Detection

#### Idle Resources
```
Criteria:
  EC2 / VM:        CPU < 5% for 7 consecutive days
  RDS:             Connections = 0 for 7 days
  Load Balancer:   0 healthy targets for 24 hours
  ElastiCache:     Hit rate > 0% but hits = 0 for 7 days
  S3 Bucket:       0 GET requests in 30 days
  EBS Volume:      Not attached to running instance

Action: Generate report → auto-tag for cleanup → delete after 14-day notice
```

#### Oversized Resources (Right-Sizing)
```
Compute:
  Actual CPU p95 < 20% of requested → Downsize recommendation
  Actual Memory p95 < 40% of requested → Downsize recommendation

Database:
  CPU p95 < 20% → Smaller instance class
  IOPS p95 < 30% of provisioned → Reduce provisioned IOPS
  Storage utilization < 50% → Reduce allocated storage

Estimated savings per recommendation calculated.
```

#### Non-Production Environment Waste
```
Dev / Staging:
  Schedule shutdown: Mon-Fri 20:00 → 08:00, weekends off
  Estimated saving: 70% reduction in non-prod compute costs

Implementation:
  - AWS Instance Scheduler / Lambda cron
  - Kubernetes Cluster Autoscaler (scale to 0 on nights/weekends)
  - Database: Stop RDS instances outside business hours
```

### Phase 3: Commitment Discount Analysis
```
Reserved Instances / Savings Plans:
  Analyze 90-day usage history
  Identify stable baseline workloads
  Generate 1-year and 3-year commitment recommendations
  Calculate break-even point and projected savings

Spot / Preemptible Instances:
  Identify stateless workloads suitable for spot
  Calculate cost reduction (60-90% savings)
  Generate fault-tolerant spot configuration
```

### Phase 4: Architecture Cost Impact
```
Patterns that reduce cost:
  1. CDN for static assets (reduce origin server load)
  2. Read replicas for analytics (reduce primary DB load)
  3. Cache layer for repeated queries (reduce DB costs)
  4. Event-driven async (reduce synchronous waiting)
  5. Data tiering (S3 Intelligent Tiering for old data)
  6. Multi-tenant architecture (shared resources per customer)
  7. Serverless for sporadic workloads (Lambda/Cloud Functions)
```

---

## Cost Optimization Report

```markdown
# Cloud Cost Optimization Report
Period: {month} | Total Spend: ${total}
Potential Monthly Savings: ${savings} ({percent}%)

## Quick Wins (< 1 day effort, immediate savings)
1. 12 idle EC2 instances → Terminate → Save $2,400/month
2. 3 unattached EBS volumes → Delete → Save $180/month
3. Dev environment scheduling → Save $1,800/month

## Right-Sizing (1 week effort)
1. order-service: c5.2xlarge → c5.large (CPU p95: 12%) → Save $580/month
2. RDS db.r5.2xlarge → db.r5.large (CPU p95: 8%) → Save $920/month

## Commitment Discounts (1 day effort, annual commitment)
1. EC2 Savings Plan (1yr): Save 38% on compute → $14,200/year

## Architecture Changes (2-4 weeks effort)
1. Add Redis cache for catalog API: Reduce RDS read IOPS 60% → Save $1,200/month
```

---

## FinOps Governance
- Monthly cost review with engineering managers
- Cost allocated by service team via tagging policy
- Budget alerts at 80% and 100% of monthly budget
- Cost anomaly detection (> 20% day-over-day increase alerts immediately)
- Engineering awareness: cost per service shown in engineering dashboard
