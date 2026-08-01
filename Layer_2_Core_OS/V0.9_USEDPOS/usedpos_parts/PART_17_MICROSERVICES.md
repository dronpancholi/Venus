# PART 17 — Microservices
## V0.9 USEDPOS | Universal Software Engineering, Delivery & Production Operating System

---

## 1. Purpose

Microservices defines when microservices are appropriate, how to decompose a system into services, how services communicate, how they are deployed, and what organizational structures are required to make microservices succeed. Microservices are not a default — they are a pattern that carries significant operational cost. This part establishes the evidence-based rules for their adoption.

---

## 2. When Microservices Are Appropriate

**Choose microservices when ALL of the following are true**:
- Multiple teams need to deploy independently
- Clear domain boundaries exist (from DDD analysis, Part 03)
- Team size > 15 engineers, or multiple autonomous teams
- Different services have fundamentally different scaling requirements
- Engineering organization can invest in platform/DevOps infrastructure
- The system has survived as a modular monolith first (Part 18)

**Do NOT choose microservices when**:
- < 5 engineers
- Bounded contexts are unclear
- No DevOps/platform team to support infrastructure
- Starting a new product (start with modular monolith)
- The team has never operated a distributed system

---

## 3. Service Decomposition Principles

### 3.1 Single Responsibility per Service
Each microservice is responsible for exactly one bounded context. It owns its data, its API, and its business rules.

```
CORRECT:
  order-service     → Manages order lifecycle
  payment-service   → Manages payment processing
  inventory-service → Manages stock levels
  notification-service → Manages all outbound communications

INCORRECT:
  user-order-payment-service → Too many responsibilities
```

### 3.2 Service Size Heuristics
- **Two-pizza rule**: A service team should be feedable by two pizzas (5–8 people)
- **Deployment frequency**: A service should be deployable independently at least weekly
- **Code size**: Not a meaningful metric — use business capability ownership instead

### 3.3 Strangler Fig Pattern (Migration from Monolith)
```
Step 1: Identify bounded context to extract
Step 2: Build new service alongside monolith
Step 3: Route traffic to new service gradually (feature flag / proxy)
Step 4: Deprecate monolith functionality once new service stable
Step 5: Remove code from monolith

Never: Big bang rewrite. Always: Incremental strangling.
```

---

## 4. Inter-Service Communication

### 4.1 Synchronous Communication (REST / gRPC)
Use when: A response is required in the same request cycle.

```
REST:  For external-facing APIs, mobile clients, cross-team contracts
gRPC:  For internal high-performance service-to-service calls

Rules:
  - Always set explicit timeouts
  - Implement circuit breakers (Part 16)
  - Retry only idempotent operations
  - Use service mesh for mTLS and retry policies
```

### 4.2 Asynchronous Communication (Events)
Use when: Decoupling is more important than immediacy.

```
Patterns:
  Event notification:    "Something happened" (minimal payload)
  Event-carried state:   "Something happened and here's the full new state"
  Event sourcing:        Events are the source of truth

Rules:
  - At-least-once delivery with idempotent consumers (Part 14)
  - Use Outbox Pattern for transactional publishing (Part 14)
  - Schema Registry for contract stability
```

---

## 5. Service Mesh

All VENUS microservice deployments use a service mesh (Istio or Linkerd) for:

| Capability | Implementation |
|---|---|
| **mTLS** | Automatic certificate rotation, encrypted service-to-service |
| **Load Balancing** | Round-robin, least connections, weighted |
| **Circuit Breaking** | Envoy proxy circuit breaker |
| **Retry Policies** | Automatic retry with backoff |
| **Observability** | Automatic metrics, traces, logs per service |
| **Traffic Management** | Canary, blue-green, header-based routing |

---

## 6. API Gateway

```
External Client → API Gateway → Internal Microservices

API Gateway Responsibilities:
  - Authentication & token validation
  - Rate limiting
  - Request routing
  - Protocol translation (REST → gRPC)
  - SSL termination
  - Request/response logging
  - API versioning
  - IP allowlisting / DDoS protection

Tools: Kong, AWS API Gateway, Traefik, Nginx Plus
```

---

## 7. Service Contract Standards

Every microservice must publish:
- **OpenAPI spec** or **gRPC proto** for its API
- **AsyncAPI spec** for events it produces
- **Changelog** with semantic versioning
- **Consumer-driven contracts** for critical integrations (Pact)
- **SLA**: Latency (p95, p99), availability (e.g., 99.9%)

---

## 8. Data Ownership

```
RULE: Each microservice owns its database exclusively.
      No other service can access it directly.
      Data sharing happens through API or events only.

Order Service:      orders_db (PostgreSQL)
Payment Service:    payments_db (PostgreSQL)
Inventory Service:  inventory_db (PostgreSQL + Redis)
Notification Service: notifications_db (MongoDB)

FORBIDDEN:
  Payment Service connects to orders_db
  Any service shares tables with another service
```

---

## 9. Microservice Production Checklist

- [ ] Service has its own CI/CD pipeline
- [ ] Service has its own Kubernetes namespace and RBAC
- [ ] Service owns its own database schema
- [ ] Health check endpoints implemented
- [ ] Circuit breakers configured for all upstream dependencies
- [ ] OpenAPI spec published and versioned
- [ ] Runbook documented and linked in service README
- [ ] SLO defined (availability, latency)
- [ ] Distributed tracing instrumented
- [ ] Chaos engineering tests run in staging
