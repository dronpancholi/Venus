# ENGINE — Refactoring Engine
## V0.9 USEDPOS | Universal Software Engineering, Delivery & Production Operating System

---

## Purpose
Analyzes existing codebases and produces structured refactoring plans with prioritized, safe, incremental steps. Identifies anti-patterns, measures technical debt, and generates transformation code while preserving behaviour.

---

## Input Requirements
```
Required:
  - Codebase directory or specific files/modules
  - Target architecture (hexagonal, clean, modular monolith)
  - Business constraints (what cannot change, what is brittle)

Optional:
  - Performance targets to achieve via refactoring
  - Test coverage baseline
  - Timeline and team size constraints
```

---

## Analysis Phase

### Step 1: Code Smell Detection
Automatically detect and categorize:

| Smell | Severity | Detection |
|---|---|---|
| God Class / God Service | Critical | > 500 lines, > 20 methods |
| Feature Envy | High | Method uses other class's data more than its own |
| Long Method | High | > 40 lines |
| Primitive Obsession | Medium | Domain concepts as raw strings/ints |
| Duplicate Code | High | > 3 duplicated blocks |
| Dead Code | Medium | Unreachable code, unused methods |
| Magic Numbers | Medium | Unexplained numeric literals |
| Deep Nesting | High | > 3 levels of nesting |
| Shotgun Surgery | High | One change requires edits across many files |
| Data Clumps | Medium | Same 3+ fields always together |

### Step 2: Architectural Boundary Violations
- Domain importing infrastructure (violation of dependency rule)
- Cross-module direct imports (violation of module boundaries)
- Circular dependencies
- Missing abstractions (concrete types where interfaces should exist)

### Step 3: Technical Debt Quantification
```
Debt score per file = Σ(smell_severity_weight × occurrence_count)

Prioritization:
  P0 (Critical):  Blocking reliability or correctness
  P1 (High):      Impeding team velocity significantly
  P2 (Medium):    Slowing feature development
  P3 (Low):       Cosmetic / maintainability
```

---

## Refactoring Plan Generation

### Extract Method
```typescript
// BEFORE (detected: long method)
async processOrder(orderId: string, userId: string): Promise<void> {
  // 80 lines of mixed concerns
}

// AFTER (generated)
async processOrder(orderId: string, userId: string): Promise<void> {
  const order = await this.loadAndValidateOrder(orderId)
  await this.authorizeUserForOrder(userId, order)
  await this.applyBusinessRules(order)
  await this.persistAndPublish(order)
}
```

### Extract Value Object
```typescript
// BEFORE (detected: primitive obsession)
class User { email: string }

// AFTER (generated)
class EmailAddress {
  private constructor(private readonly value: string) {}
  static create(raw: string): EmailAddress {
    if (!isValidEmail(raw)) throw new InvalidEmailError(raw)
    return new EmailAddress(raw)
  }
  toString(): string { return this.value }
}
class User { email: EmailAddress }
```

---

## Safety Guarantees
- Refactoring steps are sequenced to maintain compilability at each step
- Test suite must pass after each step
- Behaviour-preserving transformations only (never change semantics)
- Each step generates a dedicated PR with isolated scope
- Rollback is always a single git revert

---

## Output
- Prioritized refactoring backlog (markdown table)
- Per-item: effort estimate, risk level, before/after code
- Suggested PR sequence (dependency-ordered)
- Updated [TECH_DEBT_REGISTER](../usedpos_templates/TECH_DEBT_REGISTER.md)
