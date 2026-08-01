# API Rate Limit & Quota Plan
**Document ID:** VENUS-STD-030
**Version:** 1.0.0
**Status:** Approved
**Effective Date:** 2026-06-26

## 1. Rate Limit Tiers
Rate limiting prevents system exhaustion. The sliding-window rate limit tiers are configured as:

| Tier | Window | Max Request Quota | Status on Exceeded |
| :--- | :--- | :--- | :--- |
| **Anonymous** | 1 Minute | 60 | HTTP 429 Too Many Requests |
| **Standard User** | 1 Minute | 1,000 | HTTP 429 Too Many Requests |
| **Enterprise Client**| 1 Minute | 10,000 | HTTP 429 Too Many Requests |

## 2. Redis Key Structure for Sliding Window
```
Key Format: rate_limit:{tier}:{user_id}:{timestamp_minute}
TTL: 120 seconds
```

---

## 3. Reusable Checklist & Exit Criteria
*   [ ] Checked that rate-limit values match target infrastructure boundaries.
*   [ ] Confirmed Redis rate limiter key structures utilize active TTL settings.
*   [ ] Verified fallback mechanisms preserve service flow if Redis is offline.
