# Template: Scalability Model

## 1. Document Control
*   **Project Name**: [Project Name]
*   **Target Scale**: [e.g., Tier 4 (100,000 users)]
*   **Scale Model ID**: SCA-[UUID]

---

## 2. Resource & Concurrency Projections

| Scale Tier | Concurrent Users | Projected Requests/sec | DB Connection Pool Required | Average CPU/RAM Budget |
|---|---|---|---|---|
| **Tier 1 (100)** | 10 | 5 | 5 | 0.5 CPU / 512MB RAM |
| **Tier 2 (1K)** | 100 | 50 | 10 | 1 CPU / 1GB RAM |
| **Tier 3 (10K)** | 1,000 | 500 | 25 | 4 CPU / 8GB RAM |
| **Tier 4 (100K)**| 10,000 | 5,000 | 100 | 16 CPU / 32GB RAM |

---

## 3. Scale Bottlenecks & Mitigations
*   **Database CPU Saturation**: Triggers when concurrent reads exceed 3,000. *Mitigation*: Add 2 read replicas.
*   **Worker Queue Congestion**: Triggers when queue lag > 1000 tasks. *Mitigation*: Enable horizontal auto-scaling on workers based on queue latency metrics.
