# Template: Performance Budget

## 1. Document Control
*   **Project Name**: [Project Name]
*   **Performance ID**: PERF-[UUID]

---

## 2. Resource & Latency Allocations

| System Component | CPU Allocation | Memory Ceiling | Max Latency Budget (p95) | Bandwidth Budget |
|---|---|---|---|---|
| **api-gateway** | 0.5 vCPU | 256 MB | 50 ms | 100 Mbps |
| **user-profile**| 1.0 vCPU | 512 MB | 20 ms | 50 Mbps |
| **crawler-worker**| 2.0 vCPU | 1024 MB | 5000 ms (Long task) | 500 Mbps |
| **database-node**| 4.0 vCPU | 8192 MB | 10 ms (Query execution) | 1000 Mbps |

---

## 3. Web UI Performance Budgets (Core Web Vitals)
*   **Largest Contentful Paint (LCP)**: <= 2.5 seconds.
*   **Interaction to Next Paint (INP)**: <= 200 milliseconds.
*   **Cumulative Layout Shift (CLS)**: <= 0.1.

---

## 4. Verification Check
*   [ ] Checked k6 stress tests latency output budgets.
*   [ ] Checked memory bounds inside docker files.
*   [ ] Lighthouse score automated audits pass.
