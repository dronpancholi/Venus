# Distributed Locking (Redlock) Specification
**Document ID:** VENUS-STD-050
**Version:** 1.0.0
**Status:** Approved
**Effective Date:** 2026-06-26

## 1. Redlock Algorithm
To acquire a distributed lock safely across $N$ Redis masters, the lock must be acquired before timeout elapsed:

$$	ext{Lock Acquired} \iff 	ext{Acquired count} \ge \lfloor N / 2 floor + 1 \quad 	ext{and} \quad T_{elapsed} < T_{ttl} - \delta$$

Where:
- $T_{elapsed}$: Total time taken to acquire locks across nodes.
- $\delta$: Clock drift margin buffer.

## 2. Lock Acquisition Code
```python
# lock.py
import uuid

def acquire_lock(redis_nodes, resource: str, ttl: int) -> str:
    value = str(uuid.uuid4())
    acquired = 0
    for node in redis_nodes:
        if node.set(resource, value, px=ttl, nx=True):
            acquired += 1
    if acquired >= (len(redis_nodes) // 2) + 1:
        return value
    # Release if failed
    return ""
```

---

## 3. Reusable Checklist & Exit Criteria
*   [ ] Checked that release scripts execute check-and-delete commands atomically via Lua.
*   [ ] Verified lock timeouts prevent permanent system blockages.
*   [ ] Confirmed resource ownership tokens are verified prior to execution.
