# USPTCROS PKI Architecture Specification
**Document Link:** [PKI Architecture Spec](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/PKI_ARCHITECTURE_SPEC.md)  
**References:** [Certificate Policy & CPS](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/CERTIFICATE_POLICY_CPS.md), [TLS/mTLS Configuration Guide](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/TLS_MTLS_CONFIGURATION_GUIDE.md)

## 1. Hierarchy Diagram
The Public Key Infrastructure (PKI) for Project Venus is structured in a two-tier hierarchy.

```
┌─────────────────────────────────┐
│     Offline Root CA             │ (Keys stored in HSM with m-of-n quorum)
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│     Online Intermediate CA      │ (Enforces Certificate Signing Requests)
└────────────────┬────────────────┘
                 │
        ┌────────┴────────┐
        ▼                 ▼
┌───────────────┐ ┌───────────────┐
│  Server Leaf  │ │  Client Leaf  │ (Automated via ACME / cert-manager)
└───────────────┘ └───────────────┘
```

## 2. Technical Profile Specifications
* **Root CA Key Size:** RSA 4096 or ECDSA P-384. Signature Algorithm: SHA-384. Lifetime: 10 Years.
* **Intermediate CA Key Size:** RSA 4096 or ECDSA P-384. Signature Algorithm: SHA-384. Lifetime: 3 Years.
* **Leaf Certificate Key Size:** RSA 2048 or ECDSA P-256. Signature Algorithm: SHA-256. Lifetime: 90 Days.

## 3. Revocation Infrastructure
Revocation verification is enforced using Online Certificate Status Protocol (OCSP) Stapling with fallback to Certificate Revocation Lists (CRLs). Max OCSP cache expiration: 8 hours.
