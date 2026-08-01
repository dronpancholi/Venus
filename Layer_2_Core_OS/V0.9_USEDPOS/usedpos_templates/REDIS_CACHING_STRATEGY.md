# Redis Caching Strategy
**Document ID:** VENUS-STD-038
**Version:** 1.0.0
**Status:** Approved
**Effective Date:** 2026-06-26

## 1. Caching Model: Cache-Aside
Application code queries the cache first; on miss, it reads from PostgreSQL and populates Redis:

```python
# cache_aside.py
import json

def get_account_balance(client, db, account_id: str) -> float:
    cache_key = f"account:balance:{account_id}"
    cached = client.get(cache_key)
    if cached:
        return float(cached)
    
    # Cache Miss
    balance = db.fetch_value("SELECT balance FROM accounts WHERE id = %s", (account_id,))
    client.setex(cache_key, 300, str(balance)) # Cache with 5-minute TTL
    return balance
```

---

## 2. Reusable Checklist & Exit Criteria
*   [ ] Checked that all cache-aside operations define a default TTL.
*   [ ] Verified that fallback logic exists for cache timeouts or cluster connection failures.
*   [ ] Confirmed cache serialization uses standard JSON or binary protobufs.
