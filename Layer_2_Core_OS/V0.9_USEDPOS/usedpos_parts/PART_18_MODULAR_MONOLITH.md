# PART 18 — Modular Monolith
## V0.9 USEDPOS | Universal Software Engineering, Delivery & Production Operating System

---

## 1. Purpose

The Modular Monolith is VENUS's default starting architecture for new products. It combines the simplicity of deployment and debugging inherent to a single deployable unit with the architectural discipline of clear module boundaries that enable future decomposition into microservices without a rewrite.

---

## 2. The Modular Monolith Philosophy

The distributed systems community has historically presented a false dichotomy: monolith (bad, unscalable) vs microservices (good, scalable). The reality:

```
Big Ball of Mud Monolith     — Unstructured, unmaintainable. Avoid.
Modular Monolith             — Structured, maintainable, deployable. VENUS Default.
Premature Microservices      — Distributed complexity without the scale. Avoid.
Microservices at Scale       — Right for large organizations. Evolve into, not start with.
```

The Modular Monolith preserves module boundaries in code while deploying as one unit. When the time comes to split, the split is trivial — the seams are already clean.

---

## 3. Module Structure

### 3.1 Directory Layout
```
src/
├── core/                   # Cross-cutting concerns
│   ├── errors/
│   ├── events/
│   ├── middleware/
│   └── database/
├── modules/
│   ├── orders/             # Order Management Module
│   │   ├── domain/
│   │   ├── application/
│   │   ├── infrastructure/
│   │   └── index.ts        # Public API — only export allowed
│   ├── billing/            # Billing Module
│   │   ├── domain/
│   │   ├── application/
│   │   ├── infrastructure/
│   │   └── index.ts
│   ├── identity/           # Identity Module
│   │   ├── domain/
│   │   ├── application/
│   │   ├── infrastructure/
│   │   └── index.ts
│   └── notifications/      # Notifications Module
│       ├── domain/
│       ├── application/
│       ├── infrastructure/
│       └── index.ts
└── app/                    # Application bootstrap, routing
```

### 3.2 Module Boundary Rules
```
PERMITTED:
  orders module imports from: orders/domain, orders/application, orders/infrastructure, core/
  orders module imports events from: billing module (via event bus, not direct import)

PROHIBITED:
  orders module directly imports billing/domain/entities/Invoice.ts
  orders module calls billing/application/services/BillingService.ts directly
  Any module imports from another module's domain or infrastructure layer

Module communication:
  - Synchronous: Call the module's public API (index.ts exports only)
  - Asynchronous: Emit and subscribe to domain events via in-process event bus
```

---

## 4. In-Process Event Bus

Modules communicate asynchronously via an in-process event bus:

```typescript
// Module boundary crossing via events
// orders module emits:
eventBus.emit('orders.order.placed', { orderId, customerId, items, total })

// billing module subscribes:
eventBus.on('orders.order.placed', async (event) => {
  await billingService.createInvoice(event)
})

// This preserves decoupling while avoiding network overhead
// When extracting to microservices, replace eventBus.emit → Kafka publish
```

---

## 5. Module Isolation Enforcement

### 5.1 Static Analysis (ArchUnit / dependency-cruiser)
Configure boundary rules in CI:

```javascript
// dependency-cruiser config
module.exports = {
  forbidden: [
    {
      name: 'no-cross-module-internal-imports',
      comment: 'Modules may only import from each other via their index.ts',
      severity: 'error',
      from: { path: '^src/modules/([^/]+)/' },
      to: {
        path: '^src/modules/(?!$1)[^/]+/(domain|application|infrastructure)/'
      }
    }
  ]
}
```

### 5.2 Module API Contract
Each module exposes only through `index.ts`:

```typescript
// modules/orders/index.ts — Public API
export { CreateOrderUseCase } from './application/use-cases/CreateOrderUseCase'
export { GetOrderQuery } from './application/queries/GetOrderQuery'
export type { OrderDTO } from './application/dtos/OrderDTO'
export type { CreateOrderCommand } from './application/commands/CreateOrderCommand'
// Nothing from domain/ or infrastructure/ is exported
```

---

## 6. Database Strategy in Modular Monolith

### 6.1 Schema-Per-Module (Recommended)
```sql
-- Each module gets its own PostgreSQL schema
CREATE SCHEMA orders;
CREATE SCHEMA billing;
CREATE SCHEMA identity;
CREATE SCHEMA notifications;

-- Tables within their schema
CREATE TABLE orders.orders (...);
CREATE TABLE billing.invoices (...);
CREATE TABLE identity.users (...);
```

### 6.2 Cross-Schema Query Policy
- Modules NEVER join across schemas in application code
- Reporting/analytics queries may join schemas (read-only, separate connection)
- Cross-module data needs are fulfilled by reading via the module's public API or events

---

## 7. Modular Monolith to Microservices Migration

When a module needs to be extracted:

```
Step 1: Verify module boundaries are clean (no cross-module internal imports)
Step 2: Extract module's database schema to its own database
Step 3: Replace in-process event bus with Kafka/RabbitMQ
Step 4: Replace public API imports with HTTP/gRPC calls
Step 5: Deploy extracted module as independent service
Step 6: Remove module from monolith

Migration time estimate: 2–4 weeks per module (vs. months for a tangled monolith)
```

---

## 8. When to Choose Modular Monolith

| Situation | Recommendation |
|---|---|
| New product, < 20 engineers | Start here |
| Single deployment team | Start here |
| Bounded contexts not yet validated | Start here |
| Uncertain scaling requirements | Start here |
| Multiple autonomous teams, proven scale | Migrate to microservices from modular monolith |
