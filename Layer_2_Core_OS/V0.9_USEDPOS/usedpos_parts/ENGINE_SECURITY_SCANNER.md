# ENGINE — Security Scanner
## V0.9 USEDPOS | Universal Software Engineering, Delivery & Production Operating System

---

## Purpose
Performs multi-layer security scanning across code, dependencies, infrastructure, and runtime. Integrates SAST, DAST, SCA, secrets detection, and container security into a unified security posture report.

---

## Scanning Layers

### Layer 1: SAST (Static Application Security Testing)
```
Tools: Semgrep, CodeQL, Bandit (Python), ESLint security plugins

Vulnerabilities Detected:
  - SQL Injection (unsanitized query construction)
  - XSS (unsanitized output rendering)
  - Command Injection (shell exec with user input)
  - Path Traversal (file access with user-controlled paths)
  - Insecure Deserialization
  - Hardcoded Credentials
  - Weak Cryptography (MD5, SHA1, ECB mode)
  - Insecure Random Number Generation
  - Missing Security Headers
  - Unsafe Reflection
```

### Layer 2: DAST (Dynamic Application Security Testing)
```
Tools: OWASP ZAP, Nuclei

Tests against running application:
  - OWASP API Security Top 10
  - Authentication bypass attempts
  - Authorization flaws (IDOR, privilege escalation)
  - Rate limiting bypass
  - CSRF token validation
  - Injection attacks via all input vectors
  - Sensitive data exposure in responses
  - Security header presence
```

### Layer 3: Secrets Detection
```
Tools: Gitleaks, TruffleHog, detect-secrets

Patterns Scanned:
  - API keys (AWS, GCP, Stripe, Twilio, etc.)
  - Private keys (RSA, EC, PGP)
  - Database connection strings
  - JWT secrets
  - OAuth tokens
  - Generic high-entropy strings

Scanning Scope:
  - Current codebase
  - Full git history (deep scan mode)
  - CI/CD environment variable names
  - Docker image layers
```

### Layer 4: Container Security
```
Tools: Trivy, Grype, Syft

Scans:
  - OS package vulnerabilities in base image
  - Application dependency vulnerabilities in image
  - Dockerfile security misconfigurations:
    - Running as root
    - ADD vs COPY
    - Secrets in ENV or ARG
    - Latest tag usage
    - Missing USER instruction
  - SBOM (Software Bill of Materials) generation
```

### Layer 5: Infrastructure Security (IaC Scanning)
```
Tools: Checkov, tfsec, kube-score

Checks:
  - Terraform: Public S3 buckets, unencrypted RDS, open security groups
  - Kubernetes: Privileged containers, missing network policies, host namespace
  - Docker Compose: Host volume mounts, privileged mode
```

---

## OWASP API Security Top 10 Gate
Before any API is deployed to production, automated tests validate:
1. Broken Object Level Authorization (BOLA)
2. Broken Authentication
3. Broken Object Property Level Authorization
4. Unrestricted Resource Consumption
5. Broken Function Level Authorization
6. Unrestricted Access to Sensitive Business Flows
7. Server-Side Request Forgery (SSRF)
8. Security Misconfiguration
9. Improper Inventory Management
10. Unsafe Consumption of APIs

---

## Report Output

```markdown
# Security Scan Report
Service: {name} | Scan Date: {date} | Gate: PASS | FAIL

## CRITICAL (0 permitted to deploy)
## HIGH (must fix within 7 days)
## MEDIUM (fix within 30 days)
## LOW (fix within 90 days)
## INFORMATIONAL

Security Score: {N}/100
Compliance: SOC2-ready | PCI-DSS: N/A | HIPAA: N/A
```

---

## CI/CD Integration
- SAST on every PR (< 3 min)
- Secrets detection on every commit (pre-push hook + CI)
- Container scan on every image build
- DAST weekly against staging environment
- Full security report monthly to CISO/CTO
