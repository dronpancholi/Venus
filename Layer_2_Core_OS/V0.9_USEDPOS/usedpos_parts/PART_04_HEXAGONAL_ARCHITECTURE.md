# PART 04 — Hexagonal Architecture (Ports & Adapters)
## V0.9 USEDPOS | Universal Software Engineering, Delivery & Production Operating System

---

## 1. Purpose

Hexagonal Architecture — also known as Ports & Adapters — is the primary structural pattern for all application-layer systems built under VENUS. It enforces a strict separation between domain logic and infrastructure concerns, making systems independently testable, technology-agnostic, and resilient to infrastructure change.

---

## 2. Architecture Overview

```
                    ┌─────────────────────────────────────────┐
                    │              DRIVING SIDE                │
                    │   (What initiates interaction)           │
                    │  REST API | CLI | GraphQL | Event | gRPC │
                    └──────────────┬──────────────────────────┘
                                   │  (Primary Adapters)
                                   ▼
                    ┌─────────────────────────────────────────┐
                    │           PRIMARY PORTS                  │
                    │  (Interfaces defined by the application) │
                    └──────────────┬──────────────────────────┘
                                   │
                    ┌──────────────▼──────────────────────────┐
                    │         APPLICATION CORE                 │
                    │                                          │
                    │  ┌─────────────────────────────────┐    │
                    │  │       DOMAIN MODEL               │    │
                    │  │  Entities │ Value Objects        │    │
                    │  │  Aggregates │ Domain Services    │    │
                    │  │  Domain Events │ Specifications  │    │
                    │  └─────────────────────────────────┘    │
                    │                                          │
                    │  ┌─────────────────────────────────┐    │
                    │  │     APPLICATION SERVICES         │    │
                    │  │  Use Cases │ Command Handlers    │    │
                    │  │  Query Handlers │ Event Handlers │    │
                    │  └─────────────────────────────────┘    │
                    └──────────────┬──────────────────────────┘
                                   │
                    ┌──────────────▼──────────────────────────┐
                    │          SECONDARY PORTS                 │
                    │  (Interfaces defined by the application) │
                    └──────────────┬──────────────────────────┘
                                   │  (Secondary Adapters)
                                   ▼
                    ┌─────────────────────────────────────────┐
                    │             DRIVEN SIDE                  │
                    │  Database │ Cache │ Queue │ Email │ S3   │
                    └─────────────────────────────────────────┘
```

---

## 3. The Three Layers

### 3.1 Domain Layer (Core)
The purest layer. Contains zero infrastructure dependencies. Has no knowledge of HTTP, databases, queues, or external services.

**Contents**:
- Entities and Aggregates
- Value Objects
- Domain Events
- Domain Services
- Repository Interfaces (Ports)
- Domain Exceptions

**Dependency rule**: Zero outward dependencies. Nothing in the domain layer imports from application or infrastructure.

### 3.2 Application Layer
Orchestrates domain objects to fulfill use cases. Defines the primary ports (inbound) and secondary ports (outbound).

**Contents**:
- Application Services / Use Cases
- Command and Query objects (CQRS)
- Command Handlers
- Query Handlers
- Event Handlers
- DTO definitions
- Port interfaces (for external dependencies)

**Dependency rule**: Only depends on the domain layer. Never imports from infrastructure.

### 3.3 Infrastructure Layer
Implements the ports defined by the application and domain layers. Contains all technology-specific code.

**Contents**:
- Repository implementations (PostgreSQL, MongoDB, Redis)
- HTTP Controllers (REST, GraphQL, gRPC)
- Message queue producers and consumers
- Email / SMS adapters
- External API clients
- File storage adapters
- Authentication middleware

**Dependency rule**: Depends on application and domain layers. Never the other way around.

---

## 4. Port Definitions

### 4.1 Primary Ports (Inbound)
Interfaces that the application exposes for driving adapters to call.

```typescript
// Primary Port — defined in Application Layer
interface CreateOrderUseCase {
  execute(command: CreateOrderCommand): Promise<CreateOrderResult>
}

interface GetOrderQuery {
  execute(query: GetOrderByIdQuery): Promise<OrderDTO | null>
}
```

### 4.2 Secondary Ports (Outbound)
Interfaces that the application defines for infrastructure adapters to implement.

```typescript
// Secondary Port — defined in Domain/Application Layer
interface OrderRepository {
  findById(id: OrderId): Promise<Order | null>
  save(order: Order): Promise<void>
  findByCustomer(customerId: CustomerId): Promise<Order[]>
}

interface EmailService {
  sendOrderConfirmation(to: EmailAddress, order: Order): Promise<void>
}

interface EventPublisher {
  publish(event: DomainEvent): Promise<void>
}
```

---

## 5. Adapter Implementation Pattern

```typescript
// Infrastructure Adapter implementing Secondary Port
class PostgresOrderRepository implements OrderRepository {
  constructor(private readonly db: DatabaseConnection) {}

  async findById(id: OrderId): Promise<Order | null> {
    const row = await this.db.query('SELECT * FROM orders WHERE id = $1', [id.value])
    if (!row) return null
    return OrderMapper.toDomain(row)
  }

  async save(order: Order): Promise<void> {
    const data = OrderMapper.toPersistence(order)
    await this.db.upsert('orders', data)
    // Publish domain events
    for (const event of order.domainEvents) {
      await this.eventPublisher.publish(event)
    }
    order.clearDomainEvents()
  }
}
```

---

## 6. Dependency Injection Container

All adapters are wired to ports via a DI container at the composition root. The composition root is the only place where concrete implementations are referenced.

```typescript
// Composition Root — Infrastructure Layer
container.bind<OrderRepository>('OrderRepository').to(PostgresOrderRepository)
container.bind<EmailService>('EmailService').to(SendGridEmailService)
container.bind<EventPublisher>('EventPublisher').to(KafkaEventPublisher)
container.bind<CreateOrderUseCase>('CreateOrderUseCase').to(CreateOrderService)
```

---

## 7. Testing Strategy in Hexagonal Architecture

| Test Type | What is tested | Infrastructure |
|---|---|---|
| **Unit Tests** | Domain layer, Application layer | In-memory fakes / mocks for ports |
| **Integration Tests** | Infrastructure adapters | Real database (test container) |
| **Contract Tests** | Port/Adapter compatibility | Consumer-driven contract tests |
| **E2E Tests** | Full system | Deployed system |

**Key benefit**: The entire domain and application layer can be tested without any infrastructure running.

---

## 8 Hexagonal Architecture Compliance Checklist

- [ ] Domain layer has zero infrastructure imports
- [ ] Application layer has zero infrastructure imports
- [ ] All external dependencies accessed through interfaces (ports)
- [ ] Adapters implement ports — never the other way
- [ ] Composition root is the sole location where implementations are bound to interfaces
- [ ] All use cases are unit-testable with in-memory fakes
- [ ] No HTTP/database/queue-specific code in domain or application layers
