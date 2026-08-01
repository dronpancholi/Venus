# USPTCROS Session Management Policy
**Document Link:** [Session Management Policy](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/SESSION_MANAGEMENT_POLICY.md)

## 1. Session Lifetime Constants
* **Session Idle Timeout:** 15 minutes. Session is invalidated if no activity occurs.
* **Absolute Session Lifetime:** 8 hours. Re-authentication is required regardless of activity.
* **Concurrent Session Limit:** Maximum 2 concurrent active sessions per user account.

## 2. Session Token Storage & Constraints
* **Web Browsers:** Access tokens must be stored in memory. Refresh tokens must be stored in secure, `HttpOnly`, `Secure`, `SameSite=Strict` cookies.
* **Opaque Tokens:** Used for high-security endpoints. Opaque sessions are resolved in a fast-access Redis cache.

## 3. Session Revocation Pattern
On logoff, the session registry must invalidate tokens immediately:
```python
def invalidate_session(session_token: str, session_store) -> bool:
    # Mark token in Redis as blacklisted with TTL matching original expiration
    session_store.setex(f"blacklist:{session_token}", 3600, "revoked")
    return True
```
