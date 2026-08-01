# PART 15 — Message Brokers
## V0.9 USEDPOS | Universal Software Engineering, Delivery & Production Operating System

---

## 1. Purpose

Message Brokers are the infrastructure backbone of event-driven systems. They provide durable, scalable, ordered message delivery between producers and consumers. This part defines broker selection criteria, configuration standards, topic design, consumer group patterns, and operational requirements.

---

## 2. Broker Selection Matrix

| Broker | Throughput | Ordering | Retention | Best For |
|---|---|---|---|---|
| **Apache Kafka** | Millions/sec | Per-partition | Days to forever | Event streaming, audit logs, replay |
| **AWS SQS/SNS** | Thousands/sec | FIFO option | Up to 14 days | Simple queuing, AWS-native workloads |
| **RabbitMQ** | Hundreds K/sec | Per-queue | Until consumed | Complex routing, work queues, priorities |
| **Google Pub/Sub** | Millions/sec | No guarantee | 7 days default | GCP-native, global fan-out |
| **NATS JetStream** | Millions/sec | Per-subject | Configurable | Low-latency, IoT, edge |
| **Azure Service Bus** | Thousands/sec | Session support | Up to 14 days | Azure-native enterprise workloads |

**VENUS Default**: Apache Kafka for high-throughput event streaming and audit trails. RabbitMQ for task queues with complex routing.

---

## 3. Kafka Architecture Standards

### 3.1 Topic Design
```
Naming: {domain}.{entity}.{event-type}.v{version}

Examples:
  orders.order.placed.v1
  billing.payment.failed.v1
  inventory.stock.reserved.v2
  users.user.registered.v1

Rules:
  - Never use generic topics (events, messages)
  - One topic per event type per domain
  - Version topics when schema breaks backward compatibility
  - Use dot notation for hierarchy
```

### 3.2 Partition Count Guidelines
| Throughput | Partitions |
|---|---|
| < 10K events/sec | 6 partitions |
| 10K–100K events/sec | 12–24 partitions |
| 100K–1M events/sec | 48–96 partitions |
| > 1M events/sec | Custom sizing required |

**Rule**: More partitions = more parallelism but more overhead. Never over-partition.

### 3.3 Replication Factor
| Environment | Replication Factor |
|---|---|
| Development | 1 |
| Staging | 2 |
| Production | 3 (minimum) |

### 3.4 Retention Policy
| Topic Type | Retention |
|---|---|
| Business events (orders, payments) | 90 days |
| Audit log events | 7 years |
| Analytics events | 30 days |
| Ephemeral commands | 24 hours |

### 3.5 Kafka Configuration Standards
```properties
# Producer settings
acks=all                    # All replicas must acknowledge
enable.idempotence=true     # Exactly-once producer semantics
max.in.flight.requests.per.connection=5
compression.type=snappy     # Compress for network efficiency
batch.size=65536            # 64KB batch
linger.ms=5                 # Wait 5ms to accumulate batch

# Consumer settings
enable.auto.commit=false    # Manual offset commit (explicit control)
isolation.level=read_committed
max.poll.records=500
auto.offset.reset=earliest  # New consumer groups start from beginning
```

---

## 4. Consumer Group Patterns

### 4.1 Competing Consumers (Work Queue)
Multiple instances of the same service share work. Each message processed by exactly one instance.

```
Topic: orders.order.placed.v1  [6 partitions]
Consumer Group: order-fulfillment-service

Instance 1: partitions [0, 1]
Instance 2: partitions [2, 3]
Instance 3: partitions [4, 5]
```

### 4.2 Fan-Out (Pub/Sub)
Multiple independent services each consume all messages.

```
Topic: orders.order.placed.v1
Consumer Group A: notification-service    (sends confirmation email)
Consumer Group B: analytics-service       (records business metric)
Consumer Group C: inventory-service       (reserves stock)
```

---

## 5. Dead Letter Queue (DLQ) Pattern

All consumers must implement DLQ handling:

```
Main Topic: orders.order.placed.v1
     ↓ (processing fails after N retries)
Retry Topic: orders.order.placed.v1.retry-1
     ↓ (still fails)
Retry Topic: orders.order.placed.v1.retry-2
     ↓ (still fails)
DLQ:         orders.order.placed.v1.dlq

DLQ Policy:
  - Retain for 30 days
  - Alert on any DLQ message arrival
  - Runbook for DLQ investigation linked in monitoring
  - Manual replay tooling available
```

---

## 6. Idempotent Consumer Standard

Every consumer must handle duplicate delivery:

```typescript
async function handleOrderPlaced(event: OrderPlacedEvent): Promise<void> {
  // Idempotency check
  const alreadyProcessed = await processedEventStore.exists(event.eventId)
  if (alreadyProcessed) {
    logger.info({ eventId: event.eventId }, 'Duplicate event skipped')
    return
  }

  // Process event
  await processOrder(event)

  // Mark as processed
  await processedEventStore.markProcessed(event.eventId)
}
```

---

## 7. RabbitMQ Standards (Task Queues)

```
Exchange Types:
  direct:  Route by exact routing key
  topic:   Route by pattern (orders.*)
  fanout:  Broadcast to all bound queues
  headers: Route by message headers

Queue Configuration:
  durable: true          # Survive broker restart
  x-dead-letter-exchange # DLQ routing
  x-message-ttl          # Message expiry
  x-max-length           # Queue depth limit (circuit breaker)
  prefetch: 10           # Consumer prefetch (backpressure)
```

---

## 8. Broker Observability

```
Kafka Metrics (per topic/partition):
  kafka.consumer.lag                (alert > 10K messages)
  kafka.producer.request.rate
  kafka.consumer.fetch.rate
  kafka.network.io.rate

RabbitMQ Metrics (per queue):
  rabbitmq.queue.messages.ready     (alert > 1000)
  rabbitmq.queue.consumers
  rabbitmq.queue.message.publish_rate
  rabbitmq.queue.message.ack_rate
```
