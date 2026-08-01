# USPTCROS Envelope Encryption Sizing Model
**Document Link:** [Envelope Encryption Sizing Model](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/ENVELOPE_ENCRYPTION_SIZING_MODEL.md)  
**References:** [Secrets Management Vault Policy](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/SECRETS_MANAGEMENT_VAULT_POLICY.md)

## 1. Envelope Encryption Sizing Model
Envelope encryption wraps Data Encryption Keys (DEKs) using a remote Key Encryption Key (KEK).

```
   ┌────────────────────────────────────────────────────────┐
   │                     Ciphertext Block                   │
   │  ┌───────────────────────┐  ┌───────────────────────┐  │
   │  │   Encrypted Payload   │  │    Encrypted DEK      │  │
   │  │     (AES-GCM-256)     │  │   (Wrapped by KEK)    │  │
   │  └───────────────────────┘  └───────────────────────┘  │
   └────────────────────────────────────────────────────────┘
```

## 2. Sizing and Metadata Formulation
The total storage overhead ($S_{total}$) for an encrypted record is calculated as:
$$S_{total} = S_{payload} + S_{iv} + S_{tag} + S_{wrapped\_dek}$$

Where:
* $S_{payload}$: Size of the original database field.
* $S_{iv}$ (Initialization Vector): 12 Bytes.
* $S_{tag}$ (Authentication Tag): 16 Bytes.
* $S_{wrapped\_dek}$ (KMS Key wrapping payload): 512 Bytes.
