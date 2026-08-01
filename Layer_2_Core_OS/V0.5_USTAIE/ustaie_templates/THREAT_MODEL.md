# Template: Threat Model

## 1. Document Control
*   **Project Name**: [Project Name]
*   **Threat Model ID**: THR-[UUID]
*   **Audit Date**: [Date]

---

## 2. Threat Analysis (STRIDE)

| STRIDE Category | Threat Description | Affected Resource | Mitigation Strategy | Status |
|---|---|---|---|---|
| **Spoofing** | Unauthorized user accesses database | API endpoints | JWT signature authentication | **MITIGATED** |
| **Tampering** | API payload data modified in transit | Public routing | Force TLS 1.3 | **MITIGATED** |
| **Repudiation** | Transaction execution denied by user | Transaction records | Enforce database audit write log | **MITIGATED** |
| **Information Disclosure** | Database table leakage | Database storage | Enable AES-256 field encryption | **MITIGATED** |
| **Denial of Service** | Botnet floods HTTP endpoints | API Gateway | Configure Cloudflare Rate Limiter | **MITIGATED** |
| **Elevation of Privilege**| Worker process accesses admin config | IAM Credentials | Enforce role-based IAM boundaries | **MITIGATED** |

---

## 3. Trust Boundary Diagram
*Map the security trust boundaries (e.g. Public Internet vs. Private VPC subnet).*

```
[Public User Client]
─────────────────────── Trust Boundary (TLS 1.3 / API Gateway) ───────────────────────
[VPC Private Subnet: API Services] --> [Isolated Database Subnet: PostgreSQL]
```
