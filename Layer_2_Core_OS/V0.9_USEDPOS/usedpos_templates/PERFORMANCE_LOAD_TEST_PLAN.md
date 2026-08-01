# Performance and Load Test Plan
**Document ID:** VENUS-STD-065
**Version:** 1.0.0
**Status:** Approved
**Effective Date:** 2026-06-26

## 1. Objectives and KPIs
The performance testing strategy ensures the system remains responsive under extreme usage scenarios.

| Metric | Target | Failure Condition |
| :--- | :--- | :--- |
| **Throughput** | 1000 requests per second (RPS) | < 800 RPS |
| **95th Percentile Latency (p95)**| < 200 ms | >= 300 ms |
| **99th Percentile Latency (p99)**| < 500 ms | >= 800 ms |
| **Error Rate** | < 0.1% | >= 1.0% |

## 2. Load Profile Strategy
1. **Smoke Test:** Validate baseline configuration (10 RPS, 2 minutes).
2. **Stress Test:** Double standard usage to locate service failure limits (2000 RPS, 30 minutes).
3. **Soak / Endurance Test:** Run sustained load (1000 RPS, 12 hours) to verify memory leak occurrences.

## 3. B-Tree Index Database Sizing Estimations
Before executing load tests, database disk growth should be estimated. A B-Tree index has size $S_{\text{index}}$ calculated by:

$$S_{\text{index}} \approx N \times (S_{\text{key}} + S_{\text{pointer}}) \times \frac{1}{\text{Fill Factor}}$$

Where:
- $N$ is the number of rows expected ($10,000,000$).
- $S_{\text{key}}$ is the key field size ($32$ bytes for UUID).
- $S_{\text{pointer}}$ is the database disk pointer size ($8$ bytes).
- $\text{Fill Factor}$ is the page node fill efficiency ($0.7$ for typical index write usage).

$$S_{\text{index}} \approx 10,000,000 \times (32 + 8) \times 1.43 = 572,000,000\text{ bytes} \approx 572\text{ MB}$$

Multiply this calculations for every index to ensure IOPS limit margins.

## 4. load Test Script Specification (k6)
```javascript
import http from 'k6/http';
import { sleep, check } from 'k6';

export const options = {
  stages: [
    { duration: '2m', target: 200 }, // ramp-up to 200 virtual users (VUs)
    { duration: '5m', target: 200 }, // stay at 200 VUs
    { duration: '2m', target: 0 },   // scale down to 0 VUs
  ],
  thresholds: {
    http_req_duration: ['p(95)<200', 'p(99)<500'],
    http_req_failed: ['rate<0.001'],
  },
};

export default function () {
  const url = 'https://api-perf.venus.internal/v1/orders';
  const payload = JSON.stringify({
    productId: 'prod_9091',
    quantity: 2
  });
  const params = {
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer test-perf-token',
    },
  };

  const res = http.post(url, payload, params);
  
  check(res, {
    'status is 201': (r) => r.status === 201,
    'transaction content verified': (r) => r.json().hasOwnProperty('id'),
  });

  sleep(1);
}
```

## 5. Cross-References
- [Test Plan Strategy](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usedpos_templates/TEST_PLAN_STRATEGY.md)
- [Chaos Engineering Specification](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usedpos_templates/CHAOS_ENGINEERING_STEADY_STATE.md)
