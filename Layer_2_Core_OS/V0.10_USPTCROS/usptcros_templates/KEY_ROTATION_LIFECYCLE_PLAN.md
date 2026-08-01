# USPTCROS Key Rotation Lifecycle Plan
**Document Link:** [Key Rotation Lifecycle Plan](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/KEY_ROTATION_LIFECYCLE_PLAN.md)  
**References:** [HSM Integration Spec](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/HSM_INTEGRATION_SPEC.md)

## 1. Key Rotation Lifecycle Schedule
Cryptographic keys are rotated automatically based on their usage category:

| Key Classification | Rotation Period | Overlap Window (Transition) | Verification Task |
|---|---|---|---|
| **Data Encryption Keys (DEKs)** | 90 Days | 7 Days | Verify automatic decryptions |
| **Key Encryption Keys (KEKs)** | 365 Days | 30 Days | Run KMS status test |
| **TLS Private Keys** | 90 Days | 24 Hours | Run mTLS boundary check |
| **SSH User Credentials** | 30 Days | None | Run SSH auth logs trace |

## 2. Rotation Transition Workflow
1. **Active Phase:** Key is used for both encryption and decryption operations.
2. **Post-Rotation Phase:** Old key is retired from encryption but remains available for decryption of legacy datasets.
3. **Deprecated Phase:** Key is removed from the active memory pool and archived.
4. **Destroyed Phase:** Key is zeroized. See [Key Destruction Protocol](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/KEY_DESTRUCTION_PROTOCOL.md).

## 3. Rotation Code Example (AWS KMS Mock Pattern)
```python
def rotate_kms_key(kms_client, key_id: str):
    # Trigger rotation API on Key Management Service
    response = kms_client.enable_key_rotation(KeyId=key_id)
    return response["ResponseMetadata"]["HTTPStatusCode"] == 200
```
