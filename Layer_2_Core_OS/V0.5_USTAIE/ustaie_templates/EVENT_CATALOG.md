# Template: Event Catalog

## 1. Document Control
*   **Project Name**: [Project Name]
*   **Event Log ID**: EVT-[UUID]

---

## 2. Event Registry
*Track all events, topics, and message formats in the distributed system.*

| Topic Name | Producer Service | Consumer Service | Message Format Schema |
|---|---|---|---|
| `user.created` | user-profile | payment-worker | `{ "user_id": "UUID", "email": "string" }` |
| `payment.processed` | payment-worker | user-profile | `{ "transaction_id": "UUID", "status": "string" }` |
| `campaign.started` | api-gateway | crawler-worker | `{ "campaign_id": "UUID", "urls": [] }` |

---

## 3. Serialization & Broker Details
*   **Broker Middleware**: Apache Kafka / AWS SQS.
*   **Serialization Type**: JSON / Avro Schemas.
*   **Delivery Guarantees**: At least once delivery; consumers must enforce idempotence.

---

## 4. Failure Queues & DLQs
*   **Dead Letter Queue (DLQ)**: `user.created.dlq`
*   *Retry Policy*: Exponential backoff (initial delay 1s, backoff factor 2.0, max attempts 5).
