# PART 05 — Clean Architecture
## V0.9 USEDPOS | Universal Software Engineering, Delivery & Production Operating System

---

## 1. Purpose

Clean Architecture — formalized by Robert C. Martin — provides the concentric ring model that VENUS uses to enforce the Dependency Rule: source code dependencies can only point inward. No inner circle knows anything about an outer circle. Clean Architecture complements Hexagonal Architecture (Part 04) by providing additional layer granularity for complex enterprise systems.

---

## 2. The Concentric Ring Model

```
  ┌─────────────────────────────────────────────────────────────┐
  │                     FRAMEWORKS & DRIVERS                    │  ← Outermost
  │          Web │ UI │ DB │ External Interfaces │ Devices      │
  ├─────────────────────────────────────────────────────────────┤
  │                    INTERFACE ADAPTERS                       │
  │         Controllers │ Presenters │ Gateways │ Mappers       │
  ├─────────────────────────────────────────────────────────────┤
  │                    APPLICATION RULES                        │
  │             Use Cases │ Application Services                 │
  ├─────────────────────────────────────────────────────────────┤
  │                    ENTERPRISE RULES                         │
  │         Entities │ Value Objects │ Domain Events            │  ← Innermost
  └─────────────────────────────────────────────────────────────┘
                         ↑ Dependencies only point inward ↑
```

---

## 3. Layer-by-Layer Specification

### 3.1 Enterprise Rules (Innermost)
The most stable, least-likely-to-change layer. Contains the core business rules of the organization.

- Pure business logic with no framework dependencies
- Entities encapsulating the most critical business rules
- Value Objects representing domain concepts
- Domain Events communicating state changes
- **Zero external dependencies**
- Stable for years regardless of technical changes

### 3.2 Application Rules (Use Cases)
Orchestrates the flow of data to and from entities, executing application-specific business rules.

- One Use Case per business capability
- Coordinates entity interactions
- Defines input/output data structures (Request/Response DTOs)
- Depends only on Enterprise Rules layer
- Does not know about HTTP, databases, or UI frameworks
- Pure application logic

**Use Case Structure**:
```
UseCase:
  Input: Command or Query DTO
  Output: Result DTO or void
  Steps:
    1. Validate input
    2. Load domain objects via port interfaces
    3. Execute domain logic
    4. Persist state via port interfaces
    5. Return output DTO
```

### 3.3 Interface Adapters
Converts data between formats used by Use Cases and formats used by external agencies (DB, Web, etc.).

- **Controllers**: Convert HTTP requests → Use Case inputs; Use Case outputs → HTTP responses
- **Presenters**: Format data for display (view models)
- **Repository Implementations**: Convert domain objects ↔ database records
- **Mappers**: Transform between domain, persistence, and API models
- No business logic — pure transformation

### 3.4 Frameworks & Drivers (Outermost)
The glue between the application and the external world. Contains framework-specific wiring.

- Web framework configuration (Express, Fastify, NestJS)
- Database drivers and ORM configuration
- DI container setup (composition root)
- Route registration
- Middleware setup
- No business logic whatsoever

---

## 4. The Dependency Rule (Absolute)

```
Frameworks → Interface Adapters → Use Cases → Entities

NEVER:
Entities → Use Cases (direction is inward only)
Use Cases → Frameworks (breaks dependency rule)
Entities → Databases (breaks dependency rule)
```

This rule is enforced through:
1. Static analysis tools (dependency-cruiser, ArchUnit, etc.)
2. CI/CD gate: build fails if dependency rule is violated
3. Code review checklist item
4. Module bundler constraints (module boundary linting)

---

## 5. Data Flow Pattern

```
[HTTP Request]
     │
     ▼
[Controller] → transforms to → [UseCase Input DTO]
                                        │
                                        ▼
                              [Application Use Case]
                              ├── loads via [Repository Port]
                              ├── executes [Domain Logic]
                              └── saves via [Repository Port]
                                        │
                                        ▼
                              [UseCase Output DTO]
                                        │
                                        ▼
[Controller] → transforms to → [HTTP Response]
```

---

## 6. Clean Architecture vs Hexagonal Architecture

| Aspect | Clean Architecture | Hexagonal Architecture |
|---|---|---|
| **Mental Model** | Concentric rings | Hexagon with ports/adapters |
| **Focus** | Dependency rule | Driving vs driven distinction |
| **Layer Count** | 4 named layers | 3 conceptual zones |
| **Use Case** | Complex enterprise systems | Any size system |
| **VENUS Usage** | Enterprise-scale services | All services |

**VENUS Standard**: Use both together. Hexagonal Architecture defines the port/adapter pattern; Clean Architecture defines the layer hierarchy within the application core.

---

## 7. Clean Architecture Violations (Prohibited)

| Violation | Example | Consequence |
|---|---|---|
| **Inner knows outer** | Entity imports Express.Request | Build failure |
| **Use Case imports ORM** | Use Case imports TypeORM entity | Build failure |
| **Controller contains business logic** | Discount calculation in controller | Code review rejection |
| **Repository returns ORM models** | Repository returns Prisma objects, not domain objects | Build failure |
| **Entity depends on environment config** | Entity reads process.env | Build failure |

---

## 8. Directory Structure for Clean Architecture

```
src/
├── domain/                    # Enterprise Rules
│   ├── entities/
│   ├── value-objects/
│   ├── events/
│   ├── repositories/          # Port interfaces
│   └── services/
├── application/               # Application Rules
│   ├── use-cases/
│   ├── commands/
│   ├── queries/
│   └── dtos/
├── infrastructure/            # Interface Adapters + Frameworks
│   ├── http/                  # Controllers, middleware
│   ├── persistence/           # Repository implementations
│   ├── messaging/             # Queue adapters
│   ├── external/              # Third-party API adapters
│   └── config/                # DI container, app bootstrap
└── shared/                    # Cross-cutting utilities
    ├── errors/
    ├── types/
    └── utils/
```
