# Dependency Whitelist Policy
**Document ID:** VENUS-STD-057
**Version:** 1.0.0
**Status:** Approved
**Effective Date:** 2026-06-26

## 1. Purpose
This policy regulates the ingestion of third-party open-source packages, libraries, and frameworks into Project Venus repositories to mitigate license compliance risks and supply chain security vulnerabilities.

## 2. Approved License Whitelist
Only libraries distributed under the following licenses may be used without explicit legal approval:

| License Class | Allowed | Example Licenses |
| :--- | :--- | :--- |
| **Permissive** | YES | MIT, Apache 2.0, BSD-2-Clause, BSD-3-Clause, ISC |
| **Weak Copyleft** | CONDITIONAL | LGPL (Dynamic linking only, no static linking allowed) |
| **Strong Copyleft** | NO | GPL v2/v3, AGPL, CC-BY-NC (Non-commercial) |

*Condition for Copyleft:* Use of any GPL/AGPL library requires a written waiver signed by the Chief Architect and Corporate Legal Counsel.

## 3. Dependency Vulnerability Thresholds
Prior to merging, automated pipeline scanners (Snyk, npm audit, pip-audit, or trivy) must evaluate all packages.

| Vulnerability Severity | Pipeline Policy | Remediation Deadline |
| :--- | :--- | :--- |
| **Critical** | Block Build / Merge | Immediate (Before Merge) |
| **High** | Block Build / Merge | Immediate (Before Merge) |
| **Medium** | Warning | 14 Days |
| **Low** | Logged | 60 Days |

## 4. Ingestion Procedure for New Dependencies
When a developer wants to add a dependency not already in the approved lockfile:
1. Run local scan: `npm audit` or equivalent to confirm zero Critical/High vulnerabilities.
2. Verify license is in the Permissive class list.
3. Submit a Pull Request documenting the dependency name, purpose, license type, and size impact.
4. Obtain approval from the designated Security Champion for the repository.

## 5. Cross-References
- [Coding Standards and Linter Rules](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usedpos_templates/CODING_STANDARDS_LINTER_RULES.md)
- [Pull Request Template](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usedpos_templates/PULL_REQUEST_TEMPLATE.md)
