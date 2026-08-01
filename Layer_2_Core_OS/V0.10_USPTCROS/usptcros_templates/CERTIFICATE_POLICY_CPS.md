# USPTCROS Certificate Policy & Certification Practice Statement (CP/CPS)
**Document Link:** [Certificate Policy & CPS](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/CERTIFICATE_POLICY_CPS.md)

## 1. Certification Practices (CPS)
This document outlines the operational policy of the local Certificate Authority (CA) systems.

## 2. Key Generation & Protection Controls
* **Key Ceremony:** CA keys are generated inside an HSM during a formal key ceremony witnessed by at least 3 trust officers.
* **Multisignature Access (m-of-n):** Activating the Root CA private key requires the physical presence of 2 out of 3 key custodians.
* **Key Storage:** Root CA keys are never present in plaintext on system RAM or disk. They are held within FIPS 140-2 Level 3 HSM hardware.

## 3. Certificate Lifecycle Management
| Lifecycle Phase | Policy Rules |
|---|---|
| **Registration** | Entities must present valid cryptographic proof of domain control (ACME DNS-01 or HTTP-01). |
| **Issuance** | Automatic validation and generation by the intermediate CA cluster. |
| **Renewal** | Permitted starting 30 days before expiration. See [Certificate Auto-Renewal Config](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/CERTIFICATE_AUTO_RENEWAL_CONFIG.md). |
| **Revocation** | Triggered immediately on detection of private key compromise or host decommission. |
