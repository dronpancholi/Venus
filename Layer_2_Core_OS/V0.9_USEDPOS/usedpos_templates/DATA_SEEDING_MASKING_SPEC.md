# Data Seeding & Masking Specification
**Document ID:** VENUS-STD-037
**Version:** 1.0.0
**Status:** Approved
**Effective Date:** 2026-06-26

## 1. Production Masking Rules
To protect PII, data transferred from production database snapshots to staging environments must undergo sanitization:

```python
# data_masking.py
import hashlib

def mask_email(email: str, salt: str) -> str:
    # Hash email prefix using SHA-256, preserving domain
    prefix, domain = email.split('@')
    hashed = hashlib.sha256((prefix + salt).encode('utf-8')).hexdigest()[:12]
    return f"{hashed}@{domain}"
```

## 2. Seed Data Schema
Staging environments utilize standard seed datasets representing mock accounts:
- **`seed_accounts.csv`**: Contains UUIDs and preset balances.

---

## 3. Reusable Checklist & Exit Criteria
*   [ ] Checked that database export pipelines run the masking processor.
*   [ ] Verified that cleartext passwords are encrypted/hashed.
*   [ ] Confirmed anonymized profiles maintain relational database keys.
