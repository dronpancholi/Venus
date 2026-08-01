# ENGINE — Code Review Engine
## V0.9 USEDPOS | Universal Software Engineering, Delivery & Production Operating System

---

## Purpose
Performs systematic, AI-augmented code review against all VENUS engineering standards. Produces structured feedback with severity classification, specific line references, corrective examples, and automated fix suggestions.

---

## Review Dimensions

### Dimension 1: Correctness
- Logic errors, off-by-one errors, null pointer risks
- Race conditions and concurrency issues
- Error handling completeness (no silent swallows)
- Edge case coverage

### Dimension 2: Security
- Input validation at all boundaries
- SQL injection / XSS / command injection risk
- Authentication and authorization enforcement
- Secret exposure in code or logs
- OWASP Top 10 scan

### Dimension 3: Architecture Compliance
- Dependency rule enforcement (inner layers not importing outer)
- Module boundary violations
- Correct layer placement of business logic
- Domain model purity

### Dimension 4: Code Quality
- Function length ≤ 40 lines
- Cyclomatic complexity ≤ 10
- No magic numbers or strings
- Naming convention compliance
- DRY violations across bounded contexts

### Dimension 5: Test Quality
- Test coverage ≥ 85%
- Tests test behaviour, not implementation
- No test interdependency
- Meaningful assertion messages

### Dimension 6: Performance
- N+1 query detection
- Missing index on foreign key
- Synchronous operations that should be async
- Memory leak patterns

---

## Review Output Format

```markdown
## Code Review Report
**PR**: #{number} — {title}
**Reviewer**: VENUS Code Review Engine v0.9
**Date**: {date}
**Overall**: APPROVE | REQUEST_CHANGES | COMMENT

---

### 🔴 Critical (Must fix before merge)

**File**: `src/application/use-cases/CreateOrder.ts` **Line**: 45
**Issue**: Business logic in infrastructure layer — discount calculation must not
live in the repository adapter.
**Severity**: CRITICAL — Violates hexagonal architecture dependency rule.
**Fix**:
```typescript
// Move to domain service
class DiscountDomainService {
  calculate(order: Order, coupon: Coupon): Money { ... }
}
```

---

### 🟡 Warning (Should fix)

**File**: `src/infrastructure/http/OrderController.ts` **Line**: 23
**Issue**: Missing input validation on `customerId` parameter.
**Severity**: WARNING — Could allow invalid UUIDs to reach the database layer.
**Fix**: Add `z.string().uuid()` validation in the request schema.

---

### 🔵 Suggestion (Consider)

**File**: `src/domain/entities/Order.ts` **Line**: 67
**Issue**: Method `calculateTotal()` is called 3 times in the same scope.
**Suggestion**: Compute once, store in variable for clarity and minor performance.

---

### ✅ Positive Observations
- Domain events correctly emitted on all state transitions
- Value objects properly immutable
- Test coverage: 91% ✓
```

---

## Automated Checks Integrated
- ESLint with VENUS rule set
- TypeScript strict mode
- SonarQube quality gate
- Snyk security scan
- Complexity analysis (complexity-report)
- Import boundary analysis (dependency-cruiser)

---

## SLA
- Automated review posted within 5 minutes of PR open
- Human reviewer SLA: 1 business day (Part 07)
- Blocking issues must be resolved before merge
