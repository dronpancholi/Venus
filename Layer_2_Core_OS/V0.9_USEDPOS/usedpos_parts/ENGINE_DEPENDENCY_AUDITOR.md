# ENGINE — Dependency Auditor
## V0.9 USEDPOS | Universal Software Engineering, Delivery & Production Operating System

---

## Purpose
Performs comprehensive auditing of all software dependencies across vulnerability, license, maintenance, and supply chain dimensions. Produces prioritized remediation plans and enforces dependency policies.

---

## Audit Dimensions

### Dimension 1: Security Vulnerability Audit
```
Sources:
  - OSV (Open Source Vulnerability) database
  - GitHub Advisory Database
  - Snyk vulnerability database
  - NVD (National Vulnerability Database)

Severity Classification:
  CRITICAL: CVSS >= 9.0  → Block deployment, fix within 24 hours
  HIGH:     CVSS 7.0-8.9 → Fix within 7 days
  MEDIUM:   CVSS 4.0-6.9 → Fix within 30 days
  LOW:      CVSS < 4.0   → Fix in next planned update
```

### Dimension 2: License Compliance Audit
```
Approved Licenses:
  MIT, Apache 2.0, BSD-2, BSD-3, ISC, CC0, Unlicense

Restricted (Legal Review Required):
  LGPL, MPL, CDDL

Prohibited (Commercial Use):
  GPL, AGPL, SSPL, Commons Clause

Actions:
  Prohibited dependency found → Build fails, legal team notified
  Restricted dependency found → PR blocked pending legal sign-off
```

### Dimension 3: Maintenance Health Audit
```
Red flags:
  - Last commit > 12 months ago
  - Open issues > 200 with no recent responses
  - No active maintainers
  - Package deprecated in registry
  - Downloads declining > 50% in 6 months

Assessment:
  HIGH RISK:   2+ red flags → Evaluate replacement
  MEDIUM RISK: 1 red flag  → Monitor quarterly
  LOW RISK:    0 red flags → Annual review
```

### Dimension 4: Supply Chain Security
```
Checks:
  - Package name squatting detection (typosquatting)
  - Verify package signatures (npm provenance, PyPI sigstore)
  - Lock file integrity (package-lock.json / poetry.lock checksums)
  - No postinstall scripts from unknown packages
  - Dependency tree depth analysis (minimize transitive deps)
  - Private package exposure (internal packages in public registry)
```

### Dimension 5: Version Currency
```
Policy:
  - Stay within 2 major versions of latest
  - Apply security patches within SLA
  - Minor version updates: monthly batch
  - Major version updates: quarterly planned upgrade

Current State Report per dependency:
  package | current | latest | major-behind | security-issues
```

---

## Report Output

```markdown
# Dependency Audit Report
Service: order-service | Date: {date} | Total Dependencies: 284

## 🚨 CRITICAL — Immediate Action Required
1. lodash@4.17.20 — CVE-2024-XXXXX (CVSS 9.8: Prototype Pollution)
   Fix: Upgrade to 4.17.21
   Command: pnpm update lodash@4.17.21

## 🔴 HIGH — Fix Within 7 Days
1. jsonwebtoken@8.5.1 — CVE-2022-23529 (CVSS 7.6)
   Fix: Upgrade to 9.0.0 (breaking change — migration guide attached)

## ⚠️ LICENSE VIOLATIONS
1. gpl-licensed-package@1.0.0 — GPL-3.0 (PROHIBITED)
   Action: Remove immediately — legal team notified

## 📦 MAINTENANCE CONCERNS
1. legacy-xml-parser@2.1.0 — No commits in 18 months, 340 open issues
   Recommendation: Replace with fast-xml-parser@4.x

## ✅ Summary
Total Packages: 284 | Critical: 1 | High: 3 | License Issues: 1
Maintenance Concerns: 2 | Outdated (2+ major): 8
```

---

## CI/CD Integration
- Runs on every PR and nightly
- Critical vulnerabilities block all deployments
- Weekly report to security team and engineering manager
- Automated PRs for safe dependency updates (Dependabot equivalent)
