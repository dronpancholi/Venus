# ENGINE — Git Workflow Validator
## V0.9 USEDPOS | Universal Software Engineering, Delivery & Production Operating System

---

## Purpose
Continuously validates that git workflow standards from Part 07 are being followed across all repositories. Detects violations, enforces commit standards, monitors branch hygiene, and generates team-level workflow health reports.

---

## Validation Checks

### Check 1: Commit Message Validation
```
Enforced via: commitlint (pre-commit hook + CI)

Validates:
  ✅ Type is one of: feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert
  ✅ Scope is defined (when applicable)
  ✅ Description is present and < 100 characters
  ✅ Body, if present, is separated by blank line
  ✅ Footer references ticket ID for feat/fix commits
  ✅ BREAKING CHANGE explicitly declared in footer

Rejections:
  ❌ "fixed bug" → missing type
  ❌ "feat: " → empty description
  ❌ "FEAT: add thing" → type must be lowercase
  ❌ "feat: Add payment [no ticket reference]" → missing ticket ID
```

### Check 2: Branch Naming Validation
```
Pattern enforced: ^(feature|fix|hotfix|refactor|chore|docs|test|release)\/[A-Z]+-\d+-[a-z0-9-]+$

Valid examples:
  feature/VENUS-123-add-payment-retry
  fix/VENUS-456-null-session-on-logout
  hotfix/VENUS-789-stripe-timeout

Invalid:
  my-branch        → No ticket reference
  Feature/VENUS-1  → Capital letter in type
  fix/just-a-fix   → No ticket number
```

### Check 3: Branch Lifespan Monitoring
```
Alert Thresholds:
  Branch age > 2 days (feature branch) → Warning to author + manager
  Branch age > 5 days → Escalation to tech lead
  Branch age > 7 days → Mandatory sync with main required

Stale branch report (weekly):
  Branch | Author | Age | Last Commit | Status
  feature/VENUS-99 | alice | 8 days | 6 days ago | STALE
```

### Check 4: PR Size Monitoring
```
Line changes tracked per PR:
  < 200 lines: ✅ Small — preferred
  200-500:     ⚠️ Medium — comment suggesting split if feature complete
  500-1000:    🔴 Large — reviewer SLA extended, split recommended
  > 1000:      ❌ Extra Large — PR comment: must split before review

Monthly report: Team's average PR size trend (up/down)
```

### Check 5: Merge Pattern Compliance
```
Validates:
  - No direct pushes to main (outside of CI service accounts)
  - All merges via PR (merge commit or squash)
  - Rebase-and-merge only used with team lead approval
  - Force pushes to main: zero tolerance (alert immediately)
```

### Check 6: Code Review SLA
```
Monitor PR open → first review time:
  Critical/Hotfix: Alert if > 2 hours without review
  Normal: Alert if > 1 business day without review
  
Weekly report by reviewer:
  Reviewer | Avg Review Time | PRs Reviewed | Pending
  alice    | 4.2 hours       | 23           | 2
  bob      | 18.1 hours      | 8            | 5
```

---

## Workflow Health Dashboard
```
Team: Backend Engineering
Week of: {date}

Commit Quality:     94% conventional commits ✅ (target: 100%)
Branch Hygiene:     3 stale branches ⚠️ (target: 0)
PR Size:            Avg 245 lines ✅ (target: < 400)
Review SLA:         87% reviewed within 1 day ⚠️ (target: 95%)
Direct Pushes:      0 ✅
Failed CI on Main:  0 ✅

Action Items:
  1. alice: Close or merge stale branch feature/VENUS-87 (12 days old)
  2. bob: 5 PRs awaiting review > 1 business day
```

---

## Automated Enforcement Actions
| Violation | Automated Action |
|---|---|
| Invalid commit message | Commit rejected (pre-commit hook) |
| Invalid branch name | Push rejected (pre-push hook) |
| Direct push to main | Revert + alert to security + engineering manager |
| PR > 1000 lines | Comment added, reviewer not assigned until split |
| Force push to main | Immediate rollback + incident created |
