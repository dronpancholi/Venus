# Outbox Pattern Reconciliation
**Document ID:** VENUS-STD-045
**Version:** 1.0.0
**Status:** Approved
**Effective Date:** 2026-06-26

## 1. Outbox Database Schema
To guarantee at-least-once message delivery without distributed transactions, services utilize outbox patterns:

```sql
CREATE TABLE outbox_events (
    id UUID PRIMARY KEY,
    aggregate_type VARCHAR(255) NOT NULL,
    aggregate_id VARCHAR(255) NOT NULL,
    payload JSONB NOT NULL,
    status VARCHAR(20) DEFAULT 'PENDING' NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);
```

## 2. Reconciliation Engine
A background daemon queries pending events, publishes them to Kafka, and marks them as `PROCESSED`.

---

## 3. Reusable Checklist & Exit Criteria
*   [ ] Checked that outbox inserts execute in the same transactional boundary as business mutations.
*   [ ] Verified that daemon loops include deduplication safeguards.
*   [ ] Confirmed outbox tables prune processed rows regularly.
