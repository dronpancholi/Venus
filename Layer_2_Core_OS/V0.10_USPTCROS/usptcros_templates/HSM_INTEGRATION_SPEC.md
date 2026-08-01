# USPTCROS HSM Integration Specification
**Document Link:** [HSM Integration Spec](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/HSM_INTEGRATION_SPEC.md)  
**References:** [Key Rotation Lifecycle Plan](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/KEY_ROTATION_LIFECYCLE_PLAN.md)

## 1. Hardware Integration Architecture
This specification details the interfaces, libraries, and hardware properties of the HSM.

```
  ┌────────────────────────────────────────────────────────┐
  │                 Application Space                      │
  │  (Loads PKCS#11 Shared Library: libCryptoki.so)        │
  └───────────────────────────┬────────────────────────────┘
                              │
                    (PKCS#11 API Calls)
                              ▼
  ┌────────────────────────────────────────────────────────┐
  │                 HSM Cryptographic Core                 │
  │  (FIPS 140-2 Level 3 Sealed Cryptographic Boundary)   │
  └────────────────────────────────────────────────────────┘
```

## 2. PKCS#11 Connection Config
```ini
# PKCS11 Token Driver Configuration File
[Token]
DriverPath = /usr/lib/hsm/libCryptoki.so
SlotID = 1
UserPIN = "ENV[HSM_USER_PIN]"
SessionLimit = 64
```

## 3. Partition Settings
* **Root Partition:** Houses Root Certification Authority Keys. Restricted to root custodians.
* **Transit Partition:** Houses dynamic DEK wrapper keys for the application's column encryption mechanisms.
