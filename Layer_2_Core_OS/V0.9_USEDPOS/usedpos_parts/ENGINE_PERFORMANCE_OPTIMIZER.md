# ENGINE — Performance Optimizer
## V0.9 USEDPOS | Universal Software Engineering, Delivery & Production Operating System

---

## Purpose
Analyzes production performance metrics, traces, and query plans to identify bottlenecks and generate concrete optimization recommendations with estimated impact. Targets SLO compliance at every scale tier.

---

## Input Sources
```
Required:
  - OpenTelemetry traces (distributed traces)
  - Application metrics (Prometheus / Datadog)
  - Database slow query logs
  - HTTP access logs with timing

Optional:
  - Heap profiling snapshots
  - CPU profiling flamegraphs
  - k6 / Gatling load test results
  - Current SLO targets and thresholds
```

---

## Analysis Framework

### Step 1: SLO Breach Identification
```
For each endpoint/operation:
  If p95 latency > SLO target:
    → Flag as optimization candidate
    → Trace breakdown analysis
    → Identify contributing phases

Phases analyzed:
  - Network ingress time
  - Authentication / middleware overhead
  - Application processing time
  - Database query time (N+1 detection)
  - External API call time
  - Serialization / deserialization
  - Network egress time
```

### Step 2: Database Query Analysis
```sql
-- Automatically executed against slow query log:

-- Find N+1 patterns
SELECT query, calls, mean_exec_time, stddev_exec_time, rows
FROM pg_stat_statements
WHERE query LIKE '%SELECT%FROM%orders%'
  AND calls > 100
ORDER BY total_exec_time DESC
LIMIT 20;

-- Find missing indexes
SELECT schemaname, tablename, attname, n_distinct, correlation
FROM pg_stats
WHERE tablename = '{table}' AND attname = '{frequently_queried_column}';

-- Check index usage
SELECT schemaname, tablename, indexname, idx_scan, idx_tup_read
FROM pg_stat_user_indexes
WHERE idx_scan = 0;  -- Unused indexes — remove these
```

### Step 3: Memory and CPU Profiling Analysis
- Parse heap snapshots for retention patterns
- Identify objects not being garbage collected
- Detect synchronous CPU-bound operations blocking event loop
- Find inefficient serialization (large JSON payloads)

---

## Optimization Recommendations Generated

### Database Optimizations
```
1. Add index on orders.customer_id (estimated 15x query speedup)
   Current: Seq Scan cost=0.00..45821.90
   After:   Index Scan cost=0.00..8.29

2. Replace N+1 query in OrderService.getWithItems():
   Current: 1 query + N queries (N=items per order, avg 8) = 9 queries
   Fix: Single JOIN or DataLoader batching
   Estimated improvement: 340ms → 45ms p95

3. Add connection pooling (PgBouncer):
   Current: 200 direct connections (PostgreSQL max_connections=300)
   Target: 5-20 pooled connections per service instance
   Estimated improvement: Eliminates connection overhead ~12ms/request
```

### Application Optimizations
```
4. Cache product catalog (TTL=300s):
   Current: 87 DB queries/sec for static catalog data
   Fix: Redis cache-aside, invalidate on product.updated event
   Estimated improvement: 200ms → 2ms for catalog reads

5. Async email sending (current: synchronous in request path):
   Current: Order creation p95 = 1.2s (includes email API call)
   Fix: Publish domain event, send email in background consumer
   Estimated improvement: 1.2s → 180ms order creation p95
```

---

## Performance Budget Enforcement
Every optimization recommendation includes:
- Before/after metric comparison
- Confidence level (based on profiling evidence)
- Implementation effort (hours)
- Risk level
- Rollback plan

---

## Continuous Monitoring
- Performance regression alerts fire within 5 minutes
- Weekly performance trend report
- Pre-deployment performance gate (p95 must not degrade > 10%)
