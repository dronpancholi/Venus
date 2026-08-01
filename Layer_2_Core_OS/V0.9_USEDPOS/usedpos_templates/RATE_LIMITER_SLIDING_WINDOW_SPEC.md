# Rate Limiter Sliding Window Specification
**Document ID:** VENUS-STD-049
**Version:** 1.0.0
**Status:** Approved
**Effective Date:** 2026-06-26

## 1. Sliding Window Algorithm (Redis Sorted Set)
The rate limiter records timestamps inside a Redis Sorted Set (`zset`), pruning elements older than the window length:

```python
# rate_limiter.py
import time

def is_allowed(redis_client, user_id: str, limit: int, window: int) -> bool:
    now = time.time()
    key = f"limiter:{user_id}"
    clear_before = now - window
    
    pipeline = redis_client.pipeline()
    pipeline.zremrangebyscore(key, 0, clear_before)
    pipeline.zcard(key)
    pipeline.zadd(key, {str(now): now})
    pipeline.expire(key, window + 10)
    _, count, _, _ = pipeline.execute()
    
    return count < limit
```

---

## 2. Reusable Checklist & Exit Criteria
*   [ ] Checked that rate-limit checks run inside a Redis transaction pipeline.
*   [ ] Verified the prune queries prevent memory leak accumulation in zsets.
*   [ ] Confirmed clients receive correct retry-after header fields on failure.
