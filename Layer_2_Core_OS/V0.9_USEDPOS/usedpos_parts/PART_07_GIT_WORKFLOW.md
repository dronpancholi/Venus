# PART 07 — Git Workflow
## V0.9 USEDPOS | Universal Software Engineering, Delivery & Production Operating System

---

## 1. Purpose

Git Workflow defines the branching strategy, commit standards, pull request process, and code review protocol for all VENUS repositories. A consistent Git workflow eliminates merge conflicts, enables continuous delivery, and maintains a clean, navigable history that serves as an audit trail.

---

## 2. Branching Strategy

VENUS adopts a **Trunk-Based Development** model with short-lived feature branches for all services targeting continuous delivery. GitFlow is adopted for libraries and SDK releases requiring explicit versioning.

### 2.1 Trunk-Based Development (Default)

```
main (trunk)
├── feature/VENUS-123-add-payment-retry
├── feature/VENUS-456-refactor-order-aggregate
├── fix/VENUS-789-null-pointer-checkout
└── release/v2.1.0 (only for versioned releases)
```

**Rules**:
- `main` is always deployable
- Feature branches live ≤ 2 days
- No long-lived feature branches
- Merge to main via PR with at least 1 approval
- Feature flags gate incomplete features

### 2.2 Branch Naming Convention

```
{type}/{ticket-id}-{short-description}

Types:
  feature/   — New capability
  fix/       — Bug fix
  hotfix/    — Critical production fix
  refactor/  — Refactoring without behaviour change
  chore/     — Maintenance tasks (dependencies, tooling)
  docs/      — Documentation only
  test/      — Test additions/modifications
  release/   — Release preparation

Examples:
  feature/VENUS-101-user-authentication-flow
  fix/VENUS-202-null-session-on-logout
  hotfix/VENUS-303-payment-gateway-timeout
  refactor/VENUS-404-extract-order-domain-service
```

### 2.3 Protected Branches

| Branch | Protection Rules |
|---|---|
| `main` | Require PR, require passing CI, require 1 approval, no force push |
| `release/*` | Require PR, require passing CI, require 2 approvals, no force push |

---

## 3. Commit Standards

VENUS enforces **Conventional Commits** specification.

### 3.1 Commit Message Format
```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

### 3.2 Types
| Type | Usage |
|---|---|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `style` | Formatting, no logic change |
| `refactor` | Refactoring without feature/fix |
| `perf` | Performance improvement |
| `test` | Adding/updating tests |
| `build` | Build system changes |
| `ci` | CI/CD configuration changes |
| `chore` | Maintenance, dependency updates |
| `revert` | Reverts a previous commit |
| `BREAKING CHANGE` | Introduces breaking API change |

### 3.3 Commit Message Examples

```
feat(orders): add retry logic for payment processing

Implements exponential backoff with jitter for payment gateway calls.
Max 3 retry attempts with configurable delay.

Closes VENUS-101

---

fix(auth): resolve null session on concurrent logout

Race condition in session invalidation caused null pointer exceptions.
Added distributed lock around session cleanup logic.

Fixes VENUS-202

---

feat(api)!: rename createOrder to placeOrder

BREAKING CHANGE: The createOrder endpoint has been renamed to placeOrder.
All clients must update their API calls before the next major release.
Migration guide: docs/migrations/v2-api-changes.md
```

### 3.4 Atomic Commits
Each commit must represent a single logical change. Commits should be:
- Compilable in isolation
- Independently revertable
- Meaningfully described without reading the diff

---

## 4. Pull Request Protocol

### 4.1 PR Size Limits
| Size | Lines Changed | Status |
|---|---|---|
| **Small** | < 200 lines | Preferred |
| **Medium** | 200–500 lines | Acceptable |
| **Large** | 500–1000 lines | Requires justification |
| **XL** | > 1000 lines | Split required |

### 4.2 PR Description Template
```markdown
## What
Brief description of what changed.

## Why
Context and motivation for the change.

## How
Technical approach and key decisions.

## Testing
How this was tested (unit, integration, manual).

## Screenshots (if UI change)

## Checklist
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] No secrets committed
- [ ] Breaking changes documented
- [ ] Performance impact assessed
```

### 4.3 Review SLAs
| PR Priority | First Review | Resolution |
|---|---|---|
| **Critical / Hotfix** | 2 hours | Same day |
| **Normal** | 1 business day | 2 business days |
| **Low / Chore** | 2 business days | 5 business days |

---

## 5. Merge Strategies

| Strategy | When to Use |
|---|---|
| **Squash and Merge** | Feature branches (clean history on main) |
| **Merge Commit** | Release branches (preserve branch history) |
| **Rebase and Merge** | Prohibited on shared branches |

---

## 6. Git Hooks (Mandatory)

All repositories must configure the following hooks:

| Hook | Enforces |
|---|---|
| `pre-commit` | Linting, formatting, no secrets |
| `commit-msg` | Conventional commit format |
| `pre-push` | Unit test execution |
| `pre-merge-commit` | Conflict detection |
