# Webhook Integration Specification
**Document ID:** VENUS-STD-031
**Version:** 1.0.0
**Status:** Approved
**Effective Date:** 2026-06-26

## 1. Signature Verification
To verify authenticity, webhook payloads are signed using SHA256 HMAC.

```python
# signature_verification.py
import hmac
import hashlib

def verify_signature(payload: bytes, secret: str, signature: str) -> bool:
    expected = hmac.new(
        key=secret.encode('utf-8'),
        msg=payload,
        digestmod=hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)
```

## 2. Webhook Event Payload Wrapper
```json
{
  "eventId": "evt_8877665544",
  "eventType": "transaction.completed",
  "created": 1782470000,
  "data": {
    "transactionId": "tx_221199",
    "amount": 1500.0,
    "currency": "USD"
  }
}
```

---

## 3. Reusable Checklist & Exit Criteria
*   [ ] Checked that all outgoing webhooks are signed using unique payload keys.
*   [ ] Verified signature validation scripts run in test suites.
*   [ ] Confirmed webhook delivery queues have defined exponential backoff retries.
