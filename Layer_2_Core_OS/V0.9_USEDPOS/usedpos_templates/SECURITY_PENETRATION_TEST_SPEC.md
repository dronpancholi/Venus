# Security Penetration Testing Specification
**Document ID:** VENUS-STD-066
**Version:** 1.0.0
**Status:** Approved
**Effective Date:** 2026-06-26

## 1. Scope of Penetration Testing
Penetration tests must cover:
1. All public REST/GraphQL endpoints.
2. Web UI applications (XSS, Clickjacking, CSRF).
3. Cloud networking boundaries (firewall misconfigurations, open port scans).

## 2. Vulnerability Severity Matrix (CVSS v3.1)
All findings must be classified according to CVSS scoring definitions:

| CVSS Score | Severity | CI/CD Action Gate | Remediation SLA |
| :--- | :--- | :--- | :--- |
| **9.0 - 10.0** | Critical | Block Deployment / Immediate Rollback | 24 Hours |
| **7.0 - 8.9** | High | Block Deployment | 72 Hours |
| **4.0 - 6.9** | Medium | Warning Logged | 30 Days |
| **0.1 - 3.9** | Low | Info Logged | 90 Days |

## 3. OWASP Top 10 Attack Vector Validations
Each test suite must include validations for:
*   **A01:2021-Broken Access Control:** Testing for Privilege Escalation (horizontal and vertical).
*   **A03:2021-Injection:** Testing SQL parameter leaks using automated injection techniques.
*   **A05:2021-Security Misconfiguration:** Verifying TLS settings, headers (`X-Frame-Options`, `Content-Security-Policy`), and disabled default accounts.

## 4. Automated Pen Testing Commands
Run OWASP ZAP baseline scan in pipeline:
```bash
docker run -v $(pwd):/zap/wrk/:rw -t ghcr.io/zaproxy/zaproxy:stable zap-baseline.py \
  -t https://staging.venus.internal \
  -g gen.conf \
  -r zap_report.html
```

## 5. Cross-References
- [Dependency Whitelist Policy](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usedpos_templates/DEPENDENCY_WHITELIST_POLICY.md)
- [Secrets Management Vault Policy](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usedpos_templates/SECRETS_MANAGEMENT_VAULT_POLICY.md)
