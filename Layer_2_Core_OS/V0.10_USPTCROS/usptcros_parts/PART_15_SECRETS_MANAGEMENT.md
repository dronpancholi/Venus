# Project Venus USPTCROS — Part 15: Secrets Management

## 1. Executive Summary
Secrets are highly sensitive credentials (keys, tokens, database passwords) that require automated lifecycles. This module outlines the standards for secret creation, isolation, injection, and rotation using cloud KMS.

## 2. Envelope Encryption Design
Venus secures secrets using envelope encryption:
1. **Data Encryption Key (DEK)**: Generated locally to encrypt the secret payload using AES-256-GCM.
2. **Key Encryption Key (KEK)**: Managed securely inside the Cloud Key Management Service (KMS) and used to encrypt the DEK.

$$\text{Ciphertext} = \text{Encrypt}_{DEK}(\text{Secret})$$
$$\text{WrappedKey} = \text{Encrypt}_{KEK}(\text{DEK})$$

---

## 3. Decrypting Secrets Using KMS (Implementation Example)
The following Python script reads a secret from GCP Secret Manager and decrypts the payload locally using Cloud KMS.

```python
import base64
from google.cloud import secretmanager
from google.cloud import kms

def fetch_and_decrypt_secret(project_id: str, secret_id: str, key_name: str) -> str:
    # 1. Fetch encrypted payload from Secret Manager
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    encrypted_payload = response.payload.data

    # 2. Decrypt DEK using Cloud KMS
    kms_client = kms.KeyManagementServiceClient()
    decrypt_response = kms_client.decrypt(
        request={
            "name": key_name,
            "ciphertext": encrypted_payload
        }
    )
    
    # 3. Return plaintext credential
    return decrypt_response.plaintext.decode("utf-8")
```

---

## 4. Secrets Management Audit Checklist
- [ ] Verify that no secrets are committed to Git repositories (enforce via pre-commit hooks).
- [ ] Configure automatic rotation of database passwords every 30 days.
- [ ] Enforce that secrets are injected at runtime via environment variables or ephemeral memory volumes.
- [ ] Revoke access permissions immediately upon service account decommission.

---

## 5. Absolute System Links
- **Previous Chapter**: [Part 14: Zero Trust](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_parts/PART_14_ZERO_TRUST.md)
- **Next Chapter**: [Part 16: Cryptography](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_parts/PART_16_CRYPTOGRAPHY.md)
