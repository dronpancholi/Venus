# PART 16 — Distributed Systems
## V0.9 USEDPOS | Universal Software Engineering, Delivery & Production Operating System

---

## 1. Purpose

Distributed Systems defines the fundamental principles, consistency models, consensus mechanisms, failure patterns, and resilience strategies that govern how networked services in VENUS behave under real-world conditions. Building distributed systems without understanding their theoretical foundations leads to data loss, corruption, and cascading failures.

---

## 2. Fundamental Laws

### 2.1 The CAP Theorem
A distributed system can guarantee at most two of three properties simultaneously:

| Property | Meaning |
|---|---|
| **Consistency (C)** | Every read receives the most recent write or an error |
| **Availability (A)** | Every request receives a response (not necessarily most recent) |
| **Partition Tolerance (P)** | System continues despite network partitions |

**Network partitions will occur in any real distributed system. Therefore P is always required.**

This means the practical choice is: **CP** (consistency over availability) or **AP** (availability over consistency).

| System | Choice | Examples |
|---|---|---|
| Financial transactions | CP | PostgreSQL, etcd, ZooKeeper |
| Social media feed | AP | Cassandra, DynamoDB, CouchDB |
| VENUS Default per domain | Context-dependent | Evaluate per business requirement |

### 2.2 The PACELC Theorem (Extension of CAP)
Even without a partition, there is a trade-off between latency and consistency:
- **Partition**: CP vs AP
- **Else (no partition)**: Lower Latency vs Higher Consistency

### 2.3 Fallacies of Distributed Computing
Engineers must never assume:
1. The network is reliable
2. Latency is zero
3. Bandwidth is infinite
4. The network is secure
5. Topology doesn't change
6. There is one administrator
7. Transport cost is zero
8. The network is homogeneous

---

## 3. Consistency Models

| Model | Guarantees | Example |
|---|---|---|
| **Linearizability** | Strongest: operations appear instantaneous and sequential | Distributed locks, leader election |
| **Sequential Consistency** | All operations appear in some sequential order, consistent across nodes | etcd, ZooKeeper |
| **Causal Consistency** | Causally related operations ordered; concurrent ops may diverge | Collaborative editors |
| **Eventual Consistency** | All replicas converge given no new updates | DNS, S3, DynamoDB default |
| **Read-your-writes** | You always read what you wrote | Session consistency, user profiles |

---

## 4. Resilience Patterns

### 4.1 Circuit Breaker
Prevents cascading failures by stopping calls to a failing dependency.

```
States:
  CLOSED  → All requests pass through (healthy)
  OPEN    → All requests fail fast (dependency failing)
  HALF-OPEN → Limited requests probe for recovery

Configuration:
  failure_threshold:    50% failure rate in last 60 seconds
  open_duration:        30 seconds (no calls allowed)
  half_open_probes:     5 requests before transitioning
  success_threshold:    3 consecutive successes → CLOSED
```

### 4.2 Retry with Exponential Backoff and Jitter
```
Attempt 1: Immediate
Attempt 2: base_delay * 2^1 + jitter = ~2s
Attempt 3: base_delay * 2^2 + jitter = ~4s
Attempt 4: base_delay * 2^3 + jitter = ~8s
Max attempts: 5
Max delay: 30 seconds
Jitter: Random 0–100% of calculated delay (prevents thundering herd)
```

### 4.3 Bulkhead Pattern
Isolate failures by separating resource pools. Failures in one pool don't exhaust shared resources.

```
Without Bulkhead: One slow endpoint exhausts all 20 thread pool slots
With Bulkhead:
  - Pool A (critical paths): 10 threads
  - Pool B (background): 5 threads
  - Pool C (reporting): 5 threads
  Failure in Pool B doesn't affect Pool A
```

### 4.4 Timeout Pattern
Every network call must have an explicit timeout. Default: never.

```
Service call timeouts:
  Database queries: 10s
  External API calls: 15s
  Message queue publish: 5s
  Cache operations: 200ms
  Internal service calls: 3s
```

### 4.5 Backpressure
Consumers signal producers to slow down when overwhelmed.

```
Implementations:
  - Queue depth limits (RabbitMQ x-max-length)
  - Consumer prefetch limits
  - Rate limiting on API ingress
  - Reactive Streams backpressure signals
```

---

## 5. Distributed Consensus

### 5.1 Leader Election
Required for: distributed locks, single-writer primary databases, task schedulers.

**Tools**: etcd (Raft consensus), ZooKeeper (ZAB protocol), Consul

### 5.2 Distributed Locking
```
Redis SETNX-based (Redlock for multi-node):
  1. Set lock with TTL: SET lock_key owner_id NX PX 30000
  2. Execute critical section
  3. Release lock: DEL lock_key (only if owner_id matches)

Requirements:
  - TTL must be shorter than SLA for the critical section
  - Lock owner must be unique per request
  - Fencing token prevents stale lock holder from writing
```

---

## 6. Data Replication Strategies

| Strategy | Description | Use Case |
|---|---|---|
| **Synchronous Replication** | Write confirmed only after all replicas ack | Financial data, strong consistency |
| **Asynchronous Replication** | Write confirmed at primary; replicas lag | High write throughput, eventual consistency |
| **Semi-Synchronous** | At least one replica must ack | Balance between durability and throughput |
| **Chain Replication** | Writes flow through chain; reads from tail | High throughput with strong consistency |

---

## 7. Distributed Observability Requirements

```
Every distributed operation must include:
  - Trace ID: Unique per user request, propagated across all services
  - Span ID: Unique per service operation within a trace
  - Parent Span ID: Links child spans to parent

Context propagation via:
  - W3C Trace Context headers (HTTP)
  - Kafka message headers (async)
  - gRPC metadata (gRPC)

Tools: OpenTelemetry (collector + SDK), Jaeger, Tempo, Datadog
```
