# Part 09 — Performance

## 1. Resource Allocations & Budgets
Performance models latency constraints, concurrency limits, database connection ceilings, cold start latency budgets, and resource allocation models (CPU, memory, storage).

---

## 2. Quantitative Performance Formulas

### 2.1 Amdahl's Law (Concurrency limits)
Projections must estimate maximum expected speedup from parallel execution:

\[S_{Latency}(s) = \frac{1}{(1 - p) + \frac{p}{s}}\]

Where:
*   \(p\): Proportion of program execution that can be parallelized.
*   \(s\): Speedup factor of the parallel components.

### 2.2 Little's Law (Concurrency capacity)
Enforce concurrent request limits to prevent buffer memory saturation:

\[L = \lambda \times W\]

Where:
*   \(L\): Average concurrent request count in queue.
*   \(\lambda\): Average request arrival rate.
*   \(W\): Average processing time per request.

---

## 3. Performance Budget Allocation
Assign resource limits prior to implementation:
*   **API Gateway**: Max latency 50ms | Memory limit 256MB.
*   **Worker Node**: Max CPU usage 80% | Memory limit 512MB.
*   **Database**: Query timeout 2000ms | Connection limit 100.

---

## 4. Performance Checklist
*   [ ] Solved Little's Law to verify system queue limits.
*   [ ] Checked database query timeouts.
*   [ ] Configured memory budgets on docker compose nodes.
*   [ ] Audited cold start profiles.
