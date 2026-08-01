# USPTCROS Cryptographic Key Inventory
**Document Link:** [Cryptographic Key Inventory](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/CRYPTOGRAPHIC_KEY_INVENTORY.md)  
**References:** [Key Rotation Lifecycle Plan](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/KEY_ROTATION_LIFECYCLE_PLAN.md)

## 1. Key Registry System
This register catalogs all active cryptographic assets within the subsystem.

| Key Identifier | Algorithm | Key Size | Lifecycle Status | Purpose | HSM Slot | Next Rotation |
|---|---|---|---|---|---|---|
| **KEY-KMS-001** | AES-GCM | 256 bits | Active | Root Database KEK | Slot 1 | 2026-09-26 |
| **KEY-CA-001** | ECDSA | Curve P-384 | Active | Root CA Signing | Slot 0 | 2029-06-26 |
| **KEY-JWT-001** | RSA-PSS | 4096 bits | Active | JWT Identity Tokens| Slot 2 | 2026-12-26 |
| **KEY-DEK-109** | AES-GCM | 256 bits | Active | User Table DEK | Vault-RAM | 2026-09-26 |

## 2. Key Inspection Validation Script
Verify matching cryptographic attributes:
```bash
# Check key metadata using HSM CLI tools
pkcs11-tool --module /usr/lib/hsm/libCryptoki.so --list-objects --login
```
