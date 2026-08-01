# Template: Constraint Register

## 1. Meta Control
*   **Project Name**: [Project Name]
*   **Intake ID**: INT-[UUID]
*   **Constraint Doc ID**: CON-[UUID]
*   **Verification Lead**: [Name]
*   **Last Updated**: [Date]

---

## 2. Hard Constraints Directory
*Hard constraints represent absolute, non-negotiable boundaries. If a solution breaches any of these, it must be rejected immediately.*

| Constraint ID | Category | Description | Limit / Metric | Verification Strategy |
|---|---|---|---|---|
| **CON-TECH-01** | Technical | [e.g., Must support Postgres 15+ backend] | Postgres >= 15.0 | Docker Compose setup validation |
| **CON-FIN-01** | Financial | [e.g., Running costs per transaction max] | <= $0.05 / trans | Automated cost profiling script |
| **CON-REG-01** | Regulatory | [e.g., HIPAA compliance for user data] | Zero unencrypted logs | Static analysis audit rules |
| **CON-PERF-01** | Performance | [e.g., Client-side page rendering time] | LCP <= 2.5 seconds | Lighthouse automated check |
| **CON-OPER-01** | Operational | [e.g., Team must operate with no on-call] | Zero night deployments | Deployment pipeline block policy |
| **CON-TIME-01** | Time | [e.g., Project must go live before Black Friday] | Date: YYYY-MM-DD | Critical path project tracking |
| **CON-GEOG-01** | Geographical | [e.g., Storage must reside in EU West 1] | EU-West-1 only | Terraform provider configuration |

---

## 3. Soft Constraints & Trade-offs (Negotiable Boundaries)
*Soft constraints are preferred states or limitations that can be compromised if hard constraints force a trade-off.*

1.  **CON-SOFT-01**: [e.g., System should use Python as primary backend language for team familiarity.]
    *   *Trade-off Policy*: If latency requirements (CON-PERF-01) cannot be met in Python, Rust or Go extensions are allowed.
2.  **CON-SOFT-02**: [e.g., Prefers open-source analytics engines over paid SaaS tools.]
    *   *Trade-off Policy*: If hosting costs exceed the cost of a managed SaaS alternative, adoption of a SaaS platform is permitted.

---

## 4. Constraint Dependency Graph
*Map how constraints interact and restrict each other. For example, a legal requirement (encryption) creates performance constraints (latency).*

```
           +────────────────────────────────────────+
           | CON-REG-01: HIPAA Zero Unencrypted Logs|
           +────────────────────────────────────────+
                               │
                       (Forces / Restricts)
                               ▼
           +────────────────────────────────────────+
           | CON-TECH-02: App-level AES-256 Decrypt |
           +────────────────────────────────────────+
                               │
                       (Forces / Restricts)
                               ▼
           +────────────────────────────────────────+
           | CON-PERF-02: Transaction Latency <50ms |
           +────────────────────────────────────────+
```

*   **Dependency Node 1**: [Constraint ID]
    *   *Downstream Impact*: [Constraint ID] | *Reason*: [Description]
*   **Dependency Node 2**: [Constraint ID]
    *   *Downstream Impact*: [Constraint ID] | *Reason*: [Description]

---

## 5. Constraint Verification Test Suite
*Define how each constraint is programmatically checked before staging/production deployment.*

*   **Test Script**: `scripts/verify_constraints.sh`
*   **Rules Checklist**:
    *   [ ] Checked database version (Postgres version meets CON-TECH-01).
    *   [ ] Checked GCP region configuration (matches CON-GEOG-01).
    *   [ ] Executed load test pass (LCP checked under 100 concurrent requests).
    *   [ ] Scanned configuration file settings for PII leak check.
