# PART 14 — Event Driven Systems
## V0.9 USEDPOS | Universal Software Engineering, Delivery & Production Operating System

---

## 1. Purpose

Event Driven Systems defines the architectural patterns, event design standards, ordering guarantees, consistency models, delivery semantics, and operational requirements for all asynchronous and event-driven capabilities within VENUS. Events are the lifeblood of decoupled, scalable, and resilient distributed systems.

---

## 2. Why Event-Driven Architecture

Traditional request-response architectures create temporal and spatial coupling. Service A must be available, reachable, and responsive for Service B to function. Event-Driven Architecture (EDA) inverts this relationship:

```
Tight Coupling:  Service A calls Service B synchronously
                 → A fails if B is down
                 → A is slow if B is slow
                 → A must know B's API

Loose Coupling:  Service A emits OrderPlaced event
                 → A doesn't know who consumes it
                 → A succeeds even if consumers are offline
                 → New consumers can be added without modifying A
```

---

## 3. Event Types

### 3.1 Domain Events
Represent facts about business state changes within a bounded context.

```typescript
interface DomainEvent {
  eventId: string;         // UUID
  eventType: string;       // PascalCase past tense: OrderPlaced
  occurredAt: string;      // ISO-8601
  aggregateId: string;     // The aggregate that changed
  aggregateType: string;   // The type: Order, User, Payment
  version: number;         // Schema version
  payload: unknown;        // Event-specific data
}
```

### 3.2 Integration Events
Domain events transformed for cross-bounded-context communication. Published to the event bus after successful transaction commit.

```typescript
interface IntegrationEvent extends DomainEvent {
  sourceService: string;   // Originating service
  correlationId: string;   // Trace correlation
  causationId: string;     // ID of the event that caused this event
}
```

### 3.3 Command Events
Instructions to perform an operation (usually internal to a service or saga).

```typescript
interface CommandEvent {
  commandId: string;
  commandType: string;  // Imperative: ProcessPayment, SendEmail
  issuedAt: string;
  payload: unknown;
}
```

---

## 4. Event Design Standards

### 4.1 Event Naming
```
Format: {Noun}{PastTenseVerb}

Examples:
  OrderPlaced
  PaymentFailed
  UserRegistered
  InventoryReserved
  ShipmentDispatched
  InvoiceGenerated
```

### 4.2 Event Schema Standards
- Events are **immutable** once published
- Events must be **self-describing** (contain all needed data, not just IDs)
- Events must be **versioned** (schema version field)
- Events must be **idempotent** to process (consumers handle duplicates)
- Events must include **correlation and causation IDs** for tracing

### 4.3 Fat vs Thin Events
| Type | Contains | Best For |
|---|---|---|
| **Fat Event** | Full entity state | New consumers that need full context |
| **Thin Event** | Just IDs + type | When consumers fetch data they need |
| **VENUS Default** | Include key fields + ID for fetch | Balance between coupling and convenience |

---

## 5. Delivery Semantics

| Guarantee | Description | Use Case |
|---|---|---|
| **At-most-once** | Event may be lost, never duplicated | Metrics, analytics (loss acceptable) |
| **At-least-once** | Event guaranteed delivered, may duplicate | Business events (idempotent consumers) |
| **Exactly-once** | Delivered exactly once | Financial transactions (expensive) |

**VENUS Default**: At-least-once with idempotent consumers.

---

## 6. Event Ordering

### 6.1 Ordering Guarantees

| Level | Guarantee |
|---|---|
| **Global ordering** | All events in strict sequence — impractical at scale |
| **Partition ordering** | Events ordered per partition key — VENUS standard |
| **No ordering** | Events unordered — only for idempotent, commutative operations |

### 6.2 Partition Key Strategy
```
Orders domain:     partition_key = orderId   (all events for an order ordered)
Users domain:      partition_key = userId    (all events for a user ordered)
Payments domain:   partition_key = paymentId
```

---

## 7. Saga Pattern (Distributed Transactions)

When a business operation spans multiple services, use the Saga pattern:

### 7.1 Choreography-Based Saga (No central coordinator)
```
Service A: OrderPlaced →
Service B: InventoryReserved →
Service C: PaymentProcessed →
Service D: ShipmentScheduled

On failure:
Service C: PaymentFailed →
Service B: InventoryReleased →
Service A: OrderCancelled
```

### 7.2 Orchestration-Based Saga (Central coordinator)
```
Saga Orchestrator:
  1. → Command: ReserveInventory
  2. ← Event: InventoryReserved
  3. → Command: ProcessPayment
  4. ← Event: PaymentProcessed
  5. → Command: ScheduleShipment
  6. ← Event: ShipmentScheduled
  7. → Command: ConfirmOrder

On failure at step 4:
  5b. → Compensate: ReleaseInventory
  6b. → Compensate: CancelOrder
```

**VENUS Default**: Orchestration for complex sagas; choreography for simple linear flows.

---

## 8. Outbox Pattern (Transactional Event Publishing)

Guarantees that domain events are published if and only if the database transaction succeeds.

```sql
-- Outbox table
CREATE TABLE outbox_events (
  id          UUID        PRIMARY KEY,
  event_type  TEXT        NOT NULL,
  payload     JSONB       NOT NULL,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
  published_at TIMESTAMPTZ,
  retry_count  INT        NOT NULL DEFAULT 0
);

-- Application atomically writes to both tables in same transaction
BEGIN;
  UPDATE orders SET status = 'placed' WHERE id = $1;
  INSERT INTO outbox_events (id, event_type, payload) VALUES ($2, 'OrderPlaced', $3);
COMMIT;

-- Outbox relay process publishes events and marks them published
```

---

## 9. Event Schema Registry

All event schemas are registered in a central Schema Registry:
- Avro or JSON Schema format
- Compatibility modes: BACKWARD, FORWARD, or FULL
- Schema evolution: only additive changes allowed on stable schemas
- Consumers validate events against registered schema on receipt
