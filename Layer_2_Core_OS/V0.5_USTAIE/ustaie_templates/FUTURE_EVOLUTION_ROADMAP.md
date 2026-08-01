# Template: Future Evolution Roadmap

## 1. Document Control
*   **Project Name**: [Project Name]
*   **Roadmap ID**: EVL-[UUID]

---

## 2. 5-Year Scaling Timeline
*Plan the architectural migrations required as system utilization scales.*

```
[Year 1: Modular Monolith] ──► [Year 3: Microservices Split] ──► [Year 5: Cell Architecture]
  (SQLite -> Postgres)             (Kafka / RabbitMQ)               (Multi-region Nodes)
```

---

## 3. Scaling Triggers & Migrations

| Scale Trigger Point | Target Migration | Expected Architecture Impact |
|---|---|---|
| **DB size > 10GB** | Migrate from SQLite to PostgreSQL | Introduces network query latency (+2ms). |
| **Outreach Queue > 100K/day**| Migrate worker pool to AWS SQS queue | Decouples api-gateway thread loops from worker crashes. |
| **Tenant count > 1,000** | Implement Cell partitioning | Controls failure blast radius; increases deployment cost. |
