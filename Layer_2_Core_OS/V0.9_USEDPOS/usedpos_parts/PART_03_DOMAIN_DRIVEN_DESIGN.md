# PART 03 — Domain Driven Design (DDD)
## V0.9 USEDPOS | Universal Software Engineering, Delivery & Production Operating System

---

## 1. Purpose

Domain Driven Design is the primary modelling methodology for all complex software systems built under VENUS. It ensures the software structure mirrors the business reality, enabling long-term maintainability, clear ownership boundaries, and precise language alignment between engineers and domain experts.

---

## 2. Strategic DDD

### 2.1 Ubiquitous Language
Every team must define and maintain a living glossary of domain terms. All code, documentation, conversations, and system designs use the same language. There is no translation layer between what the domain expert says and what the code implements.

**Rule**: If a term does not appear in the ubiquitous language, it does not appear in the codebase.

### 2.2 Bounded Contexts
A Bounded Context is an explicit boundary within which a domain model applies. The same concept may be modelled differently across bounded contexts.

| Bounded Context | Owns | Does NOT own |
|---|---|---|
| Order Management | Order lifecycle, fulfilment | Payment processing |
| Billing | Payment, invoicing | Order status |
| Identity | User credentials, sessions | User preferences |
| Notifications | Message delivery, templates | Business rules triggering notifications |

**Rule**: One team, one bounded context. Never let two teams own the same bounded context.

### 2.3 Context Map
The Context Map documents the relationships between bounded contexts. Relationships include:

- **Partnership**: Two contexts evolve together; changes are coordinated
- **Customer/Supplier**: Downstream team is customer; upstream team is supplier
- **Conformist**: Downstream adopts upstream model without negotiation
- **Anticorruption Layer (ACL)**: Downstream translates upstream model to protect its own
- **Open Host Service**: Upstream exposes a stable protocol for many downstreams
- **Published Language**: Shared, well-documented exchange format

---

## 3. Tactical DDD Building Blocks

### 3.1 Entities
Objects defined by their identity, not their attributes. An `Order` with ID `ORD-001` is the same order regardless of how its status changes.

```
Entity:
  - Has a unique identity (ID)
  - Mutable over time
  - Identity persists across state changes
  - Equality determined by ID, not attributes
```

### 3.2 Value Objects
Objects defined entirely by their attributes. Two `Money` objects with `amount: 100, currency: USD` are identical and interchangeable.

```
Value Object:
  - No identity
  - Immutable
  - Equality determined by all attributes
  - Examples: Money, Address, DateRange, EmailAddress
```

### 3.3 Aggregates
A cluster of domain objects treated as a single unit of consistency. Every aggregate has a root entity through which all external interactions must pass.

```
Aggregate Rules:
  1. Reference other aggregates only by ID
  2. Apply invariants within aggregate boundary only
  3. Emit domain events on state change
  4. One transaction per aggregate
  5. Size: as small as possible while maintaining invariants
```

### 3.4 Domain Events
Immutable records of something significant that happened in the domain. Domain events capture facts about the past.

```
Domain Event Structure:
  - eventId: UUID
  - eventType: string (past tense: OrderPlaced, PaymentFailed)
  - occurredAt: timestamp
  - aggregateId: string
  - payload: typed domain data
  - version: schema version
```

### 3.5 Domain Services
Stateless operations that don't naturally belong to an entity or value object.

```
Use Domain Services when:
  - The operation involves multiple aggregates
  - The concept is purely a behaviour with no natural home
  - The operation represents a domain process, not a data transformation
```

### 3.6 Repositories
Provide collection-like access to aggregates. Repositories abstract persistence concerns from the domain model.

```
Repository Interface (defined in Domain):
  find(id: AggregateId): Promise<Aggregate | null>
  findAll(specification: Specification): Promise<Aggregate[]>
  save(aggregate: Aggregate): Promise<void>
  delete(id: AggregateId): Promise<void>
```

### 3.7 Application Services
Orchestrate domain objects to fulfill use cases. They are thin coordinators — they load aggregates, invoke domain operations, persist state, and emit integration events.

---

## 4. DDD Anti-Patterns (Prohibited)

| Anti-Pattern | Description | Correct Approach |
|---|---|---|
| **Anemic Domain Model** | Domain objects are pure data containers; all logic in services | Move logic into entities and value objects |
| **Fat Service Layer** | Application services contain business logic | Business logic belongs in the domain |
| **Cross-Aggregate Transactions** | ACID transactions spanning multiple aggregates | Use eventual consistency and domain events |
| **Shared Database Anti-Pattern** | Multiple bounded contexts sharing a database schema | Each context owns its own schema/database |
| **Feature Envy** | A class that uses another class's data excessively | Move the behaviour to the class that owns the data |

---

## 5. DDD Modelling Checklist

Before finalizing any domain model, validate:

- [ ] Ubiquitous language documented and agreed with domain experts
- [ ] Bounded contexts identified and mapped
- [ ] Aggregates sized as small as possible while enforcing invariants
- [ ] All domain events identified and documented
- [ ] Repository interfaces defined in domain layer (not infrastructure)
- [ ] Context map relationships classified and documented
- [ ] Anticorruption layers in place for legacy/third-party integrations
