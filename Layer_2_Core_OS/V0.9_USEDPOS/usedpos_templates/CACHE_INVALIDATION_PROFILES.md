# Cache Invalidation Profiles
**Document ID:** VENUS-STD-039
**Version:** 1.0.0
**Status:** Approved
**Effective Date:** 2026-06-26

## 1. Invalidation Profiles
To ensure consistency, Redis cache invalidation follows these rules:

| Key Pattern | Lifecycle TTL | Invalidation Trigger Event | Invalidation Method |
| :--- | :--- | :--- | :--- |
| `account:balance:{id}` | 300 Seconds | Transaction settled event | Explicit Key Delete |
| `user:profile:{id}` | 3,600 Seconds| User updates profile data | Explicit Key Delete |
| `system:config` | 86,400 Seconds| Configuration change saved | Publish Redis PubSub message |

---

## 2. Reusable Checklist & Exit Criteria
*   [ ] Checked that write operations include corresponding invalidation calls.
*   [ ] Verified that TTL configurations prevent cache-stampede anomalies.
*   [ ] Confirmed cache-clearing hooks execute in transactional blocks.
