# ENGINE — Repository Auditor
## V0.9 USEDPOS | Universal Software Engineering, Delivery & Production Operating System

---

## Purpose
Performs comprehensive audits of all repositories against VENUS engineering standards. Evaluates repository health, architecture compliance, documentation completeness, security posture, and team practices. Produces a scored compliance report with remediation roadmap.

---

## Audit Dimensions

### Dimension 1: Architecture Compliance (Weight: 25%)
```
Evaluated by: dependency-cruiser, ArchUnit, custom rules

Checks:
  ✅ No cross-layer imports (inner importing outer)
  ✅ No circular dependencies
  ✅ Module boundaries respected
  ✅ No domain logic in infrastructure layer
  ✅ Repository interfaces in domain layer
  ✅ No direct database access from controllers

Scoring: (violations × -5) → deducted from 25 points max
```

### Dimension 2: Code Quality (Weight: 25%)
```
Checks:
  ✅ Test coverage ≥ 85%
  ✅ Zero critical/high SonarQube issues
  ✅ Cyclomatic complexity ≤ 10 for all functions
  ✅ Function length ≤ 40 lines
  ✅ Naming conventions followed
  ✅ No magic numbers or strings
  ✅ Zero ESLint errors

Scoring: Each failed check: -3 to -5 points from 25 max
```

### Dimension 3: Security Posture (Weight: 20%)
```
Checks:
  ✅ No critical/high CVEs in dependencies
  ✅ No secrets detected in git history
  ✅ Branch protection rules configured correctly
  ✅ CODEOWNERS file present and complete
  ✅ Signed commits enabled
  ✅ Security policy (SECURITY.md) present
  ✅ Dependabot / Renovate configured

Scoring: Critical violations: -10 each. High: -5 each.
```

### Dimension 4: Documentation Quality (Weight: 15%)
```
Checks:
  ✅ README.md present with getting-started instructions
  ✅ CONTRIBUTING.md present
  ✅ CHANGELOG.md maintained
  ✅ Architecture documented (at least HLD)
  ✅ API documented (OpenAPI spec)
  ✅ All public functions have JSDoc
  ✅ Runbooks present for on-call
  ✅ ADRs present for significant decisions

Scoring: Each missing document: -2 points from 15 max
```

### Dimension 5: Operational Readiness (Weight: 15%)
```
Checks:
  ✅ Health check endpoints implemented
  ✅ Structured logging configured
  ✅ Metrics endpoint (Prometheus)
  ✅ Distributed tracing instrumented
  ✅ Graceful shutdown implemented
  ✅ Docker image builds with non-root user
  ✅ Kubernetes manifests present
  ✅ Resource limits configured

Scoring: Each missing item: -2 points from 15 max
```

---

## Audit Report Output

```markdown
# Repository Audit Report
Repository: order-service | Date: {date}
Overall Score: 76/100 | Grade: B | Status: NEEDS IMPROVEMENT

## Architecture Compliance: 20/25
Issues:
  - 3 cross-module imports detected (src/modules/orders → src/modules/billing/domain)
  - 1 circular dependency: OrderService ↔ NotificationService

## Code Quality: 18/25
Issues:
  - Test coverage: 72% (threshold: 85%) → -5 points
  - 2 functions with complexity > 10 → -4 points

## Security Posture: 17/20
Issues:
  - 2 high CVEs in dependencies → -6 points

## Documentation: 11/15
Issues:
  - CHANGELOG.md outdated (last updated 90 days ago) → -2 points
  - No runbook present → -2 points

## Operational Readiness: 10/15
Issues:
  - Metrics endpoint not implemented → -2 points
  - No distributed tracing instrumented → -3 points

## Remediation Plan (Prioritized)
P0 (this sprint):  Fix cross-module imports, patch CVEs
P1 (next sprint):  Increase test coverage to 85%, add metrics endpoint
P2 (this quarter): Complete documentation, add tracing

Next audit: 30 days
```

---

## Compliance Thresholds
| Grade | Score | Implications |
|---|---|---|
| A | 90–100 | Exemplary — eligible for promotion to reference architecture |
| B | 75–89 | Good — minor remediation required |
| C | 60–74 | Needs improvement — remediation sprint required |
| D | 45–59 | Poor — tech debt sprint mandatory before new features |
| F | < 45 | Critical — feature freeze until remediation plan approved |
