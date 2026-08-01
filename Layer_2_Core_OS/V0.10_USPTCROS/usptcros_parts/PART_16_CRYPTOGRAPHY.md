# Project Venus USPTCROS — Part 16: Cryptographic Standards

## 1. Executive Summary
This module specifies the cryptographic standards, algorithms, and key sizes approved for use across all Project Venus systems. It enforces strong, modern primitives and defines key derivation mechanisms.

## 2. Cryptographic Primitives
Venus mandates the following cryptographic standards:
- **Symmetric Encryption**: AES-256-GCM (Galois/Counter Mode) only.
- **Asymmetric Encryption / Signatures**: ECDSA (Curve P-384) or Ed25519. RSA-4096 is deprecated and only allowed for legacy integrations.
- **Hashing**: SHA-384 or SHA-512. MD5 and SHA-1 are strictly banned.
- **Key Derivation (KDF)**: HKDF-SHA256 (HMAC-based Extract-and-Expand Key Derivation Function) or Argon2id for password hashing.

### 2.1 HKDF Mathematical Definition
HKDF is defined in RFC 5869. It consists of two steps:
1. **Extract**:
   $$\text{PRK} = \text{HMAC-Hash}(\text{salt}, \text{IKM})$$
   Where:
   - $IKM$ is the Input Keying Material.
   - $PRK$ is the Pseudorandom Key.
2. **Expand**:
   $$T(0) = \text{empty string}$$
   $$T(i) = \text{HMAC-Hash}(\text{PRK}, T(i-1) \mathbin{\Vert} \text{info} \mathbin{\Vert} i)$$
   $$\text{Output} = T(1) \mathbin{\Vert} T(2) \mathbin{\Vert} \dots \mathbin{\Vert} T(L)$$
   Where $i$ is the block index, and $info$ represents optional context-specific information.

---

## 3. Cryptographic Policy JSON Schema
This schema validates the cryptographic configuration parameters inside a deployment manifest.

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "VenusCryptoPolicyConfig",
  "type": "object",
  "properties": {
    "symmetric_algorithm": { "type": "string", "enum": ["AES-256-GCM"] },
    "asymmetric_algorithm": { "type": "string", "enum": ["ECDSA-P384", "Ed25519", "RSA-4096"] },
    "digest_algorithm": { "type": "string", "enum": ["SHA-384", "SHA-512"] },
    "kdf": { "type": "string", "enum": ["HKDF-SHA256", "Argon2id"] }
  },
  "required": ["symmetric_algorithm", "asymmetric_algorithm", "digest_algorithm", "kdf"]
}
```

---

## 4. Cryptographic Validation Checklist
- [ ] Ensure that initialization vectors (IVs) for AES-256-GCM are generated using a cryptographically secure random number generator and are never reused with the same key.
- [ ] Verify that no custom cryptographic algorithms are implemented (use standard libraries only).
- [ ] Confirm that cryptographic keys are stored in hardware security modules (HSM) or secure KMS.
- [ ] Ensure that RSA signature padding uses PSS (Probabilistic Signature Scheme).

---

## 5. Absolute System Links
- **Previous Chapter**: [Part 15: Secrets Management](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_parts/PART_15_SECRETS_MANAGEMENT.md)
- **Next Chapter**: [Part 17: PKI](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_parts/PART_17_PKI.md)
