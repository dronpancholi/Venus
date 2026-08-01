# ENGINE — Autonomous Refactoring Agent
## V0.9 USEDPOS | Universal Software Engineering, Delivery & Production Operating System

---

## Purpose
An autonomous agent that executes safe, incremental, behaviour-preserving refactoring of existing code. Operates systematically from the tech debt register, prioritizes by impact, and executes refactoring tasks independently with full test validation.

---

## Autonomous Refactoring Protocol

### Safety Invariants (Never Violated)
```
Before any refactoring begins:
  1. Test suite must pass (100% green)
  2. Code coverage ≥ 85% for the target file
  3. If coverage < 85%: write characterization tests first
  4. Create git branch: refactor/{ticket}-{description}
  5. Commit after every atomic step (compilable, tests pass)

During refactoring:
  6. Run tests after every change
  7. If tests break: immediately revert the last change
  8. Never change public interfaces without version bump
  9. Never change business logic (ONLY structural changes)
  10. Commit message: "refactor: {description} [no behavior change]"

After completion:
  11. Diff review: confirm no logic changes crept in
  12. Run full test suite + integration tests
  13. Create PR with before/after complexity metrics
  14. Flag for human review before merge
```

---

## Refactoring Playbook

### Task: Extract Method
```
Trigger: Function > 40 lines OR complexity > 10

Process:
  1. Identify cohesive sub-blocks within the function
  2. Determine extracted function name (intent-revealing)
  3. Identify parameters needed
  4. Extract with IDE refactoring tool (not manual text editing)
  5. Verify extracted method has its own test
  6. Verify original function tests still pass
```

### Task: Extract Value Object
```
Trigger: Primitive obsession detected (email as string, money as number)

Process:
  1. Create value object class with:
     - Private constructor
     - Static factory with validation
     - Immutable fields
     - Equality by value
     - toString() / valueOf()
  2. Update all usages to use new type
  3. Add unit tests for validation rules
  4. Verify all calling tests still pass
```

### Task: Extract Interface (Port)
```
Trigger: Concrete class used where an abstraction should exist

Process:
  1. Identify methods used by external callers
  2. Create interface with only those methods
  3. Implement interface on existing class
  4. Update all callers to depend on interface
  5. Update DI container to bind interface to implementation
  6. Verify tests: replace concrete with mock via interface
```

### Task: Decompose God Class
```
Trigger: Class > 500 lines OR > 20 methods

Process:
  1. Group methods by cohesion (what data they operate on)
  2. Each group becomes a new class (or domain service)
  3. Move methods one at a time
  4. Run tests after each move
  5. Remove original class when empty
  6. Update references
```

### Task: Remove Duplicate Code
```
Trigger: 3+ identical/near-identical code blocks

Process:
  1. Identify the canonical version of the logic
  2. Parameterize to cover all variations
  3. Replace all duplicates with calls to canonical version
  4. Test each replacement site
  5. Document if the duplication was intentional (bounded context isolation)
```

---

## Progress Tracking

The agent maintains a refactoring log:
```
Refactoring Session: 2024-01-15
Repository: order-service
Branch: refactor/VENUS-234-extract-payment-domain-service

Step 1/5: Extract PaymentCalculationService from OrderService ✅ (Tests: 243 pass)
Step 2/5: Extract value objects Money and Currency ✅ (Tests: 251 pass)
Step 3/5: Replace primitive amount with Money in Order entity ✅ (Tests: 251 pass)
Step 4/5: Update tests to use Money assertions ✅ (Tests: 251 pass)
Step 5/5: Update DI container bindings ✅ (Tests: 251 pass)

Before: OrderService complexity = 34, length = 287 lines
After:  OrderService complexity = 8,  length = 94 lines
        PaymentCalculationService complexity = 6, length = 67 lines

PR created: #456 — awaiting human review
```
