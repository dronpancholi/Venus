# Project Venus USPTCROS — Part 19: Key Rotation Standards

## 1. Executive Summary
This chapter covers cryptographic key rotation intervals, deprecation, and destruction. Regularly rotating keys minimizes the volume of data exposed if a key is compromised.

## 2. Key Metadata & Versioning Logic
Venus requires ciphertexts to contain key version headers to support seamless key transitions:

`[Ciphertext Header] = [Magic Bytes (4B)] || [Key Version ID (16B)] || [Nonce/IV (12B)]`

During decryption:
1. Parse the **Key Version ID** from the header.
2. Retrieve the matching key version from KMS.
3. Decrypt the payload.

---

## 3. KMS Key Rotation Script (Implementation Example)
The following Python script connects to Google Cloud KMS to trigger the manual rotation of a key version.

```python
from google.cloud import kms

def rotate_kms_key(project_id: str, location_id: str, key_ring_id: str, key_id: str) -> str:
    client = kms.KeyManagementServiceClient()
    
    # Build Key Path
    key_path = client.crypto_key_path(project_id, location_id, key_ring_id, key_id)
    
    # Create new Cryptokey Version
    new_version = client.create_crypto_key_version(
        parent=key_path,
        crypto_key_version={}
    )
    
    # Set the new version as the primary key for encryption
    client.update_crypto_key_primary_version(
        name=key_path,
        crypto_key_version_id=new_version.name.split("/")[-1]
    )
    
    return new_version.name
```

---

## 4. Key Rotation Checklist
- [ ] Ensure symmetric keys (DEKs/KEKs) rotate automatically every 90 days.
- [ ] Configure key rotation schedules via Terraform.
- [ ] Confirm that compromised or retired keys are kept in "Decrypt-Only" state for 1 year before destruction.
- [ ] Log all decryption attempts using legacy key versions to identify un-migrated datasets.

---

## 5. Absolute System Links
- **Previous Chapter**: [Part 18: Certificate Lifecycle](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_parts/PART_18_CERTIFICATE_LIFECYCLE.md)
- **Next Chapter**: [Part 20: Application Security](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_parts/PART_20_APPLICATION_SECURITY.md)
