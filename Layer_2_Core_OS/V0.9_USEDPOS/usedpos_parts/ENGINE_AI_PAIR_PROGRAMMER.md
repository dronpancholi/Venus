# ENGINE — AI Pair Programmer
## V0.9 USEDPOS | Universal Software Engineering, Delivery & Production Operating System

---

## Purpose
The AI Pair Programmer is a context-aware, standards-enforcing coding assistant that operates within the VENUS engineering framework. It does not just generate code — it generates VENUS-compliant code that adheres to hexagonal architecture, DDD patterns, clean code principles, and all VENUS engineering standards.

---

## Capabilities

### Capability 1: Context-Aware Code Generation
```
Context loaded before any code generation:
  - Current bounded context and domain model
  - Existing entity and value object definitions
  - Port interface definitions
  - Established naming conventions in the codebase
  - Active feature flags and environment configuration
  - Current test patterns used in the service

Code generated:
  - Follows existing patterns in the codebase (not generic patterns)
  - Uses established naming conventions
  - Respects domain boundaries
  - Generates corresponding tests automatically
```

### Capability 2: VENUS Standard Enforcement
```
Every code suggestion validated against:
  ✅ Function length ≤ 40 lines (auto-refactors if exceeded)
  ✅ Cyclomatic complexity ≤ 10 (decomposes if exceeded)
  ✅ Naming conventions (warns if violated)
  ✅ No magic numbers (suggests named constants)
  ✅ No cross-layer imports (rejects suggestions that violate)
  ✅ Error handling present (never swallowed exceptions)
  ✅ Tests generated alongside implementation
```

### Capability 3: Domain-Driven Code Generation
```
Given: "Add an order cancellation feature"

AI Pair Programmer generates:

1. Domain event: OrderCancelled
2. Domain method: order.cancel(reason: CancellationReason)
   - Validates invariant: Cannot cancel FULFILLED orders
   - Emits OrderCancelled domain event
3. Value object: CancellationReason (validated enum)
4. Application use case: CancelOrderUseCase
   - Loads order via OrderRepository port
   - Invokes order.cancel()
   - Saves updated order
   - Returns result
5. HTTP controller: POST /orders/{id}/cancel
   - Request validation schema
   - Authorization check
   - Delegates to use case
6. Unit tests:
   - Happy path: pending order cancelled
   - Edge case: fulfilled order cannot be cancelled
   - Edge case: non-existent order returns 404
7. Integration test
8. API documentation update
```

### Capability 4: Code Review Assistance
```
Analyzes PR diff and provides:
  - Potential bugs (null checks, race conditions)
  - Security issues (injection, exposure)
  - Architecture violations (layer boundaries)
  - Performance concerns (N+1, missing index)
  - Better alternatives to proposed approach
  - Missing edge case tests
```

### Capability 5: Legacy Code Understanding
```
Given a complex, undocumented legacy function:
  1. Generates natural language explanation
  2. Identifies what it does, edge cases, side effects
  3. Proposes refactoring plan with steps
  4. Generates characterization tests before any refactoring
  5. Executes refactoring incrementally with test validation
```

---

## Interaction Protocol

### Format: Structured Request
```
Context: [service/module name]
Task: [what needs to be done]
Constraints: [existing patterns, performance requirements, deadlines]
Existing Code: [relevant existing code]
```

### Response Format
```
1. Analysis (what the code should do)
2. Architecture placement (which layer/module)
3. Implementation (complete, tested code)
4. Edge cases considered
5. What was NOT implemented and why
6. Follow-up suggestions
```

---

## Guardrails (Never Does)
- Never generates code that introduces a dependency rule violation
- Never generates code without corresponding tests
- Never hardcodes secrets, credentials, or environment values
- Never introduces new dependencies without noting them
- Never generates placeholder/TODO code without marking it clearly
- Never modifies production data in development scripts
