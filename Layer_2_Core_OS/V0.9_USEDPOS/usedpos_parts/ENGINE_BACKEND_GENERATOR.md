# ENGINE — Backend Generator
## V0.9 USEDPOS | Universal Software Engineering, Delivery & Production Operating System

---

## Purpose
Generates complete, production-grade backend service codebases from a service specification. Applies hexagonal architecture, domain-driven design, clean code principles, and all VENUS backend standards automatically.

---

## Input Requirements
```
Required:
  - Service name and bounded context
  - Domain entities and aggregates
  - Use cases (CRUD + domain operations)
  - API protocol (REST / gRPC / GraphQL)
  - Database technology
  - Authentication requirements

Optional:
  - Existing API contracts to conform to
  - Performance targets
  - Integration requirements
```

---

## Generation Process

### Step 1: Project Scaffold
Generate project structure per Part 09 standards:
```
{service-name}/
├── src/
│   ├── domain/
│   ├── application/
│   ├── infrastructure/
│   └── shared/
├── tests/
├── k8s/
├── Dockerfile
└── package.json
```

### Step 2: Domain Layer Generation
- Entity classes with identity and invariant enforcement
- Value objects (immutable, equality by value)
- Aggregate roots with domain event collection
- Repository port interfaces
- Domain service interfaces

### Step 3: Application Layer Generation
- Use case classes (one per business operation)
- Command and Query DTOs
- Command handlers (write operations)
- Query handlers (read operations)
- Application service orchestrators

### Step 4: Infrastructure Layer Generation
- Repository implementations (ORM layer)
- HTTP controllers with validation
- Middleware (auth, rate limiting, logging)
- Database connection and migration setup
- External API client adapters

### Step 5: Testing Generation
- Unit tests for all domain logic
- Integration tests for all use cases
- API contract tests for all endpoints
- Test factories and fixtures

---

## Output Templates
Produces: [TDD](../usedpos_templates/TDD_TECHNICAL_DESIGN_DOCUMENT.md), [LLD](../usedpos_templates/LLD_LOW_LEVEL_DESIGN.md), [UNIT_TEST_SPECIFICATION](../usedpos_templates/UNIT_TEST_SPECIFICATION.md)

---

## Code Quality Gates
- Zero TypeScript errors
- ESLint: zero errors
- Test coverage ≥ 85%
- All use cases have corresponding tests
- No direct database access from domain/application layers
