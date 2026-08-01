# API Versioning Policy
**Document ID:** VENUS-STD-029
**Version:** 1.0.0
**Status:** Approved
**Effective Date:** 2026-06-26

## 1. Versioning Strategy
API versioning must be explicit, preventing regressions for consumers.

### 1.1 URI Path Versioning
Major API versions must be defined in the URI path:
```
https://api.project-venus.net/v1/transactions
https://api.project-venus.net/v2/transactions
```

### 1.2 Deprecation & Sunset Timeline
- **Deprecation**: Announced via the standard HTTP `Deprecation` header.
- **Sunset**: Target date defined in the HTTP `Sunset` header (minimum 90 days after deprecation).

```http
HTTP/1.1 200 OK
Deprecation: @1771142400
Sunset: Tue, 30 Jun 2026 23:59:59 GMT
```

---

## 2. Reusable Checklist & Exit Criteria
*   [ ] Checked that URI schemas contain a major version prefix.
*   [ ] Verified that deprecated APIs return standard header warnings.
*   [ ] Confirmed backward compatibility checks pass on patch revisions.
