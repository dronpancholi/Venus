# PART 08 — Branch Protection
## V0.9 USEDPOS | Universal Software Engineering, Delivery & Production Operating System

---

## 1. Purpose

Branch Protection defines the automated gates and enforcement rules that prevent unreviewed, untested, or broken code from entering protected branches. Branch protection is a mandatory safety layer for every VENUS repository.

---

## 2. Protection Rules Matrix

### 2.1 Main Branch (Production Gateway)

| Rule | Setting | Rationale |
|---|---|---|
| Require pull request before merging | **ENABLED** | No direct pushes to main |
| Required approvals | **Minimum 1** (senior engineer) | Human review gate |
| Dismiss stale reviews on new push | **ENABLED** | Previous approvals invalidated by new changes |
| Require review from code owners | **ENABLED** | Domain experts must review their code |
| Require status checks to pass | **ENABLED** | All CI checks must be green |
| Require branches to be up to date | **ENABLED** | No stale merges |
| Require signed commits | **ENABLED** | Cryptographic authorship verification |
| Require linear history | **ENABLED** | Clean, navigable commit graph |
| Restrict who can push | **ENABLED** | Only CI/CD service accounts direct push |
| Allow force pushes | **DISABLED** | History is immutable |
| Allow deletions | **DISABLED** | Protected branches cannot be deleted |

### 2.2 Release Branches

| Rule | Setting |
|---|---|
| Required approvals | Minimum 2 (including release manager) |
| Require status checks | All checks + integration tests |
| Require signed commits | ENABLED |
| Allow force pushes | DISABLED |

### 2.3 Feature Branches
No automated protection. Engineers are responsible for their own branch hygiene.

---

## 3. Required Status Checks

All of the following must pass before any PR can be merged to `main`:

| Check | Description | Failure Action |
|---|---|---|
| `ci/unit-tests` | All unit tests pass | Block merge |
| `ci/integration-tests` | Integration tests against test environment | Block merge |
| `ci/lint` | Zero linting errors | Block merge |
| `ci/type-check` | Zero type errors | Block merge |
| `ci/coverage` | Coverage ≥ 85% | Block merge |
| `ci/security-scan` | Zero critical/high vulnerabilities | Block merge |
| `ci/dependency-audit` | No prohibited dependencies | Block merge |
| `ci/build` | Application builds successfully | Block merge |
| `ci/contract-tests` | API contracts pass | Block merge (for API changes) |

---

## 4. CODEOWNERS Integration

Branch protection enforces that file owners must review changes to their owned files before merge.

```
# Example CODEOWNERS enforcement:
# If a PR touches src/domain/payment/*, the @billing-team must approve.
# The PR cannot merge until a member of @billing-team approves.
```

This prevents domain boundary violations by ensuring domain experts review cross-domain changes.

---

## 5. Automated Security Gates

### 5.1 Secret Detection
- Gitleaks or TruffleHog scans every commit
- Any detected secret blocks the push immediately
- Alert sent to Security team Slack channel
- Engineer must rotate the credential and audit scope

### 5.2 Dependency Vulnerability Scanning
- Dependabot or Snyk scans dependencies on every PR
- Critical severity CVEs block merge
- High severity CVEs require security team sign-off
- Policy: patch within 48h (critical), 7 days (high), 30 days (medium)

### 5.3 License Compliance
- All new dependencies scanned against approved license list
- GPL/AGPL/SSPL licenses prohibited in commercial products without legal approval
- Copyleft licenses flagged for review

---

## 6. Merge Queue (High-Throughput Repositories)

For repositories with > 20 PRs/day, a **Merge Queue** prevents merge race conditions:

1. PRs join the queue when approved and all checks pass
2. Queue re-validates against latest `main` before merging
3. Batching: up to 5 PRs tested together for throughput
4. Failed batch: individual PRs retested to isolate failure

---

## 7. Enforcement Monitoring

Weekly automated report delivered to engineering leadership:

| Metric | Alert Threshold |
|---|---|
| Direct pushes to main | > 0 |
| PRs merged without required reviews | > 0 |
| PRs merged with failing checks | > 0 |
| Secrets detected and blocked | Any occurrence triggers incident |
| Critical CVEs present in `main` | > 0 |

---

## 8. Emergency Override Protocol

In genuine production emergencies where branch protection must be bypassed:

1. VP Engineering or CTO authorization required
2. Written justification logged in incident management system
3. Security team notified immediately
4. Post-incident review mandatory
5. Bypass logged with cryptographic timestamp
6. Protection restored within 4 hours

**This protocol is audited quarterly. Abuse results in access revocation.**
